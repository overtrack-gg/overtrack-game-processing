import bisect
import datetime
import logging
import string
from collections import defaultdict, deque, namedtuple
from typing import Counter, List, Optional, Tuple, Dict, Any, Sequence

import numpy as np
import shortuuid
import Levenshtein as levenshtein
import typedload
from dataclasses import dataclass
from scipy.signal import medfilt

from overtrack.apex import data
from overtrack.apex.game.map import Location
from overtrack.apex.game.squad_summary.squad_summary_processor import PlayerStats
from overtrack.frame import Frame
from overtrack.util import arrayops, s2ts, textops

logger = logging.getLogger(__name__)


class Player:

    def __init__(self, name: Optional[str], champion: str, frames: List[Frame]):
        squad_summaries = [f.squad_summary for f in frames if 'squad_summary' in f]

        logger.info(f'Resolving player with estimated name="{name}", champion={champion} from {len(squad_summaries)} squad summary frames')
        self.name = name
        self.champion = champion

        if len(squad_summaries) and self.name:
            each_stats: Tuple[List[PlayerStats], List[PlayerStats], List[PlayerStats]] = ([], [], [])
            for summary in squad_summaries:
                for i in range(3):
                    each_stats[i].append(summary.player_stats[i])

            matches = [levenshtein.seqratio([name] * len(stats), [s.name for s in stats]) for stats in each_stats]
            best = arrayops.argmax(matches)
            if matches[best] < 0.85:
                logger.warning(f'Got potentially bad match {name}<->{[Counter(s.name for s in stat) for stat in each_stats]} ~ {best}: {matches[best]:1.2f}')
            else:
                logger.info(f'Got stats for {name} = {Counter(s.name for s in each_stats[best])}')

            own_stats = each_stats[best]

            # use name from stats screen as this is easier to OCR
            names = [s.name for s in own_stats]
            own_stats_name = levenshtein.median(names)
            if len(names) > 3 and own_stats_name != self.name:
                logger.warning(f'Updating name from game name to stats name: "{self.name}" -> "{own_stats_name}"')
                self.name = own_stats_name

            self.stats = self._get_mode_stats(own_stats)
        else:
            self.stats = None

        logger.info(f'Resolved to: {self}')

    def _get_mode_stats(self, stats: List[PlayerStats]) -> PlayerStats:
        mode = {}
        for name in 'kills', 'damage_dealt', 'survival_time', 'players_revived', 'players_respawned':
            values = [getattr(s, name) for s in stats]
            counter = Counter(v for v in values if v is not None)
            if len(counter):
                mode[name] = counter.most_common(1)[0][0]
            else:
                mode[name] = None
            logger.info(f'{self.name} > {name} : {counter} > {mode[name]}')
        return PlayerStats(
            self.name,
            **mode
        )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'name={repr(self.name)}, ' \
               f'champion={self.champion}, ' \
               f'stats={self.stats}' \
               f')'

    __repr__ = __str__

    def to_dict(self) -> Dict[str, Any]:
        stats = None
        if self.stats:
            stats = typedload.dump(self.stats)
            del stats['name']
        return {
            'name': self.name,
            'champion': self.champion,
            'stats': stats
        }


class Squad:

    def __init__(self, frames: List[Frame], debug: bool = False):
        self.squad = [f.squad for f in frames if 'squad' in f]
        logger.info(f'Processing squad from {len(self.squad)} squad frames')

        self.player = Player(
            self._get_name(),
            self._get_champion(),
            frames
        )
        self.squadmates = (
            Player(self._get_squadmate_name(0), self._get_squadmate_champion(0), frames),
            Player(self._get_squadmate_name(1), self._get_squadmate_champion(1), frames),
        )
        self.squad_kills = self._get_squad_kills(frames)

    def _get_name(self) -> Optional[str]:
        return levenshtein.median([s.name for s in self.squad if s.name])

    def _get_champion(self) -> Optional[str]:
        return self._get_matching_champion([s.champion for s in self.squad])

    def _get_squadmate_name(self, index: int) -> Optional[str]:
        return levenshtein.median([s.squadmate_names[index] for s in self.squad if s.squadmate_names[index]])

    def _get_squadmate_champion(self, index: int) -> Optional[str]:
        return self._get_matching_champion([s.squadmate_champions[index] for s in self.squad])

    def _get_matching_champion(self, arr: List[List[float]]) -> Optional[str]:
        # only look at data where we match at least one champions decently
        # This avoids looking at e.g. respawn screens
        matches = np.array([
            x for x in arr if np.max(x) > 0.9
        ])
        if len(matches) < 10:
            logger.warning(f'Could not identify champion - average matches={np.median(arr, axis=0)}')
            return None

        matches = np.percentile(
            matches,
            25,
            axis=0
        )
        match = arrayops.argmax(matches)
        champion = data.champions[list(data.champions.keys())[match]]
        if matches[match] > 0.9:
            logger.info(f'Got champion={champion}, match={matches[match]:1.4f}')
            return champion.name
        else:
            logger.warning(f'Could not identify champion - best={champion}, match={matches[match]:1.4f}')
            return None

    def _get_squad_kills(self, frames: List[Frame]) -> Optional[int]:
        squad_summary = [f.squad_summary for f in frames if 'squad_summary' in f]
        logger.info(f'Parsing squad kills from {len(squad_summary)} squad summary frames')
        squad_kills_counter = Counter([s.squad_kills for s in squad_summary if s.squad_kills is not None])
        if not len(squad_kills_counter):
            logger.warning(f'No squad kills parsed')
            return None
        else:
            squad_kills, count = squad_kills_counter.most_common(1)[0]
            if count != len(squad_summary):
                logger.warning(f'Got disagreeing placed counts: {squad_kills_counter}')
            logger.info(f'Got squad_kills={squad_kills}')
            return squad_kills

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'player={self.player}, ' \
               f'squadmates=({self.squadmates[0]}, {self.squadmates[1]})' \
               f')'

    __repr__ = __str__

    def to_dict(self) -> Dict[str, Any]:
        return {
            'player': self.player.to_dict(),
            'squadmates': (self.squadmates[0].to_dict(), self.squadmates[1].to_dict()),
            'squad_kills': self.squad_kills
        }


@dataclass
class CombatEvent:
    timestamp: float
    type: str
    inferred: bool = False
    weapon: Optional[str] = None
    location: Optional[Tuple[int, int]] = None


class Combat:

    def __init__(self, frames: List[Frame], debug: bool = False):
        self.combat_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'combat_log' in f]
        self.combat_data = [f.combat_log for f in frames if 'combat_log' in f]
        logger.info(f'Resolving combat from {len(self.combat_data)} combat frames')

        if debug:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.title('Combat Log Widths')
            for t, l in zip(self.combat_timestamp, self.combat_data):
                plt.scatter([t]*len(l.events), [e.width for e in l.events])
            plt.show()

        self.events = []

        self.eliminations = []
        self.knockdowns = []
        self.elimination_assists = []
        self.knockdown_assists = []

        seen_events = []
        for ts, combat in zip(self.combat_timestamp, self.combat_data):
            for event in combat.events:
                matching = [
                    other_ts for other_ts, other in seen_events if
                    ts - other_ts < 10 and event.type == other.type and abs(event.width - other.width) < 10
                ]
                if not len(matching):
                    # new event
                    logger.info(f'Got new event @ {ts:.1f}s: {event}')
                    combat_event = None
                    if event.type == 'ELIMINATED':
                        # If we see an ELIMINATED, it means we have also scored a knockdown on that player
                        # Because knocking and eliminating the last player is equivalent, only ELIMINATED will show
                        # Insert the missing knock down if needed
                        matching_knockdowns = [
                            other_ts for other_ts, other in seen_events if
                            ts - other_ts < 30 and other.type == 'KNOCKED DOWN' and abs(event.width - other.width) < 7
                        ]
                        if not len(matching_knockdowns):
                            # don't have a matching knockdown for this elim - create one now
                            knockdown = CombatEvent(ts, 'KNOCKED DOWN', inferred=True)
                            logger.info(f'Could not find knockdown for {event} - inserting {knockdown}')
                            self.knockdowns.append(knockdown)
                            self.events.append(knockdown)

                        # add after inferred event
                        combat_event = CombatEvent(ts, 'eliminated')
                        self.eliminations.append(combat_event)

                    elif event.type == 'KNOCKED DOWN':
                        combat_event = CombatEvent(ts, 'downed')
                        self.knockdowns.append(combat_event)
                    elif event.type == 'ASSIST, ELIMINATION':
                        combat_event = CombatEvent(ts, 'assist.eliminated')
                        self.elimination_assists.append(combat_event)
                    elif event.type == 'ASSIST, KNOCK DOWN':
                        combat_event = CombatEvent(ts, 'assist.downed')
                        self.knockdown_assists.append(combat_event)

                    assert combat_event

                    # add last so inferred events are inserted first
                    self.events.append(combat_event)

                else:
                    logger.info(f'Already seen event @ {ts:.1f}s: {event} {ts - matching[-1]:.1f}s ago')
                seen_events.append((ts, event))

        logger.info(
            f'Got '
            f'eliminations: {self.eliminations}, '
            f'knockdowns: {self.knockdowns}, '
            f'elimination_assists: {self.elimination_assists}, '
            f'knockdown_assists: {self.knockdown_assists}'
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'eliminations': typedload.dump(self.eliminations),
            'knockdowns': typedload.dump(self.knockdowns),
            'elimination_assists': typedload.dump(self.elimination_assists),
            'knockdown_assists': typedload.dump(self.knockdown_assists),
        }


@dataclass
class WeaponStats:
    weapon: str
    time_held: float = 0
    time_active: float = 0

    knockdowns: int = 0


class Weapons:

    def __init__(self, frames: List[Frame], combat: Combat, debug: bool = False):
        self.weapon_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'weapons' in f]
        self.weapon_data = [f.weapons for f in frames if 'weapons' in f]
        logger.info(f'Resolving weapons from {len(self.weapon_data)} weapon frames')

        weapon1 = self._get_weapon_map(0)
        weapon1_selected_vals = np.array([w.selected_weapons[0] for w in self.weapon_data])
        weapon1_selected = medfilt(weapon1_selected_vals, 3) < 200
        # ammo1 = [wep.clip if sel else np.nan for sel, wep in zip(weapon1_selected, self.weapon_data)]

        weapon2 = self._get_weapon_map(1)
        weapon2_selected_vals = np.array([w.selected_weapons[1] for w in self.weapon_data])
        weapon2_selected = medfilt(weapon2_selected_vals, 3) < 200
        # ammo2 = [wep.clip if sel else np.nan for sel, wep in zip(weapon2_selected, self.weapon_data)]

        have_weapon = np.convolve(np.not_equal(weapon1, -1) + np.not_equal(weapon2,  -1), np.ones((10,)), mode='valid')
        self.first_weapon_timestamp = self._get_firstweapon_pickup_time(have_weapon)

        self.weapon_stats: List[WeaponStats] = []
        self.selected_weapon_at: List[WeaponStats] = [None for _ in self.weapon_timestamp]
        self._add_weapon_stats(weapon1, weapon1_selected)
        self._add_weapon_stats(weapon2, weapon2_selected)
        self._add_combat_weaponstats(combat)
        self.weapon_stats = sorted(self.weapon_stats, key=lambda stat: (stat.knockdowns, stat.time_active), reverse=True)
        self.weapon_stats = [w for w in self.weapon_stats if w.time_held > 15 or w.knockdown_assists > 0 or w.knockdowns > 0]
        logger.info(f'Resolved weapon stats: {self.weapon_stats}')

        if debug:
            self._debug(combat, have_weapon, weapon1, weapon1_selected, weapon1_selected_vals, weapon2, weapon2_selected, weapon2_selected_vals)

    def _debug(self, combat, have_weapon, weapon1, weapon1_selected, weapon1_selected_vals, weapon2, weapon2_selected, weapon2_selected_vals):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.title('Selected Weapon')
        plt.plot(self.weapon_timestamp, weapon1_selected_vals)
        plt.plot(self.weapon_timestamp, weapon2_selected_vals)

        # plt.figure()
        # plt.title('Ammo')
        # plt.plot(self.weapon_timestamp, ammo1)
        # plt.plot(self.weapon_timestamp, ammo2)

        def make_weaponplot():
            for event in combat.events:
                c = None
                if event.type == 'KNOCKED DOWN':
                    c = 'red'
                elif event.type == 'ASSIST, ELIMINATION':
                    c = 'orange'
                if c:
                    plt.axvline(event.timestamp, color=c)
            for i, n in enumerate(data.weapon_names):
                plt.text(0, i + 0.25, n)

        plt.figure()
        plt.title('Weapon 1')
        plt.scatter(self.weapon_timestamp, weapon1)
        plt.plot(self.weapon_timestamp, weapon1_selected * 5)
        make_weaponplot()
        plt.figure()

        plt.title('Weapon 2')
        plt.scatter(self.weapon_timestamp, weapon2)
        plt.plot(self.weapon_timestamp, weapon2_selected * 5)
        make_weaponplot()

        plt.figure('Have Weapon')
        plt.plot(have_weapon)
        plt.axhline(6, color='r')
        plt.show()

    def _get_weapon_map(self, index: int) -> np.ndarray:
        normname = lambda n: textops.strip_string(n, string.ascii_uppercase + string.digits + '- ')

        weapon = np.full((len(self.weapon_data, )), fill_value=-1, dtype=np.int)
        name2index = {normname(n): i for i, n in enumerate(data.weapon_names)}
        for i, weapons in enumerate(self.weapon_data):
            name = weapons.weapon_names[index]
            ratio, match = textops.matches_ratio(
                normname(name),
                data.weapon_names
            )
            if ratio > 0.75:
                weapon[i] = name2index[match]
        return weapon

    def _get_firstweapon_pickup_time(self, have_weapon: np.ndarray) -> Optional[float]:
        have_weapon_inds = np.where(have_weapon > 6)[0]
        if len(have_weapon_inds):
            first_weapon_index = have_weapon_inds[0] + 5
            if 0 <= first_weapon_index < len(self.weapon_timestamp):
                ts = self.weapon_timestamp[first_weapon_index]
                logger.info(f'Got first weapon pickup at {s2ts(ts)}')
                return ts
            else:
                logger.warning(f'Got weapon pickup at invalid index: {first_weapon_index}')
                return None
        else:
            logger.warning(f'Did not see any weapons')
            return None

    def _add_weapon_stats(self, weapon: Sequence[int], weapon_selected: Sequence[bool]) -> None:
        weapon_stats_lookup = {
            s.weapon: s for s in self.weapon_stats
        }

        last: Optional[Tuple[float, int, bool]] = None
        for i, (ts, weapon_index, selected) in enumerate(zip(self.weapon_timestamp, weapon, weapon_selected)):
            if last is not None:
                weapon_name = data.weapon_names[weapon_index]
                weapon_stats = weapon_stats_lookup.get(weapon_name)
                if not weapon_stats:
                    weapon_stats = WeaponStats(weapon_name)
                    self.weapon_stats.append(weapon_stats)
                    weapon_stats_lookup[weapon_name] = weapon_stats

                if last[1] == weapon_index:
                    weapon_stats.time_held += ts - last[0]

                if selected:
                    self.selected_weapon_at[i] = weapon_stats
                    if last[2]:
                        weapon_stats.time_active += ts - last[0]

            last = ts, weapon_index, selected

    def _add_combat_weaponstats(self, combat: Combat):
        # n.b. the weapon is only relevant for knockdowns and elimination_assists, and only useful for knockdowns of these
        # knockdowns: we knocked someone down - don't know who will finish or how
        # elimination_assists: we eliminated someone ourselves with a weapon
        for event in combat.knockdowns:
            weapon_stats = self._get_weapon_at(event.timestamp)
            if weapon_stats:
                weapon_stats.knockdowns += 1
                event.weapon = weapon_stats.weapon

    def _get_weapon_at(self, timestamp: float, max_distance: float = 10) -> Optional[WeaponStats]:
        index = bisect.bisect(self.weapon_timestamp, timestamp) - 1
        if not (0 <= index < len(self.weapon_timestamp)):
            logger.error(f'Got invalid index trying to find weapon @ {timestamp:.1f}s', exc_info=True)
            return None

        logger.debug(
            f'Trying to resolve weapon at {timestamp:.1f}s - '
            f'got weapon index={index} -> {self.weapon_timestamp[index]:.1f}s'
        )
        for ofs in range(-5, 6):
            check = index + ofs
            if 0 <= check < len(self.weapon_timestamp):
                logger.debug(f'{ofs}: {check} {self.weapon_timestamp[check]} > {self.selected_weapon_at[check]}')

        for fan_out in range(20):
            for sign in -1, 1:
                check = index + sign * fan_out
                if 0 <= check < len(self.weapon_timestamp):
                    ts = self.weapon_timestamp[check]
                    distance = abs(timestamp - ts)
                    if distance < max_distance:
                        stat = self.selected_weapon_at[check]
                        if stat:
                            logger.debug(f'Found {stat} at {ts:.1f}s - distance {distance}')
                            return stat

        logger.warning(f'Could not find weapon for ts={timestamp:.1f}s')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'weapon_stats': typedload.dump(self.weapon_stats)
        }


class Route:

    def __init__(self, frames: List[Frame], weapons: Weapons, combat: Combat, debug: bool = False):
        self.locations = []
        recent = deque(maxlen=5)
        for i, frame in enumerate([f for f in frames if 'location' in f]):
            ts, location = frame.timestamp, frame.location
            if location.match > 0.85:
                continue

            if len(recent) >= recent.maxlen:
                last = np.mean(recent, axis=0)
                dist = np.sqrt(np.sum((np.array(last) - np.array(location.coordinates)) ** 2))
                if dist < 10:
                    # too close to last - filter data down
                    pass
                if dist < 150:
                    self.locations.append((ts - frames[0].timestamp, location.coordinates))
                else:
                    logger.warning(
                        f'Ignoring location {i}: {location} {dist:.1f} away from average {np.round(last, 1)}'
                    )
            recent.append(location.coordinates)

        logger.info(f'Processing route from {len(self.locations)} locations')
        if not len(self.locations):
            logger.warning(f'Got no locations')
            self.time_landed = None
            self.landed_location_index = None
            self.landed_location = None
            self.landed_name = None
            self.locations_visited = []
        else:
            if weapons.first_weapon_timestamp is not None:
                self.time_landed = weapons.first_weapon_timestamp
            else:
                logger.warning(f'Did not see weapon - assuming drop location = last location seen')
                self.time_landed = self.locations[-2][0]
            self.landed_location_index = max(0, min(bisect.bisect(self.locations, (self.time_landed, (0, 0))) + 1, len(self.locations) - 1))

            # average location of first 5 locations
            mean_location = np.mean([
                l[1] for l
                in self.locations[
                   max(0, self.landed_location_index - 2):
                   min(self.landed_location_index + 3, len(self.locations) - 1)
                   ]],
                axis=0
            )
            self.landed_location = int(mean_location[0]), int(mean_location[1])
            self.landed_name = data.map_locations[self.landed_location]

            self._process_locations_visited()

        for event in combat.events:
            event.location = self._get_location_at(event.timestamp)

        if debug:
            self._debug(frames)

    def _debug(self, frames):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.title('Location Match')
        plt.plot([f.location.match for f in frames if 'location' in f])

        import cv2
        from overtrack.apex.game.map import MapProcessor
        from colorsys import hsv_to_rgb
        image = MapProcessor.MAP.copy()
        for frame in [f for f in frames if 'location' in f]:
            h = 240 - 240 * frame.location.match
            c = np.array(hsv_to_rgb(h / 255, 1, 1))
            cv2.circle(
                image,
                frame.location.coordinates,
                5,
                c * 255,
                -1
            )
        plt.figure()
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), interpolation='none')

        plt.figure()
        plt.imshow(cv2.cvtColor(self.make_image(), cv2.COLOR_BGR2RGB), interpolation='none')
        plt.show()

    def _process_locations_visited(self):
        self.locations_visited = [self.landed_name]
        last_location = self.locations[self.landed_location_index][0], self.landed_name
        for ts, location in self.locations[self.landed_location_index + 1:]:
            location_name = data.map_locations[location]
            if location_name == 'Unknown':
                continue
            if location_name == last_location[1] and ts - last_location[0] > 30:
                if self.locations_visited[-1] != location_name:
                    self.locations_visited.append(location_name)
            elif location_name != last_location[1]:
                logger.info(f'Spent {ts - last_location[0]:.1f}s in {last_location[1]}')
                last_location = ts, location_name

    def make_image(self, combat: Optional[Combat] = None) -> np.ndarray:
        import cv2
        from overtrack.apex.game.map import MapProcessor
        image = MapProcessor.MAP.copy()
        last = self.locations[self.landed_location_index][1]
        for ts, l in self.locations[self.landed_location_index + 1:]:
            dist = np.sqrt(np.sum((np.array(last) - np.array(l)) ** 2))
            cv2.line(
                image,
                last,
                l,
                (0, 255, 0) if dist < 60 else (0, 0, 255),
                2,
                cv2.LINE_AA
            )
            last = l

        if self.landed_location:
            for t, c in (10, (0, 0, 0)), (2, (180, 0, 200)):
                cv2.putText(
                    image,
                    'Landed',
                    self.landed_location,
                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    1.2,
                    c,
                    t
                )

        if combat:
            for event in combat.events:
                location = self._get_location_at(event.timestamp)
                if location:
                    cv2.putText(
                        image,
                        'x',
                        location,
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        1.2,
                        (0, 0, 255),
                        1
                    )

        return image

    def _get_location_at(self, timestamp: float, max_distance: float = 20) -> Optional[Tuple[int, int]]:
        ts = [l[0] for l in self.locations]
        xy = [l[1] for l in self.locations]
        index = bisect.bisect(ts, timestamp) - 1
        if not (0 <= index < len(ts)):
            logger.error(f'Got invalid index trying to find location @ {timestamp:.1f}s', exc_info=True)
            return None

        logger.debug(
            f'Trying to resolve location at {timestamp:.1f}s - '
            f'got weapon index={index} -> {ts[index]:.1f}s'
        )
        for fan_out in range(20):
            for sign in -1, 1:
                check = index + sign * fan_out
                if 0 <= check < len(ts):
                    ts = ts[check]
                    distance = abs(timestamp - ts)
                    if distance < max_distance:
                        loc = xy[check]
                        logger.debug(f'Found {loc} at {ts:.1f}s - distance {distance}')
                        return loc

        logger.warning(f'Could not find location for ts={timestamp:.1f}s')
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'locations': self.locations,

            'time_landed': self.time_landed,
            'landed_location_index': self.landed_location_index,
            'landed_location': self.landed_location,
            'landed_name': self.landed_name,
            'locations_visited': self.locations_visited
        }


class ApexGame:

    def __init__(self, frames: List[Frame], key: str = None, debug: bool = False):
        your_squad_index = 0
        for i, f in enumerate(frames):
            if 'your_squad' in f:
                your_squad_index = i
                break

        logger.info(f'Processing game from {len(frames) - your_squad_index} frames and {your_squad_index} menu frames')

        self.player_name = levenshtein.median([f.apex_play_menu.player_name for f in frames if 'apex_play_menu' in f])
        logger.info(f'Resolved player name={repr(self.player_name)} from menu frames')

        self.frames = frames[your_squad_index:]

        self.timestamp = round(frames[0].timestamp, 2)
        if key:
            self.key = key
        else:
            datetimestr = datetime.datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d-%H-%M')
            self.key = f'{datetimestr}-{shortuuid.uuid()[:6]}'

        self.match_summary = [f.match_summary for f in self.frames if 'match_summary' in f]
        self.match_status = [f.match_status for f in self.frames if 'match_status' in f]

        self.squad = Squad(frames, debug=debug)
        self.combat = Combat(frames, debug=debug)
        self.weapons = Weapons(frames, self.combat, debug=debug)
        self.route: Route = Route(frames, self.weapons, self.combat, debug=debug)
        # self.stats = Stats(frames, self.squad)  # TODO: stats using match summary

        self.placed = self._get_placed(debug)
        self.kills = max(
            self._get_kills(debug) or 0,
            self.squad.player.stats.kills or 0 if self.squad.player.stats else 0,
            len(self.combat.eliminations),
            # self.stats.kills
        )

    def _get_placed(self, debug: bool = False) -> int:
        logger.info(f'Getting squad placement from {len(self.match_summary)} summary frames and {len(self.match_status)} match status frames')

        summary_placed: Optional[int] = None
        if len(self.match_summary):
            placed_counter = Counter([s.placed for s in self.match_summary])
            summary_placed, count = placed_counter.most_common(1)[0]
            if count != len(self.match_summary):
                logger.warning(f'Got disagreeing placed counts: {placed_counter}')

            logger.info(f'Got placed={summary_placed} from summary')
        else:
            logger.info(f'Did not get match summary')

        # TODO: detect CHAMPIONS OF THE ARENA and override placed as 1 if seen

        if len(self.match_status) > 10:
            # TODO: record this plot as edges
            squads_alive = arrayops.modefilt([s.squads_left for s in self.match_status], 5)
            last_squads_alive = squads_alive[-1]
            logger.info(f'Got placed={last_squads_alive} from last seen squads_alive')
            if summary_placed:
                if last_squads_alive != summary_placed:
                    logger.warning(f'Match summary placed={summary_placed} did not agree with last seen squads_alive={last_squads_alive} - using summary')
                return int(summary_placed)
            else:
                return int(last_squads_alive)
        else:
            logger.warning(f'Did not get any match summaries - using placed=20')
            return 20

    def _get_kills(self, debug: bool = False) -> int:
        summary_kills_seen = [s.xp_stats.kills for s in self.match_summary if s.xp_stats.kills is not None]
        kills_seen = [s.kills for s in self.match_status if s.kills]
        logger.info(
            f'Getting kills from {len(self.match_summary)} summary frames with {len(summary_kills_seen)} killcounts parsed '
            f'and {len(self.match_status)} match status frames with {len(kills_seen)} killcounts seen'
        )

        summary_kills: Optional[int] = None
        if len(summary_kills_seen):
            kills_counter = Counter(summary_kills_seen)
            summary_kills, count = kills_counter.most_common(1)[0]
            if count != len(summary_kills_seen):
                logger.warning(f'Got disagreeing summary kill counts: {kills_counter}')

        if len(kills_seen) > 10:
            kills_seen = arrayops.modefilt(kills_seen, 5)

            if debug:
                import matplotlib.pyplot as plt
                plt.figure()
                plt.title('Kills')
                if summary_kills is not None:
                    plt.axhline(summary_kills, color='r')
                plt.plot(kills_seen)
                plt.show()

            final_kills = kills_seen[-1]
            logger.info(f'Got final_kills={final_kills}')

            last_killcount = int(final_kills)
        else:
            logger.info(f'Only saw {len(kills_seen)} killcounts - using last_killcount=0')
            last_killcount = 0

        if summary_kills is not None:
            if summary_kills != last_killcount:
                logger.warning(f'Match summary kills={summary_kills} did not agree with last seen kills={last_killcount}')
            logger.info(f'Using summary_kills={summary_kills}')
            return summary_kills
        else:
            logger.warning(f'Did not get summary kills - using last seen kills={last_killcount}')
            return last_killcount

    @property
    def won(self) -> bool:
        return self.placed == 1

    @property
    def duration(self) -> float:
        return round(self.frames[-1].timestamp - self.frames[0].timestamp, 2)

    @property
    def season(self) -> int:
        for season in data.seasons:
            if season.start < self.timestamp < season.end:
                return season.index
        logger.error(f'Could not get season for {self.timestamp} - using {len(data.seasons)}', exc_info=True)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'key={self.key}, ' \
               f'duration={s2ts(self.duration)}, ' \
               f'frames={len(self.frames)}, ' \
               f'squad={self.squad}, ' \
               f'landed={self.route.landed_name}, ' \
               f'placed={self.placed}, ' \
               f'kills={self.kills}' \
               f')'

    __repr__ = __str__

    def to_dict(self) -> Dict[str, Any]:
        return {
            'key': self.key,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'season': self.season,

            # 'player_name': self.player_name,
            'kills': self.kills,
            'placed': self.placed,

            'squad': self.squad.to_dict(),
            'combat': self.combat.to_dict(),
            'route': self.route.to_dict(),
            'weapons': self.weapons.to_dict()
        }


def main() -> None:
    import requests
    import json
    from pprint import pprint
    from overtrack.util import referenced_typedload
    from overtrack.util.logging_config import config_logger

    config_logger('apex_game', logging.INFO, False)

    # data = requests.get('https://overtrack-games.sfo2.digitaloceanspaces.com/EeveeA-1716/2019-03-20-00-40-apex-8vSqu2.frames.json')
    with open('../../../dev/ERRORS/EeveeA-1716_2019-03-20-02-58-apex-ntTJtP.frames.json') as f:
        frames = referenced_typedload.load(json.load(f), List[Frame])

    game = ApexGame(frames)
    print(game)
    pprint(game.to_dict())

    from models.apex_game_summary import ApexGameSummary

    g = ApexGameSummary.create(game, -1)
    print(g)


if __name__ == '__main__':
    main()

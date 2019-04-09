import bisect
import datetime
import logging
import string
from collections import deque, Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import Levenshtein as levenshtein
import numpy as np
import shortuuid
import tabulate
import typedload
from dataclasses import dataclass, fields

from overtrack.apex import data
from overtrack.apex.game.match_summary.models import MatchSummary
from overtrack.apex.game.squad_summary.models import PlayerStats as SquadSummaryStats
from overtrack.frame import Frame
from overtrack.util import arrayops, s2ts, textops

logger = logging.getLogger(__name__)


@dataclass
class PlayerStats:
    kills: Optional[int]
    damage_dealt: Optional[int]
    survival_time: Optional[int]
    players_revived: Optional[int]
    players_respawned: Optional[int]

    def merge(self, other: 'PlayerStats'):
        for f in fields(self):
            name = f.name
            own_value = getattr(self, name)
            other_value = getattr(other, name)
            if own_value is None and other_value is not None:
                setattr(self, name, other_value)
            elif own_value is not None and other_value is not None:
                logger.warning(f'Got PlayerStats.{name} {own_value} != {other_value}')


class Player:
    logger = logging.getLogger('Player')

    def __init__(self,
                 name: Optional[str],
                 champion: str,
                 stats: List[SquadSummaryStats],
                 frames: List[Frame],
                 use_match_summary: bool = False):

        squad_summaries = [f.squad_summary for f in frames if 'squad_summary' in f]

        self.logger.info(
            f'Resolving player with estimated name="{name}", champion={champion} '
            f'from {len(squad_summaries)} squad summary frames'
        )
        self.name = name
        self.champion = champion

        if len(stats):
            # use name from stats screen as this is easier to OCR
            names = [s.name for s in stats]
            own_stats_name = levenshtein.median(names)
            if len(names) > 3 and own_stats_name != self.name and len(own_stats_name) > 3:
                self.logger.warning(f'Updating name from game name to stats name: "{self.name}" -> "{own_stats_name}"')
                self.name = own_stats_name

            self.stats = self._get_mode_stats(stats)
        else:
            self.stats = None

        if use_match_summary:
            summaries = [f.match_summary for f in frames if 'match_summary' in f]
            self.logger.info(f'Resolving stat from {len(summaries)} match summary (XP) frames')
            stats = self._get_mode_summary_stats(summaries)
            if stats:
                if self.stats is None:
                    self.logger.info(f'Using stats from summary: {stats}')
                    self.stats = stats
                elif self.stats != stats:
                    self.logger.warning(f'Merging squad stats {self.stats} with summary stats {stats}')
                    self.stats.merge(stats)
                else:
                    self.logger.info(f'Squad stats and summary stats agree')

        self.logger.info(f'Resolved to: {self}')

    def _get_mode_stats(self, stats: List[SquadSummaryStats]) -> PlayerStats:
        mode = {}
        for name in 'kills', 'damage_dealt', 'survival_time', 'players_revived', 'players_respawned':
            values = [getattr(s, name) for s in stats]
            counter = Counter([v for v in values if v is not None])
            if len(counter):
                mode[name] = counter.most_common(1)[0][0]
            else:
                mode[name] = None
            self.logger.info(f'{self.name} > {name} : {counter} > {mode[name]}')
        return PlayerStats(
            **mode
        )

    def _get_mode_summary_stats(self, summaries: List[MatchSummary]) -> PlayerStats:
        return self._get_mode_stats([
            SquadSummaryStats(
                name='',
                kills=s.xp_stats.kills,
                damage_dealt=s.xp_stats.damage_done,
                survival_time=s.xp_stats.time_survived,
                players_revived=s.xp_stats.revive_ally,
                players_respawned=s.xp_stats.respawn_ally
            ) for s in summaries
        ])

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
        return {
            'name': self.name,
            'champion': self.champion,
            'stats': stats
        }


class Squad:
    logger = logging.getLogger('Squad')

    def __init__(self, frames: List[Frame], menu_names: List[str], debug: Union[bool, str]= False):
        self.squad = [f.squad for f in frames if 'squad' in f]
        self.logger.info(f'Processing squad from {len(self.squad)} squad frames')

        names = [
            self._get_name(menu_names),
            self._get_squadmate_name(0),
            self._get_squadmate_name(1)
        ]
        champions = [
            self._get_champion(debug),
            self._get_squadmate_champion(0, debug),
            self._get_squadmate_champion(1, debug)
        ]

        squad_summaries = [f.squad_summary for f in frames if 'squad_summary' in f]
        if len(squad_summaries):
            self.logger.info(f'Resolving players from {len(squad_summaries)} squad summary frames')
            all_player_stats: List[List[SquadSummaryStats]] = [[], [], []]
            for summary in squad_summaries:
                for i in range(3):
                    all_player_stats[i].append(summary.player_stats[i])

            self.player = None
            self.squadmates = (None, None)
            matches = []
            for name in names:
                matches.append([])
                for player_stats in all_player_stats:
                    matches[-1].append(levenshtein.seqratio([name] * len(player_stats), [s.name for s in player_stats]))

            table = [[names[i]] + matches[i] for i in range(3)]
            headers = [levenshtein.median([s.name for s in stats]) for stats in all_player_stats]
            self.logger.info(f'Got name/stat matches:\n{tabulate.tabulate(table, headers=headers)}')

            matches = np.array(matches)
            for i in range(3):
                names_index, stats_index = np.unravel_index(np.argmax(matches), matches.shape)
                match = matches[names_index, stats_index]
                name = names[names_index]
                champion = champions[names_index]
                stats = all_player_stats[stats_index]
                if match > 0.75:
                    self.logger.info(f'Matched {name} <-> {headers[stats_index]}: {match:1.2f} - champion={champion}')
                else:
                    self.logger.warning(
                        f'Got potentially bad match {name}<->{[Counter(s.name for s in stats)]}: {match:1.2f} - '
                        f'champion={champion} ({2-i} other options)'
                    )
                matches[names_index, :] = -1
                matches[:, stats_index] = -1

                player = Player(
                    name,
                    champion,
                    stats,
                    frames,
                    use_match_summary=names_index == 0
                )
                if names_index == 0:
                    self.player = player
                elif names_index == 1:
                    self.squadmates = (player, self.squadmates[1])
                else:
                    self.squadmates = (self.squadmates[0], player)
        else:
            logger.info(f'Did not get any squad summary frames')

            self.player = Player(
                names[0],
                champions[0],
                [],
                frames,
                use_match_summary=True
            )
            self.squadmates = (
                Player(names[1], champions[1], [], frames),
                Player(names[2], champions[2], [], frames),
            )

        self.squad_kills = self._get_squad_kills(frames)

        if debug is True or debug == self.__class__.__name__:
            import matplotlib.pyplot as plt

            ts = [frame.timestamp - frames[0].timestamp for frame in frames if 'squad' in frame]

            def make_champion_plot(vals):
                for i, (s, c) in enumerate(data.champions.items()):
                    plt.plot(ts, [v[i] for v in vals], label=s)
                plt.legend()

            plt.figure()
            plt.title('Player Champion')
            make_champion_plot([s.champion for s in self.squad])

            plt.figure()
            plt.title('Squadmate 1 Champion')
            make_champion_plot([s.squadmate_champions[0] for s in self.squad])

            plt.figure()
            plt.title('Squadmate 2 Champion')
            make_champion_plot([s.squadmate_champions[1] for s in self.squad])

            plt.show()

    def _median_name(self, names: List[str]):
        name = levenshtein.median(names)
        self.logger.debug(f'Resolving median name {Counter(names)}/{len(names)} -> {name}')
        return name

    def _get_name(self, menu_names: List[str]) -> Optional[str]:
        return self._median_name([s.name for s in self.squad if s.name] + menu_names)

    def _get_champion(self, debug: Union[bool, str] = False) -> Optional[str]:
        return self._get_matching_champion([s.champion for s in self.squad], debug)

    def _get_squadmate_name(self, index: int) -> Optional[str]:
        return self._median_name([s.squadmate_names[index] for s in self.squad if s.squadmate_names[index]])

    def _get_squadmate_champion(self, index: int, debug: Union[bool, str] = False) -> Optional[str]:
        return self._get_matching_champion([s.squadmate_champions[index] for s in self.squad], debug)

    def _get_matching_champion(self, arr: List[List[float]], debug: Union[bool, str] = False ) -> Optional[str]:
        champions = list(data.champions.keys())

        current_champ = np.full((len(arr), ), fill_value=np.nan, dtype=np.float)
        for i, vals in enumerate(arr):
            am = int(np.argmax(vals))
            if vals[am] > 0.9:
                current_champ[i] = am

        current_champ_where_known = current_champ[~np.isnan(current_champ)].astype(np.int)

        if len(current_champ_where_known) <= 3:
            self.logger.warning(f'Could not identify champion - average matches={np.nanmedian(arr, axis=0)}')
            return None

        current_champ_where_known = arrayops.modefilt(current_champ_where_known, 9)

        if debug is True or debug == self.__class__.__name__:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.title('Champion Index')
            plt.plot(current_champ_where_known)
            plt.show()

        champion_changed = np.where(current_champ_where_known[1:] != current_champ_where_known[:-1])[0]
        if len(champion_changed) and 1 < champion_changed[0] < len(current_champ_where_known):
            before = champions[arrayops.most_common(current_champ_where_known[:champion_changed[0] - 1])]
            count_before = champion_changed[0]

            after = champions[arrayops.most_common(current_champ_where_known[champion_changed[0] + 1:])]
            count_after = len(current_champ_where_known) - count_before

            if before != after:
                if count_before > count_after:
                    self.logger.warning(
                        f'Champion changed from {before} -> {after} at {count_before} / {len(current_champ_where_known)} - '
                        f'using first champion'
                    )
                    return before
                else:
                    self.logger.warning(
                        f'Champion changed from {before} -> {after} at {count_before} / {len(current_champ_where_known)} - '
                        f'using second champion'
                    )
                    return after

        champion, count = Counter(current_champ_where_known).most_common(1)[0]
        champion = champions[champion]
        self.logger.info(f'Got champion={champion} ~ {count}')
        return champion

    def _get_matching_stats(self, name: str, player_summary_stats: List[List[SquadSummaryStats]]) -> List[SquadSummaryStats]:
        self.logger.info(
            f'Trying to match player name {name} against {len(player_summary_stats)} sets of stats: '
            f'{[levenshtein.median([s.name for s in stats]) for stats in player_summary_stats]}'
        )
        matches = [levenshtein.seqratio([name] * len(stats), [s.name for s in stats]) for stats in player_summary_stats]
        best = arrayops.argmax(matches)
        match = player_summary_stats[best]
        if matches[best] < 0.85:
            self.logger.warning(
                f'Got potentially bad match {name}<->{[Counter(s.name for s in stat) for stat in player_summary_stats]} ~ '
                f'{best}: {matches[best]:1.2f}'
            )
        else:
            self.logger.info(f'Got stats for {name} = {Counter(s.name for s in player_summary_stats[best])}')
        player_summary_stats.remove(match)
        return match

    def _get_squad_kills(self, frames: List[Frame]) -> Optional[int]:
        squad_summary = [f.squad_summary for f in frames if 'squad_summary' in f]
        self.logger.info(f'Parsing squad kills from {len(squad_summary)} squad summary frames')
        squad_kills_counter = Counter([s.squad_kills for s in squad_summary if s.squad_kills is not None])
        if not len(squad_kills_counter):
            self.logger.warning(f'No squad kills parsed')
            return None
        else:
            squad_kills, count = squad_kills_counter.most_common(1)[0]
            if count != len(squad_summary):
                self.logger.warning(f'Got disagreeing placed counts: {squad_kills_counter}')
            self.logger.info(f'Got squad_kills={squad_kills}')
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

    logger = logging.getLogger('Combat')

    def __init__(self, frames: List[Frame], placed: int, squad: Squad, debug: Union[bool, str]= False):
        self.combat_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'combat_log' in f]
        self.combat_data = [f.combat_log for f in frames if 'combat_log' in f]
        self.logger.info(f'Resolving combat from {len(self.combat_data)} combat frames')

        if debug is True or debug == self.__class__.__name__:
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
                    self.logger.info(f'Got new event @ {ts:.1f}s: {event}')
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
                            knockdown = CombatEvent(ts, 'downed', inferred=True)
                            self.logger.info(f'Could not find knockdown for {event} - inserting {knockdown}')
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
                    self.logger.info(f'Already seen event @ {ts:.1f}s: {event} {ts - matching[-1]:.1f}s ago')
                seen_events.append((ts, event))

        if placed == 1 and squad.player.stats and squad.player.stats.kills and squad.player.stats.kills > len(self.eliminations):
            last_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'match_status' in f][-1]
            self.logger.warning(
                f'Got won game with {squad.player.stats.kills} kills, but only saw {len(self.eliminations)} eliminations from combat - '
                f'Trying to resolve final fight (ended {s2ts(last_timestamp)})'
            )
            # convert all recent kockdowns to elims
            for knock in self.knockdowns:
                print(last_timestamp - knock.timestamp)
                if last_timestamp - knock.timestamp < 60:
                    self.logger.warning(f'Adding elim for final-fight knockdown @{s2ts(knock.timestamp)}')
                    self.eliminations.append(CombatEvent(last_timestamp, 'eliminated'))

            if squad.player.stats.kills > len(self.eliminations):
                # still lacking on elims - this player got the final kill
                self.logger.warning(f'Still have outstanding kills - Adding down+elim for final kill of the match')
                self.knockdowns.append(CombatEvent(last_timestamp, 'downed'))
                self.eliminations.append(CombatEvent(last_timestamp, 'eliminated'))

        self.logger.info(
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
    logger = logging.getLogger('Weapons')

    def __init__(self, frames: List[Frame], combat: Combat, debug: Union[bool, str]= False):
        self.weapon_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'weapons' in f]
        self.weapon_data = [f.weapons for f in frames if 'weapons' in f]
        self.logger.info(f'Resolving weapons from {len(self.weapon_data)} weapon frames')

        weapon1 = self._get_weapon_map(0)
        weapon1_selected_vals = np.array([w.selected_weapons[0] for w in self.weapon_data])
        weapon1_selected = (arrayops.medfilt(weapon1_selected_vals, 3) < 200) & np.not_equal(weapon1, -1)
        # ammo1 = [wep.clip if sel else np.nan for sel, wep in zip(weapon1_selected, self.weapon_data)]

        weapon2 = self._get_weapon_map(1)
        weapon2_selected_vals = np.array([w.selected_weapons[1] for w in self.weapon_data])
        weapon2_selected = (arrayops.medfilt(weapon2_selected_vals, 3) < 200) & np.not_equal(weapon2, -1)
        # ammo2 = [wep.clip if sel else np.nan for sel, wep in zip(weapon2_selected, self.weapon_data)]

        have_weapon = np.convolve(np.not_equal(weapon1, -1) + np.not_equal(weapon2,  -1), np.ones((10,)), mode='valid')
        self.first_weapon_timestamp = self._get_firstweapon_pickup_time(have_weapon)

        self.weapon_stats: List[WeaponStats] = []
        self.selected_weapon_at: List[Optional[WeaponStats]] = [None for _ in self.weapon_timestamp]
        self._add_weapon_stats(weapon1, weapon1_selected)
        self._add_weapon_stats(weapon2, weapon2_selected)
        self._add_combat_weaponstats(combat)
        self.weapon_stats = sorted(self.weapon_stats, key=lambda stat: (stat.knockdowns, stat.time_active), reverse=True)
        self.weapon_stats = [w for w in self.weapon_stats if w.time_held > 15 or w.knockdowns > 0]
        self.logger.info(f'Resolved weapon stats: {self.weapon_stats}')

        if debug is True or debug == self.__class__.__name__:
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
        have_weapon_inds = np.where(have_weapon > 4)[0]
        if len(have_weapon_inds):
            first_weapon_index = have_weapon_inds[0] + 5
            if 0 <= first_weapon_index < len(self.weapon_timestamp):
                ts = self.weapon_timestamp[first_weapon_index]
                self.logger.info(f'Got first weapon pickup at {s2ts(ts)}')
                return ts
            else:
                self.logger.warning(f'Got weapon pickup at invalid index: {first_weapon_index}')
                return None
        else:
            self.logger.warning(f'Did not see any weapons')
            return None

    def _add_weapon_stats(self, weapon: Sequence[int], weapon_selected: Sequence[bool]) -> None:
        weapon_stats_lookup = {
            s.weapon: s for s in self.weapon_stats
        }

        last: Optional[Tuple[float, int, bool]] = None
        for i, (ts, weapon_index, selected) in enumerate(zip(self.weapon_timestamp, weapon, weapon_selected)):
            if weapon_index == -1:
                continue
            if last is not None:
                weapon_name = data.weapons[weapon_index].name
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
            self.logger.error(f'Got invalid index trying to find weapon @ {timestamp:.1f}s', exc_info=True)
            return None

        self.logger.debug(
            f'Trying to resolve weapon at {timestamp:.1f}s - '
            f'got weapon index={index} -> {self.weapon_timestamp[index]:.1f}s'
        )
        for ofs in range(-5, 6):
            check = index + ofs
            if 0 <= check < len(self.weapon_timestamp):
                weap = self.selected_weapon_at[check]
                self.logger.debug(f'ofs={ofs:+d} > ind={check} ts={self.weapon_timestamp[check]:.1f} > weap={weap.weapon if weap else None}')

        for fan_out in range(20):
            for sign in -1, 1:
                check = index + sign * fan_out
                if 0 <= check < len(self.weapon_timestamp):
                    ts = self.weapon_timestamp[check]
                    distance = abs(timestamp - ts)
                    if distance < max_distance:
                        stat = self.selected_weapon_at[check]
                        if stat:
                            self.logger.debug(f'Found {stat} at {ts:.1f}s - distance {distance}')
                            return stat

        self.logger.warning(f'Could not find weapon for ts={timestamp:.1f}s')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'weapon_stats': typedload.dump(self.weapon_stats)
        }


class Route:
    logger = logging.getLogger('Route')

    def __init__(self, frames: List[Frame], weapons: Weapons, combat: Combat, debug: Union[bool, str]= False):
        self.locations = []
        recent = deque(maxlen=5)
        for i, frame in enumerate([f for f in frames if 'location' in f]):
            ts, location = frame.timestamp, frame.location
            if location.match > 0.7:
                continue

            if len(recent) >= recent.maxlen:
                last = np.mean(recent, axis=0)
                dist = np.sqrt(np.sum((np.array(last) - np.array(location.coordinates)) ** 2))
                if dist < 150:
                    self.locations.append((ts - frames[0].timestamp, location.coordinates))
                else:
                    self.logger.warning(
                        f'Ignoring location {i}: {location} {dist:.1f} away from average {np.round(last, 1)}'
                    )
            recent.append(location.coordinates)

        self.logger.info(f'Processing route from {len(self.locations)} locations')
        if not len(self.locations):
            self.logger.warning(f'Got no locations')
            self.time_landed = None
            self.landed_location_index = None
            self.landed_location = None
            self.landed_name = None
            self.locations_visited = []
        else:
            if weapons.first_weapon_timestamp is not None:
                self.time_landed = weapons.first_weapon_timestamp
            else:
                self.logger.warning(f'Did not see weapon - assuming drop location = last location seen')
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

        if debug is True or debug == self.__class__.__name__:
            self._debug(frames)

    def _debug(self, frames):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.title('Location Match')
        plt.plot([f.location.match for f in frames if 'location' in f])

        import cv2
        from overtrack.apex.game.map.map_processor import MapProcessor
        from colorsys import hsv_to_rgb
        image = MapProcessor.MAP.copy()
        for frame in [f for f in frames if 'location' in f]:
            h = 240 - 240 * frame.location.match
            c = np.array(hsv_to_rgb(h / 255, 1, 1))
            cv2.circle(
                image,
                frame.location.coordinates,
                1,
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
                self.logger.info(f'Spent {ts - last_location[0]:.1f}s in {last_location[1]}')
                last_location = ts, location_name

    def make_image(self, combat: Optional[Combat] = None) -> np.ndarray:
        import cv2
        from overtrack.apex.game.map.map_processor import MapProcessor
        image = MapProcessor.MAP.copy()
        last = self.locations[self.landed_location_index][1]
        for ts, l in self.locations[self.landed_location_index + 1:]:
            dist = np.sqrt(np.sum((np.array(last) - np.array(l)) ** 2))
            cv2.line(
                image,
                last,
                l,
                (0, 255, 0) if dist < 60 else (0, 0, 255),
                1,
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

    def _get_location_at(self, timestamp: float, max_distance: float = 120) -> Optional[Tuple[int, int]]:
        ts = [l[0] for l in self.locations]
        xy = [l[1] for l in self.locations]
        index = min(max(0, bisect.bisect(ts, timestamp) - 1), len(ts) - 1)
        if not (0 <= index < len(ts)):
            self.logger.error(f'Got invalid index {index} trying to find location @ {timestamp:.1f}s', exc_info=True)
            return None

        self.logger.debug(
            f'Trying to resolve location at {timestamp:.1f}s - '
            f'got location index={index} -> {ts[index]:.1f}s'
        )
        for fan_out in range(100):
            for sign in -1, 1:
                check = index + sign * fan_out
                if 0 <= check < len(ts):
                    ats = ts[check]
                    distance = abs(timestamp - ats)
                    if distance < max_distance:
                        loc = xy[check]
                        if distance < 30:
                            level = logging.DEBUG
                        else:
                            level = logging.WARNING
                        self.logger.log(level, f'Found {loc} at {ats:.1f}s - distance {distance}s')
                        return loc

        self.logger.warning(f'Could not find location for ts={timestamp:.1f}s')
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
    logger = logging.getLogger('ApexGame')

    def __init__(self, frames: List[Frame], key: str = None, debug: Union[bool, str]= False):
        your_squad_index = 0
        for i, f in enumerate(frames):
            if 'your_squad' in f:
                your_squad_index = i
                break

        self.logger.info(f'Processing game from {len(frames) - your_squad_index} frames and {your_squad_index} menu frames')

        menu_names = [f.apex_play_menu.player_name for f in frames if 'apex_play_menu' in f]
        self.player_name = levenshtein.median(menu_names)
        self.logger.info(f'Resolved player name={repr(self.player_name)} from menu frames')

        end_index = len(frames) - 1
        for i in range(end_index, 0, -1):
            if 'squad_summary' in frames[i]:
                self.logger.info(
                    f'Found last squad_summary at {i} -> {s2ts(frames[i].timestamp - frames[your_squad_index].timestamp)}: '
                    f'pulling end back from {end_index} -> {s2ts(frames[-1].timestamp - frames[your_squad_index].timestamp)}. '
                    f'{end_index - i} frames dropped'
                )
                end_index = i
                break
            elif 'match_status' in frames[i]:
                self.logger.info(
                    f'Found last match_status at {i} -> {s2ts(frames[i].timestamp - frames[your_squad_index].timestamp)}: '
                    f'pulling end back from {end_index} -> {s2ts(frames[-1].timestamp - frames[your_squad_index].timestamp)}. '
                    f'{(end_index + 10) - i} frames dropped'
                )
                end_index = i + 10
                break
        else:
            logger.warning(f'Did not see squad_summary or match_status - not trimming')

        self.frames = frames[your_squad_index:end_index]
        self.timestamp = round(self.frames[0].timestamp, 2)
        if key:
            self.key = key
        else:
            datetimestr = datetime.datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d-%H-%M')
            self.key = f'{datetimestr}-{shortuuid.uuid()[:6]}'

        self.match_summary_frames = [f.match_summary for f in self.frames if 'match_summary' in f]
        self.squad_summary_frames = [f.squad_summary for f in self.frames if 'squad_summary' in f]
        self.match_status_frames = [f.match_status for f in self.frames if 'match_status' in f]

        self.placed = self._get_placed(debug)

        self.squad = Squad(self.frames, menu_names, debug=debug)
        self.combat = Combat(self.frames, self.placed, self.squad, debug=debug)
        self.weapons = Weapons(self.frames, self.combat, debug=debug)
        self.route: Route = Route(self.frames, self.weapons, self.combat, debug=debug)
        # self.stats = Stats(frames, self.squad)  # TODO: stats using match summary

        self.kills = max(
            self._get_kills(debug) or 0,
            self.squad.player.stats.kills or 0 if self.squad.player.stats else 0,
            len(self.combat.eliminations),
            # self.stats.kills
        )

    def _get_placed(self, debug: Union[bool, str]= False) -> int:
        self.logger.info(f'Getting squad placement from '
                         f'{len(self.match_summary_frames)} summary frames, '
                         f'{len(self.squad_summary_frames)} squad summary frames, '
                         f'{len(self.match_status_frames)} match status frames')

        match_summary_placed: Optional[int] = None
        if len(self.match_summary_frames):
            placed_counter = Counter([s.placed for s in self.match_summary_frames])
            match_summary_placed, count = placed_counter.most_common(1)[0]
            if count != len(self.match_summary_frames):
                self.logger.warning(f'Got disagreeing match summary placed counts: {placed_counter}')

            self.logger.info(f'Got match summary > placed={match_summary_placed} from summary')
        else:
            self.logger.info(f'Did not get match summary')

        squad_summary_placed: Optional[int] = None
        if len(self.squad_summary_frames):
            champions = np.mean([s.champions for s in self.squad_summary_frames])
            if champions > 0.75:
                logger.info(f'Got champions={champions:1.1f} from squad summary - using placed = 1')
                return 1

            placed_vals = [s.placed for s in self.squad_summary_frames if s.placed]
            if len(placed_vals):
                placed_counter = Counter(placed_vals)
                squad_summary_placed, count = placed_counter.most_common(1)[0]
                if count != len(self.squad_summary_frames):
                    self.logger.warning(f'Got disagreeing squad summary placed counts: {placed_counter}')

                self.logger.info(f'Got squad summary > placed = {squad_summary_placed}')

        if len(self.match_status_frames) > 10:
            # TODO: record this plot as edges
            squads_alive = arrayops.modefilt([s.squads_left for s in self.match_status_frames], 5)
            last_squads_alive = int(squads_alive[-1])
            self.logger.info(f'Got last seen squads alive = {last_squads_alive}')
        else:
            self.logger.warning(f'Did not get any match summaries - last seen squads alive = 20')
            last_squads_alive = 20

        if match_summary_placed and squad_summary_placed:
            if match_summary_placed != squad_summary_placed:
                logger.error(f'Got match summary > placed: {match_summary_placed} != squad summary > placed: {squad_summary_placed}')

        if match_summary_placed:
            logger.info(f'Using placed from match summary: {match_summary_placed}')
            return match_summary_placed
        elif squad_summary_placed:
            logger.info(f'Using placed from squad summary: {squad_summary_placed}')
            return squad_summary_placed
        else:
            logger.info(f'Using placed from last squads alive: {last_squads_alive}')
            return last_squads_alive

    def _get_kills(self, debug: Union[bool, str]= False) -> int:
        summary_kills_seen = [s.xp_stats.kills for s in self.match_summary_frames if s.xp_stats.kills is not None]
        kills_seen = [s.kills for s in self.match_status_frames if s.kills]
        self.logger.info(
            f'Getting kills from {len(self.match_summary_frames)} summary frames with {len(summary_kills_seen)} killcounts parsed '
            f'and {len(self.match_status_frames)} match status frames with {len(kills_seen)} killcounts seen'
        )

        summary_kills: Optional[int] = None
        if len(summary_kills_seen):
            kills_counter = Counter(summary_kills_seen)
            summary_kills, count = kills_counter.most_common(1)[0]
            if count != len(summary_kills_seen):
                self.logger.warning(f'Got disagreeing summary kill counts: {kills_counter}')

        if len(kills_seen) > 10:
            kills_seen = arrayops.modefilt(kills_seen, 5)

            if debug is True or debug == self.__class__.__name__:
                import matplotlib.pyplot as plt
                plt.figure()
                plt.title('Kills')
                if summary_kills is not None:
                    plt.axhline(summary_kills, color='r')
                plt.plot(kills_seen)
                plt.show()

            final_kills = kills_seen[-1]
            self.logger.info(f'Got final_kills={final_kills}')

            last_killcount = int(final_kills)
        else:
            self.logger.info(f'Only saw {len(kills_seen)} killcounts - using last_killcount=0')
            last_killcount = 0

        if summary_kills is not None:
            if summary_kills != last_killcount:
                self.logger.warning(f'Match summary kills={summary_kills} did not agree with last seen kills={last_killcount}')
            self.logger.info(f'Using summary_kills={summary_kills}')
            return summary_kills
        else:
            self.logger.warning(f'Did not get summary kills - using last seen kills={last_killcount}')
            return last_killcount

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp)

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
        self.logger.error(f'Could not get season for {self.timestamp} - using {len(data.seasons)}', exc_info=True)

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

import bisect
import datetime
import logging
import string
from collections import defaultdict
from typing import Counter, List, Optional, Tuple, Dict, Any

import numpy as np
import shortuuid
import Levenshtein as levenshtein
import typedload

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
            logger.error(f'Could not identify champion - average matches={np.median(arr, axis=0)}')
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
            logger.error(f'Could not identify champion - best={champion}, match={matches[match]:1.4f}')
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


class Weapons:
    def __init__(self, frames: List[Frame], debug: bool = False):
        self.weapon_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'weapons' in f]
        self.have_weapon = [self._weapon_names_valid(f.weapons.weapon_names) for f in frames if 'weapons' in f]

        self.first_weapon_timestamp = self._get_first_weapon_timestamp(debug)

    def _get_first_weapon_timestamp(self, debug: bool = False) -> Optional[float]:
        # use first weapon pickup to detect when not dropping
        # TODO: use the "Hold (|) Freelook" or similar to detect when dropping
        weapon_timestamp = self.weapon_timestamp[:-9]
        have_weapon = np.convolve(self.have_weapon, np.ones((10,)), mode='valid')

        if debug:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.title('Have Weapon (convolved)')
            plt.plot(have_weapon)
            plt.show()

        have_weapon_index = np.where(have_weapon > 6)[0]
        if len(have_weapon_index):
            first_weapon_index = have_weapon_index[0] + 2
            first_weapon_timestamp = weapon_timestamp[first_weapon_index]

            logger.info(f'Got first weapon pickup at {s2ts(first_weapon_timestamp)}')
            return first_weapon_timestamp
        else:
            logger.warning(f'Did not see any weapons')
            return None

    def _weapon_names_valid(self, weapon_names: Tuple[str, str]) -> bool:
        for name in weapon_names:
            name = textops.strip_string(name, string.ascii_uppercase + string.digits + '- ')
            if len(name) < 3:
                continue
            ratio, match = textops.matches_ratio(
                name,
                data.weapon_names
            )
            if ratio > 0.75:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        # TODO: Weapons.to_dict
        return {}


class Route:

    def __init__(self, frames: List[Frame], weapons: Weapons, debug: bool = False):

        if debug:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.title('Location Match')
            plt.plot([f.location.match for f in frames if 'location' in f])
            plt.show()

        self.locations = []
        last: Optional[Location] = None
        last_valid = 100
        for frame in [f for f in frames if 'location' in f]:
            ts, location = frame.timestamp, frame.location
            if location.match > 0.75:
                continue
            if not last:
                dist = 0
            else:
                dist = np.sqrt(np.sum((np.array(last.coordinates) - np.array(location.coordinates)) ** 2))
            if last_valid < 10:
                if dist < 50:
                    last_valid += 1
                    if last_valid == 10:
                        logger.warning(f'Location became valid again: {location}')
            elif dist < 50:
                self.locations.append((ts - frames[0].timestamp, location.coordinates))
            else:
                logger.warning(
                    f'Ignoring location {dist:.1f} away from previous: {location} - '
                    f'invalidating location until we see 10 locations within close proximity'
                )
                last_valid = 0
            last = location

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

            # TODO: average location of first 5 or so locations
            self.landed_location = self.locations[self.landed_location_index][1]
            self.landed_name = data.map_locations[self.landed_location]

            self._process_locations_visited()

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

    def show(self):
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
        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), interpolation='none')
        plt.show()

    def to_dict(self) -> Dict[str, Any]:
        # TODO: Route.to_dict
        return {}


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
        self.weapons = Weapons(frames, debug=debug)
        self.route = Route(frames, self.weapons, debug=debug)
        # self.stats = Stats(frames, self.squad)  # TODO: stats using match summary

        self.placed = self._get_placed(debug)
        self.kills = self._get_kills(debug)

        # TODO: check playername, kills against Squad.player and Stats.
        # TODO: remove some logic from _get_placed/_get_kills and just read from squad/stats

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
            # TODO: record kill timestamps, correlate with weapons
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
        logger.error(f'Could not get season for {self.timestamp} - using {len(data.seasons)}')

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

            'player_name': self.player_name,
            'kills': self.kills,
            'placed': self.placed,

            'squad': self.squad.to_dict(),
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

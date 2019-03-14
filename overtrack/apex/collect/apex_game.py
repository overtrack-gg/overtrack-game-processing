import bisect
import logging
import string
from typing import Counter, List, Optional, Tuple

import numpy as np

from overtrack.apex import data
from overtrack.apex.data import Champion
from overtrack.frame import Frame
from overtrack.util import arrayops, s2ts, textops

logger = logging.getLogger(__name__)


# @dataclass
# class Champion:
#     name: str
#
# @dataclass
# class Squad:
#     champion: Optional[Champion]
#     squadmates_champions: Tuple[Optional[Champion], Optional[Champion]]
#
# @dataclass
# class ApexGame:
#     timestamp: float
#     duration: float
#     frames: int
#     squad: Squad
#     placed: int
#     kills: int


class Squad:

    def __init__(self, frames: List[Frame]):
        self.squad = [f.squad for f in frames if 'squad' in f]
        logger.info(f'Processing squad from {len(self.squad)} squad frames')

        self.champion = self._get_champion()
        self.squadmates = (
            self._get_squadmate(0),
            self._get_squadmate(1),
        )

    def _get_champion(self) -> Optional[Champion]:
        return self._get_matching_champion([s.champion for s in self.squad])

    def _get_squadmate(self, index: int) -> Optional[Champion]:
        return self._get_matching_champion([s.squadmate_champions[index] for s in self.squad])

    def _get_matching_champion(self, arr: List[List[float]]) -> Optional[Champion]:
        # only look at data where we are sure that it was one of the champions
        matches = np.array([
            x for x in arr if np.max(x) > 0.98
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
        if matches[match] > 0.99:
            logger.info(f'Got champion={champion}, match={matches[match]:1.4f}')
            return champion
        else:
            logger.warning(f'Could not identify champion - best={champion}, match={matches[match]:1.4f}')
            return None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'champion={self.champion.name if self.champion else "?"}, ' \
               f'squadmates=({self.squadmates[0].name if self.squadmates[0] else "?"}, {self.squadmates[1].name if self.squadmates[1] else "?"})' \
               f')'

    __repr__ = __str__


class Route:

    def __init__(self, frames: List[Frame]):
        self.locations = []
        last: Optional[Tuple[int, int]] = None
        last_valid = 100
        for frame in [f for f in frames if 'location' in f]:
            ts, location = frame.timestamp, frame.location
            if not last:
                dist = 0
            else:
                dist = np.sqrt(np.sum((np.array(last) - np.array(location)) ** 2))
            if last_valid < 10:
                if dist < 50:
                    last_valid += 1
                    if last_valid == 10:
                        logger.warning(f'Location became valid again')
            elif dist < 50:
                self.locations.append((ts - frames[0].timestamp, location))
            else:
                logger.warning(
                    f'Ignoring location {dist:.1f} away from previous - '
                    f'invalidating location until we see 10 locations within close proximity'
                )
                last_valid = 0
            last = location

        logger.info(f'Processing route from {len(self.locations)} locations')

        self.time_landed = self._get_landed_timestamp(frames)
        self.landed_location_index = bisect.bisect(self.locations, (self.time_landed, (0, 0))) + 1
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

    def _get_landed_timestamp(self, frames: List[Frame]) -> float:
        # use first weapon pickup to detect when not dropping
        # TODO: use the "Hold (|) Freelook" or similar to detect when dropping
        weapon_timestamp = [f.timestamp for f in frames if 'weapons' in f]
        have_weapon = [self._weapon_names_valid(f.weapons.weapon_names) for f in frames if 'weapons' in f]

        weapon_timestamp = weapon_timestamp[:-9]
        have_weapon = np.convolve(have_weapon, np.ones((10, )), mode='valid')

        got_weapon_index = np.where(have_weapon > 6)[0][0] + 2
        got_weapon_timestamp = weapon_timestamp[got_weapon_index]

        game_relative_timestamp = got_weapon_timestamp - frames[0].timestamp

        logger.info(f'Got first weapon pickup at {s2ts(game_relative_timestamp)}')
        return game_relative_timestamp

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

    def show(self):
        import cv2
        from overtrack.apex.game.map import MapProcessor
        image = MapProcessor.MAP.copy()
        last = self.locations[self.landed_location_index][1]
        for ts, l in self.locations[self.landed_location_index + 1:]:
            cv2.line(
                image,
                last,
                l,
                (0, 255, 0),
                3
            )
            last = l
        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), interpolation='none')
        plt.show()


class ApexGame:

    def __init__(self, frames: List[Frame], key: str = None, debug: bool = False):
        self.timestamp = frames[0].timestamp
        self.frames = frames

        self.match_summary = [f.match_summary for f in self.frames if 'match_summary' in f]
        self.match_status = [f.match_status for f in self.frames if 'match_status' in f]

        self.placed = self._get_placed()
        self.kills = self._get_kills()

        self.squad = Squad(frames)

        self.route: Route = Route(frames)

    def _get_placed(self) -> int:
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
                return summary_placed
            else:
                return last_squads_alive
        else:
            logger.warning(f'Did not get any match summaries - using placed=20')
            return 20

    def _get_kills(self) -> int:
        kills_seen = [s.kills for s in self.match_status if s.kills]
        logger.info(f'Getting kills from {len(self.match_status)} match status frames with {len(kills_seen)} killcounts seen')
        if len(kills_seen) > 10:
            # TODO: record kill timestamps, correlate with weapons
            kills_seen = arrayops.modefilt(kills_seen, 5)

            final_kills = kills_seen[-1]
            logger.info(f'Got final_kills={final_kills}')

            return final_kills
        else:
            logger.info(f'Only saw {len(kills_seen)} killcounts - using final_kills=0')
            return 0

    @property
    def won(self) -> bool:
        return self.placed == 1

    @property
    def duration(self) -> float:
        return self.frames[-1].timestamp - self.frames[0].timestamp

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'duration={s2ts(self.duration)}, ' \
               f'frames={len(self.frames)}, ' \
               f'squad={self.squad}, ' \
               f'landed={self.route.landed_name}, ' \
               f'placed={self.placed}, ' \
               f'kills={self.kills}' \
               f')'

    __repr__ = __str__

import bisect
from collections import deque, Counter

import cv2
import logging
import numpy as np
from dataclasses import dataclass
from typing import ClassVar, List, NamedTuple, Optional, Tuple, Union

from overtrack.apex.collect.apex_game.combat import Combat
from overtrack.apex.collect.apex_game.weapons import Weapons
from overtrack.util import s2ts, validate_fields
from overtrack_cv.frame import Frame
from overtrack_cv.games.apex import data
from overtrack_cv.games.apex.data import MapLocations


class Coordinates(NamedTuple):
    x: float
    y: float


class Location(NamedTuple):
    timestamp: float
    coordinates: Coordinates


def rel_error(x1: float, x2: float) -> float:
    return abs(x1-x2)/abs(x2)


@dataclass
@validate_fields
class Route:
    map: str
    locations: List[Location]
    time_landed: float
    landed_location_index: int
    landed_location: Coordinates
    landed_name: str
    locations_visited: List[str]

    version: int

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)
    VERSION: ClassVar[int] = 1

    def __init__(self, frames: List[Frame], weapons: Weapons, combat: Combat, season: int, debug: Union[bool, str] = False):
        self.season = season
        self.version = self.VERSION

        maps_seen_c = Counter([f.apex.map_loading.map for f in frames if f.apex.map_loading]).most_common()
        self.logger.info(f'Seen maps: {maps_seen_c}')
        if len(maps_seen_c):
            map_name = maps_seen_c[0][0]
            if map_name == "King's Canyon":
                self.map = 'kings_canyon.s8'
                map_location_names = data.kings_canyon_locations
            elif map_name == "Olympus":
                self.map = 'olympus.s8'
                map_location_names = None
            elif map_name == "World's Edge":
                self.map = 'worlds_edge.s8'
                map_location_names = data.worlds_edge_locations
            else:
                raise ValueError(f"Could not recognise map {map_name}")
            self.logger.info(f'Found map={map_name} -> {self.map}')
        else:
            self.logger.warning("Did not see any map_loading frames - using map = kings canyon")
            map_name = 'kings_canyon'
            self.map = 'kings_canyon.s8'
            map_location_names = data.kings_canyon_locations

        alive = np.array([
            bool(f.apex.squad or f.apex.match_status) for f in frames
        ])
        alive = np.convolve(alive, np.ones(10, ), mode='valid')
        alive_at = np.zeros(int((frames[-1].timestamp - frames[0].timestamp) / 10) + 5, dtype=np.bool)
        alive_at[:20] = True
        alive_at[-20:] = True
        for f, a in zip(frames, alive):
            alive_at[int((f.timestamp - frames[0].timestamp) / 10)] |= (a > 2)

        if debug is True or debug == 'Alive':
            import matplotlib.pyplot as plt

            plt.figure()
            plt.title('alive')
            plt.plot([f.timestamp for f in frames[:-9]], alive)

            plt.figure()
            plt.title('alive at')
            plt.scatter(np.linspace(0, 10 * alive_at.shape[0], alive_at.shape[0]), alive_at)
            plt.show()

        champion_i = np.max(np.where([f.apex.champion_squad is not None for f in frames])[0])
        coordframes = [f for f in frames[champion_i:] if f.apex.coordinates]
        x = np.array([f.apex.coordinates.x for f in coordframes])
        y = np.array([f.apex.coordinates.y for f in coordframes])
        t = np.round(np.array([f.timestamp for f in coordframes]) - frames[0].timestamp, 2)

        # from overtrack_cv.util import debugops
        # import cv2
        #
        # def draw_route(img, scale_0_500_103, xoff_0_1000_500, yoff_0_1000_500):
        #     image = img.copy()
        #
        #     scale = scale_0_500_103 / 10 + 50
        #     xoff = xoff_0_1000_500
        #     yoff = yoff_0_1000_500 + 500
        #     print(scale, xoff, yoff)
        #
        #     xs = (x / scale + xoff).astype(np.int) * 2
        #     ys = (-y / scale + yoff).astype(np.int) * 2
        #     for i in range(len(xs) - 1):
        #         lerp = int((i / len(xs)) * 255)
        #         cv2.line(
        #             image,
        #             (xs[i], ys[i]),
        #             (xs[i+1], ys[i+1]),
        #             (lerp, 0, 255),
        #             2,
        #             cv2.LINE_AA
        #         )
        #     return image
        #
        # image = cv2.imread(f"C:/Users/simon/overtrack_2/overtrack-web-2/overtrack_web/static/images/apex/{self.map}.jpg")
        # debugops.sliders(
        #     image,
        #     scale=0.6,
        #     draw_route=draw_route
        # )

        SCALE = 60.3
        if self.map.split('.')[0] == 'kings_canyon':
            XOFFSET = 562
            YOFFSET = 676
        elif self.map.split('.')[0] == 'olympus':
            XOFFSET = 864
            YOFFSET = 793
        else:
            raise ValueError(f'Don\'t know how to transform map coordinates for {map_name}')
        x = (x / SCALE + XOFFSET).astype(np.int)
        y = (-y / SCALE + YOFFSET).astype(np.int)

        self.locations = []
        recent = deque(maxlen=10)

        ignored = 0
        final_game_time = None
        last_location_timestamp = 0
        for i, frame in enumerate(coordframes):
            if 'game_time' in frame:
                final_game_time = frame.game_time

            coordinates = Coordinates(int(x[i]), int(y[i]))

            rts = round(frame.timestamp - frames[0].timestamp, 2)
            thresh_dist = 200
            if len(recent):
                last = np.mean(recent, axis=0)
                dist = np.sqrt(np.sum((np.array(last) - np.array(coordinates)) ** 2))
                if not alive_at[int(rts / 10)]:
                    # ignore route - not from this player
                    self.logger.debug(f'Ignoring location {i}: {frame.apex.minimap.location} - not alive')
                elif dist < thresh_dist:
                    if frame.timestamp - last_location_timestamp > 2.5:
                        self.locations.append(Location(rts, coordinates))
                        last_location_timestamp = frame.timestamp

                else:
                    ignored += 1
                    self.logger.warning(
                        f'Ignoring location {i} @{frame.game_time if "game_time" in frame else 0:.1f}s: {frame.apex.coordinates} - {dist:.1f} away from average {np.round(last, 1)}'
                    )
            recent.append(coordinates)

        if debug == self.__class__.__name__:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x, y, t, c='green', marker='o')
            # plt.show()

            image = cv2.imread("C:/Users/simon/overtrack_2/overtrack-web-2/overtrack_web/static/images/apex/olympus.s8.jpg")
            image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            # image = cv2.imread("C:/tmp/kingscanyon.png")
            # image = cv2.imread(r"C:\Users\simon\overtrack_2\overtrack-cv\overtrack_cv\games\apex\processors\minimap\data\9.png")[
            #         :,
            #         data.worlds_edge_locations.width:
            # ]

            for i in range(len(self.locations) - 1):
                cv2.line(
                    image,
                    (self.locations[i].coordinates.x, self.locations[i].coordinates.y),
                    (self.locations[i + 1].coordinates.x, self.locations[i + 1].coordinates.y),
                    (255, 0, 255),
                    1,
                )
            import matplotlib.pyplot as plt
            plt.figure()
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            plt.show()

        self.logger.info(f'Processing route from {len(self.locations)} locations (ignored {ignored} locations with bad match)')
        if not len(self.locations):
            raise ValueError(f'Got no locations')
        else:
            x = np.array([l[1][0] for l in self.locations])
            y = np.array([l[1][1] for l in self.locations])
            ts = np.array([l[0] for l in self.locations])

            if len(ts) < 3:
                self.logger.warning(f'Only got {len(ts)} locations - assuming drop location = last location seen')
                self.landed_location_index = len(ts) - 1
                self.time_landed = float(ts[self.landed_location_index])
            else:
                time_offset = np.array(ts[1:] - ts[:-1])
                speed = np.sqrt((x[1:] - x[:-1]) ** 2 + (y[1:] - y[:-1]) ** 2) / time_offset
                speed_smooth = np.convolve(speed, np.ones(3) / 3, mode='same')
                # accel = np.diff(speed_smooth)
                self.landed_location_index = int(np.argmax(speed_smooth < 6)) + 1
                self.time_landed = float(ts[self.landed_location_index])
                self.logger.info(f'Speed dropped below 4 @ {s2ts(self.time_landed)}, index={self.landed_location_index}')

            # average location of first 5 locations
            mean_location = np.mean([
                l[1] for l
                in self.locations[
                   max(0, self.landed_location_index - 2):
                   min(self.landed_location_index + 3, len(self.locations))
                   ]],
                axis=0
            )
            self.landed_location = Coordinates(int(mean_location[0]), int(mean_location[1]))
            if map_location_names:
                self.landed_name = map_location_names[self.landed_location]
            else:
                self.landed_name = ''

            if map_location_names:
                self._process_locations_visited(map_location_names)
            else:
                self.locations_visited = []

        for event in combat.events:
            event.location = self.get_location_at(event.timestamp)
            lname = map_location_names[event.location] if map_location_names and event.location else ""
            self.logger.info(f'Found location={lname} for {event}')

        # if debug is True or debug == self.__class__.__name__:
        #     self._debug(frames)

    def _process_locations_visited(self, map_location_names: MapLocations):
        self.locations_visited = [self.landed_name]
        last_location = self.locations[self.landed_location_index][0], self.landed_name
        for ts, location in self.locations[self.landed_location_index + 1:]:
            location_name = map_location_names[location]
            if location_name == 'Unknown':
                continue
            if location_name == last_location[1] and ts - last_location[0] > 30:
                if self.locations_visited[-1] != location_name:
                    self.locations_visited.append(location_name)
            elif location_name != last_location[1]:
                self.logger.info(f'Spent {ts - last_location[0]:.1f}s in {last_location[1]}')
                last_location = ts, location_name

    def get_location_at(self, timestamp: float, max_distance: float = 120) -> Optional[Tuple[int, int]]:
        ts = [l[0] for l in self.locations]
        xy = [l[1] for l in self.locations]
        index = min(max(0, bisect.bisect(ts, timestamp) - 1), len(ts))
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
                        self.logger.log(level, f'Found {loc} at {ats:.1f}s - time delta {distance:.1f}s')
                        return loc

        self.logger.warning(f'Could not find location for ts={timestamp:.1f}s')
        return None

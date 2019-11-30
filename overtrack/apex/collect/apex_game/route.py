import bisect
import logging
from collections import deque, defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union, DefaultDict

import numpy as np
import typedload
from dataclasses import dataclass

from overtrack.apex import data
from overtrack.apex.collect.apex_game.combat import Combat
from overtrack.apex.collect.apex_game.weapons import Weapons
from overtrack.apex.data import get_round_state, ROUNDS
from overtrack.apex.game.minimap import Circle, Location
from overtrack.frame import Frame
from overtrack.util import s2ts


@dataclass(frozen=True)
class Ring:
    round: int
    center: Tuple[int, int]
    radius: int
    start_time: float
    end_time: float


def rel_error(x1: float, x2: float) -> float:
    return abs(x1-x2)/abs(x2)


class Route:
    logger = logging.getLogger('Route')

    def __init__(self, frames: List[Frame], weapons: Weapons, combat: Combat, season: int, debug: Union[bool, str] = False):
        self.season = season
        alive = np.array([
            ('squad' in f or 'match_status' in f) for f in frames
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

        self.locations = []
        circles: DefaultDict[int, List[Circle]] = defaultdict(list)
        recent = deque(maxlen=10)

        def add_circle(location: Location, circle: Circle, expected_radius: float, circle_index: int, closing: Optional[bool], game_time: float, name: str):
            error = rel_error(circle.r, expected_radius)
            if circle.points < 30 or circle.residual > 100:
                self.logger.debug(f'Ignoring {name} {circle} | game_time={s2ts(game_time)}, round={state.round}')
            elif error < 0.05:
                self.logger.debug(
                    f'Using {name} {circle} | '
                    f'expected radius={expected_radius} for ring {circle_index} (error={error * 100:.0f}%) | '
                    f'game time={frame.game_time:.0f}s, round={state.round}' +
                    (f', closing={closing}' if closing is not None else '')
                )

                circles[circle_index].append(circle)

            elif error < 0.2 and not closing and circle.r > 200:
                # Use a circle with the in the same direction as the observed circle, but with the correct radius
                # This assumes the observed circle is the correct circle, and that the center of the arc is in the correct position,
                #   but that the radius calculation is incorrect
                offset = np.array(circle.coordinates) - location.coordinates
                scale = expected_radius / circle.r
                new_center = np.array(location.coordinates) + offset * scale
                new_circle = Circle(
                    coordinates=(new_center[0], new_center[1]),
                    r=expected_radius
                )
                self.logger.debug(
                    f'Using {name} arc {circle} => '
                    f'corrected to Circle(coordinates={new_circle.coordinates}, r={new_circle.r:.0f}) | '
                    f'scaled offset/radius by {scale:.2f} for ring {circle_index} | '
                    f'game time={frame.game_time:.0f}s, round={state.round}' +
                    (f', closing={closing}' if closing is not None else '')
                )
                circles[circle_index].append(new_circle)
            else:
                self.logger.debug(
                    f'Ignoring {name} {circle} | '
                    f'expected r={expected_radius:.1f} for ring {circle_index} (error={error * 100:.0f}%) | '
                    f'game time={frame.game_time:.0f}s, round={state.round}' +
                    (f', closing={closing}' if closing is not None else '')
                )

        ignored = 0
        final_game_time = None
        last_location_timestamp = 0
        for i, frame in enumerate([f for f in frames if 'location' in f or 'minimap' in f]):
            if 'game_time' in frame:
                final_game_time = frame.game_time

            minimap = None
            if 'minimap' in frame:
                ts, location = frame.timestamp, frame.minimap.location
                minimap = frame.minimap
                coordinates = location.coordinates
                if season <= 2:
                    coordinates = (
                        int(coordinates[0] * 0.987 + 52),
                        int(coordinates[1] * 0.987 + 48)
                    )
            else:
                ts, location = frame.timestamp, frame.location
                coordinates = location.coordinates

            rts = round(ts - frames[0].timestamp, 2)
            thresh = 0.55
            if 'minimap' in frame and frame.minimap.version == 1:
                thresh = 0.2
            if location.match > thresh:
                ignored += 1
                continue

            thresh_dist = 100
            if 'game_time' in frame and frame.game_time < 80:
                # dropship speed
                thresh_dist = 500
            elif location.match < 0.1 and 'minimap' in frame and frame.minimap.version > 0:
                # allow high speeds from e.g. running forwards on train, balooning if the match is good
                thresh_dist = 250

            if len(recent):
                last = np.mean(recent, axis=0)
                dist = np.sqrt(np.sum((np.array(last) - np.array(coordinates)) ** 2))
                if not alive_at[int(rts / 10)]:
                    # ignore route - not from this player
                    self.logger.debug(f'Ignoring location {i}: {location} - not alive')
                elif dist < thresh_dist:
                    if 'game_time' in frame:
                        state = get_round_state(frame.game_time)

                        if minimap and state.ring_radius and minimap.outer_circle:
                            if state.ring_closing:
                                circle_index = state.round
                            else:
                                circle_index = state.round - 1
                            add_circle(minimap.location, minimap.outer_circle, state.ring_radius, circle_index, state.ring_closing, frame.game_time, 'outer')

                        if minimap and state.next_ring_radius and minimap.inner_circle:
                            add_circle(minimap.location, minimap.inner_circle, state.next_ring_radius, state.round, None, frame.game_time, 'inner')

                    if frame.timestamp - last_location_timestamp > 2.5:
                        self.locations.append((rts, coordinates))
                        last_location_timestamp = frame.timestamp

                else:
                    self.logger.warning(
                        f'Ignoring location {i} @{frame.game_time if "game_time" in frame else 0:.1f}s: {location} - {dist:.1f} away from average {np.round(last, 1)}'
                    )
            recent.append(coordinates)

        self.logger.info(f'Processing route from {len(self.locations)} locations (ignored {ignored} locations with bad match)')
        if not len(self.locations):
            self.logger.warning(f'Got no locations')
            self.time_landed = None
            self.landed_location_index = None
            self.landed_location = None
            self.landed_name = None
            self.locations_visited = []
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
            self.landed_location = int(mean_location[0]), int(mean_location[1])
            if season <= 2:
                self.landed_name = data.KINGS_CANYON_LOCATIONS[self.landed_location]
            else:
                self.landed_name = data.WORLDS_EDGE_LOCATIONS[self.landed_location]

            self._process_locations_visited()

        self.rings: List[Optional[Ring]] = []
        for round_ in ROUNDS[1:]:
            circs = circles[round_.index]
            if len(circs):
                xs, ys = [c.coordinates[0] for c in circs], [c.coordinates[1] for c in circs]
                x, y = int(np.median(xs) + 0.5), int(np.median(ys) + 0.5)
                std = (np.std(xs) + np.std(ys)) / 2
                self.logger.info(f'Ring {round_.index}: center=({x}, {y}), r={round_.radius}, std=({np.std(xs):.1f}, {np.std(ys):.1f}) => {std:.1f}, count={len(xs)}')
                self.logger.debug(f'    X={xs}')
                self.logger.debug(f'    Y={ys}')
                if (round_.index <= 2 and std > 20) or (round_.index > 2 and std > 7):
                    self.logger.warning(f'Rejecting ring {round_.index} - stddev to high')
                    self.rings.append(None)
                else:
                    self.rings.append(Ring(
                        round_.index,
                        (x, y),
                        round_.radius,
                        round(round_.start_time, 2),
                        round(round_.end_time, 2),
                    ))
            else:
                self.logger.warning(f'Rejecting ring {round_.index} - no data')
                self.rings.append(None)

            if final_game_time and round_.end_time > final_game_time:
                self.logger.info(f'Final ring is {round_.index}, next round starts in {round_.end_time - final_game_time:.0f}s')
                break

        if debug is True or debug == 'Rings':
            import matplotlib.pyplot as plt
            import cv2
            plt.figure()
            map_with_rings = self.make_image()
            for ring in self.rings:
                if ring:
                    cv2.circle(map_with_rings, ring.center, ring.radius, (255, 0, 255), 1)
            plt.imshow(map_with_rings, interpolation='none')
            plt.show()

        for event in combat.events:
            event.location = self._get_location_at(event.timestamp)
            if season <= 2:
                lname = data.KINGS_CANYON_LOCATIONS[event.location] if event.location else "???"
            else:
                lname = data.WORLDS_EDGE_LOCATIONS[event.location] if event.location else "???"
            self.logger.info(f'Found location={lname} for {event}')

        if debug is True or debug == self.__class__.__name__:
            self._debug(frames)

    def _debug(self, frames):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        assert Axes3D, 'Axes3D import required for 3D plots'

        plt.figure()
        plt.title('Location Match')
        plt.plot([f.location.match for f in frames if 'location' in f] + [f.minimap.location.match for f in frames if 'minimap' in f])

        import cv2
        from colorsys import hsv_to_rgb
        from overtrack.apex.game.minimap.minimap_processor import MinimapProcessor

        image = cv2.cvtColor(MinimapProcessor().MAP, cv2.COLOR_GRAY2BGR)
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
        plt.imshow(cv2.cvtColor(self.make_image(), cv2.COLOR_BGR2RGB), interpolation='none')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x = np.array([f.minimap.location.coordinates[0] for f in frames if 'minimap' in f])
        y = np.array([f.minimap.location.coordinates[1] for f in frames if 'minimap' in f])
        t = [f.minimap.location.match for f in frames if 'minimap' in f]
        ax.scatter(x, y, t, c='green', marker='o')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x = np.array([l[1][0] for l in self.locations])
        y = np.array([l[1][1] for l in self.locations])
        t = [l[0] for l in self.locations]
        ax.scatter(x, y, t, c='green', marker='o')

        ts = np.array([l[0] for l in self.locations])
        plt.figure()
        plt.title('time offsets')
        time_offset = np.array(ts[1:] - ts[:-1])
        plt.plot(time_offset)

        plt.figure()
        plt.title('speed')
        speed = np.sqrt((x[1:] - x[:-1]) ** 2 + (y[1:] - y[:-1]) ** 2) / time_offset
        plt.plot(speed)
        # q
        # plt.figure()
        # plt.title('speed2')
        # speed2 = speed / time_offset
        # plt.plot(speed2)

        speed_smooth = np.convolve(speed, np.ones(3) / 3, mode='valid')
        plt.figure()
        plt.title('speed_smooth')
        plt.plot(speed_smooth)

        plt.figure()
        plt.title('accel')
        accel = np.diff(speed_smooth)
        plt.plot(accel)

        t, x, y, r = [], [], [], []
        for f in frames:
            if 'minimap' in f and f.minimap.inner_circle:
                t.append(f.game_time)
                x.append(f.minimap.inner_circle.coordinates[0])
                y.append(f.minimap.inner_circle.coordinates[1])
                r.append(f.minimap.inner_circle.r)
        plt.figure()
        plt.title('inner')
        plt.scatter(t, x, label='x')
        plt.scatter(t, y, label='y')
        plt.scatter(t, r, label='r')
        plt.legend()

        t, x, y, r = [], [], [], []
        for f in frames:
            if 'minimap' in f and f.minimap.outer_circle:
                t.append(f.game_time)
                x.append(f.minimap.outer_circle.coordinates[0])
                y.append(f.minimap.outer_circle.coordinates[1])
                r.append(f.minimap.outer_circle.r)
        plt.figure()
        plt.title('outer')
        plt.scatter(t, x, label='x')
        plt.scatter(t, y, label='y')
        plt.scatter(t, r, label='r')
        plt.legend()

        plt.show()

    def make_image(self, combat: Optional[Combat] = None) -> np.ndarray:
        import cv2
        from overtrack.apex.game.minimap.minimap_processor import MinimapProcessor

        image = cv2.cvtColor(MinimapProcessor().MAP, cv2.COLOR_GRAY2BGR)

        if len(self.locations):
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

    def _process_locations_visited(self):
        self.locations_visited = [self.landed_name]
        last_location = self.locations[self.landed_location_index][0], self.landed_name
        for ts, location in self.locations[self.landed_location_index + 1:]:
            if self.season <= 2:
                location_name = data.KINGS_CANYON_LOCATIONS[location]
            else:
                location_name = data.WORLDS_EDGE_LOCATIONS[location]
            if location_name == 'Unknown':
                continue
            if location_name == last_location[1] and ts - last_location[0] > 30:
                if self.locations_visited[-1] != location_name:
                    self.locations_visited.append(location_name)
            elif location_name != last_location[1]:
                self.logger.info(f'Spent {ts - last_location[0]:.1f}s in {last_location[1]}')
                last_location = ts, location_name

    def _get_location_at(self, timestamp: float, max_distance: float = 120) -> Optional[Tuple[int, int]]:
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            'locations': self.locations,

            'time_landed': self.time_landed,
            'landed_location_index': self.landed_location_index,
            'landed_location': self.landed_location,
            'landed_name': self.landed_name,
            'locations_visited': self.locations_visited,

            'rings': typedload.dump(self.rings)
        }


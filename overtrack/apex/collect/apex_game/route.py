import bisect
import logging
import time
from collections import defaultdict, deque
from typing import Any, ClassVar, DefaultDict, List, NamedTuple, Optional, Tuple, Union

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.apex import data
from overtrack.apex.collect.apex_game.combat import Combat
from overtrack.apex.collect.apex_game.weapons import Weapons
from overtrack.apex.data import rounds, get_round_state, MapLocations
from overtrack.apex.game.minimap import Circle as FrameCircle, Location as FrameLocation, Minimap
from overtrack.apex.game.minimap.models import RingsComposite
from overtrack.frame import Frame
from overtrack.util import s2ts, validate_fields

Coordinates = Tuple[int, int]


@dataclass
class Ring:
    round: int
    center: Coordinates
    radius: int
    start_time: float
    end_time: float


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
    rings: List[Optional[Ring]]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

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
        circles: DefaultDict[int, List[FrameCircle]] = defaultdict(list)
        recent = deque(maxlen=10)

        ignored = 0
        final_game_time = None
        last_location_timestamp = 0
        for i, frame in enumerate([f for f in frames if 'minimap' in f]):
            if 'game_time' in frame:
                final_game_time = frame.game_time

            coordinates = frame.minimap.location.coordinates
            if season <= 2:
                coordinates = (
                    int(coordinates[0] * 0.987 + 52),
                    int(coordinates[1] * 0.987 + 48)
                )

            rts = round(frame.timestamp - frames[0].timestamp, 2)
            thresh = 0.55
            if 'minimap' in frame and frame.minimap.version == 1:
                thresh = 0.2
            if frame.minimap.location.match > thresh:
                ignored += 1
                continue

            thresh_dist = 100
            if 'game_time' in frame and frame.game_time < 80:
                # dropship speed
                thresh_dist = 500
            elif frame.minimap.location.match < 0.1 and 'minimap' in frame and frame.minimap.version > 0:
                # allow high speeds from e.g. running forwards on train, balooning if the match is good
                thresh_dist = 250

            if len(recent):
                last = np.mean(recent, axis=0)
                dist = np.sqrt(np.sum((np.array(last) - np.array(coordinates)) ** 2))
                if not alive_at[int(rts / 10)]:
                    # ignore route - not from this player
                    self.logger.debug(f'Ignoring location {i}: {frame.minimap.location} - not alive')
                elif dist < thresh_dist:
                    if 'game_time' in frame:
                        self._add_circles(circles, frame.game_time, frame.minimap)

                    if frame.timestamp - last_location_timestamp > 2.5:
                        self.locations.append(Location(rts, coordinates))
                        last_location_timestamp = frame.timestamp

                else:
                    self.logger.warning(
                        f'Ignoring location {i} @{frame.game_time if "game_time" in frame else 0:.1f}s: {frame.minimap.location} - {dist:.1f} away from average {np.round(last, 1)}'
                    )
            recent.append(coordinates)

        self.logger.info(f'Processing route from {len(self.locations)} locations (ignored {ignored} locations with bad match)')
        if not len(self.locations):
            raise ValueError(f'Got no locations')
        else:
            x = np.array([l[1][0] for l in self.locations])
            y = np.array([l[1][1] for l in self.locations])
            ts = np.array([l[0] for l in self.locations])

            worlds_edge_match = np.mean((x < data.worlds_edge_locations.width))
            self.logger.info(f'Got worlds edge match: {worlds_edge_match:.2f}')
            if worlds_edge_match < 0.25 and len(ts) > 10:
                self.map = 'kings_canyon.s2'
                self.logger.info(f'Classifying map as Kings Canyon ({self.map!r})')
                map_location_names = data.kings_canyon_locations

                self.locations = [
                    Location(
                        timestamp=l.timestamp,
                        coordinates=(
                            l.coordinates[0] - data.worlds_edge_locations.width,
                            l.coordinates[1],
                        )
                    )
                    for l in self.locations
                ]
                x -= data.worlds_edge_locations.width
                y = np.clip(y, 0, data.kings_canyon_locations.height)
            else:
                self.map = 'worlds_edge.s4'
                self.logger.info(f'Classifying map as Worlds Edge ({self.map!r})')
                map_location_names = data.worlds_edge_locations

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
            print(self.landed_location)
            self.landed_name = map_location_names[self.landed_location]

            self._process_locations_visited(map_location_names)

        self._process_rings(circles, final_game_time)

        rings_composite = None
        for f in frames:
            if 'minimap' in f and f.minimap.rings_composite:
                rings_composite = f.minimap.rings_composite
                break
        if rings_composite:
            self._process_rings_v2(rings_composite, debug in [True, 'Rings'])

        if debug is True or debug == 'Rings':
            import matplotlib.pyplot as plt
            import cv2
            plt.figure()
            map_with_rings = self._make_image()
            for ring in self.rings:
                if ring:
                    cv2.circle(map_with_rings, ring.center, ring.radius, (255, 0, 255), 1)
            plt.imshow(map_with_rings, interpolation='none')
            plt.show()

        for event in combat.events:
            event.location = self.get_location_at(event.timestamp)
            lname = map_location_names[event.location] if event.location else "???"
            self.logger.info(f'Found location={lname} for {event}')

        if debug is True or debug == self.__class__.__name__:
            self._debug(frames)

    def _add_circles(
        self,
        circles: DefaultDict[int, List[FrameCircle]],
        game_time: float,
        minimap: Minimap,
    ) -> None:
        state = get_round_state(game_time)

        if state.ring_radius and minimap.outer_circle:
            if state.ring_closing:
                circle_index = state.round
            else:
                circle_index = state.round - 1

            self._add_circle(
                circles,
                minimap.location,
                minimap.outer_circle,
                state.ring_radius,
                circle_index,
                state.ring_closing,
                game_time,
                'outer'
            )

        if state.next_ring_radius and minimap.inner_circle:
            self._add_circle(
                circles,
                minimap.location,
                minimap.inner_circle,
                state.next_ring_radius,
                state.round,
                None,
                game_time,
                'inner'
            )

    def _add_circle(
        self,
        circles: DefaultDict[int, List[FrameCircle]],
        location: FrameLocation,
        circle: FrameCircle,
        expected_radius: float,
        circle_index: int,
        closing: Optional[bool],
        game_time: float,
        circle_name: str
    ) -> None:
        error = rel_error(circle.r, expected_radius)
        if circle.points < 30 or circle.residual > 100:
            self.logger.debug(f'Ignoring {circle_name} {circle} | game_time={s2ts(game_time)}')
        elif error < 0.05:
            self.logger.debug(
                f'Using {circle_name} {circle} | '
                f'expected radius={expected_radius} for ring {circle_index} (error={error * 100:.0f}%) | '
                f'game time={game_time:.0f}s' +
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
            new_circle = FrameCircle(
                coordinates=(new_center[0], new_center[1]),
                r=expected_radius
            )
            self.logger.debug(
                f'Using {circle_name} arc {circle} => '
                f'corrected to Circle(coordinates={new_circle.coordinates}, r={new_circle.r:.0f}) | '
                f'scaled offset/radius by {scale:.2f} for ring {circle_index} | '
                f'game time={game_time:.0f}s' +
                (f', closing={closing}' if closing is not None else '')
            )
            circles[circle_index].append(new_circle)
        else:
            self.logger.debug(
                f'Ignoring {circle_name} {circle} | '
                f'expected r={expected_radius:.1f} for ring {circle_index} (error={error * 100:.0f}%) | '
                f'game time={game_time:.0f}s' +
                (f', closing={closing}' if closing is not None else '')
            )

    def _process_rings(self, circles: DefaultDict[int, List[FrameCircle]], final_game_time: float) -> None:
        self.logger.info(f'Processing rings from {sum([len(v) for v in circles.values()])} recorded circles')

        self.rings = []
        for round_ in rounds[1:]:
            circs = circles[round_.index]
            if len(circs):
                xs, ys = [c.coordinates[0] for c in circs], [c.coordinates[1] for c in circs]
                x, y = int(np.median(xs) + 0.5), int(np.median(ys) + 0.5)
                std = (np.std(xs) + np.std(ys)) / 2
                self.logger.info(
                    f'Ring {round_.index}: center=({x}, {y}), r={round_.radius}, std=({np.std(xs):.1f}, {np.std(ys):.1f}) => {std:.1f}, count={len(xs)}')
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

    def _process_rings_v2(self, composites: RingsComposite, debug: bool = False) -> None:
        self.logger.info(f'Processing rings (v2) from {len(composites.images)} composite images')

        if debug:
            comb = None
            for index in composites.images:
                im = composites.images[index].array.astype(np.float) / 255.0
                if comb is None:
                    comb = im.copy()
                else:
                    comb += im
            if comb is not None:
                import matplotlib.pyplot as plt
                plt.figure()
                plt.imshow(comb, interpolation='none')
                plt.show()

        t0 = time.perf_counter()
        for index in composites.images:
            round_ = rounds[index]
            radius = round_.radius

            image = composites.images[index].array.astype(np.float) / 255.0
            image *= 30

            # handle issue where the harvester adds a lot of noise to the images
            cv2.circle(
                image,
                (353, 463),
                45,
                0.,
                -1
            )

            # accumulator = self._hough_circles(image, ROUNDS[index].radius // 2)
            accumulator = self._hough_circles(cv2.erode(image, None), radius // 2)

            mnv, mxv, mnl, mxl = cv2.minMaxLoc(accumulator)
            center = (mxl[0] * 2, mxl[1] * 2)

            self.logger.info(f'Found ring {index} (radius={radius}) at {center} - match={mxv:.2f}')
            if mxv > 400:
                old = self.rings[index - 1]
                if old:
                    dist = np.sqrt(np.sum((np.array(old.center) - center) ** 2))
                    self.logger.log(
                        logging.INFO if dist < 25 else logging.WARNING,
                        f'Updating ring {index} center {old.center} -> {center} - update distance: {dist:.2f}'
                    )
                else:
                    self.logger.info(f'Ring {index} was unknown by previous method - setting')
                self.rings[index - 1] = Ring(
                    round_.index,
                    center,
                    round_.radius,
                    round(round_.start_time, 2),
                    round(round_.end_time, 2),
                )
            else:
                self.logger.info(f'Ignoring ring with low match')

            if debug:
                import matplotlib.pyplot as plt

                plt.figure()
                plt.title(f'ring {index}')
                plt.imshow(image, interpolation='none')

                plt.figure()
                plt.title(f'accumulator {index} | max={np.max(accumulator):.1f}')
                plt.imshow(accumulator / np.max(accumulator), interpolation='none')

                gim = ((image / np.max(image)) * 255).astype(np.uint8)
                cim = np.zeros_like(gim)
                cv2.circle(cim, mxl, radius // 2, 255)
                im = np.stack(
                    (
                        gim,
                        gim,
                        cim
                    ),
                    axis=-1,
                )
                plt.figure()
                plt.imshow(im, interpolation='none')
                plt.show()

                # flat = accumulator.flatten()
                # flat = flat[flat > 1]
                # plt.figure()
                # plt.title('accumulator hist')
                # plt.hist(flat, bins=100, range=(0, 200))

        self.logger.info(f'Took {(time.perf_counter() - t0) * 1000:.2f}ms')

    def _hough_circles(self, image: np.ndarray, radius: int, threshold: float = 2.) -> np.ndarray:
        # precompute circle points
        blank = np.zeros(image.shape, dtype=np.uint8)
        cv2.circle(
            blank,
            (radius, radius),
            radius,
            255,
            1,
        )
        ys, xs = np.where(blank > 0)

        # we add `radius` to each edge of accumulator. This is done to
        # a) handle `xs` and `ys` being offset by `radius`
        # b) ignore the accumulator values outside of `image` (by cropping `radius` off each edge after)
        accumulator = np.zeros(
            (image.shape[0] + radius * 2, image.shape[1] + radius * 2),
            dtype=np.float
        )

        # add intensities for each pixel in the image that surpasses threshold
        for y, x in zip(*np.where(image >= threshold)):
            accumulator[
                ys + y,
                xs + x
            ] += image[y, x]
        return accumulator[radius:-radius, radius:-radius]

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
        plt.imshow(cv2.cvtColor(self._make_image(), cv2.COLOR_BGR2RGB), interpolation='none')

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

    def _make_image(self, combat: Optional[Combat] = None) -> np.ndarray:
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
                    location = self.get_location_at(event.timestamp)
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

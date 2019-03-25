import logging
import os
from typing import List, NamedTuple, Optional, Tuple

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, ts2s, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection


@dataclass
class Location:
    coordinates: Tuple[int, int]
    match: float


def _draw_map_location(
        debug_image: Optional[np.ndarray],
        map_image: np.ndarray,
        location: Location,
        min_loc: Tuple[int, int],
        shape: Tuple[int, int]) -> None:
    if debug_image is None:
        return
    out = map_image.copy()
    cv2.circle(
        out,
        location.coordinates,
        6,
        (0, 255, 0),
        4
    )
    cv2.putText(
        out,
        f'{location.match:1.4f}',
        location.coordinates,
        cv2.FONT_HERSHEY_SIMPLEX,
        3,
        (0, 255, 0),
        2
    )
    cv2.rectangle(
        out,
        min_loc,
        (min_loc[0] + shape[1], min_loc[1] + shape[0]),
        (0, 0, 255),
        4
    )
    out = cv2.resize(out, (0, 0), fx=0.25, fy=0.25)
    debug_image[100:100 + out.shape[0], 400:400 + out.shape[1]] = out


class MapProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), '..', 'data', 'regions', '16_9.zip'))
    MAP = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'map.png'))
    MAP_TEMPLATE = cv2.GaussianBlur(
        cv2.Canny(
            cv2.GaussianBlur(
                MAP,
                (0, 0),
                0.5
            ),
            30,
            100
        ),
        (0, 0),
        1.5
    )
    MAP_MASK = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'map_mask.png'), 0) == 255
    TEMPLATE_OFFSET = (0, -3)

    class Location(NamedTuple):
        location: Tuple[int, int]

    @time_processing
    def process(self, frame: Frame):
        map_image = self.REGIONS['map'].extract_one(frame.image)

        map_image = cv2.GaussianBlur(map_image, (0, 0), 0.5)
        map_image = cv2.Canny(map_image, 30, 100)
        map_image = cv2.GaussianBlur(map_image, (0, 0), 1.5)

        template = cv2.resize(
            map_image,
            (0, 0),
            fx=0.987,
            fy=0.987
        )
        match = cv2.matchTemplate(
            self.MAP_TEMPLATE,
            template,
            cv2.TM_SQDIFF_NORMED
        )

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
        coords = min_loc[0] + template.shape[1] // 2 + self.TEMPLATE_OFFSET[0], min_loc[1] + template.shape[0] // 2 + self.TEMPLATE_OFFSET[1]

        location = Location(
            coords,
            round(min_val, 5)
        )
        _draw_map_location(
            frame.debug_image,
            self.MAP,
            location,
            min_loc,
            template.shape
        )

        if min_val < 0.85 and self.MAP_MASK[location.coordinates[1], location.coordinates[0]]:
            self.REGIONS.draw(frame.debug_image)
            frame.location = location
            return min_val < 0.6

        return False


def main() -> None:
    # frame = Frame.create(
    #     cv2.imread(
    #         "C:/Users/simon/workspace/overtrack_2/dev/apex_images/mpv-shot0171.png"
    #     ),
    #     0,
    #     True
    # )
    # MapProcessor().process(
    #     frame
    # )
    # cv2.imshow('debug', frame.debug_image)
    # cv2.waitKey(0)
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = MapProcessor()
    path: List[Tuple[int, int]] = []

    from overtrack.source.stream import Twitch

    source = Twitch(
        'https://www.twitch.tv/videos/387748639',
        2,
        keyframes_only=False,
        seek=ts2s('5:54:30'),
        debug_frames=True
    )
    f = True
    while True:
        frame = source.get()
        if frame is None:
            break

        if pipeline.process(frame):
            location = frame.location
            path.append(location.coordinates)

        cv2.imshow('debug', frame.debug_image)

        map = pipeline.MAP.copy()
        if len(path):
            prev = path[0]
            for p in path:
                cv2.line(
                    map,
                    prev,
                    p,
                    (0, 255, 0),
                    1
                )
                prev = p
        cv2.imshow(
            'map',
            cv2.resize(map, (0, 0), fx=0.8, fy=0.8)
        )

        # if f:
        #     cv2.waitKey(0)
        #     f = False

        cv2.waitKey(1)


if __name__ == '__main__':
    main()

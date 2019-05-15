import logging
import os
from collections import deque
from typing import Optional, Tuple

import cv2
import numpy as np

from overtrack.apex import ocr
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.apex.game.map.models import Location

logger = logging.getLogger('MapProcessor')

def _draw_map_location(
        debug_image: Optional[np.ndarray],
        map_image: np.ndarray,
        location: Location,
        min_loc: Optional[Tuple[int, int]],
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
    if min_loc:
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
                1.0
            ),
            70,
            150
        ),
        (0, 0),
        2.0
    )
    MAP_MASK = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'map_mask.png'), 0) == 255
    TEMPLATE_OFFSET = (0, -3)

    def __init__(self):
        self.map_rotated = deque(maxlen=10)

    def eager_load(self):
        self.REGIONS.eager_load()

    @time_processing
    def process(self, frame: Frame):
        map_image = self.REGIONS['map'].extract_one(frame.image)

        map_image = cv2.GaussianBlur(map_image, (0, 0), 0.5)
        map_image = cv2.Canny(map_image, 50, 100)
        map_image = cv2.GaussianBlur(map_image, (0, 0), 2.0)

        map_fragment = cv2.resize(
            map_image,
            (0, 0),
            fx=0.987,
            fy=0.987
        )

        if len(self.map_rotated) and sum(self.map_rotated) / len(self.map_rotated) > 0.75:
            # try rotated map first
            rotated_map = True
            bearing, location, min_loc, min_val = self._get_location_rotated(frame, map_fragment)
            if not bearing or min_val > 0.9:
                location2, min_loc2, min_val2 = self._get_location(map_fragment)
                if not bearing or min_val2 < min_val:
                    rotated_map = False
                    location, min_loc, min_val = location2, min_loc2, min_val2
        else:
            # by default try without rotating map
            rotated_map = False
            location, min_loc, min_val = self._get_location(map_fragment)
            if min_val > 0.9:
                bearing, location2, min_loc2, min_val2 = self._get_location_rotated(frame, map_fragment)
                if bearing and min_val2 < min_val:
                    rotated_map = True
                    location, min_loc, min_val = location2, min_loc2, min_val2
            else:
                bearing = None

        _draw_map_location(
            frame.debug_image,
            self.MAP,
            location,
            min_loc if not rotated_map else None,
            map_fragment.shape
        )

        if min_val < 0.85 and self.MAP_MASK[location.coordinates[1], location.coordinates[0]]:
            self.REGIONS.draw(frame.debug_image)

            self.map_rotated.append(rotated_map)
            frame.location = location
            frame.location.bearing = bearing
            frame.location.rotated_map = rotated_map
            return min_val < 0.6

        return False

    def _get_location_rotated(self, frame, map_fragment):
        bearing_image = self.REGIONS['bearing'].extract_one(frame.image_yuv[:, :, 0])
        bearing = imageops.tesser_ocr(bearing_image, expected_type=int, engine=ocr.tesseract_ttlakes_digits)
        if not bearing or not 0 <= bearing <= 360:
            logger.warning(f'Got invalid bearing: {bearing}')
            return None, None, None, 1
        if bearing:
            rot = cv2.getRotationMatrix2D(
                (self.MAP_TEMPLATE.shape[1] // 2, self.MAP_TEMPLATE.shape[0] // 2),
                bearing - 360,
                1
            )
            logger.debug(f'Got bearing={bearing}')
            location2, min_loc2, min_val2 = self._get_location(map_fragment, rotation=rot)
            return bearing, location2, min_loc2, min_val2
        else:
            return None, None, None, 1

    def _get_location(self, region: np.ndarray, rotation=None):
        if rotation is None:
            map_template = self.MAP_TEMPLATE
        else:
            height, width = self.MAP_TEMPLATE.shape
            map_template = cv2.warpAffine(
                self.MAP_TEMPLATE,
                rotation,
                (width, height)
            )

        match = cv2.matchTemplate(
            map_template,
            region,
            cv2.TM_SQDIFF_NORMED
        )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)

        # d = cv2.cvtColor(map_template, cv2.COLOR_GRAY2BGR)
        # cv2.rectangle(d, min_loc, (min_loc[0] + region.shape[1], min_loc[1] + region.shape[0]), (0, 255, 0))
        # cv2.circle(
        #     d,
        #     (min_loc[0] + region.shape[1] // 2 + self.TEMPLATE_OFFSET[0], min_loc[1] + region.shape[0] // 2 + self.TEMPLATE_OFFSET[1]),
        #     3,
        #     (0, 0, 255),
        #     -1
        # )
        # cv2.imshow('template_rot', d)
        # cv2.imshow('fragment', region)

        coords = min_loc[0] + region.shape[1] // 2 + self.TEMPLATE_OFFSET[0], min_loc[1] + region.shape[0] // 2 + self.TEMPLATE_OFFSET[1]
        if rotation is not None:
            inv = cv2.invertAffineTransform(rotation)
            coords = tuple(cv2.transform(np.array([[coords]]), inv)[0][0])

        # d2 = cv2.cvtColor(self.MAP_TEMPLATE, cv2.COLOR_GRAY2BGR)
        # cv2.circle(
        #     d2,
        #     coords,
        #     3,
        #     (0, 0, 255),
        #     -1
        # )
        # cv2.imshow('template', d2)

        location = Location(
            coords,
            round(min_val, 5)
        )
        return location, min_loc, min_val


def main() -> None:
    import glob

    config_logger('map_processor', logging.DEBUG, write_to_file=False)

    pipeline = MapProcessor()


    from overtrack.source.video import VideoFrameExtractor

    for frame in VideoFrameExtractor("M:/test.mkv", extract_fps=1, debug_frames=True, seek=12*60).tqdm():
        pipeline.process(frame)
        print(frame)
        pipeline.REGIONS.draw(frame.debug_image)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)


if __name__ == '__main__':
    main()

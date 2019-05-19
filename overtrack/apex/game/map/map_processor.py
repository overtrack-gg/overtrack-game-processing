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


def _debug_map_canny(map_image: np.ndarray) -> None:
    cv2.namedWindow('canny')
    cv2.createTrackbar('b1', 'canny', 50, 200, lambda x: None)
    cv2.createTrackbar('c1', 'canny', 30, 200, lambda x: None)
    cv2.createTrackbar('c2', 'canny', 100, 200, lambda x: None)
    cv2.createTrackbar('b2', 'canny', 150, 300, lambda x: None)
    last = None
    while True:
        b1 = (cv2.getTrackbarPos('b1', 'canny') + 1) / 100
        b2 = (cv2.getTrackbarPos('b2', 'canny') + 1) / 100

        c1 = cv2.getTrackbarPos('c1', 'canny')
        c2 = cv2.getTrackbarPos('c2', 'canny')

        cv2.imshow('canny', cv2.GaussianBlur(
            cv2.Canny(
                cv2.GaussianBlur(
                    map_image,
                    (0, 0),
                    b1
                ),
                c1,
                c2
            ),
            (0, 0),
            b2
        ))
        k = cv2.waitKey(10) & 0xFF
        if k == 27:
            break
        current = b1, b2, c1, c2
        if current != last:
            print(current)
            last = current
    cv2.destroyAllWindows()


def _debug_map_match(coords, template_offset, raw_map_template, map_template, min_loc, region):
    d = cv2.cvtColor(map_template, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(d, min_loc, (min_loc[0] + region.shape[1], min_loc[1] + region.shape[0]), (0, 255, 0))
    cv2.circle(
        d,
        (min_loc[0] + region.shape[1] // 2 + template_offset[0], min_loc[1] + region.shape[0] // 2 + template_offset[1]),
        3,
        (0, 0, 255),
        -1
    )
    cv2.imshow('template_rot', d)
    cv2.imshow('fragment', region)
    d2 = cv2.cvtColor(raw_map_template, cv2.COLOR_GRAY2BGR)
    cv2.circle(
        d2,
        coords,
        3,
        (0, 0, 255),
        -1
    )
    cv2.imshow('template', d2)


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

    # _debug_map_canny(MAP)

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

        coords = min_loc[0] + region.shape[1] // 2 + self.TEMPLATE_OFFSET[0], min_loc[1] + region.shape[0] // 2 + self.TEMPLATE_OFFSET[1]
        if rotation is not None:
            inv = cv2.invertAffineTransform(rotation)
            coords = tuple(cv2.transform(np.array([[coords]]), inv)[0][0])

        # _debug_map_match(coords, self.TEMPLATE_OFFSET, self.MAP_TEMPLATE, map_template, min_loc, region)

        location = Location(
            coords,
            round(min_val, 5)
        )
        return location, min_loc, min_val


def main() -> None:
    import glob

    config_logger('map_processor', logging.DEBUG, write_to_file=False)

    pipeline = MapProcessor()

    print(os.path.abspath('../../../../dev/images/map/'))
    for p in glob.glob('../../../../dev/images/map/*.png'):
        print(p)
        try:
            frame = Frame.create(
                cv2.resize(cv2.imread(p), (1920, 1080)),
                0,
                True
            )
        except:
            continue
        pipeline.process(frame)
        print(frame)
        pipeline.REGIONS.draw(frame.debug_image)
        cv2.imshow('debug', frame.debug_image)

        if 'match_status' in frame and frame.match_status.kills:
            cv2.waitKey(0)
        else:
            cv2.waitKey(0)

    from overtrack.source.video import VideoFrameExtractor

    for frame in VideoFrameExtractor("M:/test.mkv", extract_fps=1, debug_frames=True, seek=12*60).tqdm():
        pipeline.process(frame)
        print(frame)
        pipeline.REGIONS.draw(frame.debug_image)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)


if __name__ == '__main__':
    main()

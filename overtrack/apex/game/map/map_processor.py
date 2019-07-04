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


def _debug_map_match(map_template, min_loc, min_val, region, rotation):
    d = cv2.cvtColor(map_template, cv2.COLOR_GRAY2BGR)
    if min_val < 1.0:
        cv2.rectangle(d, min_loc, (min_loc[0] + region.shape[1], min_loc[1] + region.shape[0]), (0, 255, 0))
        cv2.circle(
            d,
            (min_loc[0] + region.shape[1] // 2, min_loc[1] + region.shape[0] // 2),
            3,
            (0, 0, 255),
            -1
        )
        cv2.putText(
            d,
            f'{min_val:.3f}',
            (min_loc[0] + region.shape[1] // 2 + 15, min_loc[1] + region.shape[0] // 2),
            cv2.FONT_HERSHEY_COMPLEX,
            1.0,
            (0, 255, 0),
            1
        )
    cv2.imshow('fragment', region)
    cv2.imshow('template' + ('_rot' if rotation is not None else ''), d)


template_blur_pre = 1.0
template_canny_t1 = 30
template_canny_t2 = 100
template_blur_post = 2.0


class MapProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), '..', 'data', 'regions', '16_9.zip'))
    MAP = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'map.png'))
    MAP_TEMPLATE = cv2.GaussianBlur(
        cv2.Canny(
            cv2.GaussianBlur(
                cv2.cvtColor(MAP, cv2.COLOR_BGR2YUV)[:, :, 0],
                (0, 0),
                template_blur_pre
            ),
            template_canny_t1,
            template_canny_t2
        ),
        (0, 0),
        template_blur_post
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
        map_image = self.REGIONS['map'].extract_one(frame.image_yuv)[:, :, 0]

        map_image_canny = cv2.GaussianBlur(map_image, (0, 0), template_blur_pre)
        map_image_canny = cv2.Canny(map_image_canny, template_canny_t1, template_canny_t2)
        map_image_canny = cv2.GaussianBlur(map_image_canny, (0, 0), template_blur_post)

        map_fragment = cv2.resize(
            map_image_canny,
            (0, 0),
            fx=0.987,
            fy=0.987
        )

        if len(self.map_rotated) and sum(self.map_rotated) / len(self.map_rotated) > 0.75:
            # try rotated map first
            rotated_map = True
            bearing, location, min_loc, min_val = self._get_location_rotated(frame, map_fragment)
            if not bearing or min_val > 0.5:
                location2, min_loc2, min_val2 = self._get_location(map_fragment)
                logger.debug(
                    f'Got rotated: bearing={bearing}, loc={location.coordinates if location else None}, match={min_val:.3f} | '
                    f'unrotated: loc={location2.coordinates if location2 else None}, match={min_val2:.3f}'
                )
                if not bearing or min_val2 < min_val:
                    rotated_map = False
                    location, min_loc, min_val = location2, min_loc2, min_val2
            else:
                logger.debug(f'Got rotated: bearing={bearing}, loc={location.coordinates if location else None}, match={min_loc} | unrotated: <skipped>')
        else:
            # by default try without rotating map
            rotated_map = False
            location, min_loc, min_val = self._get_location(map_fragment)
            if min_val > 0.5:
                bearing, location2, min_loc2, min_val2 = self._get_location_rotated(frame, map_fragment)
                logger.debug(
                    f'Got urotated: loc={location.coordinates if location else None}, match={min_val:.3f} | '
                    f'rotated: bearing={bearing}, loc={location2.coordinates if location2 else None}, match={min_val2:.3f}'
                )
                if bearing and min_val2 < min_val:
                    rotated_map = True
                    location, min_loc, min_val = location2, min_loc2, min_val2
            else:
                bearing = None
                logger.debug(f'Got urotated: loc={location.coordinates if location else None}, match={min_val} | rotated: <skipped>')

        _draw_map_location(
            frame.debug_image,
            self.MAP,
            location,
            min_loc if not rotated_map else None,
            map_fragment.shape
        )

        # _debug_map_canny(map_image)

        if min_val < 0.85 and \
                0 <= location.coordinates[1] < self.MAP_MASK.shape[1] and \
                0 <= location.coordinates[0] < self.MAP_MASK.shape[1] and \
                self.MAP_MASK[location.coordinates[1], location.coordinates[0]]:

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
            logger.debug(f'Got invalid bearing: {bearing}')
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

        # match2 = cv2.matchTemplate(
        #     map_template,
        #     region,
        #     cv2.TM_CCORR_NORMED
        # )
        # print(min_val, np.max(match2))

        coords = min_loc[0] + region.shape[1] // 2 + self.TEMPLATE_OFFSET[0], min_loc[1] + region.shape[0] // 2 + self.TEMPLATE_OFFSET[1]
        if rotation is not None:
            inv = cv2.invertAffineTransform(rotation)
            coords = tuple(cv2.transform(np.array([[coords]]), inv)[0][0])

        # _debug_map_match(map_template, min_loc, min_val, region, rotation)

        location = Location(
            coords,
            round(min_val, 5)
        )
        return location, min_loc, min_val


def find_best_match():
    im = cv2.imread("C:/tmp/frames/1558234981.88_image.png")
    frame = Frame.create(
        im,
        0,
        True
    )
    pipeline = MapProcessor()

    map_image_o = pipeline.REGIONS['map'].extract_one(frame.image)

    template_blur_pre = 0.8
    template_canny_t1 = 70
    template_canny_t2 = 150
    template_blur_post = 2.0

    fragment_blur_pre = 0.5
    fragment_canny_t1 = 50
    fragment_canny_t2 = 100
    fragment_blur_post = 2.0

    fragment_blur_pre = template_blur_pre
    fragment_canny_t1 = template_canny_t1
    fragment_canny_t2 = template_canny_t2
    fragment_blur_post = template_blur_post

    min_val = check_params(
        fragment_blur_post,
        fragment_blur_pre,
        fragment_canny_t1,
        fragment_canny_t2,
        frame,
        map_image_o,
        pipeline,
        template_blur_post,
        template_blur_pre,
        template_canny_t1,
        template_canny_t2
    )
    print(min_val)
    cv2.waitKey(0)


def check_params(fragment_blur_post, fragment_blur_pre, fragment_canny_t1, fragment_canny_t2, frame, map_image_o, pipeline, template_blur_post,
                 template_blur_pre, template_canny_t1, template_canny_t2):
    pipeline.MAP_TEMPLATE = cv2.GaussianBlur(
        cv2.Canny(
            cv2.GaussianBlur(
                pipeline.MAP,
                (0, 0),
                template_blur_pre
            ),
            template_canny_t1,
            template_canny_t2
        ),
        (0, 0),
        template_blur_post
    )
    map_image = cv2.GaussianBlur(map_image_o, (0, 0), fragment_blur_pre)
    map_image = cv2.Canny(map_image, fragment_canny_t1, fragment_canny_t2)
    map_image = cv2.GaussianBlur(map_image, (0, 0), fragment_blur_post)
    map_fragment = cv2.resize(
        map_image,
        (0, 0),
        fx=0.987,
        fy=0.987
    )

    rot = cv2.getRotationMatrix2D(
        (pipeline.MAP_TEMPLATE.shape[1] // 2, pipeline.MAP_TEMPLATE.shape[0] // 2),
        63 - 360,
        1
    )

    location, min_loc, min_val = pipeline._get_location(map_fragment, rotation=rot)
    return min_val


def main() -> None:
    import glob

    config_logger('map_processor', logging.DEBUG, write_to_file=False)

    find_best_match()
    # exit(0)

    pipeline = MapProcessor()
    print(os.path.abspath('../../../../dev/images/map/'))
    for p in ["C:/tmp/frames/1558234981.88_image.png"] + glob.glob('../../../../dev/images/map/*.png'):
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


if __name__ == '__main__':
    main()

import logging
import os
import string
from typing import List, NamedTuple, Optional, Tuple

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.apex import ocr
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import arrayops, imageops, debugops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection


class SelectedLegend(NamedTuple):
    player: str
    legend: str


@dataclass
class LegendSelect:
    selected: List[SelectedLegend]

#
#
# def _draw_match(debug_image: Optional[np.ndarray], ready_match: float, cancel_match: float, required_match: float) -> None:
#     if debug_image is None:
#         return
#     for y, t, m in (920, 'ready', ready_match), (970, 'cancel', cancel_match):
#         cv2.putText(
#             debug_image,
#             f'{t}: {m:1.2f}',
#             (450, y),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.6,
#             (0, 255, 0) if m > required_match else (0, 0, 255),
#             2
#         )
#
#
# def _draw_squad(debug_image: Optional[np.ndarray], squad: Squad) -> None:
#     if debug_image is None:
#         return
#     cv2.putText(
#         debug_image,
#         f'{squad}',
#         (50, 720),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.75,
#         (255, 0, 255),
#         2
#     )


class SelectProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    # READY = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'ready.png'), 0)
    # CANCEL = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'cancel.png'), 0)
    # REQUIRED_MATCH = 0.9

    SHEAR = 0.7
    TARGET_AREA = 2300

    @time_processing
    def process(self, frame: Frame) -> bool:
        y = frame.image_yuv[:, :, 0]

        if self.detect_hero_select(y):
            frame.legend_select = LegendSelect(
                [self._parse_player(r) for r in self.REGIONS['selection'].extract(y)]
            )

            im = np.vstack(self.REGIONS['selection'].extract(y))
            debugops.manual_unsharp_mask(im)
            # [debugops.manual_thresh_otsu(im, scale=1.5) for im in self.REGIONS['selection'].extract(y)]

            return True
        else:
            return False

    def detect_hero_select(self, im: np.ndarray) -> bool:
        pathfinder_region = self.REGIONS['pathfinder'].extract_one(im)
        pathfinder_region = cv2.resize(
            pathfinder_region,
            (300, 100),
            cv2.INTER_NEAREST
        )
        _, thresh = cv2.threshold(
            pathfinder_region,
            0,
            255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU
        )
        cv2.imshow('thresh', thresh)
        cv2.imshow('thresh2', cv2.warpAffine(thresh, np.array([
            [1, self.SHEAR, 0],
            [0, 1., 0]]
        ), (thresh.shape[1], thresh.shape[0])))
        contours, _ = imageops.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if area < 1000:
                continue
            print(abs(area - self.TARGET_AREA), area)
            if abs(area - self.TARGET_AREA) < 500:
                # cnt = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
                cnt = cv2.transform(
                    cnt,
                    np.array([
                        [1, self.SHEAR, 0],
                        [0, 1., 0]]
                    ),
                )
                (x, y), (width, height), angle = cv2.minAreaRect(cnt)
                if abs(width * height - area) > 100:
                    # not a square
                    print('notsquare', width * height, area)
                    continue

                angle = min(abs(angle), abs(angle - 90))
                angle = angle % 90
                print('an', angle)
                if angle > 5:
                    # not at right angles
                    print('angle', abs(width * height - area))
                    continue

                return True
        # debugops.manual_thresh_otsu(pathfinder_region)
        return False

    def _parse_player(self, im: np.ndarray) -> Optional[SelectedLegend]:
        text = imageops.tesser_ocr(
            im,
            scale=4
        )
        return text


def main() -> None:
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = SelectProcessor()

    import glob
    for p in glob.glob('../../../../dev/apex_images/select/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
        frame = Frame.create(
            cv2.resize(cv2.imread(p), (1920, 1080)),
            0,
            True
        )
        pipeline.process(frame)
        print(frame)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)


if __name__ == '__main__':
    main()

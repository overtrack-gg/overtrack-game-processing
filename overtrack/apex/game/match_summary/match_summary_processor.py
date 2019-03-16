import logging
import os
from typing import Optional

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection

logger = logging.getLogger(__name__)


@dataclass
class MatchSummary:
    placed: int


def _draw_match_summary(debug_image: Optional[np.ndarray], summary: MatchSummary) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'{summary}',
        (650, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


class MatchSummaryProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    MATCH_SUMMARY_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'match_summary.png'), 0)
    REQUIRED_MATCH = 0.98

    PLACED_COLOUR = (32, 61, 238)

    @time_processing
    def process(self, frame: Frame) -> bool:
        y = frame.image_yuv[:, :, 0]
        your_squad_image = self.REGIONS['match_summary'].extract_one(y)
        t, thresh = cv2.threshold(your_squad_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        match = np.max(cv2.matchTemplate(
            thresh, self.MATCH_SUMMARY_TEMPLATE, cv2.TM_CCORR_NORMED
        ))
        if match >= self.REQUIRED_MATCH:
            placed = self._get_placed(frame)
            if placed is not None:
                frame.match_summary = MatchSummary(
                    placed=placed
                )
                _draw_match_summary(frame.debug_image, frame.match_summary)
                return True

        return False

    def _get_placed(self, frame: Frame) -> Optional[int]:
        placed_image = self.REGIONS['squad_placed'].extract_one(frame.image).copy()
        cv2.normalize(placed_image, placed_image, 0, 255, cv2.NORM_MINMAX)
        orange = cv2.inRange(
            placed_image,
            np.array(self.PLACED_COLOUR) - 40,
            np.array(self.PLACED_COLOUR) + 40
        )
        text = imageops.tesser_ocr(
            orange
        )
        if text and text[0] == '#':
            try:
                placed = int(text[1:])
            except ValueError:
                logger.warning(f'Could not parse "{text}" as number')
                return None
            else:
                if 1 <= placed <= 20:
                    return placed
                else:
                    logger.warning(f'Rejected placed={placed}')
        else:
            logger.warning(f'Rejected placed text "{text}" - did not get "#"')
            return None

def main() -> None:
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = MatchSummaryProcessor()

    import glob

    for p in glob.glob('../../../../dev/apex_images/match_summary/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
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

import logging
import os
from typing import Optional

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.apex import ocr
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection

logger = logging.getLogger(__name__)


# TODO: each players stats

@dataclass
class SquadSummary:
    champions: bool
    # placed: Optional[int]
    squad_kills: Optional[int]


def _draw_squad_summary(debug_image: Optional[np.ndarray], squad_summary: SquadSummary) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'{squad_summary}',
        (480, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


class SquadSummaryProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    ELIMINATED_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'squad_eliminated.png'), 0)
    CHAMPIONS_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'champions_of_the_arena.png'), 0)
    REQUIRED_MATCH = 0.95

    @time_processing
    def process(self, frame: Frame) -> bool:
        y = frame.image_yuv[:, :, 0]
        champions_eliminated = self.REGIONS['champions_eliminated'].extract_one(y)
        t, thresh = cv2.threshold(champions_eliminated, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        match = np.max(cv2.matchTemplate(
            thresh, self.CHAMPIONS_TEMPLATE, cv2.TM_CCORR_NORMED
        ))
        if match > self.REQUIRED_MATCH:
            champions = True
        else:
            champions = False
            match = np.max(cv2.matchTemplate(
                thresh, self.ELIMINATED_TEMPLATE, cv2.TM_CCORR_NORMED
            ))
        if match > self.REQUIRED_MATCH:
            frame.squad_summary = SquadSummary(
                champions=champions,
                squad_kills=self._process_squad_kills(frame)
            )
            _draw_squad_summary(frame.debug_image, frame.squad_summary)
            return True

        return False

    def _process_squad_kills(self, frame: Frame) -> Optional[int]:
        squad_kills_image = self.REGIONS['squad_kills'].extract_one(frame.image).copy()

        # mask out only yellow text (digits)
        yellow = cv2.inRange(
            squad_kills_image,
            (0,  40,  150),
            (90, 230, 255)
        )
        yellow = cv2.dilate(yellow, None)
        squad_kills_image = cv2.bitwise_and(squad_kills_image, cv2.cvtColor(yellow, cv2.COLOR_GRAY2BGR))

        # cv2.imshow('yellow', yellow)
        # cv2.imshow('squad_kills_image', squad_kills_image)

        squad_kills = imageops.tesser_ocr(
            squad_kills_image,
            engine=ocr.tesseract_ttlakes,
            expected_type=int
        )
        logger.info(f'Got squad_kills={squad_kills}')
        return squad_kills


def main() -> None:
    config_logger('squad_summary', logging.INFO, write_to_file=False)

    pipeline = SquadSummaryProcessor()

    import glob

    for p in glob.glob('../../../../dev/apex_images/squad_summary/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
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

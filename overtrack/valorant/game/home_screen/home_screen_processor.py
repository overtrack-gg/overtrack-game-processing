import logging
import os
from typing import Optional
import Levenshtein as levenshtein

import cv2
import numpy as np

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import time_processing, imageops
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.valorant.game.home_screen.models import HomeScreen


logger = logging.getLogger('HomeScreenProcessor')


def draw_home_screen(debug_image: Optional[np.ndarray], home_screen: HomeScreen) -> None:
    if debug_image is None:
        return

    for c, t in ((0, 0, 0), 4), ((0, 255, 128), 2):
        cv2.putText(
            debug_image,
            str(home_screen),
            (1450, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            c,
            t,
        )


class HomeScreenProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))

    @time_processing
    def process(self, frame: Frame) -> bool:
        if frame.valorant.home_screen:
            return True

        if self.ocr_match(frame, 'social', 'SOCIAL', 0.8) and (
            self.ocr_match(frame, 'home', 'HOME', 0.7) or
            self.ocr_match(frame, 'play', 'PLAY', 0.7)
        ):
            frame.valorant.home_screen = HomeScreen()
            draw_home_screen(frame.debug_image, frame.valorant.home_screen)
            return True

        return False

    def ocr_match(self, frame: Frame, region: str, target: str, requirement: float) -> bool:
        text = self.ocr_region(frame, region)
        match = levenshtein.ratio(text.upper(), target.upper())
        logger.debug(f'OCR match {text.upper()!r} ~ {target.upper()!r} => {match:.2f} > {requirement:.2f} => {match > requirement}')
        return match > requirement

    def ocr_region(self, frame: Frame, target_region: str):
        region = self.REGIONS[target_region].extract_one(frame.image)
        gray = 255 - imageops.normalise(np.min(region, axis=2))
        text = imageops.tesser_ocr(
            gray,
            engine=imageops.tesseract_lstm,
        )
        return text


def main():
    from overtrack.util.logging_config import config_logger
    from overtrack import util
    config_logger(os.path.basename(__file__), level=logging.DEBUG, write_to_file=False)
    
    util.test_processor('home_screen', HomeScreenProcessor(), 'valorant.home_screen', game='valorant')


if __name__ == '__main__':
    main()

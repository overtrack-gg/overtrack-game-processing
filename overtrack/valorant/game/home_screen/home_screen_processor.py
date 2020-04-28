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
        practice_im = self.REGIONS['practice'].extract_one(frame.image)
        practice_gray = 255 - imageops.normalise(np.min(practice_im, axis=2))
        practice_text = imageops.tesser_ocr(
            practice_gray,
            engine=imageops.tesseract_lstm,
        )
        if levenshtein.ratio(practice_text, 'PRACTICE') > 0.8:
            frame.valorant.home_screen = HomeScreen()
            draw_home_screen(frame.debug_image, frame.valorant.home_screen)
            return True

        return False

def main():
    from overtrack.util.logging_config import config_logger
    from overtrack import util
    config_logger(os.path.basename(__file__), level=logging.DEBUG, write_to_file=False)
    util.test_processor('home_screen', HomeScreenProcessor(), 'home_screen', game='valorant')


if __name__ == '__main__':
    main()

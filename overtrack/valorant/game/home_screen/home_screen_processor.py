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
        social_im = self.REGIONS['social'].extract_one(frame.image)
        social_gray = 255 - imageops.normalise(np.min(social_im, axis=2))
        social_text = imageops.tesser_ocr(
            social_gray,
            engine=imageops.tesseract_lstm,
        )
        logger.debug(f'Social text: {social_text!r}')
        if levenshtein.ratio(social_text, 'SOCIAL') > 0.8:

            play_im = self.REGIONS['play'].extract_one(frame.image)
            play_gray = 255 - imageops.normalise(np.min(play_im, axis=2))
            play_text = imageops.tesser_ocr(
                play_gray,
                engine=imageops.tesseract_lstm,
            )
            logger.debug(f'Menu type string: {play_text!r}')
            if levenshtein.ratio(play_text, 'PLAY') > 0.7:
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

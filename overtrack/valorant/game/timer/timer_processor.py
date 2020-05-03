import string

import cv2
import logging
import numpy as np
import os
import re
from typing import Optional

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import time_processing, imageops, debugops
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.valorant.game.timer.models import Timer


logger = logging.getLogger('TimerProcessor')


def draw_timer(debug_image: Optional[np.ndarray], timer: Timer) -> None:
    if debug_image is None:
        return

    for c, t in ((0, 0, 0), 4), ((0, 255, 128), 2):
        cv2.putText(
            debug_image,
            str(timer),
            (700, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            c,
            t,
        )


class TimerProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    SPIKE_PLANTED_TEMPLATE = cv2.imread(os.path.join(os.path.dirname(__file__), 'data', 'spike_planted.png'), 0)
    SPIKE_PLANTED_REQUIRED_MATCH = 0.5
    BUY_PHASE_TEMPLATE = cv2.imread(
        os.path.join(os.path.dirname(__file__), 'data', 'buy_phase.png'),
        0
    )

    @time_processing
    def process(self, frame: Frame) -> bool:
        # timer_y = self.REGIONS['timer'].extract_one(frame.image_yuv[:, :, 0])
        # _, timer_y_thresh = cv2.threshold(timer_y, 230, 255, cv2.THRESH_BINARY)

        spike_planted_im = self.REGIONS['spike_planted'].extract_one(frame.image)
        spike_planted_thresh = cv2.inRange(
            spike_planted_im,
            (0, 0, 130),
            (10, 10, 250),
        )
        # cv2.imshow('spike_planted_im', spike_planted_im)
        # cv2.imshow('spike_planted_thresh', spike_planted_thresh)
        # cv2.imshow('SPIKE_PLANTED_TEMPLATE', self.SPIKE_PLANTED_TEMPLATE)
        spike_planted_match = np.max(cv2.matchTemplate(
            spike_planted_thresh,
            self.SPIKE_PLANTED_TEMPLATE,
            cv2.TM_CCORR_NORMED,
        ))
        logger.debug(f'Spike planted match: {spike_planted_match:.2f}')
        spike_planted = bool(spike_planted_match > self.SPIKE_PLANTED_REQUIRED_MATCH)

        if spike_planted:
            buy_phase = False
        else:
            buy_phase_gray = np.min(self.REGIONS['buy_phase'].extract_one(frame.image), axis=2)
            buy_phase_norm = imageops.normalise(buy_phase_gray, bottom=70)
            # cv2.imshow('buy_phase_norm', buy_phase_norm)
            buy_phase_match = np.max(cv2.matchTemplate(buy_phase_norm, self.BUY_PHASE_TEMPLATE, cv2.TM_CCORR_NORMED))
            logger.debug(f'Buy phase match: {buy_phase_match}')
            buy_phase = buy_phase_match > 0.9


        countdown_text = None
        if not spike_planted:
            countdown_gray = np.min(self.REGIONS['timer'].extract_one(frame.image), axis=2)
            countdown_norm = 255 - imageops.normalise(countdown_gray, bottom=80)
            # debugops.test_tesser_engines(
            #     countdown_norm
            # )
            countdown_text = imageops.tesser_ocr(
                countdown_norm,
                # whitelist=string.digits + ':.',
                engine=imageops.tesseract_only
            )

            if len(countdown_text) > 6:
                countdown_text = None

        frame.valorant.timer = Timer(
            spike_planted=spike_planted,
            buy_phase=buy_phase,
            countdown=countdown_text,
        )
        draw_timer(frame.debug_image, frame.valorant.timer)
        return frame.valorant.timer.valid


def main():
    from overtrack.util.logging_config import config_logger
    from overtrack import util
    config_logger(os.path.basename(__file__), level=logging.DEBUG, write_to_file=False)
    util.test_processor('ingame', TimerProcessor(), 'timer', game='valorant', wait=True)


if __name__ == '__main__':
    main()

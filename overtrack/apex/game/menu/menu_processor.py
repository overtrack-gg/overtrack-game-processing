import logging
import os

import cv2
import numpy as np

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection
from .models import *


def _draw_buttons_match(debug_image: Optional[np.ndarray], ready_match: float, cancel_match: float, required_match: float) -> None:
    if debug_image is None:
        return
    for y, t, m in (920, 'ready', ready_match), (970, 'cancel', cancel_match):
        cv2.putText(
            debug_image,
            f'{t}: {m:1.2f}',
            (0, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0) if m > required_match else (0, 0, 255),
            2
        )


def _draw_play_menu(debug_image: Optional[np.ndarray], menu: PlayMenu) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'{menu}',
        (50, 720),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 0, 255),
        2
    )


class MenuProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    READY = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'ready.png'), 0)
    CANCEL = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'cancel.png'), 0)
    REQUIRED_MATCH = 0.9

    CROWN = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'crown.png'), 0)

    @time_processing
    def process(self, frame: Frame):
        y = frame.image_yuv[:, :, 0]

        ready_button = self.REGIONS['ready_button'].extract_one(y)
        t, thresh = cv2.threshold(ready_button, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        ready_match = np.max(cv2.matchTemplate(
            thresh, self.READY, cv2.TM_CCORR_NORMED
        ))
        if ready_match >= self.REQUIRED_MATCH:
            cancel_match = 0.
        else:
            cancel_match = np.max(cv2.matchTemplate(
                thresh, self.CANCEL, cv2.TM_CCORR_NORMED
            ))
        frame.apex_play_menu_match = round(float(max(ready_match, cancel_match)), 5)
        _draw_buttons_match(frame.debug_image, ready_match, cancel_match, self.REQUIRED_MATCH)

        if ready_match >= self.REQUIRED_MATCH or cancel_match >= self.REQUIRED_MATCH:
            player_name_image = self.REGIONS['player_name'].extract_one(y)
            mate1, mate2 = self.REGIONS['squadmates'].extract(y)
            frame.apex_play_menu = PlayMenu(
                player_name=self._ocr_playername(player_name_image),
                squadmates=(self._ocr_playername(mate1), self._ocr_playername(mate2)),
                ready=cancel_match >= self.REQUIRED_MATCH
            )
            self.REGIONS.draw(frame.debug_image)
            _draw_play_menu(frame.debug_image, frame.apex_play_menu)

            return True

        else:
            return False

    def _ocr_playername(self, player_name_image: np.ndarray) -> str:
        # crop out crown
        _, thresh = cv2.threshold(player_name_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        mnv, mxv, mnl, mxl = cv2.minMaxLoc(cv2.matchTemplate(thresh, self.CROWN, cv2.TM_CCORR_NORMED))
        if mxv > 0.99:
            player_name_image = player_name_image[:, mxl[0] + self.CROWN.shape[1]:]

        player_name = imageops.tesser_ocr(
            player_name_image,
            scale=4
        )
        return player_name


def main() -> None:
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = MenuProcessor()

    import glob
    for p in glob.glob('../../../../dev/apex_images/menu/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
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

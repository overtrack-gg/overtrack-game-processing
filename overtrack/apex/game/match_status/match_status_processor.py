import logging
import os
import string
import Levenshtein as levenshtein
from typing import List, Optional, Tuple

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.apex import data, ocr
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection


logger = logging.getLogger(__name__)


@dataclass
class MatchStatus:
    squads_left: int
    players_alive: Optional[int]
    kills: Optional[int]


def _draw_status(debug_image: Optional[np.ndarray], status: MatchStatus) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'{status}',
        (1150, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 0, 255),
        2
    )


class MatchStatusProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), '..', 'data', 'regions', '16_9.zip'))
    SKULL_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'skull.png'), 0)
    SUBS = [
        '?2',
        'O0',
        'L1',
        'I1',
        'B6',
    ]

    @time_processing
    def process(self, frame: Frame):
        y = cv2.cvtColor(frame.image, cv2.COLOR_BGR2YUV)[:, :, 0]

        squads_left = self._get_squads_left(y)
        if squads_left is not None:
            frame.match_status = MatchStatus(
                squads_left=squads_left,
                players_alive=self._get_players_alive(y) if squads_left > 4 else None,
                kills=self._get_kills(y)
            )
            _draw_status(frame.debug_image, frame.match_status)
            return True
        else:
            return False

    def _get_squads_left(self, y: np.ndarray) -> Optional[int]:
        squads_left_text = imageops.tesser_ocr(
            self.REGIONS['squads_left'].extract_one(y),
            engine=imageops.tesseract_lstm,
            scale=2,
            invert=True
        ).upper()
        squads_left_text = ''.join(
            c for c in squads_left_text if c in string.ascii_uppercase + string.digits + ' '
        ).strip().replace('B', '6')
        text_match = levenshtein.ratio(squads_left_text[2:].replace(' ', ''), 'SQUADSLEFT')
        if text_match > 0.8:
            number_text = squads_left_text[:3].split(' ', 1)[0]
            for s1, s2 in self.SUBS:
                number_text = number_text.replace(s1, s2)
            try:
                squads_left = int(number_text)
            except ValueError:
                logger.warning(f'Failed to parse "{number_text}" as int - extracted from "{squads_left_text}"')
                return None
            else:
                if 2 <= squads_left <= 20:
                    return squads_left
                else:
                    logger.warning(f'Got squads_left={squads_left} - rejecting. Extracted from "{squads_left_text}"')
                    return None
        elif text_match > 0.6:
            logger.warning(f'Refusing to parse "{squads_left_text} as squads left - match={text_match}')
            return None
        else:
            return None

    def _get_players_alive(self, y: np.ndarray) -> Optional[int]:
        players_alive = imageops.tesser_ocr(
            self.REGIONS['alive'].extract_one(y),
            engine=ocr.tesseract_ttlakes_digits,
            scale=4,
            expected_type=int
        )
        # shows a '?' if below 10
        if players_alive and 10 <= players_alive <= 60:
            return players_alive
        else:
            logger.warning(f'Rejecting players_alive={players_alive}')
            return None

    def _get_kills(self, y: np.ndarray) -> Optional[int]:
        kills_image = self.REGIONS['kills'].extract_one(y)
        _, kills_thresh = cv2.threshold(kills_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        match = cv2.matchTemplate(
            kills_thresh,
            self.SKULL_TEMPLATE,
            cv2.TM_CCORR_NORMED
        )
        mn, mx, mnloc, mxloc = cv2.minMaxLoc(match)
        if mx > 0.9:
            kills_image = kills_image[:, mxloc[0] + self.SKULL_TEMPLATE.shape[1]:]
            # cv2.imshow('kills', cv2.resize(kills_image, (100, 100)))

            kills_text = imageops.tesser_ocr(
                kills_image,
                engine=imageops.tesseract_lstm,
                scale=2,
                invert=True
            ).upper().strip()
            for s1, s2 in self.SUBS:
                kills_text = kills_text.replace(s1, s2)
            try:
                kills = int(kills_text)
                if 0 < kills <= 50:
                    return kills
                else:
                    logger.warning(f'Rejecting kills={kills}')
                    return None
            except ValueError:
                logger.warning(f'Cannot parse "{kills_text}" as int')
                return None
        else:
            return None


def main() -> None:

    print(levenshtein.ratio(' SAUADS LEFT'.replace(' ', ''), 'SQUADSLEFT'))

    import glob
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = MatchStatusProcessor()
    ps = ["M:/Videos/apex/2_103.png", "C:/Users/simon/workspace/overtrack_2/dev/apex_images/mpv-shot0171.png"]
    ps += glob.glob('M:/Videos/apex/2_7*.png')
    for p in ps:
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
        cv2.imshow('debug', frame.debug_image)
        if 'match_status' in frame and frame.match_status.kills:
            cv2.waitKey(0)
        else:
            cv2.waitKey(0)


if __name__ == '__main__':
    main()

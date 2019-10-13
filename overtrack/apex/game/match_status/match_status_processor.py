import logging
import os
import re
import string
from typing import Optional, Tuple

import Levenshtein as levenshtein
import cv2
import dataclasses
import numpy as np

from overtrack.apex import ocr, data
from overtrack.apex.game.match_status import MatchStatus
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.imageops import matchTemplate
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection

logger = logging.getLogger(__name__)


def _draw_status(debug_image: Optional[np.ndarray], status: MatchStatus) -> None:
    if debug_image is None:
        return
    dstr = str(dataclasses.replace(status, rank_badge_matches=None))
    dstr = re.sub(r'([a-zA-Z]+[a-zA-Z0-9_]*=None,? ?)', '', dstr)
    lines = [
        dstr,
        '    rank_badge_matches=' + str(status.rank_badge_matches)
    ]

    for y, line in enumerate(lines):
        cv2.putText(
            debug_image,
            line,
            (400, 150 + 30 * y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 0),
            3
        )
        cv2.putText(
            debug_image,
            line,
            (400, 150 + 30 * y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 0, 255),
            1
        )


class MatchStatusProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), '..', 'data', 'regions', '16_9.zip'))
    HEAD_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'head.png'), 0)
    SKULL_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'skull.png'), 0)
    RANK_TEMPLATES = [
        (
            rank,
            imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'ranks', rank + '.png')),
            cv2.cvtColor(imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'ranks', rank + '.png'), -1)[:, :, 3], cv2.COLOR_GRAY2BGR)
        ) for rank in data.ranks
    ]
    SUBS = [
        '?2',
        'O0',
        'L1',
        'I1',
        'B6',
    ]

    def __init__(self):
        super().__init__()
        self.last_rank_template = 0

    def eager_load(self):
        self.REGIONS.eager_load()

    @time_processing
    def process(self, frame: Frame):
        y = cv2.cvtColor(frame.image, cv2.COLOR_BGR2YUV)[:, :, 0]

        # The text moves depending on normal or elite queue
        # Look for the "head" template showing players alive
        head_region = np.max(self.REGIONS['head_region'].extract_one(frame.image), axis=2)
        _, head_thresh = cv2.threshold(head_region, 200, 255, cv2.THRESH_BINARY)
        head_match = cv2.matchTemplate(head_thresh, self.HEAD_TEMPLATE, cv2.TM_CCORR_NORMED)
        mnv, mxv, mnl, mxl = cv2.minMaxLoc(head_match)
        frame.match_status_match = round(float(mxv), 2)
        if mxv < 0.9:
            return False

        # 90 for unranked, 15 for ranked
        ranked = mxl[0] < 30

        squads_left_text = self._parse_squads_left_text(y, ranked)
        squads_left = self._get_squads_left(squads_left_text)
        if not squads_left:
            solos_players_left = self._get_squads_left(squads_left_text, solos=True)
        else:
            solos_players_left = None

        if squads_left or solos_players_left:
            # if left < 1750:
            #     streak = self._get_streak(y, left + 115)
            # else:
            #     streak = None
            if squads_left and ranked:
                rank_badge_image = self.REGIONS['rank_badge'].extract_one(frame.image)
                rank_badge_matches = self._get_rank_badge(rank_badge_image)
                rank_text_image = self.REGIONS['rank_text'].extract_one(frame.image_yuv[:, :, 0])
                rank_text = imageops.tesser_ocr(
                    rank_text_image,
                    whitelist='IV',
                    scale=3,
                    invert=True,
                    engine=imageops.tesseract_only
                )
                rp_text_image = self.REGIONS['ranked_rp'].extract_one(frame.image_yuv[:, :, 0])
                rp_text = imageops.tesser_ocr(
                    rp_text_image,
                    whitelist=string.digits + '+-RP',
                    scale=3,
                    invert=True,
                    engine=imageops.tesseract_only
                )
            else:
                rank_badge_matches = None
                rank_text = None
                rp_text = None

            frame.match_status = MatchStatus(
                squads_left=squads_left,
                players_alive=self._get_players_alive(y, ranked) if squads_left and squads_left > 4 else None,
                kills=self._get_kills(y, ranked),
                ranked=ranked,

                rank_badge_matches=rank_badge_matches,
                rank_text=rank_text,
                rp_text=rp_text,

                solos_players_left=solos_players_left,
            )
            self.REGIONS.draw(frame.debug_image)
            _draw_status(frame.debug_image, frame.match_status)
            return True
        else:
            return False

    def _parse_squads_left_text(self, luma: np.ndarray, ranked: bool) -> str:
        prefix = 'ranked_' if ranked else ''
        region = self.REGIONS[prefix + 'squads_left'].extract_one(luma)
        squads_left_text = imageops.tesser_ocr(
            region,
            engine=imageops.tesseract_lstm,
            scale=2,
            invert=True
        ).upper()
        squads_left_text = ''.join(
            c for c in squads_left_text if c in string.ascii_uppercase + string.digits + ' '
        ).strip().replace('B', '6')
        return squads_left_text

    def _get_squads_left(self, squads_left_text: str, solos: bool = False) -> Optional[int]:
        expected_text = 'SQUADSLEFT' if not solos else 'PLAYERSLEFT'
        text_match = levenshtein.ratio(squads_left_text[2:].replace(' ', ''), expected_text)
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
                if 2 <= squads_left <= (20 if not solos else 60):
                    return squads_left
                else:
                    logger.warning(f'Got squads_left={squads_left} - rejecting. Extracted from "{squads_left_text}"')
                    return None
        elif text_match > 0.6:
            logger.warning(f'Refusing to parse "{squads_left_text} as squads left - match={text_match}')
            return None
        else:
            return None

    def _get_players_alive(self, luma: np.ndarray, ranked: bool) -> Optional[int]:
        prefix = 'ranked_' if ranked else ''
        region = self.REGIONS[prefix + 'alive'].extract_one(luma)
        players_alive = imageops.tesser_ocr(
            region,
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

    def _get_kills(self, luma: np.ndarray, ranked: bool) -> Optional[int]:
        prefix = 'ranked_' if ranked else ''
        region = self.REGIONS[prefix + 'kills'].extract_one(luma)
        _, kills_thresh = cv2.threshold(region, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kills_thresh = cv2.copyMakeBorder(kills_thresh, 5, 5, 0, 5, cv2.BORDER_CONSTANT, value=0)
        match = cv2.matchTemplate(
            kills_thresh,
            self.SKULL_TEMPLATE,
            cv2.TM_CCORR_NORMED
        )
        mn, mx, mnloc, mxloc = cv2.minMaxLoc(match)
        if mx > 0.9:
            kills_image = region[:, mxloc[0] + self.SKULL_TEMPLATE.shape[1]:]
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
                logger.warning(f'Cannot parse kills="{kills_text}" as int')
                return None
        else:
            return None

    def _get_rank_badge(self, rank_badge_image: np.ndarray) -> Tuple[float, ...]:
        matches = []
        for rank, template, mask in self.RANK_TEMPLATES:
            match = np.min(matchTemplate(
                rank_badge_image,
                template,
                cv2.TM_SQDIFF,
                mask=mask
            ))
            matches.append(round(match, 1))
        return tuple(matches)


if __name__ == '__main__':
    from overtrack import util

    util.test_processor('match', MatchStatusProcessor(), 'match_status', game='apex')

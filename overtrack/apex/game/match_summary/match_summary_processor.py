import logging
import os
import string
from typing import Optional, Tuple

import cv2
import numpy as np
from dataclasses import dataclass, fields

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing, debugops, textops
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.util.textops import mmss_to_seconds

logger = logging.getLogger(__name__)


@dataclass
class XPStats:
    won: bool = False
    top3_finish: bool = False
    time_survived: Optional[int] = None
    kills: Optional[int] = None
    damage_done: Optional[int] = None
    revive_ally: Optional[int] = None
    respawn_ally: Optional[int] = None

@dataclass
class MatchSummary:
    placed: int
    xp_stats: XPStats


def _draw_match_summary(debug_image: Optional[np.ndarray], summary: MatchSummary) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'MatchSummary(placed={summary.placed})',
        (650, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )
    for i, f in enumerate(fields(XPStats)):
        cv2.putText(
            debug_image,
            f'{f.name}: {getattr(summary.xp_stats, f.name)}',
            (1000, 150 + i * 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )


class MatchSummaryProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    MATCH_SUMMARY_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'match_summary.png'), 0)
    REQUIRED_MATCH = 0.98

    PLACED_COLOUR = (32, 61, 238)

    XP_STATS = [
        'Won Match',
        'Top 3 Finish',
        'Time Survived',
        'Kills',
        'Damage Done',
        'Revive Ally',
        'Respawn Ally'
    ]
    XP_STATS_NORMED = [s.replace(' ', '').upper() for s in XP_STATS]
    SUBS = [
        '[(',
        '{(',

        '])',
        '})'
    ]

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
                    placed=placed,
                    xp_stats=self._parse_xp_breakdown(y)
                )
                _draw_match_summary(frame.debug_image, frame.match_summary)
                return True

        return False

    def _parse_xp_breakdown(self, y: np.ndarray) -> XPStats:
        xp_breakdown_image = self.REGIONS['xp_breakdown'].extract_one(y)
        xp_breakdown_image = cv2.adaptiveThreshold(
            xp_breakdown_image,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            63,
            -30
        )
        lines = imageops.tesser_ocr(
            xp_breakdown_image,
            whitelist=string.ascii_letters + string.digits + '() \n',
            engine=imageops.tesseract_lstm_multiline
        )
        for s1, s2 in self.SUBS:
            lines = lines.replace(s1, s2)

        xp_stats = XPStats()
        for line in lines.splitlines():
            stat_name, stat_value = self._parse_stat(line)
            if stat_name == 'Won Match':
                xp_stats.won = True
            elif stat_name == 'Top 3 Finish':
                xp_stats.top3_finish = True
            elif stat_name and stat_value is not None:
                # require stat value parsed correctly
                if stat_name == 'Time Survived':
                    xp_stats.time_survived = mmss_to_seconds(stat_value)
                elif stat_name == 'Kills':
                    xp_stats.kills = stat_value
                elif stat_name == 'Damage Done':
                    xp_stats.damage_done = stat_value
                elif stat_name == 'Revive Ally':
                    xp_stats.revive_ally = stat_value
                elif stat_name == 'Respawn Ally':
                    xp_stats.respawn_ally = stat_value
        return xp_stats

    def _parse_stat(self, line: str) -> Tuple[Optional[str], Optional[int]]:
        if len(line) > 5:
            parts = line.split('(', 1)
            if len(parts) > 1:
                stat_name_s, stat_value_s = parts[:2]
            else:
                stat_name_s, stat_value_s = line, None
            match, stat_name_normed = textops.matches_ratio(stat_name_s.replace(' ', '').upper(), self.XP_STATS_NORMED)
            if match > 0.8:
                stat_name = self.XP_STATS[self.XP_STATS_NORMED.index(stat_name_normed)]
                if stat_value_s:
                    stat_value = self._parse_stat_number(stat_value_s)
                    if stat_value is not None:
                        logger.info(f'Parsed {stat_name}={stat_value} ("{line}" ~ {match:1.2f})')
                        return stat_name, stat_value
                    else:
                        logger.info(f'Unable to parse value for {stat_name} ("{line}" ~ {match:1.2f})')
                        return stat_name, None
                else:
                    return stat_name, None
            else:
                logger.warning(f'Don\'t know how to parse stat "{line}"')
                return None, None
        elif line:
            logger.warning(f'Ignoring stat "{line}" - too short')
            return None, None
        else:
            return None, None

    def _parse_stat_number(self, stat_value_s: str) -> Optional[int]:
        stat_value_s = stat_value_s.upper()

        # common errors in parsing digits
        for s1, s2 in 'D0', 'I1', 'L1':
            stat_value_s = stat_value_s.replace(s1, s2)

        # remove brackets, spaces, X (e.g. in "Kills (x3)"), time separators, commas
        stat_value_s = ''.join(c for c in stat_value_s if c not in '() X:.,;|')

        try:
            return int(stat_value_s)
        except ValueError:
            return None

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

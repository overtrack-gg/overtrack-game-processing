import logging
import os

import cv2
import numpy as np

from overtrack.apex import ocr
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.util.textops import mmss_to_seconds
from .models import *

logger = logging.getLogger(__name__)



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
    for i, stats in enumerate(squad_summary.player_stats):
        for t, c in (3, (0, 0, 0)), (1, (0, 255, 0)):
            cv2.putText(
                debug_image,
                f'{stats}',
                (i * 200, 550 + 30 * i),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                c,
                t
            )


def _draw_match(debug_image: Optional[np.ndarray], match: float) -> None:
    if debug_image is None:
        return


class SquadSummaryProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    ELIMINATED_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'squad_eliminated.png'), 0)
    CHAMPIONS_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'champions_of_the_arena.png'), 0)
    REQUIRED_MATCH = 0.95

    def eager_load(self):
        self.REGIONS.eager_load()

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
        frame.squad_summary_match = round(match, 5)
        if match > self.REQUIRED_MATCH:
            frame.squad_summary = SquadSummary(
                champions=champions,
                squad_kills=self._process_squad_kills(frame),
                player_stats=self._process_player_stats(y)
            )
            self.REGIONS.draw(frame.debug_image)
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

    def _process_player_stats(self, y: np.ndarray) -> Tuple[PlayerStats, PlayerStats, PlayerStats]:
        names = []
        for im in self.REGIONS['names'].extract(y):
            im = 255 - cv2.bitwise_and(
                im,
                cv2.dilate(
                    cv2.threshold(im, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1],
                    None
                )
            )
            im = cv2.resize(im, (0, 0), fx=2, fy=2)
            im = cv2.GaussianBlur(im, (0, 0), 1)

            name = imageops.tesser_ocr(
                im,
                engine=imageops.tesseract_lstm,
            ).replace(' ', '')
            match = np.mean(imageops.tesseract_lstm.AllWordConfidences())
            logger.info(f'Got name "{name}" ~ {match:1.2f}')
            if match < 0.75:
                name = imageops.tesser_ocr(
                    im,
                    engine=imageops.tesseract_only,
                )
                logger.info(f'Using "{name}" instead')
            names.append(name)

        stat_images = self.REGIONS['stats'].extract(y)
        # remove 'M' and 'S' from survived time
        for image in stat_images[6:9]:
            comp_image, comps = imageops.connected_components(cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1])
            for component in comps:
                # MS chars are 16 px high
                if 14 < component.h < 17:
                    # mask out those components
                    mask = (comp_image == component.label).astype(np.uint8) * 255
                    mask = cv2.dilate(mask, None)
                    image[:] = cv2.bitwise_and(255 - mask, image)

        stats = imageops.tesser_ocr_all(
            stat_images,
            engine=ocr.tesseract_ttlakes_digits,
            expected_type=int
        )
        for i in 6, 7, 8:
            if stats[i] is not None:
                stats[i] = mmss_to_seconds(stats[i])

        # typing: ignore
        # noinspection PyTypeChecker
        return tuple([PlayerStats(names[i], *stats[i::3]) for i in range(3)])


def main() -> None:
    config_logger('squad_summary', logging.INFO, write_to_file=False)

    pipeline = SquadSummaryProcessor()

    import glob

    ps = "C:/Users/simon/workspace/overtrack_2/dev/apex_images/squad_summary/mpv-shot0193.png"
    for p in [ps] + glob.glob('../../../../dev/apex_images/squad_summary/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
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

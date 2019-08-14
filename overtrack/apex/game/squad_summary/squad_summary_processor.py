import logging
import os
import pprint

import cv2
import dataclasses
import numpy as np

from overtrack.apex import ocr
from overtrack.apex.game.squad_summary.models import *
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.util.textops import mmss_to_seconds
from overtrack.util.uploadable_image import lazy_upload

logger = logging.getLogger(__name__)

def _draw_squad_summary(debug_image: Optional[np.ndarray], squad_summary: SquadSummary) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'{dataclasses.replace(squad_summary, player_stats=None, image=None)}',
        (100, 300),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )
    for i, stats in enumerate(squad_summary.player_stats):
        for t, c in (3, (0, 0, 0)), (1, (0, 255, 0)):
            cv2.putText(
                debug_image,
                f'{stats}',
                (i * 100, 800 + 30 * i),
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

    TEMPLATES = {
        k: imageops.imread(os.path.join(os.path.dirname(__file__), 'data', k + '.png'), 0)
        for k in [
            'squad_eliminated',
            'champions_of_the_arena',
            'match_summary'
        ]
    }

    REQUIRED_MATCH = 0.75

    def eager_load(self):
        self.REGIONS.eager_load()

    @time_processing
    def process(self, frame: Frame) -> bool:
        y = frame.image_yuv[:, :, 0]
        champions_eliminated = self.REGIONS['champions_eliminated'].extract_one(y)
        t, thresh = cv2.threshold(champions_eliminated, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # cv2.imshow('thresh', thresh)

        match, key = imageops.match_templates(
            thresh,
            self.TEMPLATES,
            cv2.TM_CCORR_NORMED,
            self.REQUIRED_MATCH
        )
        frame.squad_summary_match = round(match, 5)
        if match > self.REQUIRED_MATCH:
            champions = key in ['champions_of_the_arena']

            frame.squad_summary = SquadSummary(
                champions=champions,
                placed=self._process_yellowtext(self.REGIONS['placed'].extract_one(frame.image), hash=True),
                squad_kills=self._process_yellowtext(self.REGIONS['squad_kills'].extract_one(frame.image), hash=False),
                player_stats=self._process_player_stats(y),
                elite=False,
                image=lazy_upload('squad_summary', self.REGIONS.blank_out(frame.image), frame.timestamp, selection='last'),
            )
            self.REGIONS.draw(frame.debug_image)
            _draw_squad_summary(frame.debug_image, frame.squad_summary)
            return True

        return False

    def _process_yellowtext(self, image: np.ndarray, hash: bool) -> Optional[int]:
        # mask out only yellow text (digits)
        yellow = cv2.inRange(
            image,
            (0,  40,  150),
            (90, 230, 255)
        )
        yellow = cv2.dilate(yellow, None)
        squad_kills_image = cv2.bitwise_and(image, cv2.cvtColor(yellow, cv2.COLOR_GRAY2BGR))
        squad_kills_image_g = np.max(squad_kills_image, axis=2)
        squad_kills_image_g = cv2.erode(squad_kills_image_g, np.ones((2,2)))

        # from overtrack.util import  ps
        # cv2.imshow('yellow', yellow)
        # cv2.imshow('squad_kills_image', squad_kills_image)
        # cv2.imshow('squad_kills_image_g', squad_kills_image_g)
        # debugops.test_tesser_engines(squad_kills_image_g, scale=4)

        text = imageops.tesser_ocr(
            squad_kills_image_g,
            engine=imageops.tesseract_lstm,
            scale=4,
            blur=4,
            invert=True
        )
        otext = text
        text = text.upper()
        for s1, s2 in '|1', 'I1', 'L1', 'O0', 'S5':
            text = text.replace(s1, s2)
        logger.info(f'Got text={otext} -> {text}')

        if hash:
            for hashchar in '#H':
                text = text.replace(hashchar, '')

        try:
            return int(text)
        except ValueError:
            logger.warning(f'Could not parse "{text}" as int')
            return None

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
        # for image in stat_images[6:9]:
        #     comp_image, comps = imageops.connected_components(cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1])
        #     for component in comps:
        #         # MS chars are 17 px high
        #         if 14 < component.h < 19:
        #             # mask out those components
        #             mask = (comp_image == component.label).astype(np.uint8) * 255
        #             mask = cv2.dilate(mask, None)
        #             image[:] = cv2.bitwise_and(255 - mask, image)

        # for im in stat_images:
        #     from overtrack.util import debugops
        #     debugops.test_tesser_engines(im)

        stats = imageops.tesser_ocr_all(
            stat_images,
            engine=ocr.tesseract_ttlakes_digits_specials,
        )
        for i in range(len(stats)):
            value = stats[i]
            if value:
                value = value.lower().replace(' ', '')
                for c1, c2 in 'l1', 'i1', 'o0':
                    value = value.replace(c1, c2)
            if 6 <= i <= 8:
                # survival time
                if stats[i] is not None:
                    seconds_s = value.replace(':', '')
                    try:
                        seconds = int(seconds_s)
                    except ValueError as e:
                        logger.warning(f'Could not parse "{stats[i]}" as int: {e}')
                        seconds = None
                    else:
                        seconds = mmss_to_seconds(seconds)
                        logger.info(f'MM:SS {stats[i]} -> {seconds}')
                    stats[i] = seconds
            else:
                try:
                    stats[i] = int(value)
                except ValueError as e:
                    logger.warning(f'Could not parse "{value}" as int" {e}')
                    stats[i] = None

        # typing: ignore
        # noinspection PyTypeChecker
        r = tuple([PlayerStats(names[i], *stats[i::3]) for i in range(3)])
        logger.info(f'Got {pprint.pformat(r)}')
        return r


def main() -> None:
    config_logger('squad_summary', logging.INFO, write_to_file=False)

    pipeline = SquadSummaryProcessor()

    import glob

    for p in (list(reversed(glob.glob("C:/Users/simon/overtrack_2/apex_images/squad_summary/*.png"))) +
              glob.glob("C:/Users/simon/overtrack_2/apex_images/**/*.png", recursive=True)):
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

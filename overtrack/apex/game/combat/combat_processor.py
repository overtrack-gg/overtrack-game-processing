import logging
import os
from typing import Optional, List

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing, debugops
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection

logger = logging.getLogger(__name__)


EventTypes = [
    'ELIMINATED',
    'KNOCKED DOWN',
    'ASSIST, ELIMINATION',
    'ASSIST, KNOCK DOWN'
]

@dataclass
class Event:
    type: str
    width: int
    # name: str
    # damage: Optional[int]

    match: float


@dataclass
class CombatLog:
    events: List[Event]


def _draw_log(debug_image: Optional[np.ndarray], log: CombatLog) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'Combat Log:',
        (740, 200),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )
    for i, event in enumerate(log.events):
        cv2.putText(
            debug_image,
            f'{event}',
            (760, 200 + 30 * (i + 1)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2
        )


class CombatProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    REQUIRED_MATCH = 0.75
    TEMPLATES = {
        # these need to go first, so they can mask out the others
        'ASSIST, ELIMINATION': imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'assist_elimination.png'), 0),
        'ASSIST, KNOCK DOWN': imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'assist_knockdown.png'), 0),

        'ELIMINATED': imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'eliminated.png'), 0),
        'KNOCKED DOWN': imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'knocked_down.png'), 0),
    }

    @time_processing
    def process(self, frame: Frame) -> bool:
        image_region = self.REGIONS['kill_text']
        region = image_region.extract_one(frame.image_yuv[:, :, 0])
        region_color = image_region.extract_one(frame.image)
        thresh = imageops.unsharp_mask(
            region,
            3.5,
            6,
            254
        )
        events: List[Event] = []
        for event_type, template in self.TEMPLATES.items():
            match = cv2.matchTemplate(
                thresh,
                template,
                cv2.TM_CCORR_NORMED
            )
            for _ in range(4):
                mnv, mxv, mnl, mxl = cv2.minMaxLoc(match)
                if mxv > self.REQUIRED_MATCH:

                    width = ((1920 // 2) - (mxl[0] + image_region.regions[0][0])) * 2 - template.shape[1]
                    left = mxl[0] + template.shape[1]

                    logger.info(f'Saw {event_type} ~ {mxv:1.2f}: w={width}, x={left}')

                    # name_image = region_color[
                    #     max(0, mxl[1] - 5):min(mxl[1] + template.shape[0] + 5, region.shape[0]),
                    #     left:left + width
                    # ]
                    # cv2.imshow('name', name_image)
                    # print(width)
                    # debugops.test_tesser_engines(name_image)
                    # cv2.waitKey(0)

                    events.append(Event(
                        event_type,
                        width,
                        # None,
                        # None,

                        round(mxv, 4)
                    ))

                    match[
                        max(0, mxl[1] - 20):min(mxl[1] + 20, match.shape[0]),
                        max(0, mxl[0] - 20):min(mxl[0] + 20, match.shape[0]),
                    ] = 0
                    thresh[
                        max(0, mxl[1] - 10):min(mxl[1] + 30, match.shape[0]),
                        :
                    ] = 0
                else:
                    break

        if len(events):
            frame.combat_log = CombatLog(events)
            _draw_log(frame.debug_image, frame.combat_log)
            return True
        else:
            return False


def main() -> None:
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = CombatProcessor()

    import glob

    for p in glob.glob('../../../../dev/apex_images/kill/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
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

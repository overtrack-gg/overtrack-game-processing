import logging
import os
from typing import Optional, Tuple

import cv2
import numpy as np
from dataclasses import dataclass

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection

logger = logging.getLogger(__name__)


@dataclass
class YourSquad:
    names: Tuple[Optional[str], Optional[str], Optional[str]]


def _draw_your_squad(debug_image: Optional[np.ndarray], squad: YourSquad) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'{squad}',
        (400, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


class YourSquadProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    YOUR_SQUAD_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'your_squad.png'), 0)
    REQUIRED_MATCH = 0.95

    @time_processing
    def process(self, frame: Frame):
        y = frame.image_yuv[:, :, 0]

        your_squad_image = self.REGIONS['your_squad'].extract_one(y)
        t, thresh = cv2.threshold(your_squad_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        match = np.max(cv2.matchTemplate(
            thresh, self.YOUR_SQUAD_TEMPLATE, cv2.TM_CCORR_NORMED
        ))

        cv2.imshow('thresh', thresh)
        print(match)

        if match >= self.REQUIRED_MATCH:
            # TODO: improve OCR
            names = imageops.tesser_ocr_all(
                self.REGIONS['names'].extract(y),
                engine=imageops.tesseract_lstm,
                invert=True
            )
            frame.your_squad = YourSquad(
                (self._to_name(names[0]), self._to_name(names[1]), self._to_name(names[2]))
            )
            _draw_your_squad(frame.debug_image, frame.your_squad)
            return True
        else:
            return False

    def _to_name(self, name_text: str) -> Optional[str]:
        name_text = name_text.replace('[', '(').replace(']', ')')
        if name_text[0] == '(' and name_text[-1] == ')':
            return name_text[1:-1].replace(' ', '')
        else:
            logger.warning(f'Got name "{name_text}" for player - rejecting')
            return None


def main() -> None:
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = YourSquadProcessor()

    import glob
    ps = [
        "M:/Videos/apex/2_273.png"
    ]
    for p in ps + glob.glob('../../../../dev/apex_images/your_squad/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
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

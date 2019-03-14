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
class Data:
    pass


def _draw_data(debug_image: Optional[np.ndarray], data: Data) -> None:
    if debug_image is None:
        return
    cv2.putText(
        debug_image,
        f'{data}',
        (100, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


class TemplateProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    EXAMPLE_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'your_squad.png'), 0)
    REQUIRED_MATCH = 0.95

    @time_processing
    def process(self, frame: Frame) -> bool:
        return False


def main() -> None:
    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = TemplateProcessor()

    import glob

    for p in glob.glob('../../../../dev/apex_images/template/*.png') + glob.glob('../../../../dev/apex_images/**/*.png'):
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

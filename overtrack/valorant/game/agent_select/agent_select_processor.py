import logging
import os
from typing import Dict, Optional

import Levenshtein as levenshtein
import cv2
import numpy as np

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import time_processing, imageops
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.valorant.data import agents, AgentName
from overtrack.valorant.game.agent_select.models import AgentSelect

logger = logging.getLogger('AgentSelectProcessor')


def draw_agent_select(debug_image: Optional[np.ndarray], agent_select: AgentSelect) -> None:
    if debug_image is None:
        return

    for c, t in ((0, 0, 0), 4), ((0, 255, 64), 1):
        cv2.putText(
            debug_image,
            str(agent_select),
            (700, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            c,
            t,
        )

class AgentSelectProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    AGENT_NAME_TEMPLATES: Dict[AgentName, np.ndarray] = {
        agent_name: imageops.imread(
            os.path.join(os.path.dirname(__file__), 'data', 'agent_names', agent_name.lower() + '.png'),
            0
        )
        #     cv2.resize(
        #     cv2.imread(os.path.join(os.path.dirname(__file__), 'data', 'agent_names', agent_name + '.png'), 0),
        #     (0, 0),
        #     fx=0.5,
        #     fy=0.5,
        # )
        for agent_name in agents
    }
    AGENT_TEMPLATE_REQUIRED_MATCH = 0.75

    LOCK_IN_BUTTON_COLOR = (180, 210, 140)

    def __init__(self):
        pass

    @time_processing
    def process(self, frame: Frame) -> bool:
        agent_name_yuv = self.REGIONS['agent_name'].extract_one(frame.image_yuv)
        agent_name_thresh = cv2.inRange(
            agent_name_yuv,
            (200, 85, 120),
            (255, 115, 150)
        )
        # cv2.imshow('agent_name_thresh', agent_name_thresh)
        # cv2.imwrite(
        #     os.path.join(os.path.dirname(__file__), 'data', 'agent_names', os.path.basename(frame.source_image)),
        #     agent_name_thresh
        # )

        match, best_match = imageops.match_templates(
            agent_name_thresh,
            self.AGENT_NAME_TEMPLATES,
            method=cv2.TM_CCORR_NORMED,
            required_match=0.95,
        )
        if match > self.AGENT_TEMPLATE_REQUIRED_MATCH:
            # FIXME: locked in - only use if locked in in valorantgame

            lock_in_im = self.REGIONS['lock_in'].extract_one(frame.image)
            lock_in_col = np.median(lock_in_im, axis=(0, 1))
            lock_in_match = np.linalg.norm(
                lock_in_col - self.LOCK_IN_BUTTON_COLOR
            )
            logger.debug(f'Lock in color={lock_in_col}, match={lock_in_match:.2f}')
            can_see_lock_in = False
            if lock_in_match < 100:
                lock_in_gray = np.min(lock_in_im, axis=2)
                lock_in_norm = 255 - imageops.normalise(lock_in_gray, bottom=70)
                lock_in_text = imageops.tesser_ocr(lock_in_norm, engine=imageops.tesseract_lstm).replace(' ', '')
                lock_in_text_match = levenshtein.ratio(lock_in_text, 'LOCKIN')
                logger.debug(f'Lock in text={lock_in_text!r}, match={lock_in_text_match:.2f}')

                can_see_lock_in = lock_in_match < 25 or lock_in_text_match > 0.75

            frame.valorant.agent_select = AgentSelect(
                best_match,
                locked_in=not can_see_lock_in,

                map=imageops.ocr_region(frame, self.REGIONS, 'map'),
                game_mode=imageops.ocr_region(frame, self.REGIONS, 'game_mode'),
            )
            draw_agent_select(frame.debug_image, frame.valorant.agent_select)
            self.REGIONS.draw(frame.debug_image)
            return True

        return False



def main():
    from overtrack.util.logging_config import config_logger
    from overtrack import util
    config_logger(os.path.basename(__file__), level=logging.DEBUG, write_to_file=False)
    util.test_processor('agent_select', AgentSelectProcessor(), 'valorant.agent_select', game='valorant', test_all=False)


if __name__ == '__main__':
    main()

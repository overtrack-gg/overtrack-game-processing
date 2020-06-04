import string

import logging
import os
from typing import Dict, Optional

import Levenshtein as levenshtein
import cv2
import numpy as np

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import time_processing, imageops, debugops, textops
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
        # cv2.imshow('agent_name_yuv', agent_name_yuv)
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
            selected_agent_ims = self.REGIONS['selected_agents'].extract(frame.image)
            selected_agent_ims_gray = [
                255 - imageops.normalise(np.max(im, axis=2), bottom=50) for im in selected_agent_ims
            ]
            selected_agent_texts = imageops.tesser_ocr_all(
                selected_agent_ims_gray,
                engine=imageops.tesseract_lstm,
            )
            logger.info(f'Got selected_agent_texts={selected_agent_texts}')

            picking = True
            for i, text in enumerate(selected_agent_texts):
                for word in textops.strip_string(text, string.ascii_letters + ' .').split(' '):
                    match = levenshtein.ratio(word, best_match)
                    logger.debug(f'Player {i}: Got match {match:.2f} for {word!r} = {best_match!r}')
                    if match > 0.7:
                        logger.info(f'Found matching locked in agent {text!r} for selecting agent {best_match!r} - selection locked')
                        picking = False
            frame.valorant.agent_select = AgentSelect(
                best_match,
                locked_in=not picking,

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

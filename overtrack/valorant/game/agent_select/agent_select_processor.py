import logging
import os
from typing import Dict, Optional

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

    for c, t in ((0, 0, 0), 4), ((0, 255, 64), 2):
        cv2.putText(
            debug_image,
            str(agent_select),
            (1100, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            c,
            t,
        )

class AgentSelectProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))
    AGENT_NAME_TEMPLATES: Dict[AgentName, np.ndarray] = {
        agent_name: cv2.imread(
            os.path.join(os.path.dirname(__file__), 'data', 'agent_names', agent_name + '.png'),
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

    LOCK_IN_BUTTON_COLOR = (220, 210, 150)

    def __init__(self):
        pass

    @time_processing
    def process(self, frame: Frame) -> bool:
        agent_name_yuv = self.REGIONS['agent_name'].extract_one(frame.image_yuv)
        agent_name_thresh = cv2.inRange(
            agent_name_yuv,
            (220, 90, 120),
            (255, 110, 140)
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
            required_match=self.AGENT_TEMPLATE_REQUIRED_MATCH
        )
        if match > self.AGENT_TEMPLATE_REQUIRED_MATCH:
            # FIXME: locked in - only use if locked in in valorantgame

            lock_in_im = self.REGIONS['lock_in'].extract_one(frame.image)
            lock_in_match = np.sum(
                cv2.inRange(
                    lock_in_im,
                    (200, 200, 140),
                    (255, 255, 175)
                ) > 0
            )

            map_im = self.REGIONS['map'].extract_one(frame.image)
            map_im_gray = 255 - imageops.normalise(np.min(map_im, axis=2))
            map_text = imageops.tesser_ocr(
                map_im_gray,
                engine=imageops.tesseract_lstm,
            )
            map_confidence = np.mean(imageops.tesseract_lstm.AllWordConfidences())
            logger.debug(f'Got map={map_text!r}, confidence={map_confidence}')
            if map_confidence < 50:
                logger.warning(f'Map confidence for {map_text!r} below 50 (confidence={map_confidence}) - rejecting')
                map_text = None

            frame.valorant.agent_select = AgentSelect(
                best_match,
                locked_in=lock_in_match < 10_000,

                map=map_text,
            )
            draw_agent_select(frame.debug_image, frame.valorant.agent_select)
            return True

        return False


def main():
    from overtrack.util.logging_config import config_logger
    from overtrack import util
    config_logger(os.path.basename(__file__), level=logging.DEBUG, write_to_file=False)
    util.test_processor('agent_select', AgentSelectProcessor(), 'agent_select', game='valorant', test_all=False)


if __name__ == '__main__':
    main()

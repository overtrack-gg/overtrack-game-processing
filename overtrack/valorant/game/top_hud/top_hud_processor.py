import logging
import os
from typing import Optional, Tuple

import cv2
import numpy as np

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import time_processing, imageops
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.valorant.data import agents
from overtrack.valorant.game.top_hud.models import TopHud, TeamComp
from overtrack.valorant.ocr import din_next_regular_digits

logger = logging.getLogger('TopHudProcessor')


def draw_top_hud(debug_image: Optional[np.ndarray], top_hud: TopHud) -> None:
    if debug_image is None:
        return

    for c, t in ((0, 0, 0), 4), ((0, 128, 255), 2):
        cv2.putText(
            debug_image,
            str(top_hud),
            (300, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            c,
            t,
        )


def load_agent_template(path):
    image = imageops.imread(path, -1)[3:-3, 3:-3]
    return image[:, :, :3], cv2.cvtColor(image[:, :, 3], cv2.COLOR_GRAY2BGR)


class TopHudProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))

    AGENT_TEMPLATES = {
        name: load_agent_template(os.path.join(os.path.dirname(__file__), 'data', 'agents', name.lower() + '.png'))
        for name in agents
    }
    AGENT_TEMPLATE_REQUIRED_MATCH = 50

    @time_processing
    def process(self, frame: Frame) -> bool:
        frame.valorant.top_hud = TopHud(
            score=self.parse_score(frame),
            teams=self._parse_teams(frame),
        )
        draw_top_hud(frame.debug_image, frame.valorant.top_hud)

        self.REGIONS.draw(frame.debug_image)

        return frame.valorant.top_hud.score[0] is not None or frame.valorant.top_hud.score[1] is not None

    def parse_score(self, frame: Frame) -> Tuple[Optional[int], Optional[int]]:
        score_ims = self.REGIONS['scores'].extract(frame.image)
        score_gray = [
            np.min(im, axis=2)
            for im in score_ims
        ]
        score_norm = [
            imageops.normalise(
                im,
                bottom=80,
                top=100
            )
            for im in score_gray
        ]

        # debugops.normalise(score_gray[0])
        # cv2.imshow('score_ims', np.hstack(score_ims))
        # cv2.imshow('score_gray', np.hstack(score_gray))
        # cv2.imshow('score_ys_norm', np.hstack(score_norm))

        score = imageops.tesser_ocr_all(
            score_norm,
            expected_type=int,
            invert=True,
            engine=din_next_regular_digits
        )
        logger.debug(f'Got score={score}')
        return score[0], score[1]

    def _parse_teams(self, frame: Frame) -> Tuple[TeamComp, TeamComp]:
        agents = []
        for i, agent_im in enumerate(self.REGIONS['teams'].extract(frame.image)):
            blurlevel = cv2.Laplacian(agent_im, cv2.CV_64F).var()
            if blurlevel < 100:
                agents.append(None)
                logger.debug(f'Got agent {i}=None (blurlevel={blurlevel:.2f})')
            else:
                match, r_agent = imageops.match_templates(
                    agent_im,
                    self.AGENT_TEMPLATES,
                    method=cv2.TM_SQDIFF,
                    required_match=self.AGENT_TEMPLATE_REQUIRED_MATCH,
                    use_masks=True,
                    previous_match_context=(self.__class__.__name__, '_parse_teams', i),
                )
                agent = r_agent
                if match > self.AGENT_TEMPLATE_REQUIRED_MATCH:
                    agent = None

                logger.debug(f'Got agent {i}={agent} (best={r_agent}, match={match:.3f}, blurlevel={blurlevel:.1f})')
                agents.append(agent)
        return tuple(agents[:5]), tuple(agents[5:])

def main():
    from overtrack.util.logging_config import config_logger
    from overtrack import util
    import glob
    config_logger(os.path.basename(__file__), level=logging.DEBUG, write_to_file=False)
    util.test_processor('ingame', TopHudProcessor(), 'valorant.top_hud', game='valorant', test_all=False)

    paths = glob.glob("D:/overtrack/valorant/*.png")
    paths = [p for p in paths if 'debug' not in p]
    paths.sort()
    paths = paths[::500]
    util.test_processor(paths, TopHudProcessor(), 'valorant.top_hud', game='valorant')


if __name__ == '__main__':
    main()

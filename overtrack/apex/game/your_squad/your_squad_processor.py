import logging
import os
from typing import Union

import cv2
import numpy as np

from overtrack.apex.game.your_squad.models import *
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.util.uploadable_image import lazy_upload

logger = logging.getLogger(__name__)


def _draw_squad(debug_image: Optional[np.ndarray], squad: Union[YourSquad, ChampionSquad, YourSelection]) -> None:
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
    DUOS_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'duos.png'), 0)
    TEMPLATES = {
        k: imageops.imread(os.path.join(os.path.dirname(__file__), 'data', k + '.png'), 0)
        for k in [
            'your_squad',
            'your_selection',
            'champion_squad'
        ]
    }

    REQUIRED_MATCH = 0.95

    def eager_load(self):
        self.REGIONS.eager_load()

    @time_processing
    def process(self, frame: Frame):
        y = frame.image_yuv[:, :, 0]

        your_squad_image = self.REGIONS['your_squad'].extract_one(y)
        t, thresh = cv2.threshold(your_squad_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        match, key = imageops.match_templates(
            thresh,
            self.TEMPLATES,
            cv2.TM_CCORR_NORMED,
            self.REQUIRED_MATCH
        )
        frame.your_squadchampion_match = round(match, 4)
        if match < self.REQUIRED_MATCH:
            return False

        if key == 'your_squad':
            mode_image = self.REGIONS['game_mode'].extract_one(frame.image_yuv[:, :, 0])
            _, mode_thresh = cv2.threshold(mode_image, 180, 255, cv2.THRESH_BINARY)
            duos_match = np.max(cv2.matchTemplate(mode_thresh, self.DUOS_TEMPLATE, cv2.TM_CCORR_NORMED))
            mode = None
            if duos_match > 0.75:
                mode = 'duos'

            names_region_name = 'names' if mode != 'duos' else 'names_duos'
            names = imageops.tesser_ocr_all(
                self.REGIONS[names_region_name].extract(y),
                engine=imageops.tesseract_lstm,
                invert=True
            )
            frame.your_squad = YourSquad(
                tuple(self._to_name(n) for n in names),
                mode=mode,
                images=lazy_upload('your_squad', np.hstack(self.REGIONS[names_region_name].extract(frame.image)), frame.timestamp)
            )
            self.REGIONS.draw(frame.debug_image)
            _draw_squad(frame.debug_image, frame.your_squad)
        elif key == 'your_selection':
            frame.your_selection = YourSelection(
                name=self._to_name(imageops.tesser_ocr(
                    self.REGIONS['names'].extract(y)[1],
                    engine=imageops.tesseract_lstm,
                    invert=True
                )),
                image=lazy_upload('your_selection', self.REGIONS['names'].extract(frame.image)[1], frame.timestamp)
            )
            self.REGIONS.draw(frame.debug_image)
            _draw_squad(frame.debug_image, frame.your_selection)
        elif key == 'champion_squad':
            names = imageops.tesser_ocr_all(
                self.REGIONS['names'].extract(y),
                engine=imageops.tesseract_lstm,
                invert=True
            )
            frame.champion_squad = ChampionSquad(
                (self._to_name(names[0]), self._to_name(names[1]), self._to_name(names[2])),
                images=lazy_upload('champion_squad', np.hstack(self.REGIONS['names'].extract(frame.image)), frame.timestamp)
            )
            self.REGIONS.draw(frame.debug_image)
            _draw_squad(frame.debug_image, frame.champion_squad)

        return True

    def _to_name(self, name_text: str) -> Optional[str]:
        for s1, s2 in '[(', '{(', '])', '})':
            name_text = name_text.replace(s1, s2)
        if len(name_text) > 3 and name_text[0] == '(' and name_text[-1] == ')':
            return name_text[1:-1].replace(' ', '')
        else:
            logger.warning(f'Got name "{name_text}" for player - rejecting')
            return None


def main() -> None:
    from overtrack import util

    util.test_processor('your_squad', YourSquadProcessor(), 'your_squad', 'your_selection', 'champion_squad', 'squad_match', game='apex')


if __name__ == '__main__':
    main()

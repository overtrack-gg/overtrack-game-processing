import glob
import logging
import os
import string
from typing import Optional, NamedTuple, Tuple, Dict

import cv2
import numpy as np

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import time_processing, imageops, textops
from overtrack.util.region_extraction import ExtractionRegionsCollection
from overtrack.valorant.data import agents, AgentName
from overtrack.valorant.game.killfeed.models import Kill, KillfeedPlayer, Killfeed

logger = logging.getLogger('KillfeedProcessor')


class KillRowPosition(NamedTuple):
    match: float
    center: Tuple[int, int]
    friendly: bool


def load_agent_template(path) -> Tuple[np.ndarray, np.ndarray]:
    image = imageops.imread(path, -1)[3:-3, 3:-3]
    return image[:, :, :3], cv2.cvtColor(image[:, :, 3], cv2.COLOR_GRAY2BGR)


def str2col(s):
    s = sum(ord(c) for c in s) % 255
    return tuple(cv2.cvtColor(np.array((s, 230, 255), dtype=np.uint8).reshape((1, 1, 3)), cv2.COLOR_HSV2BGR_FULL)[0, 0].tolist())


class KillfeedProcessor(Processor):

    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), 'data', 'regions', '16_9.zip'))

    FRIENDLY_KILL_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'friendly_kill.png'), 0)
    ENEMY_KILL_TEMPLATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'enemy_kill.png'), 0)
    KILL_THRESHOLD = 0.95

    AGENT_DEATH_TEMPLATES: Dict[AgentName, Tuple[np.ndarray, np.ndarray]] = {
        name: load_agent_template(os.path.join(os.path.dirname(__file__), 'data', 'agents', name.lower() + '.png'))
        for name in agents
    }
    AGENT_KILLER_TEMPLATES: Dict[AgentName, Tuple[np.ndarray, np.ndarray]] = {
        n: (a[0][:, ::-1], a[1][:, ::-1])
        for n, a in AGENT_DEATH_TEMPLATES.items()
    }
    AGENT_THRESHOLD = 50

    WEAPON_IMAGES = {
        os.path.basename(p).rsplit('.', 1)[0]: imageops.imread(p, 0)
        for p in glob.glob(os.path.join(os.path.dirname(__file__), 'data', 'weapons', '*.png'))
    }
    WEAPON_TEMPLATES = {
        w: cv2.GaussianBlur(
            cv2.dilate(
                cv2.copyMakeBorder(image, 5, 35 - image.shape[0], 5, 145 - image.shape[1], cv2.BORDER_CONSTANT),
                None
            ),
            (0, 0),
            0.5
        )
        for w, image in WEAPON_IMAGES.items()
    }

    @time_processing
    def process(self, frame: Frame) -> bool:
        x, y, w, h = self.REGIONS['killfeed'].regions[0]
        region = self.REGIONS['killfeed'].extract_one(frame.image)

        h = cv2.cvtColor(region, cv2.COLOR_BGR2HSV_FULL)[:, :, 0] - 50

        friendly_kill_match = cv2.matchTemplate(h, self.FRIENDLY_KILL_TEMPLATE, cv2.TM_CCORR_NORMED)
        enemy_kill_match = cv2.matchTemplate(h, self.ENEMY_KILL_TEMPLATE, cv2.TM_CCORR_NORMED)
        kill_match = np.max(
            np.stack((friendly_kill_match, enemy_kill_match), axis=-1),
            axis=2,
        )

        kill_rows = []

        for _ in range(9):
            mnv, mxv, mnl, mxl = cv2.minMaxLoc(kill_match)
            if mxv < self.KILL_THRESHOLD:
                break

            kill_match[
                max(0, mxl[1] - self.FRIENDLY_KILL_TEMPLATE.shape[0] // 2):
                min(mxl[1] + self.FRIENDLY_KILL_TEMPLATE.shape[0] // 2, kill_match.shape[0]),

                max(0, mxl[0] - self.FRIENDLY_KILL_TEMPLATE.shape[1] // 2):
                min(mxl[0] + self.FRIENDLY_KILL_TEMPLATE.shape[1] // 2, kill_match.shape[1]),
            ] = 0

            center = (
                int(mxl[0] + x + 20),
                int(mxl[1] + y + self.FRIENDLY_KILL_TEMPLATE.shape[0] // 2),
            )
            friendly_kill_v = friendly_kill_match[mxl[1], mxl[0]]
            enemy_kill_v = enemy_kill_match[mxl[1], mxl[0]]
            logger.debug(f'Found kill match at {center}: friendly_kill_v={friendly_kill_v:.4f}, enemy_kill_v={enemy_kill_v:.4f}')

            kill_rows.append(
                KillRowPosition(
                    match=round(float(mxv), 2),
                    center=center,
                    friendly=bool(friendly_kill_v > enemy_kill_v),
                )
            )

            # if frame.debug_image is not None:
            #     cv2.circle(
            #         frame.debug_image,
            #         center,
            #         10,
            #         (0, 255, 0),
            #         1,
            #         cv2.LINE_AA,
            #     )
            #     for c, t in ((0, 0, 0), 3), ((0, 255, 128), 1):
            #         cv2.putText(
            #             frame.debug_image,
            #             f'{mxv:.4f}',
            #             (center[0] + 20, center[1] + 20),
            #             cv2.FONT_HERSHEY_SIMPLEX,
            #             0.5,
            #             c,
            #             t,
            #         )

        kill_rows.sort(key=lambda r: r.center[1])
        if len(kill_rows):
            kills = []

            for row in kill_rows:
                killed_agent, killed_agent_match, killed_agent_x = self._parse_agent(frame, row, True)
                if killed_agent_match > 65:
                    continue
                elif killed_agent_match > self.AGENT_THRESHOLD:
                    logger.warning(f'Ignoring kill {row} - killed_agent_match={killed_agent_match:.1f} ({killed_agent})')
                    continue

                killed_name = self._parse_killed_name(frame, row, killed_agent_x)
                if killed_name is None:
                    logger.warning(f'Ignoring kill {row} - killed name failed to parse')
                    continue

                killer_agent, killer_agent_match, killer_agent_x = self._parse_agent(frame, row, False)
                if killer_agent_match > self.AGENT_THRESHOLD:
                    logger.warning(f'Ignoring kill {row} - killer_agent_match={killer_agent_match:.1f} ({killer_agent})')
                    continue

                weapon, weapon_match, weapon_x = self._parse_weapon(frame, row, killer_agent_x, killer_agent)

                killer_name = self._parse_killer_name(frame, row, killer_agent_x, weapon_x)
                if killer_name is None:
                    logger.warning(f'Ignoring kill {row} - killer name failed to parse')
                    continue

                kill = Kill(
                    y=int(row.center[1]),
                    row_match=round(float(row.match), 2),

                    killer_friendly=row.friendly,
                    killer=KillfeedPlayer(
                        agent=killer_agent,
                        agent_match=round(killer_agent_match, 2),

                        name=killer_name,
                    ),
                    killed=KillfeedPlayer(
                        agent=killed_agent,
                        agent_match=round(killed_agent_match, 2),

                        name=killed_name,
                    ),

                    weapon=weapon,
                    weapon_match=round(weapon_match, 2),
                )
                kills.append(kill)
                logger.debug(f'Got kill: {kill}')

                if frame.debug_image is not None:
                    s = f'{row.match:.2f} | {killer_agent} ({killer_agent_match:.2f}) {killer_name!r} > {weapon} > {killed_agent} ({killed_agent_match:.2f}) {killed_name!r}'
                    (w, _), _ = (cv2.getTextSize(s, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1))
                    for c, t in ((0, 0, 0), 3), ((0, 255, 128), 1):
                        cv2.putText(
                            frame.debug_image,
                            s,
                            (killer_agent_x - (w + 35), row.center[1] + 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            c,
                            t,
                        )

            if len(kills):
                frame.valorant.killfeed = Killfeed(
                    kills=kills,
                )
                return True

        return False

    _last_image_id = None
    _last_image_names = set()
    def _get_region(self, image, y1, y2, x1, x2, c=None, debug_name=None, debug_image=None):
        if y1 < 0:
            y1 = image.shape[0] + y1
        if y2 < 0:
            y2 = image.shape[0] + y2
        if x1 < 0:
            x1 = image.shape[1] + x1
        if x2 < 0:
            x2 = image.shape[1] + x2
        if debug_image is not None:
            co = str2col(debug_name)
            cv2.rectangle(
                debug_image,
                (x1, y1),
                (x2, y2),
                co,
            )
            if id(debug_image) != self._last_image_id:
                self._last_image_names.clear()
                self._last_image_id = id(debug_image)
            if debug_name and debug_name not in self._last_image_names:
                self._last_image_names.add(debug_name)
                for col, th in ((0, 0, 0), 3), (co, 1):
                    cv2.putText(
                        debug_image,
                        debug_name,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        col,
                        th,
                    )
        region = image[
            y1:y2,
            x1:x2,
        ]
        if c is not None:
            region = region[:, :, c]
        return region

    def _parse_agent(self, frame, row, agent_death) -> Tuple[AgentName, float, int]:
        if agent_death:
            region_x = frame.image.shape[1] - 120
            agent_im = self._get_region(
                frame.image,
                row.center[1] - 20, row.center[1] + 20,
                -120, -35,
                debug_name='killed_agent',
                debug_image=frame.debug_image,
            )
        else:
            region_x = frame.image.shape[1] - 600
            agent_im = self._get_region(
                frame.image,
                row.center[1] - 20, row.center[1] + 20,
                -600, row.center[0] - 60,
                debug_name='killer_agent',
                debug_image=frame.debug_image,
            )
        agent_matches = {}
        agent_match_m = []
        t = None
        for a, t in [self.AGENT_KILLER_TEMPLATES, self.AGENT_DEATH_TEMPLATES][agent_death].items():
            match = cv2.matchTemplate(agent_im, t[0], cv2.TM_SQDIFF, mask=t[1])
            agent_matches[a] = match
            agent_match_m.append(match)
        agent_match_m = np.min(np.stack(agent_match_m, axis=-1), axis=2)
        mnv, mxv, mnl, mxl = cv2.minMaxLoc(agent_match_m)

        agent, agent_match = None, float('inf')
        for a, m in agent_matches.items():
            v = m[mnl[1], mnl[0]]
            if v < agent_match:
                agent_match = v
                agent = a

        return agent, float(agent_match), int(region_x + mnl[0])

    def _parse_killed_name(self, frame, row, killed_agent_x) -> Optional[str]:
        killed_name_gray = self._get_region(
            frame.image_yuv,
            row.center[1] - 10, row.center[1] + 10,
            row.center[0] + 10, killed_agent_x - 10,
            0,
            debug_name='killed_name',
            debug_image=frame.debug_image,
        )
        if killed_name_gray.shape[1] == 0:
            return None
        killed_name_norm = 255 - imageops.normalise(killed_name_gray, min=170)
        return textops.strip_string(
            imageops.tesser_ocr(killed_name_norm, engine=imageops.tesseract_lstm).upper(),
            alphabet=string.ascii_uppercase + string.digits + '#',
        )

    def _parse_weapon(self, frame, row, killer_agent_x, killer_agent) -> Tuple[Optional[str], float, int]:
        weapon_region_left = killer_agent_x + 60
        weapon_region_right = row.center[0] - 20
        weapon_gray = self._get_region(
            frame.image_yuv,
            row.center[1] - 15, row.center[1] + 17,
            weapon_region_left, weapon_region_right,
            0,
            debug_name='weapon',
            debug_image=frame.debug_image,
        )
        if weapon_gray.shape[1] == 0:
            return None, 0, weapon_region_right
        weapon_adapt_thresh = np.clip(
            np.convolve(
                np.percentile(
                    weapon_gray,
                    10,
                    axis=0
                ),
                [0.2, 0.6, 0.2],
                mode='same'
            ),
            160,
            200,
        )
        weapon_thresh = ((weapon_gray - weapon_adapt_thresh > 30) * 255).astype(np.uint8)

        # import matplotlib.pyplot as plt
        # f, figs = plt.subplots(4)
        # figs[0].imshow(weapon_gray)
        # figs[1].plot(weapon_adapt_thresh)
        # figs[2].imshow(weapon_gray - weapon_adapt_thresh)
        # figs[3].imshow(weapon_thresh)
        # plt.show()
        # cv2.imshow('weapon_thresh', weapon_thresh)

        weapon_image = cv2.dilate(
            cv2.copyMakeBorder(
                weapon_thresh,
                5,
                5,
                5,
                5,
                cv2.BORDER_CONSTANT,
            ),
            None
        )
        contours, hierarchy = imageops.findContours(
            weapon_image,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        best_weap_match, best_weap = 0, None
        for cnt in sorted(contours, key=lambda c: np.min(c[:, :, 0])):
            a = cv2.contourArea(cnt)
            x1, y1, w, h = cv2.boundingRect(cnt)
            x2, y2 = x1 + w, y1 + h

            fromright = weapon_image.shape[1] - x2

            if w > 145:
                logger.warning(f'Ignoring weapon contour with w={w}')
                continue
            if fromright < 30:
                # contour is far right - could be small agent ability, so be less strict
                if a < 100 or h < 10:
                    logger.debug(f'Ignoring right weapon contour {cv2.boundingRect(cnt)}, fromright={fromright}, a={a}')
                    continue
                else:
                    logger.debug(f'Allowing potential ability contour {cv2.boundingRect(cnt)}, fromright={fromright}, a={a}')
            elif a < 200 or h < 16:
                # print('ignore', cv2.boundingRect(cnt), x2, a)
                logger.debug(f'Ignoring weapon contour {cv2.boundingRect(cnt)}, fromright={fromright}, a={a}')
                continue

            weapon_im = np.zeros((h + 2, w + 2), dtype=np.uint8)
            cv2.drawContours(
                weapon_im,
                [cnt],
                -1,
                255,
                -1,
                offset=(
                    -x1 + 1,
                    -y1 + 1,
                )
            )
            weapon_match, weapon = imageops.match_templates(
                weapon_im,
                {
                    w: t
                    for w, t in self.WEAPON_TEMPLATES.items()
                    if '.' not in w or w.lower().startswith(killer_agent.lower() + '.')
                },
                cv2.TM_CCORR_NORMED,
                template_in_image=False,
                required_match=0.96,
            )
            if best_weap_match < weapon_match:
                best_weap_match, best_weap = weapon_match, weapon

            valid = weapon_match > 0.9

            if frame.debug_image is not None and a > 1:
                cv2.drawContours(
                    frame.debug_image,
                    [cnt],
                    -1,
                    (128, 255, 0) if valid else (0, 0, 255),
                    1,
                    offset=(
                        weapon_region_left - 5,
                        row.center[1] - 20,
                    )
                )

            if valid:
                return weapon, float(weapon_match), int(weapon_region_left + x1)

        logger.warning(f'Unable to find weapon - best match was {best_weap} match={best_weap_match:.2f}')

        return None, 0, weapon_region_right

    def _parse_killer_name(self, frame, row, killer_agent_x, weapon_x) -> Optional[str]:
        killer_name_gray = self._get_region(
            frame.image_yuv,
            row.center[1] - 10, row.center[1] + 10,
            killer_agent_x + 35, weapon_x - 10,
            0,
            debug_name='killer_name',
            debug_image=frame.debug_image,
        )
        if killer_name_gray.shape[1] == 0:
            return None
        killer_name_norm = 255 - imageops.normalise(killer_name_gray, min=170)
        killer_name = textops.strip_string(
            imageops.tesser_ocr(killer_name_norm, engine=imageops.tesseract_lstm).upper(),
            alphabet=string.ascii_uppercase + string.digits + '#',
        )
        return killer_name


def main():
    import glob
    import random
    from overtrack.util.logging_config import config_logger
    from overtrack import util
    config_logger(os.path.basename(__file__), level=logging.DEBUG, write_to_file=False)
    proc = KillfeedProcessor()

    # paths = glob.glob("D:/overtrack/valorant_agent_killfeed/*_image.png")
    # for p in paths:
    #     f = Frame.create(cv2.imread(p), 0)
    #     if proc.process(f):
    #         shutil.copy(p, os.path.join("C:/Users/simon/overtrack_2/valorant_images/killicons", os.path.basename(p)))

    util.test_processor("D:/overtrack/valorant_stream_client/exceptions/*.png", proc, 'valorant.killfeed', game='valorant', wait=True, test_all=False)

    killicons = glob.glob("C:/Users/simon/overtrack_2/valorant_images/killicons/*.png")
    random.shuffle(killicons)
    killicons.insert(0, r'C:/Users/simon/overtrack_2/valorant_images/killicons\1588417689.59_image.png')
    killicons.insert(0, r'D:\overtrack\valorant_stream_client\frames\2020-05-03\04\26-05-446.image.png')
    util.test_processor(killicons, proc, 'valorant.killfeed', game='valorant', wait=True, test_all=False)
    util.test_processor('ingame', proc, 'valorant.killfeed', game='valorant', wait=True, test_all=False)


if __name__ == '__main__':
    main()
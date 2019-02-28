import gc
import itertools
import logging
import os
import random
import shutil
import sys
import tarfile
from pprint import pprint
from typing import List, NamedTuple, Optional, Tuple

import boto3
import cv2
import numpy as np
import requests
import tensorflow as tf
from bs4 import BeautifulSoup
from tqdm import tqdm

from overtrack import util
from overtrack.frame import Frame
from overtrack.overwatch.game.killfeed.icon_parser import IconParser
from overtrack.overwatch.game.spectator import SpectatorProcessor
from overtrack.source.stream import Twitch
from overtrack.util import imageops, s2ts
from overtrack.util.logging_config import config_logger
from processor import Processor, ShortCircuitProcessor
from util import textops

logger = logging.getLogger(__name__)

TARGET_DIR = '/mnt/'
if not os.path.exists(TARGET_DIR):
    TARGET_DIR = 'C:/scratch/mnt/'
SAMPLES_PER_KILL = 4
ROWS_REQUIRED = 6

row_add_top = 5
row_add_bottom = 6

target_width = 50
target_height = 35
y_match = 3
x_match = 5

aws_s3 = boto3.client(
    's3',
    region_name='us-west-2',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)
""" :type aws_s3: pyboto3.s3 """

class Icon(NamedTuple):
    x: float
    y: float
    width: float
    height: float

    hero: Optional[IconParser.ParsedIcon]
    team: bool

    team_index: Optional[int]

    def key(self, teams=('red', 'blue')) -> str:
        return f'{teams[self.team] if self.team is not None else None}.{self.hero.hero.replace(".", "-") if self.hero else None}'

class KillRow(NamedTuple):
    left: Optional[Icon]
    right: Icon
    source: np.ndarray

    def matches(self, other: 'KillRow') -> bool:
        if self.left:
            if not self.left.hero:
                return False
            elif not other.left or not other.left.hero:
                return False
            elif self.left.hero.hero != other.left.hero.hero:
                return False
            elif abs(self.left.x - other.left.x) > x_match:
                return False
            elif self.left.team != other.left.team:
                return False
        elif other.left:
            # self.left is None but other.left isnt
            return False

        if not self.right.hero or not other.right.hero:
            return False
        elif self.right.hero.hero != other.right.hero.hero:
            return False
        if abs(self.right.x - other.right.x) > x_match:
            return False
        elif self.right.team != other.right.team:
            return False
        else:
            return True

    def key(self, teams=('red', 'blue')) -> str:
        return 'KillRow(left=' + (self.left.key(teams) if self.left else 'x') + ', right=' + self.right.key(teams) + ')'

    def __str__(self) -> str:
        return f'KillRow(left={self.left}, right={self.right})'

    __repr__ = __str__

    @property
    def image(self) -> np.ndarray:
        return self.source[
               int(self.right.y - target_height / 2 - row_add_top):int(self.right.y + target_height / 2 + row_add_bottom)
        ]

class Kill:

    def __init__(self, row: KillRow):
        self.rows = [row]
        self.left_name = None
        self.right_name = None

    def matches(self, row: KillRow) -> bool:
        return self.rows[0].matches(row)

    def add(self, row: KillRow) -> None:
        self.rows.append(row)

    @property
    def left(self) -> Optional[Icon]:
        return self.rows[0].left

    @property
    def right(self) -> Icon:
        return self.rows[0].right

    def key(self, teams=('red', 'blue')) -> str:
        r = ''
        if self.left:
            r += self.left.key(teams)
            if self.left_name:
                r += '.' + self.left_name
        r += '_'
        r += self.right.key(teams)
        if self.right_name:
            r += '.' + self.right_name
        return r

    def __str__(self):
        return f'Kill(' + \
               f'left=' + (f'Icon({self.left.hero.hero}, t={"HA"[self.left.team]}, x={self.left.x})' if self.left else 'None') + \
               f', right=Icon({self.right.hero.hero}, t={"HA"[self.right.team]}, x={self.right.x})' \
               f', count={len(self.rows)}' \
               f', ys={[row.right.y for row in self.rows]}' \
               f')'

    __repr__ = __str__


def bgr_2hsv(colour):
    return cv2.cvtColor(np.array(colour, np.uint8)[np.newaxis, np.newaxis, :], cv2.COLOR_BGR2HSV_FULL)[0, 0]

class IsOWLProcessor(Processor):
    target_height = 45
    target_min_width = 480
    target_max_width = 680
    tolerance = 5

    def __init__(self, away_color, spec: SpectatorProcessor):
        self.away_color = away_color
        self.spec = spec
        self.seen_ago = None
        self.template = None

    def process(self, frame: Frame) -> bool:
        bar_at_top = False
        bar_lower = False

        image = frame.image[:200]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)[:, :, 0]
        image = cv2.GaussianBlur(image, (0, 0), 1)
        _, thresh = cv2.threshold(image, 230, 255, cv2.THRESH_BINARY)

        if self.template is not None:
            match = np.min(cv2.matchTemplate(255 - thresh[:, :700], self.template, cv2.TM_SQDIFF_NORMED))
            if frame.debug_image is not None:
                cv2.putText(
                    frame.debug_image,
                    f'tm: {match:1.2f}',
                    (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 255),
                    2
                )
            if match < 0.2:
                return True

        thresh = cv2.copyMakeBorder(thresh, 10, 0, 10, 0, cv2.BORDER_CONSTANT)
        contours, _ = imageops.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # cv2.imshow('bar', image)
        # cv2.imshow('thresh', thresh)
        # cv2.waitKey(1)

        for cnt in contours:
            cnt = cv2.approxPolyDP(cnt, 0.001 * cv2.arcLength(cnt, True), True)
            (x, y), (width, height), angle = cv2.minAreaRect(cnt)
            x -= 10
            y -= 10
            angle = angle % 90
            angle = min(abs(angle), abs(angle - 90))
            width, height = max(width, height), min(width, height)
            x -= width/2
            y -= height/2

            # if x < 2 and height > 40 and width > 100:
            #     print(x, y, width, height, angle)

            bar_at_top |= (max(
                abs(x),
                abs(y),
                abs(height - self.target_height),
                abs(angle)
            ) <= self.tolerance) and (self.target_min_width < width < self.target_max_width)

            bar_lower |= \
                x < self.tolerance and \
                54 - self.tolerance < y < 54 + self.tolerance and \
                abs(height - self.target_height) < self.tolerance and \
                angle < self.tolerance and \
                self.target_min_width < width < self.target_max_width

            pass

        if bar_at_top:
            self.template = 255 - thresh[:target_height, :500]
            if self.spec.top != 72:
                self.spec.top = 72
                logger.info(f'Setting spectate bar top to {self.spec.top}')
            if self.away_color == (0, 0, 0):
                away_color = tuple(int(e) for e in np.median(frame.image[:40, -100:], axis=(0, 1)))
                self.away_color = away_color
                self.spec.set_bgcols(((255, 255, 255), self.away_color))
                logger.info(f'Setting away color to {self.away_color}')

        if bar_lower:
            self.template = 255 - thresh[66:66+target_height, 10:550]
            if self.spec.top != 118:
                self.spec.top = 118
                logger.info(f'Setting spectate bar top to {self.spec.top}')
            if self.away_color == (0, 0, 0):
                away_color = tuple(int(e) for e in np.median(frame.image[55:55+40, -100:], axis=(0, 1)))
                self.away_color = away_color
                self.spec.set_bgcols(((255, 255, 255), self.away_color))
                logger.info(f'Setting away color to {self.away_color}')

        # if self.template is not None:
        #     cv2.imshow('template', self.template)

        if bar_at_top or bar_lower:
            self.seen_ago = 0
        elif self.seen_ago is not None:
            self.seen_ago += 1
        return self.seen_ago is not None and self.seen_ago < 15


class KillfeedExtractor:

    def __init__(self, source: Twitch, away_hex: str, end_pos: int=None, debug=False):
        self.source = source
        self.end_pos = end_pos
        self.debug = debug
        # self.away_color = util.html2bgr(away_hex)
        # self.away_hsv = bgr_2hsv(self.away_color)

        self.kills: List[Kill] = []
        self.kills_by_frame: List[List[Kill]] = []

        self.iconparser = IconParser()
        self.spec = SpectatorProcessor(
            record_names=True,
            bgcols=(
                (255, 255, 255),
                util.html2bgr(away_hex)
            ),
            top=118
        )
        self.owl = IsOWLProcessor(util.html2bgr(away_hex), self.spec)
        self.pipeline = ShortCircuitProcessor(
            self.owl,
            self.spec,
            order_defined=True,
            invert=True
        )

        self.frames: List[Frame] = []

    def process(self, dest):
        frames_target = os.path.join(dest, 'frames')
        os.makedirs(frames_target, exist_ok=True)

        bar = tqdm(total=(self.end_pos - self.source.seek), ncols=200, unit_scale=True)
        title = ' - '.join(os.path.normpath(dest).split(os.path.sep)[-2:]) + \
                f' | {s2ts(self.source.seek)} : %s : {s2ts(self.end_pos)} | TTV: {self.source.stream_url.split("/")[-1]}'
        bar.set_description(title % '-')
        last = self.source.seek

        last_fullframe = 0
        for fi in itertools.count():
            frame = self.source.get()
            if frame is None:
                break

            update = frame.timestamp - last
            if update >= 0:
                bar.update(update)
                bar.set_description(title % s2ts(frame.timestamp))
                last = frame.timestamp

            if self.end_pos and frame.timestamp > self.end_pos:
                break

            self.frames.append(frame)

            if not self.pipeline.process(frame):
                if self.debug:
                    cv2.imshow('frame', frame.debug_image)
                    cv2.waitKey(1)
                if frame.timestamp - last_fullframe > 60:
                    cv2.imwrite(os.path.join(frames_target, f'{fi}_.png'), frame.image)
                    last_fullframe = frame.timestamp

                frame.strip()
                continue

            icons, killfeed_region = self.extract_icons(frame)
            has_suicide, killrows, kills_this_frame, new_kills = self.extract_kills(icons, killfeed_region)
            self.kills.extend(new_kills)
            self.kills_by_frame.append(kills_this_frame)

            if frame.debug_image is not None:
                for i, kill in enumerate(sorted(killrows, key=lambda k: k.right.y)):
                    for c, t in ((0, 0, 0), 4), ((255, 255, 255), 1):
                        cv2.putText(
                            frame.debug_image,
                            kill.key(('H', 'A')),
                            (20, 200 + 30 * i),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.75,
                            c,
                            t
                        )

                cv2.imshow('frame', frame.debug_image)
                cv2.waitKey(1)
                # if has_suicide:
                #     cv2.waitKey(0)
                #     print()

            if (has_suicide and (frame.timestamp - last_fullframe) > 5) or \
                    ((frame.timestamp - last_fullframe) > 20 and len(killrows) > 0) or \
                    ((frame.timestamp - last_fullframe) > 45 and len(killrows) == 0):
                killrows_str = '_'.join(f'{r.right.y + self.spec.top + 40:1.1f}' for r in killrows)
                cv2.imwrite(os.path.join(frames_target, f'{fi}_{killrows_str}.png'), frame.image)
                last_fullframe = frame.timestamp

            frame.strip()
            gc.collect()

        bar.close()
        print('')

    def extract_kills(self, icons: List[Icon], killfeed_region):
        # sort icons by how "correct" they are
        def goodness(icon: Icon):
            return icon.hero is not None, \
                   (icon.hero.hero if icon.hero else None) is not None, \
                   icon.team_index is not None, \
                   max(abs(icon.width - target_width), abs(icon.height - target_height)) < 4, \
                   icon.hero.match if icon.hero else 0
        icons = sorted(icons, key=goodness, reverse=True)
        _icons = list(icons)

        killrows: List[KillRow] = []
        has_suicide = False
        while len(icons):
            icon = icons[0]
            icons.remove(icon)
            samerow = [other for other in icons if abs(other.y - icon.y) < y_match]
            others = [o for o in samerow if abs(o.x - icon.x) > 10]
            if len(others):
                other = others[0]
                if len(others) > 1:
                    logger.warning(
                        f'Found {len(others)+1} kills on the same row: {[i.hero.hero if i.hero else "?" for i in ([icon] + others)]} - '
                        f'using {other.hero.hero if other.hero else "?"}'
                    )
                for i in samerow:
                    icons.remove(i)
                left, right = sorted([icon, other], key=lambda icon: icon.x)
            else:
                left, right = None, icon
                has_suicide = icon.hero is not None

            killrows.append(KillRow(left, right, killfeed_region))
        killrows = sorted(killrows, key=lambda k: k.right.y)

        kills_this_frame: List[Kill] = []
        rows_remaining = list(killrows)
        for prev_frame in self.kills_by_frame[-10:]:
            for kill in prev_frame:
                for killrow in list(rows_remaining):
                    if kill.matches(killrow):
                        kill.add(killrow)
                        kills_this_frame.append(kill)
                        rows_remaining.remove(killrow)
                        break
        # add all new kills that didnt match any existing kills
        new_kills: List[Kill] = [Kill(row) for row in rows_remaining]
        kills_this_frame.extend(new_kills)
        return has_suicide, killrows, kills_this_frame, new_kills

    def draw_fail_reason(self, frame, cnt, text):
        if frame.debug_image is None:
            return
        if 'cnt_index' not in frame:
            frame.cnt_index = [0]

        cnt_pos = (500, 200 + frame.cnt_index[0] * 30)
        frame.cnt_index[0] += 1
        cv2.drawContours(
            frame.debug_image,
            [cnt],
            -1,
            (0, 0, 255),
            1,
            offset=(1920 - 500, self.spec.top + 40)
        )
        (x, y), (width, height), angle = cv2.minAreaRect(cnt)
        x, y = int(x), int(y)
        cv2.line(
            frame.debug_image,
            (x + (1920 - 500), self.spec.top + 40 + y),
            (cnt_pos[0] + cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 4)[0][0], cnt_pos[1]),
            (0, 255, 0),
            1
        )
        for c, t in ((0, 0, 0), 4), ((255, 255, 255), 1):
            cv2.putText(
                frame.debug_image,
                text,
                cnt_pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                c,
                t
            )

    def extract_icons(self, frame: Frame) -> Tuple[List[Icon], np.ndarray]:
        killfeed_region = frame.image[
            self.spec.top + 40:self.spec.top + 640,
            1920 - 500:
        ].copy()
        icons: List[Icon] = []
        vibrance = cv2.cvtColor(killfeed_region, cv2.COLOR_BGR2YUV)[:, :, 0]
        # cv2.imwrite('v.png', vibrance)
        # vibrance = cv2.GaussianBlur(vibrance, (0, 0), 0.8)
        # vibrance = cv2.erode(vibrance, np.ones((2,2)))
        # _, thresh = cv2.threshold(
        #     vibrance,
        #     150,
        #     255,
        #     cv2.THRESH_BINARY_INV
        # )
        thresh = imageops.unsharp_mask(
            vibrance,
            7,
            20,
            180
        )
        if frame.debug_image is not None:
            frame.debug_image[
                self.spec.top + 40:self.spec.top + 640,
                1920 - 1000:1920 - 500
            ] = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        # cv2.imshow('thresh', thresh)

        contours, _ = imageops.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in sorted(contours, key=lambda c: c[0][0][1]):
            area = cv2.contourArea(cnt)
            if not 500 < area < 10000:
                continue

            area_diff = abs(area - (target_width * target_height))
            if area_diff > 800:
                # self.draw_fail_reason(frame, cnt, f'area: {area}, required: {target_width * target_height}, delta: {area_diff}')
                continue

            (x, y), (width, height), angle = cv2.minAreaRect(cnt)
            angle = angle % 90
            width, height = max(width, height), min(width, height)

            width_diff = abs(width - target_width)
            height_diff = abs(height - target_height)

            if max(width_diff, height_diff) > 12:
                self.draw_fail_reason(
                    frame,
                    cnt,
                    f'w, h: {int(width), int(height)}, '
                    f'required: {target_width, target_height}, '
                    f'delta: {int(width_diff), int(height_diff)}'
                )
                continue

            angle_diff = min(90 - angle, angle)
            if angle_diff > 2:
                self.draw_fail_reason(frame, cnt, f'angle: {angle:.0f}, delta: {angle_diff:.0f}')
                continue

            # detect hero
            icon_image = killfeed_region[
                         int(y - height / 2):int(y + height / 2),
                         int(x - width / 2):int(x + width / 2)
            ]
            icon_image = icon_image[
                         5:28 + 5,
                         4:45 + 4
            ]
            if icon_image.size < 12:
                logger.warning(f'icon_image had shape {icon_image.shape} - ignoring kill')
                continue
            icon_image = cv2.cvtColor(icon_image, cv2.COLOR_BGR2GRAY)
            try:
                parsed = self.iconparser.parse_icons([icon_image])[0]
            except Exception:
                logger.warning(f'Failed to parse icon - ignoring kill')
                continue

            if parsed.hero is None or parsed.match < 0.5:
                logger.warning(f'Hero parsed to {parsed.hero} m={parsed.match:.2f} - ignoring kill')
                parsed = None
                hero = None
            else:
                hero = parsed.hero.split('.')[0]

            # detect team
            icon_region: np.ndarray = killfeed_region[
                int(y - target_height / 2) - 4:int(y + target_height / 2) + 5,
                int(x - target_width / 2) - 4:int(x + target_width / 2) + 5
            ]
            if icon_region.size < 12:
                logger.warning(f'icon_region had shape {icon_region.shape} - ignoring kill')
                continue
            icon_surround_region = icon_region.copy().astype(np.float)
            icon_surround_region[
                2:-2,
                2:-2
            ] = np.nan
            team_color = np.nanmedian(icon_surround_region, axis=(0, 1))
            team_hsv = bgr_2hsv(team_color)
            away_hsv = bgr_2hsv(self.owl.away_color)

            if self.debug:
                cv2.imshow('icon', cv2.resize(icon_region.astype(np.uint8), (0, 0), fx=6, fy=6, interpolation=cv2.INTER_NEAREST))
                cv2.imshow('color', cv2.resize(icon_surround_region.astype(np.uint8), (0, 0), fx=6, fy=6, interpolation=cv2.INTER_NEAREST))
                cv2.waitKey(1)

            # S=0 is home, S=away_hsv[1] is away
            # s_distance_home_away ranges 0->1 for match to home->away
            s_distance_home_away = min(float(team_hsv[1]) / away_hsv[1], 1)

            # V=255 is home, V=away_hsv[2]
            v_distance = max(float(team_hsv[2]) - away_hsv[2], 1)
            v_range = 255 - away_hsv[2]
            v_distance_away_home = min(max(v_distance / v_range, 0), 1)
            v_distance_home_away = 1 - v_distance_away_home

            distance_home_away = (s_distance_home_away * 2 + v_distance_home_away) / 3

            # this seems biased towards saying things are away team - counterbalance that
            # distance_home_away -= 0.05

            if 0.45 < distance_home_away < 0.55:
                logging.warning(f'Got distance_home_away={distance_home_away:1.2f} for {parsed.hero if parsed else None} - unsure of team')
                logging.warning(f'Away HSV: {away_hsv}, Icon HSV: {team_hsv}')
                left_heroes = [p.hero if p else None for p in frame.spectator_bar.left_team]
                right_heroes = [p.hero if p else None for p in frame.spectator_bar.right_team]
                if distance_home_away < 0.5 and hero in left_heroes and hero not in right_heroes:
                    logger.warning(
                        f'Resolving team=left for {parsed.hero if parsed else None} - '
                        f'left_team={left_heroes}, right_team={right_heroes}'
                    )
                    icon_away_team = False
                elif distance_home_away > 0.5 and hero not in left_heroes and hero in right_heroes:
                    logger.warning(
                        f'Resolving team=right for {parsed.hero if parsed else None} - '
                        f'left_team={left_heroes}, right_team={right_heroes}'
                    )
                    icon_away_team = True
                else:
                    logger.warning(
                        f'Unable to resolve team for {parsed.hero if parsed else None} - '
                        f'left_team={left_heroes}, right_team={right_heroes} - ignoring kill'
                    )
                    icon_away_team = None
            elif distance_home_away < 0.5:
                # print('home', distance_home_away)
                icon_away_team = False
            else:
                # print('away', distance_home_away)
                icon_away_team = True

            # check frame of 15s ago instead as this was before kill so will show correct (and non dead) hero in spec bar
            frames = self.frames[-30:]
            frames = [f for f in frames if 'spectator_bar' in f]
            if icon_away_team is not None and len(frames):
                team_old = [frames[0].spectator_bar.left_team, frames[0].spectator_bar.right_team][icon_away_team]
                team_current = [frames[-1].spectator_bar.left_team, frames[-1].spectator_bar.right_team][icon_away_team]
                try:
                    team_index = [p.hero if p else None for p in team_old].index(hero)
                except ValueError:
                    try:
                        team_index = [p.hero if p else None for p in team_current].index(hero)
                    except ValueError:
                        logger.warning(
                            f'Could not find {hero} in {["home", "away"][icon_away_team]} team of: {[p.hero if p else None for p in team_old]} - ignoring kill'
                        )
                        team_index = None
            else:
                team_index = None

            # record icon
            icons.append(Icon(
                x, y, width, height, parsed, icon_away_team, team_index
            ))
            if frame.debug_image is not None:
                debug_region = frame.debug_image[self.spec.top + 40:self.spec.top + 840, 1920 - 500:]
                cv2.rectangle(
                    debug_region,
                    (int(x - width / 2), int(y - height / 2)),
                    (int(x + width / 2), int(y + height / 2)),
                    (0, 0, 255),
                    2
                )
                if parsed:
                    text = f'{parsed.hero} t={"HA"[icon_away_team] if team_index is not None else "?"} m={parsed.match:.2f}'
                else:
                    text = '????'
                cv2.putText(
                    debug_region,
                    text,
                    (int(x - width / 2), int(y - height / 2) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 255) if team_index is not None else (0, 0, 255),
                    1
                )

        icons = sorted(icons, key=lambda i: i.y)
        return icons, killfeed_region

    def save(self, path: str):
        self.spec.process_names()
        print(self.spec.names)
        for i, kill in enumerate(self.kills):
            if len(kill.rows) >= max(ROWS_REQUIRED, SAMPLES_PER_KILL):

                if kill.left:
                    if not kill.left.hero:
                        logger.warning(f'Ignoring kill {i} - left hero was unknown')
                        continue
                    if kill.left.team_index is None:
                        logger.warning(f'Ignoring kill {i} - left hero {kill.left.hero} was not seen in spectator bar at the time of the kill')
                        continue
                    kill.left_name = self.spec.names[kill.left.team_index + 6 * kill.left.team]
                    if not kill.left_name:
                        logger.warning(f'Ignoring kill {i} - left player was index={kill.left.team_index} but player name failed to OCR')
                        continue
                if not kill.right.hero:
                    logger.warning(f'Ignoring kill {i} - right hero was unknown')
                    continue
                if kill.right.team_index is None:
                    logger.warning(f'Ignoring kill {i} - right hero {kill.right.hero} was not seen in spectator bar at the time of the kill')
                    continue
                kill.right_name = self.spec.names[kill.right.team_index + 6 * kill.right.team]
                if not kill.right_name:
                    logger.warning(f'Ignoring kill {i} - right player was index={kill.right.team_index} but player name failed to OCR')
                    continue

                inds = random.sample(list(range(len(kill.rows))), SAMPLES_PER_KILL)
                target = os.path.join(path, 'kills', kill.key(('FFFFFF', util.bgr2html(self.owl.away_color)[1:])))
                # print(kill, target)
                os.makedirs(target, exist_ok=True)
                for row_i in inds:
                    cv2.imwrite(f'{target}/{i}_{row_i}.png', kill.rows[row_i].image)

        self.kills: List[Kill] = []
        self.kills_by_frame: List[List[Kill]] = []


def parse_twicth_timestamp(url: str):
    if 't=' not in url:
        return '0:0:0'
    if url[-1] != 's':
        url += '00s'
    if url[-4] != 'm':
        url = url[:-3] + '00m' + url[-3:]
    qs = url.split('?', 1)[1]
    assert qs.startswith('t=')
    twitch_qs = qs[2:]
    twitch_ts = twitch_qs.replace('s', '')
    twitch_ts = twitch_ts.replace('m', ':')
    if 'm' not in twitch_qs:
        twitch_ts = '0:0:' + twitch_ts
    elif 'h' in twitch_ts:
        twitch_ts = twitch_ts.replace('h', ':')
    else:
        twitch_ts = '0:' + twitch_ts
    return twitch_ts


teams_url = 'https://overwatchleague.com/en-us/api/teams'
logger.info('Fetching team data')
team_data = requests.get(teams_url).json()
team_colors = {x['name']: (x['colors']['primary'], x['colors']['secondary']) for x in team_data['data']}
logger.info(f'Loaded team colors: {team_colors}')

class OverGGGame:
    MIN_GAP = 1

    def __init__(self, url: str, debug=False):
        self.url = url
        self.debug = debug

        logger.info(f'Downloading over.gg game details from {url}')
        page = BeautifulSoup(requests.get(url).content, 'html.parser')

        self.title = page.title.text.strip().split(' - ')[0]
        logger.info(f'Match title: {self.title}')

        self.teams = [e.text.strip() for e in page.find_all(class_='wf-title-med')]
        logger.info(f'Teams: {self.teams}')
        logger.info(f'Match is {" vs. ".join(self.teams)}')
        self.away_color = team_colors[self.teams[1]][1]
        if self.away_color == '#000000':
            self.away_color = team_colors[self.teams[1]][0]
        logger.info(f'Away color is {self.away_color}')

        self.maps = [e.text.strip() for e in page.find_all(class_='game-switch-map-name')]
        self.maps = [m for m in self.maps if m != 'N/A']
        logger.info(f'Got maps: {self.maps}')

        self.vods = [e.text.strip() for e in page.find_all(class_='game-vods-site-link')]
        self.vods = [v for v in self.vods if v]
        logger.info(f'Got VODs: {self.vods}')

        self.source: Twitch = None

    def process(self):
        if not len(self.vods):
            return None

        target = self.url
        if target.endswith('/'):
            target = target[:-1]
        target_dir = os.path.join(TARGET_DIR, target.split('/')[-1])

        nextvod: Optional[str]
        for i, (map_, vod, nextvod) in enumerate(zip(self.maps, self.vods, self.vods[1:] + [None])):
            # if i != 2:
            #     continue
            try:

                vod_url = vod.split('?')[0]
                start_pos = max(0, util.ts2s(parse_twicth_timestamp(vod)) - 1.1 * 60)
                if nextvod and vod.split('?')[0] == nextvod.split('?')[0]:
                    end_pos = parse_twicth_timestamp(nextvod)
                    end_pos = util.ts2s(end_pos) - self.MIN_GAP * 60
                else:
                    end_pos = None

                if start_pos == 0:
                    if i == 0:
                        logger.warning(f'Got 0 start position for first game - advancing to 5min')
                        start_pos = 5 * 60
                    else:
                        logger.warning(f'Got 0 start position - advancing to 2min')
                        start_pos = 2 * 60
                if not end_pos:
                    logger.warning(f'Got no end positon - setting to start +30min')
                    end_pos = start_pos + 30 * 60

                logger.info(f'Map {map_} in {vod_url} {start_pos}->{end_pos}')

                self.source: Twitch = Twitch(
                    vod_url,
                    seek=start_pos,
                    debug_frames=self.debug
                )
                extractor = KillfeedExtractor(
                    self.source,
                    self.away_color,
                    end_pos=end_pos,
                    debug=self.debug
                )
                extractor.process(os.path.join(target_dir, textops.strip_string(map_).lower()))
                extractor.save(os.path.join(target_dir, textops.strip_string(map_).lower()))
            except Exception as e:
                logger.exception(f'Got exception processing {self.title} - {map_}')

        return target_dir


def main() -> None:
    frame = Frame.create(
        cv2.imread("C:/scratch/owl-killfeed/sfs-vs-val-overwatch-league-season-1-stage-1-w1/ilios/frames/2012_346.0_294.5_243.0_190.5.png"),
        0,
        True
    )

    i = frame.image[
        72 + 40:72 + 640,
        1920 - 500:
    ]

    # for c, i in zip('yuv', cv2.split(cv2.cvtColor(frame.image, cv2.COLOR_BGR2YUV))):
    #     cv2.imwrite(f'./{c}.png', i)
    #
    # for c, i in zip('hsx', cv2.split(cv2.cvtColor(frame.image, cv2.COLOR_BGR2HSV))):
    #     cv2.imwrite(f'./{c}.png', i)

    # g = cv2.cvtColor(i, cv2.COLOR_BGR2YUV)[:, :, 0]
    # debugops.manual_thresh(g, scale=1)
    # debugops.manual_unsharp_mask(g, scale=1.5)
    # debugops.manual_thresh_otsu(g, scale=1)
    #
    # exit(0)

    away_color = (0, 0, 0)
    spec = SpectatorProcessor(
        record_names=True,
        bgcols=(
            (255, 255, 255),
            away_color
        ),
        top=118
    )
    owl = IsOWLProcessor(away_color, spec)
    print(owl.process(frame))

    pipeline = ShortCircuitProcessor(
        owl,
        spec,
        order_defined=True,
        invert=True
    )
    spec.top = spec.TOP
    # noinspection PyTypeChecker
    kex = KillfeedExtractor(None, util.bgr2html(away_color))
    kex.owl = owl
    kex.spec = spec
    kex.pipeline = pipeline

    pipeline.process(frame)

    frame.spectator_bar.left_team[1] = SpectatorProcessor.Player('winston', 1, False, None)

    kex.frames.append(frame)
    icons, killfeed_region = kex.extract_icons(frame)
    pprint(icons)
    pprint(kex.extract_kills(icons, killfeed_region))
    cv2.imshow(
        'w',
        frame.debug_image
    )
    cv2.waitKey(0)

    # e = KillfeedExtractor(
    #     HLSPlaylist(
    #         'https://mlgmsod-pipeline.akamaized.net/media/production/delivery/a6/43/a6439a01-a11e-465a-b7c0-98355fe023d8/y9NJsp49Xum.xHAwgJ2w3jTc.en-US.9632a417-8a39-43bb-9d71-5892cdfc4c81_8000k.m3u8',
    #         seek=0,
    #         debug_frames=True
    #     ),
    #     '#96CA4E',
    #     True
    # )
    # e.process()
    # e.save(TARGET_DIR)

    # url = 'https://www.over.gg/6453/sfs-vs-val-overwatch-league-season-1-stage-1-w1/'
    # url = 'https://www.over.gg/6454/shd-vs-gla-overwatch-league-season-1-stage-1-w1'
    # url = 'https://www.over.gg/8960/phl-vs-ldn-overwatch-league-season-1-playoffs-finals'
    # url = 'https://www.over.gg/8195/phl-vs-fla-overwatch-league-season-1-stage-4-w1/'
    # game = OverGGGame(url, True)
    # process_and_upload(game)

    # for index in [
    #     'https://www.over.gg/event/s/177/343/overwatch-league-season-1-stage-1',
    #     'https://www.over.gg/event/s/177/367/overwatch-league-season-1-stage-2',
    #     'https://www.over.gg/event/s/177/368/overwatch-league-season-1-stage-3',
    #     'https://www.over.gg/event/s/177/369/overwatch-league-season-1-stage-4'
    # ]:
    #     logger.info(f'Downloading index {index}')
    #     page = BeautifulSoup(requests.get(index).content, 'html.parser')
    #     for match in page.find_all(class_='match-item'):
    #         # download_and_process(match)
    #         print(match['href'])

def download_and_process(match, debug=False):
    try:
        print(f'Processing {match}')
        game = OverGGGame('https://www.over.gg' + match, debug)
    except Exception as e:
        logger.exception(f'Failed to parse game')
    else:
        try:
            process_and_upload(game)
        except Exception as e:
            logger.exception(f'Failed to process  game')
        if game.source:
            logger.info(f'Stopping game.source.tsdownloader')
            game.source.ts_downloader.stop()
    gc.collect()


def process_and_upload(game: OverGGGame):
    dest = game.process()
    if dest:
        name = os.path.basename(dest)
        tar = os.path.join(TARGET_DIR, name + '.tar')
        try:
            with tarfile.open(tar, mode='a') as archive:
                archive.add(dest, recursive=True, arcname='')
            logger.info(f'Uploading {tar}')
            print(f'Uploading {tar}')
            aws_s3.upload_file(
                Filename=tar,
                Bucket='overtrack-training-data',
                Key='owl-killfeed-2/' + os.path.basename(tar)
            )
        finally:
            logger.info(f'Deleting {tar}')
            print(f'deleting {tar}')
            try:
                os.remove(tar)
            except:
                logger.exception(f'Exception deleting {tar}')
            logger.info(f'Deleting {dest}')
            print(f'Deleting {dest}')
            try:
                shutil.rmtree(dest)
            except:
                logger.exception(f'Exception deleting {dest}')


if __name__ == '__main__':
    config_logger('extract_owl_kills', logging.ERROR, use_stackdriver=True, write_to_file=True)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        download_and_process(sys.argv[1])
        # download_and_process('/6456/ldn-vs-fla-overwatch-league-season-1-stage-1-w1', True)
        # main()

        # with open('./chunkac') as f:
        #     for line in f.readlines():
        #         download_and_process(line.strip())

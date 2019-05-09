import glob
import json
import logging
import os
from pprint import pprint
from typing import Tuple, Optional, Union, Iterable, Callable

import numpy as np
import cv2
import tensorflow as tf
import tqdm

from overtrack.frame import Frame
from overtrack.overwatch.collect.killfeed import Killfeed
from overtrack.overwatch.collect.teams import Teams
from overtrack.overwatch.game.killfeed import KillRow, Player, Killfeed as FrameKillfeed
from overtrack.overwatch.game.owl.hero_only_killfeed import HeroOnlyKillfeedProcessor, HeroOnlyKillfeed, HeroOnlyKillRow, Icon
from overtrack.overwatch.game.owl.owl_processor import OWLProcessor
from overtrack.overwatch.game.spectator.spectator_processor import List, SpectatorProcessor
from overtrack.processor import ShortCircuitProcessor
from overtrack.source import Capture
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import html2bgr, referenced_typedload
from overtrack.util.logging_config import config_logger

logger = logging.getLogger(__name__)


DEBUG = True
FPS = 1
VIEW_SCALE = 1


class RawFrameExtractor(Capture):

    def __init__(self, d: str, debug_frames=False):
        self.frames = sorted(glob.glob(d + '/*.raw'), key=lambda p: float(os.path.basename(p).rsplit('.', 1)[0]))

        # self.frames = self.frames[(60+50)*60:]

        self.fiter = iter(self.frames)
        self.debug_frames = debug_frames

    def get(self) -> Optional[Union[Frame, Exception]]:
        return self.load(next(self.fiter))

    def tqdm(self) -> Iterable[Frame]:
        for p in tqdm.tqdm(self.frames):
            yield self.load(p)

    def load(self, p: str) -> Frame:
        im = np.fromfile(p, dtype=np.uint8).reshape((1080, 1920, 3))
        return Frame.create(
            im,
            float(os.path.basename(p).rsplit('.', 1)[0]),
            debug=self.debug_frames
        )


def iconstr(icon: Optional[Icon]) -> str:
    if not icon:
        return 'None'
    if not icon.hero:
        return '?'
    return 'HA'[icon.team] + '.' + icon.hero.hero


def resolve_player(players: List[str], frames: List[Frame], index: int, icon: Optional[Icon]) -> Optional[Player]:
    if not icon or not icon.hero:
        return None

    for i in range(20):
        for sign in [1, -1]:
            if i == 0 and sign == -1:
                continue
            pos = index + sign * i
            if 'spectator_bar' in frames[pos]:
                teams = [frames[pos].spectator_bar.left_team, frames[pos].spectator_bar.right_team]
                team = teams[icon.team]
                team_heroes = [p.hero if p else None for p in team]
                if icon.hero.hero in team_heroes:
                    r = Player(
                        icon.hero.hero,
                        players[int(icon.team) * 6 + team_heroes.index(icon.hero.hero)],
                        1.,
                        icon.team,
                        0
                    )
                    logger.debug(
                        f'Resolved {frames[pos].relative_timestamp_str} '
                        f'({frames[index].timestamp - frames[pos].timestamp:1.1f}): '
                        f'{iconstr(icon)} -> {r}')

                    return r

    logger.warning(f'Could not resolve {frames[index].relative_timestamp_str}: {iconstr(icon)} for team {team_heroes}')
    return None


def hero_only_to_full(frames: List[Frame]) -> List[Frame]:
    frames = [f.copy() for f in frames]
    players = frames[0].teams
    for i, frame in enumerate(frames):
        if 'hero_only_killfeed' in frame:
            frame.killfeed = FrameKillfeed()

            row: HeroOnlyKillRow
            for row in frame.hero_only_killfeed.killfeed:
                left = resolve_player(players, frames, i - 3, row.left)
                right = resolve_player(players, frames, i - 10, row.right)
                if right:
                    kill = KillRow(
                        left=left,
                        right=right,
                        y=int(np.mean([i.y for i in [row.left, row.right] if i])),
                        resurrect=left and right and left.blue_team == right.blue_team,
                    )

                    frame.killfeed.kills.append(kill)
    return frames


class OWLGameExtractor:

    def __init__(self, away_color):
        self.on_game: List[Callable[[List[Frame], Teams, Killfeed], None]] = []
        self.on_partial_game: List[Callable[[List[Frame], Teams, Killfeed], None]] = []
        self.frequency = 60

        self.last_submit: Optional[float] = None

        self.frames = []
        self.have_game = False

        self.specbar = SpectatorProcessor(
            record_names=True,
            bgcols=(
                (255, 255, 255),
                away_color
            ),
            top=118
        )
        self.owl_proc = OWLProcessor(
            away_color=away_color,
            spec=self.specbar
        )
        self.killfeed_proc = HeroOnlyKillfeedProcessor(
            away_color=away_color
        )
        self.pipeline = ShortCircuitProcessor(
            self.owl_proc,
            self.specbar,
            self.killfeed_proc,
            order_defined=True,
            invert=True
        )

    def submit_frame(self, frame: Frame):
        image = frame.get('image')
        debug_image = frame.get('debug_image')

        try:
            self.pipeline.process(frame)
        except:
            logger.exception(f'Got exception processing frame: ')
        finally:
            frame.strip()

        if VIEW_SCALE is not None:
            cv2.imshow('frame', cv2.resize(debug_image if DEBUG else image, (0, 0), fx=VIEW_SCALE, fy=VIEW_SCALE))

            if frame.get('in_game'):
                cv2.waitKey(1)
            else:
                cv2.waitKey(1)

        if frame.get('map_set'):
            self.have_game = True

        if self.have_game:
            self.frames.append(frame)

        if len(self.frames) > 100 and self.have_game and (frame.get('map_set') or frame.get('play_of_the_match')):
            self.finish()

    def finish(self):
        if len(self.frames) > 100 and self.have_game:
            self.submit(self.on_game)
            self.specbar.names = [None for _ in range(12)]
            self.have_game = False
            self.frames.clear()

    def submit(self, submit_to: List[Callable[[List[Frame], Teams, Killfeed], None]]):
        try:
            self.specbar.process_names()
            self.frames[0].teams = self.specbar.names

            frames = hero_only_to_full(self.frames)

            players = frames[0].teams
            start = frames[0].timestamp

            teams = Teams.from_names(
                players[:6],
                players[6:],
                start
            )
            killfeed = Killfeed(
                frames,
                teams,
                start
            )
            for c in submit_to:
                c(frames, teams, killfeed)

        except:
            logger.exception('')


def extract_frames(source: str, away_color: Tuple[int, int, int]) -> None:
    if source.endswith('.mp4'):
        video = VideoFrameExtractor(
            source,
            extract_fps=FPS,
            debug_frames=DEBUG,
            # seek=(1*60+50)*60
        )
    elif os.path.isdir(source):
        video = RawFrameExtractor(
            source,
            debug_frames=True
        )
    else:
        raise ValueError(f'Cannot process {source}')

    extractor = OWLGameExtractor(away_color)

    def on_game(frames: List[Frame], teams: Teams, killfeed: Killfeed) -> None:
        print(f'on_game: {len(frames)}')
        print(teams)
        pprint(killfeed.kills)
        print()

    extractor.on_game.append(on_game)
    extractor.on_partial_game.append(on_game)

    for frame in video.tqdm():
        extractor.submit_frame(frame)
    extractor.finish()


def main() -> None:
    video_path = "M:/owl/{4 4 2019} {BOS vs ATL} Player 03 POV-brloDDAP_t8.mp4"
    away_color = html2bgr('#871D25')
    frames_path = 'games/' + str(os.path.basename(video_path)).rsplit('.', 1)[0]
    os.makedirs(frames_path, exist_ok=True)

    for i, frames in enumerate(extract_frames(video_path, away_color)):
        with open(f'{frames_path}/{i}.json', 'w') as f:
            json.dump(referenced_typedload.dump(frames), f, indent=2)

    # referenced_typedload._TYPES['hero_only_killfeed'] = HeroOnlyKillfeed
    # referenced_typedload._TYPES['teams'] = List[str]
    # with open('./Game 2 CDH @ VAL _ Stage 2 Week 5-v420542121.json') as f:
    #     data = json.load(f)
    #     for f in data:
    #         if 'cnt_index' in f:
    #             del f['cnt_index']
    #     frames = referenced_typedload.load(data, List[Frame], source_type=VideoFrameExtractor.VideoFrameMetadata)
    #


if __name__ == '__main__':
    config_logger('owl_processor', logging.DEBUG, False)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

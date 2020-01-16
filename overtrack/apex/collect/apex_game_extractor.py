import json
import logging
from collections import deque
from typing import Callable, List, Optional

from overtrack.apex.collect.apex_game import ApexGame
from overtrack.frame import Frame
from overtrack.util.typedload import referenced_typedload
from overtrack.util.logging_config import config_logger

logger = logging.getLogger(__name__)


class ApexGameExtractor:
    MIN_DURATION = 60

    def __init__(
            self,
            keep_games: bool = False,
            key_generator: Callable[[float], Optional[str]] = None,
            debug: bool = False):

        self.debug = debug
        self.key_generator = key_generator

        self.on_game_complete: List[Callable[[ApexGame, bool], None]] = []
        self.on_game_started: List[Callable[[], None]] = []

        self.have_current_game = False
        self.current_key: Optional[str] = None
        self.menuframes = deque(maxlen=25)
        self.frames: List[Frame] = []
        self.last_seen_frame: Optional[Frame] = None
        self.game_start: Optional[float] = None

        self.games: Optional[List[ApexGame]] = None
        if keep_games:
            self.games: Optional[List[ApexGame]] = []

    def _finish_game(self, shutdown: bool = False) -> None:
        logger.info(f'processing game from {len(self.frames)} frames')
        game = self.get_game_in_progress()
        assert game is not None, 'get_game_in_progress() returned None'
        logger.info(f'Processed game: {game}')

        for listener in self.on_game_complete:
            listener(game, shutdown)

        if self.games is not None:
            self.games.append(game)

        logger.info(f'Clearing {len(self.frames)} frames, setting have_current_game=False')
        self.frames = []
        self.have_current_game = False
        self.current_key = None

    def get_game_in_progress(self, force: bool = False) -> Optional[ApexGame]:
        if self.have_current_game and len(self.frames) > 2:
            frames = list(self.menuframes) + self.frames
            return ApexGame(frames, key=self.current_key, debug=self.debug)
        else:
            return None

    def before_frame(self, frame: Frame) -> None:
        if self.game_start and self.game_start != frame.timestamp:
            frame.game_time = round(frame.timestamp - self.game_start, 2)

    def on_frame(self, frame: Frame) -> None:
        self.last_seen_frame = frame
        time_since_game_start = frame.timestamp - self.frames[0].timestamp if self.have_current_game else -1

        if 'your_squad' in frame or not self.have_current_game:
            self.game_start = frame.timestamp
            if time_since_game_start > 10:
                logger.warning(
                    f'Saw YOUR SQUAD @{frame.relative_timestamp_str} '
                    f'{time_since_game_start:1.1f}s after a game had started with no menu between - starting new game'
                )
                self._finish_game()
                self.menuframes.clear()

            if not self.have_current_game:
                logger.info(f'Saw YOUR SQUAD @{frame.relative_timestamp_str} - starting game')
                self.have_current_game = True
                if self.key_generator:
                    self.current_key = self.key_generator(frame.timestamp)
                else:
                    self.current_key = None
                for game_started in self.on_game_started:
                    game_started()

        if 'apex_play_menu' in frame:
            self.menuframes.append(frame)
            if self.have_current_game:
                logger.info(f'Saw play menu @{frame.relative_timestamp_str} - emitting game')
                self._finish_game()
                self.game_start = None

        if self.have_current_game:
            self.frames.append(frame)

    def finish(self) -> None:
        if self.have_current_game:
            logger.info(f'{self.__class__.__name__} finished - emitting in current game (final frame @{self.last_seen_frame.relative_timestamp_str})')
            self._finish_game()


def main() -> None:
    # import matplotlib.pyplot as plt
    # import matplotlib
    # from matplotlib.ticker import Formatter
    import pprint
    pprint.sorted = lambda x, **_: x
    from pprint import pprint
    from overtrack.source.video import VideoFrameExtractor

    config_logger('apex_game_extractor.py', logging.INFO, False)

    logger.info('Loading frames')
    with open(r"C:\Users\simon\workspace\overtrack_2\games\apex_eeveea_apex_19-03-13.json") as f:
        frames = referenced_typedload.load(json.load(f), List[Frame])
    logger.info(f'Loaded {len(frames)} frames')

    # fields = [
    #     'match_status',
    #     'match_summary',
    #     'apex_play_menu',
    #     'squad',
    #     'weapons',
    #     'your_squad',
    #     'location',
    # ]
    #
    # plt.figure()
    #
    # start = frames[0].timestamp
    #
    # ax = plt.axes()
    #
    # class S2TSFormatter(Formatter):
    #     def __call__(self, x, pos=None):
    #         return s2ts(x)
    #
    # ax.xaxis.set_major_formatter(S2TSFormatter())
    #
    # for field in fields:
    #     plt.text(0, fields.index(field) + 0.25, field)
    #     plt.scatter(
    #         [frame.timestamp - start for frame in frames if field in frame],
    #         [fields.index(field) for frame in frames if field in frame]
    #     )
    # plt.show()

    ex = ApexGameExtractor(keep_games=True, debug=False)

    for f in frames:
        ex.on_frame(f)
    ex.finish()

    assert ex.games is not None
    for game in ex.games:
        print(game.frames[0].relative_timestamp_str)
        print(game)
        print(' -> '.join(game.route.locations_visited))
        pprint(game.asdict())

        # game.route.show()

        print()


if __name__ == '__main__':
    main()

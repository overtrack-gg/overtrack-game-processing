import json
import logging
from typing import List

import matplotlib.pyplot as plt

from overtrack.collect import GameExtractor
from overtrack.game import Frame
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import referenced_typedload
from overtrack.util.logging_config import config_logger

FRAMES = '../../games/switch_heroes_2_badnames.json'


def main() -> None:
    with open(FRAMES) as f:
        frames: List[Frame] = referenced_typedload.load(json.load(f), List[Frame], source_type=VideoFrameExtractor.VideoFrameMetadata)

    game_ex = GameExtractor(keep_games=True, debug=False)
    for frame in frames:
        game_ex.on_frame(frame)
    game_ex.finish()

    game = game_ex.games[0]

    plt.figure()
    ts, ul = [], []
    for frame in frames:
        if 'hero' in frame and frame.hero.ult is not None:
            ts.append(frame.timestamp)
            ul.append(frame.hero.ult)
    plt.plot(ts, ul)
    plt.show()

    # import matplotlib.pyplot as plt
    # plt.figure()
    # timestamp = [f.timestamp for f in game.frames if 'objective' in f]
    # overwatch = [1 - f.objective.p_game_mode[0] for f in game.frames if 'objective' in f]
    # is_koth = [f.objective.p_game_mode[1] for f in game.frames if 'objective' in f]
    # checkpoint_payload = [f.objective.checkpoint_payload for f in game.frames if 'objective' in f]
    # checkpoint_quickplay = [f.objective.checkpoint_quickplay for f in game.frames if 'objective' in f]
    # checkpoint_attacking = [f.objective.checkpoint_attacking for f in game.frames if 'objective' in f]
    # plt.scatter(timestamp, overwatch, label='is overwatch')
    # plt.scatter(timestamp, is_koth, label='is koth')
    # plt.scatter(timestamp, checkpoint_payload, label='checkpoint_payload')
    # plt.scatter(timestamp, checkpoint_quickplay, label='checkpoint_quickplay')
    # plt.scatter(timestamp, checkpoint_attacking, label='checkpoint_attacking')
    # plt.legend()
    # plt.show()

    print(game)
    print(game.stages)


if __name__ == '__main__':
    config_logger('frames_to_game', level=logging.INFO)
    main()

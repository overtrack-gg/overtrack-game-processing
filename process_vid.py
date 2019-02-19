import logging
import os

import cv2
import tensorflow as tf

from overtrack.collect import Game, GameExtractor
from overtrack.game import default_pipeline
from overtrack.source.video import VideoFrameExtractor

logger = logging.getLogger(__name__)


def main(source: str):
    # extractor = HLSPlaylist(source, False, debug_frames=True)
    # extractor = VideoFrameExtractor("C:/scratch/2018-09-20 13-19-07.mp4", extract_fps=1, debug_frames=True)
    extractor = VideoFrameExtractor("S:/overwatch/r66-3hero.mp4", extract_fps=1, debug_frames=True)

    def write_game(game: Game):
        key = f'games/{game.shortkey}.frames.json'
        logger.info(f'Saving game to {key}')

        os.makedirs('games', exist_ok=True)
        with open(key, 'w') as f:
            game.dump(f)

    pipeline = default_pipeline.create_pipeline()
    game_extractor = GameExtractor(comp_only=False)
    game_extractor.listeners.append(write_game)

    while True:
        frame = extractor.get()
        if not frame:
            break

        pipeline.process(frame)

        # print('\n' * 50)
        print(frame)
        cv2.imshow('frame', cv2.resize(frame.debug_image, (1280, 720)))
        cv2.waitKey(1)

        frame.strip()
        game_extractor.on_frame(frame)

    game_extractor.finish()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    source = 'https://overtrack-playlists.sfo2.digitaloceanspaces.com/Muon-1547/2018-11-23-07-24/07-34-busan/vod.m3u8'
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 1})) as sess:
        main(source)

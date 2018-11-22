import glob
import logging
import os
import queue
import sys
import time

import cv2
import tensorflow as tf
import numpy as np

from overtrack.game import Frame
from overtrack.game.endgame import EndgameProcessor
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.loading_map import LoadingMapProcessor
from overtrack.game.menu import MenuProcessor
from overtrack.game.score import ScoreProcessor
from overtrack.game.tab import TabProcessor
from overtrack.source.stream.ts_stream import AVContainer, TSFile
from overtrack.source.video import VideoFrameExtractor
from overtrack.util.logging_config import config_logger

tests = {
    'menu': (MenuProcessor, './images/menu/*.png'),
    'killfeed': (KillfeedProcessor, './images/killfeed/*.png'),
    'score': (ScoreProcessor, './images/score/*.png'),
    'loading_map': (LoadingMapProcessor, './images/map_loading/*.png'),
    'tab': (TabProcessor, './images/tab/*.png'),

    'endgame': (EndgameProcessor, './images/endgame/*.png')
}
VIDEO_PATH = "D:/overwatch_vids/NRG Fahzix _ Educational support-v306835334.mp4"
SEGMENT_LENGTH = 5
FPS = 2
DEBUG = True


def main():
    to_test = sys.argv[1] if len(sys.argv) > 1 else input(f'test what? {list(tests.keys())}\n')
    processor = tests[to_test][0]()

    ps = glob.glob(tests[to_test][1])
    for p in ps:
        im = cv2.imread(p)
        im = cv2.resize(im, (1920, 1080))
        frame = Frame.create(
            im,
            time.time(),
            debug=True
        )
        t0 = time.time()
        processor.process(frame)
        frame.timings.processing = (time.time() - t0) * 1000

        print(frame)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # av = AVContainer(
    #     TSFile(
    #         "S:/Downloads/000250_250.ts",
    #         "S:/Downloads/000250_250.ts"
    #     ),
    #     0,
    #     0,
    #     True,
    # )
    # while av.remaining:
    #     frame = av.next()
    #
    #     t0 = time.time()
    #     processor.process(frame)
    #     frame.timings.processing = (time.time() - t0) * 1000
    #
    #     print(frame)
    #     cv2.imshow('debug', frame.debug_image)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

    # extractor = VideoFrameExtractor(
    #     VIDEO_PATH,
    #     start_timestamp=time.time(),
    #     extract_fps=FPS,
    #     debug_frames=DEBUG,
    #     seek=70 * 60
    # )
    #
    # while True:
    #     frame = extractor.get()
    #     if frame is None:
    #         break
    #
    #     if processor.process(frame):
    #         cv2.imshow('debug', frame.debug_image)
    #         print(frame)
    #         cv2.waitKey(1)
    #     else:
    #         cv2.imshow('debug', frame.debug_image)
    #         cv2.waitKey(1)


if __name__ == '__main__':
    config_logger('processors', level=logging.DEBUG, write_to_file=False)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

import glob
import logging
import os
import queue
import time

import cv2
import tensorflow as tf
import numpy as np

from ingest.worker import UploadedTSFile, TSChunkHTTPServer, FFMpeg
from overtrack.game import Frame
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.menu import MenuProcessor
from overtrack.game.score import ScoreProcessor
from overtrack.source.stream.ts_stream import TSFile, TSFrameExtractor
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import debugops

tests = {
    'menu': (MenuProcessor, './images/menu/*.png'),
    'killfeed': (KillfeedProcessor, './images/killfeed/*.png'),
    'score': (ScoreProcessor, './images/score/*.png'),
}
VIDEO_PATH = "D:/overwatch_vids/NRG Fahzix _ Educational support-v306835334.mp4"
SEGMENT_LENGTH = 5
FPS = 2
DEBUG = True

TEST = 'score'


def main():
    processor = tests[TEST][0]()

    ps = glob.glob(tests[TEST][1])
    for p in ps:
        im = cv2.imread(p)
        im = cv2.resize(im, (1920, 1080))
        frame = Frame.create(
            im,
            0,
            debug=True
        )
        t0 = time.time()
        processor.process(frame)
        frame.timings.processing = (time.time() - t0) * 1000

        print(frame)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(1 if frame.get('score_screen') else 0)

    chunks: queue.Queue = queue.Queue(10)
    ts_server = TSChunkHTTPServer(chunks, prefix='test')
    ts_server.start()
    ffmpeg = FFMpeg([
        'ffmpeg',
        '-loglevel', 'info',
        '-i', VIDEO_PATH,
        '-f', 'segment', '-acodec', 'copy', '-vcodec', 'copy', '-segment_time', str(SEGMENT_LENGTH), '-segment_format', 'mpegts',
        f'http://127.0.0.1:{ts_server.port}/chunk/%06d.ts'
    ])
    ffmpeg.start()
    extractor = TSFrameExtractor(
        chunks,
        start_timestamp=time.time(),
        extract_fps=FPS,
        debug_frames=DEBUG,
        keep_queue_below=10,
        keyframes_only=True
    )

    while True:
        frame = extractor.get()
        if frame is None:
            break

        if processor.process(frame):
            cv2.imshow('debug', frame.debug_image)
            print(frame)
            cv2.waitKey(0)
        else:
            cv2.imshow('debug', frame.debug_image)
            cv2.waitKey(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

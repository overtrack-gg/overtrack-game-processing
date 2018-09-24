import glob
import os
import time

import cv2
import tensorflow as tf
import numpy as np

from overtrack.game import Frame
from overtrack.game.menu import MenuProcessor
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import debugops


def main():
    processor = MenuProcessor()

    ps = glob.glob('./images/menu/*.png')
    for p in ps:
        im = cv2.imread(p)

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
        cv2.waitKey(0)

    extractor = VideoFrameExtractor("C:/scratch/NRG Fahzix _ Educational support-v306835334.mp4", extract_fps=1, debug_frames=True)
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
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

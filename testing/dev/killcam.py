import glob

import cv2
import tensorflow as tf

from overtrack.game import Frame
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.source.video import VideoFrameExtractor


def main():
    processor = KillfeedProcessor()

    for p in glob.glob('./images/killcam/*.png'):
        frame = Frame.create(
            cv2.imread(p),
            0,
            debug=True
        )
        processor.process(frame)
        print(frame)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)

    extractor = VideoFrameExtractor("C:/Users/simon/workspace/overtrack_2/testing/tests/killfeed_videos/killcam_only.mp4", extract_fps=2, debug_frames=True)
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
            cv2.waitKey(0)


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

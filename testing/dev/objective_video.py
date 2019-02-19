import cv2
import time

import tensorflow as tf
from tensorflow import keras

from overtrack.game.objective import ObjectiveProcessor
from overtrack.source.video import VideoFrameExtractor

VIDEO_PATH = "D:/overwatch_vids/NRG Fahzix _ Educational support-v306835334.mp4"
FPS = 1
DEBUG = True


def main() -> None:
    extractor = VideoFrameExtractor(
        VIDEO_PATH,
        start_timestamp=time.time(),
        extract_fps=FPS,
        debug_frames=DEBUG,
        seek=70 * 60
    )
    while True:
        frame = extractor.get()
        if frame is None:
            break

        if pipeline.process(frame):
            cv2.imshow('debug', frame.debug_image)
            print(frame)
            cv2.waitKey(1)
        else:
            cv2.imshow('debug', frame.debug_image)
            cv2.waitKey(1)


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        keras.backend.set_session(sess)

        pipeline = ObjectiveProcessor()
        main()

import glob
import cv2
import tensorflow as tf

from overtrack.game import Frame
from overtrack.game.endgame import EndgameProcessor


def main():
    processor = EndgameProcessor()

    for p in glob.glob('./images/endgame/*.png'):
        frame = Frame.create(
            cv2.resize(cv2.imread(p), (1920, 1080)),
            0,
            debug=True
        )
        processor.process(frame)
        cv2.imshow('debug', frame.debug_image)
        frame.strip()
        print(frame)
        cv2.waitKey(0)


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

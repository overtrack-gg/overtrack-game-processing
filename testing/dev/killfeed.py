import glob
import cv2
import tensorflow as tf

from overtrack.game import Frame
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.loading_map.loading_map_processor import LoadingMapProcessor
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import debugops


def main():
    processor = KillfeedProcessor()

    for p in glob.glob('./images/killfeed/*.png'):
        frame = Frame.create(
            cv2.imread(p),
            0,
            debug=True
        )
        processor.process(frame)
        print(frame)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

import glob
import os
from pprint import pprint

import cv2
import tensorflow as tf
import numpy as np

from overtrack.game import Frame
from overtrack.game.tab.tab_processor import TabProcessor
from overtrack.ocr import big_noodle, big_noodle_ctc
from overtrack.util import debugops


def main():
    processor = TabProcessor(save_name_images=False)

    ps = glob.glob('./images/tab/*.png')
    #ps = filter(lambda p: ' ' in p, ps)
    for p in ps:#sorted(ps, key=lambda p: int(p.split('(')[1].split(')')[0])):
        im = cv2.imread(p)
        # [:, 20:-20]
        im = cv2.resize(im, (1920, 1080))

        frame = Frame.create(
            im,
            0,
            debug=True
        )
        processor.process(frame)

        # names = frame.tab_screen.images.blue_team + frame.tab_screen.images.red_team
        # big_noodle_ctc.ocr_all(names)

        print(frame)
        d = frame.to_dict()
        pprint(d)
        print(frame.from_dict(d))
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)

        # debugops.show_ocr_segmentations(names)


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

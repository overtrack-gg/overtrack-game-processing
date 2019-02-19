import json
import logging
import os

import cv2
import tensorflow as tf
from tqdm import tqdm

from overtrack.game.default_pipeline import create_pipeline
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import referenced_typedload
from overtrack.util.logging_config import config_logger


def main():
    p = "D:/overwatch_vids/switch_heroes_2_badnames.mp4"
    source = VideoFrameExtractor(p, extract_fps=2, debug_frames=True)

    frames = []
    with tqdm(total=int((source.vid_frames / source.vid_fps) * source.extract_fps)) as progress:
        while True:
            frame = source.get()
            if not frame:
                break

            pipeline.process(frame)
            debug = frame.debug_image

            frame.strip()
            frames.append(frame)

            progress.set_description(frame.timestamp_str)
            progress.update()

            # print(frame.timings)
            cv2.imshow('frame', debug)

            o = cv2.waitKey(1)
            while o == 32:
                o = cv2.waitKey(100)
        cv2.destroyAllWindows()

    output = f'../../games/{os.path.basename(p).rsplit(".", 1)[0]}.json'
    with open(output, 'w') as f:
        json.dump(referenced_typedload.dump(frames), f, indent=2)
    print(os.path.abspath(output))


if __name__ == '__main__':
    config_logger('process_video', level=logging.DEBUG)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        pipeline = create_pipeline()
        main()

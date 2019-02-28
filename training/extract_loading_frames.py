import os
import cv2
import tensorflow as tf

from overtrack.overwatch.game.loading_map import LoadingMapProcessor
from overtrack.source.video import VideoFrameExtractor

OUT = "C:/Users/simon/workspace/overtrack_2/test/images/map_loading"


def main():
    cap = VideoFrameExtractor("M:/Videos/OBS/loading_maps.mp4", extract_fps=2)

    processor = LoadingMapProcessor()

    os.makedirs(os.path.join(OUT, 'loading_maps_mp4'), exist_ok=True)
    while True:
        frame = cap.get()
        if not frame:
            break
        processor.process(frame)
        if 'loading_map' in frame:
            cv2.imwrite(os.path.join(OUT, f'loading_maps_mp4/{frame.timestamp :1.1f}.png'), frame.image)
            print(frame.loading_map)
        s = 400/1920
        im = cv2.resize(frame.image, (0, 0), fx=s, fy=s)
        cv2.imshow('frame', im)
        cv2.waitKey(1)

    cap.close()


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

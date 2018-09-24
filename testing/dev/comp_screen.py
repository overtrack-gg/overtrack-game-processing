import glob
import cv2
import tensorflow as tf

from overtrack.game import Frame
from overtrack.game.loading_map.loading_map_processor import LoadingMapProcessor
from overtrack.util import debugops


def main():
    processor = LoadingMapProcessor(save_name_images=True)

    for p in glob.glob('./images/map_loading/*.png'):

        frame = Frame.create(
            cv2.imread(p),
            0,
            debug=True
        )
        processor.process(frame)
        print(frame)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)

        # names = frame.loading_map.teams.images.blue_team + frame.loading_map.teams.images.red_team
        # debugops.show_ocr_segmentations(names, height=37)
        # debugops.show_ocr_segmentations([frame.loading_map.images.map])
        # debugops.show_ocr_segmentations([frame.loading_map.images.game_mode])


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

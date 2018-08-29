import glob
import logging
import os
from pprint import pprint

import cv2
import tensorflow as tf

from game import Frame
from game.processor import OrderedProcessor, ConditionalProcessor, ExclusiveProcessor
from game.menu import MenuProcessor
from game.killfeed import KillfeedProcessor
from game.objective import ObjectiveProcessor

from stream.twitch import TwitchLiveTSDownloader
from stream.video import FrameExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    with tf.Session() as sess:

        pipeline = OrderedProcessor(

            ExclusiveProcessor(
                MenuProcessor(),
                ObjectiveProcessor(),
                order_defined=False
            ),

            ConditionalProcessor(
                KillfeedProcessor(),
                condition=lambda f: 'objective' in f and f.objective.is_game,
                lookbehind=5,
                lookbehind_behaviour=any,
                default_without_history=True,
            )
        )

        TWITCH = True

        if not TWITCH:
            for p in sorted(
                    glob.glob("D:/overtrack/screens/1440_defaults_0/*.png"),
                    key=lambda p: int(os.path.basename(p).split('.')[0])
            )[210:]:
                # p = "D:/overtrack/screens/1440_defaults_0/548755.png"
                image = cv2.imread(p)
                frame = Frame.create(
                    image,
                    0,
                    debug=True,
                )

                pipeline.process(frame)

                print('\n'*10)
                pprint(frame.to_dict())
                im = cv2.resize(frame.debug_image, (1280, 720))
                cv2.imshow('frame', im)
                cv2.waitKey(0)

        else:

            stream = 'eeveea_'
            stream = 'https://www.twitch.tv/eeveea_/video/301311159'
            tsdownloader = TwitchLiveTSDownloader(stream, max_kb=300)
            extractor = FrameExtractor(tsdownloader.queue, 10, max_frames_per_chunk=1, debug_frames=True)

            tsdownloader.start()
            extractor.start()

            fourcc = cv2.VideoWriter_fourcc(*'DIVX')
            writer = cv2.VideoWriter('out.mp4', fourcc, 10, (1280, 720))

            while True:
                frame = extractor.queue.get(block=True)
                if isinstance(frame, Exception):
                    raise frame

                pipeline.process(frame)

                print('\n' * 50)
                print()
                pprint(frame.to_dict())

                im = cv2.resize(frame.debug_image, (1280, 720))
                writer.write(im)
                cv2.imshow('frame', im)
                if cv2.waitKey(1) == 27:
                    break

            writer.release()
            cv2.destroyAllWindows()
            tsdownloader.stop()
            extractor.stop()

            while extractor.queue.get(block=True) is not None:
                print('.')
                pass

            tsdownloader.join()
            extractor.join()

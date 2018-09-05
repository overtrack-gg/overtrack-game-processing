import sys

import cv2
import glob
import logging
import os
import tensorflow as tf
from pprint import pprint
from typing import List


from overtrack.game import Frame
from overtrack.game.processor import OrderedProcessor, ConditionalProcessor, ExclusiveProcessor
from overtrack.game.menu import MenuProcessor
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.objective import ObjectiveProcessor
from overtrack.game.spectator import SpectatorProcessor

from stream.twitch import TwitchLiveTSDownloader
from stream.video import VideoFrameExtractor

from overtrack.data_collection.names_from_overtrack import NamesFromOvertrack
from overtrack.data_collection.names_from_spectate import NamesFromSpectate

from overtrack.util import ts2ms, ms2ts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TWITCH = True
# START = '0:0:0'
# STREAM = 'eeveea_'
STREAM, START = 'https://www.twitch.tv/eeveea_/video/301311159', '9:56:0'
# STREAM, START = 'https://www.twitch.tv/videos/303359180', '6:0:00'  # eevee 6000kb/s stream


# STREAM = 'https://www.twitch.tv/videos/248240303'  # tendies
# START = '0:1:15'


def main(source=STREAM, seek=START, display=True):
    pipeline = OrderedProcessor(

        ExclusiveProcessor(
            MenuProcessor(),
            ObjectiveProcessor(),
            order_defined=False
        ),

        ConditionalProcessor(
            OrderedProcessor(
                SpectatorProcessor(True),

                KillfeedProcessor(output_icon_images=False, output_name_images=True),

                # NamesFromOvertrack(STREAM, 'eeveea_'),


                NamesFromSpectate('contenders', source.rsplit('/', 1)[1])

            ),
            condition=lambda f: 'objective' in f and f.objective.is_game,
            lookbehind=5,
            lookbehind_behaviour=any,
            default_without_history=True,
        ),

    )

    if not TWITCH:
        for p in sorted(
                glob.glob("D:/overtrack/screens/1440_defaults_0/*.png"),
                key=lambda p: int(os.path.basename(p).split('.')[0])
        )[215:]:
            # p = "D:/overtrack/screens/1440_defaults_0/548755.png"
            image = cv2.imread(p)
            frame = Frame.create(
                image,
                0,
                debug=True,
            )

            pipeline.process(frame)

            print('\n' * 10)
            print(frame)
            print(ms2ts(frame.timestamp * 1000))
            im = cv2.resize(frame.debug_image, (1280, 720))
            cv2.imshow('frame', im)
            cv2.waitKey(0)

    else:
        # tsdownloader = TwitchLiveTSDownloader(STREAM, max_kb=300, seek=ts2ms(START) / 1000)
        # extractor = FrameExtractor(tsdownloader.queue, 10, max_frames_per_chunk=1, debug_frames=True)
        tsdownloader = TwitchLiveTSDownloader(source, seek=ts2ms(seek) / 1000)
        extractor = VideoFrameExtractor(tsdownloader.queue, 10, extract_fps=4, debug_frames=display)

        tsdownloader.start()
        extractor.start()

        if display:
            fourcc = cv2.VideoWriter_fourcc(*'DIVX')
            writer = cv2.VideoWriter('out.mp4', fourcc, 10, (1280, 720))

        i = 0
        while True:
            frame = extractor.get(block=True)
            if isinstance(frame, Exception):
                raise frame
            if frame is None:
                break

            pipeline.process(frame)

            # if not i % 10:
            #     print(ms2ts(frame.timestamp * 1000))
            # print(frame)
            if 'killfeed' in frame and len(frame.killfeed.kills) and frame.killfeed.kills[0].left:
                print(frame.killfeed.kills[0])

            if display:
                im = cv2.resize(frame.debug_image, (1280, 720))
                writer.write(im)
                cv2.imshow('frame', im)

                if cv2.waitKey(0) == 27:
                    break

            i += 1

        sys.exit(0)
        if display:
            writer.release()
            cv2.destroyAllWindows()
        tsdownloader.stop()
        extractor.stop()

        while extractor.queue.get(block=True) is not None:
            print('.')
            pass

        tsdownloader.join()
        extractor.join()


if __name__ == "__main__":
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        # main(sys.argv[1], '0:0:0', display=False)
        # main('https://www.twitch.tv/videos/250290864', '0:7:00', True)
        main()

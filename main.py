import sys
from typing import Optional

import cv2
import glob
import logging
import os

import numpy as np
import tensorflow as tf

from overtrack.game import Frame
from overtrack.game.loading_map.loading_map_processor import LoadingMapProcessor
from overtrack.game.processor import OrderedProcessor, ConditionalProcessor, ShortCircuitProcessor
from overtrack.game.menu import MenuProcessor
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.objective import ObjectiveProcessor
from overtrack.game.spectator import SpectatorProcessor
from overtrack.data_collection.names_from_spectate import NamesFromSpectate
from overtrack.game.tab.tab_processor import TabProcessor
from overtrack.source.stream.twitch import TwitchLiveTSDownloader
from overtrack.source.stream.ts_stream import TSFrameExtractor
from overtrack.source.video.video import VideoFrameExtractor
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


def main(source: str=STREAM, seek: Optional[str]=START, display: bool=True):
    pipeline = OrderedProcessor(

        ShortCircuitProcessor(
            MenuProcessor(),
            ObjectiveProcessor(save_probabilities=False),
            order_defined=False
        ),

        LoadingMapProcessor(),
        TabProcessor(),

        ConditionalProcessor(
            OrderedProcessor(
                # SpectatorProcessor(True),
                KillfeedProcessor(output_icon_images=False, output_name_images=False),
                # NamesFromOvertrack(STREAM, 'eeveea_'),
                # NamesFromSpectate('contenders', source.rsplit('/', 1)[1])
            ),
            condition=lambda f: 'objective' in f and f.objective.is_game,
            lookbehind=5,
            lookbehind_behaviour=any,
            default_without_history=True,
        ),

    )

    # if source is path:
    #     for p in sorted(
    #             glob.glob("D:/overtrack/screens/1440_defaults_0/*.png"),
    #             key=lambda p: int(os.path.basename(p).split('.')[0])
    #     )[215:]:
    #         # p = "D:/overtrack/screens/1440_defaults_0/548755.png"
    #         image = cv2.imread(p)
    #         frame = Frame.create(
    #             image,
    #             0,
    #             debug=True,
    #         )
    #
    #         pipeline.process(frame)
    #
    #         print('\n' * 10)
    #         print(frame)
    #         print(ms2ts(frame.timestamp * 1000))
    #         im = cv2.resize(frame.debug_image, (1280, 720))
    #         cv2.imshow('frame', im)
    #         cv2.waitKey(0)

    # tsdownloader = TwitchLiveTSDownloader(STREAM, max_kb=300, seek=ts2ms(START) / 1000)
    # extractor = FrameExtractor(tsdownloader.queue, 10, max_frames_per_chunk=1, debug_frames=True)

    downloading = False
    seek = ts2ms(seek) / 1000 if seek else None

    if source is None:
        import frames

        class CachedFrameExtractor:

            def __init__(self):
                self.index = 0

            def get(self):
                frame = frames.cached_frames[self.index]
                self.index += 1
                frame.debug_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
                return frame

        extractor = CachedFrameExtractor()

    elif source.startswith('http'):
        tsdownloader = TwitchLiveTSDownloader(source, seek=seek)
        extractor = TSFrameExtractor(tsdownloader.queue, 10, extract_fps=1, debug_frames=display)
        tsdownloader.start()
        extractor.start()
        downloading = True
    elif os.path.exists(source) and not os.path.isdir(source):
        extractor = VideoFrameExtractor(source, seek=seek, debug_frames=display)
    else:
        raise ValueError('Don\'t know how to read from source "%s"' % (source, ))

    if display:
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        writer = cv2.VideoWriter('out.mp4', fourcc, 10, (1280, 720))

    out = open('frames.py', 'w')

    i = 0
    while True:
        frame = extractor.get()
        if isinstance(frame, Exception):
            raise frame
        if frame is None:
            break

        if source:
            pipeline.process(frame)

        debug_image = frame.debug_image
        frame.strip()
        out.write(str(frame) + '\n')
        print(frame)
        # if not i % 10:
        #     print(ms2ts(frame.timestamp * 1000))
        # print(frame)
        # if 'killfeed' in frame and len(frame.killfeed.kills) and frame.killfeed.kills[0].left:
        #     print(frame.killfeed.kills[0])

        if display:
            im = cv2.resize(debug_image, (1280, 720))
            writer.write(im)
            cv2.imshow('frame', im)

            if cv2.waitKey(0) == 27:
                break

        i += 1

    out.close()

    if display:
        writer.release()
        cv2.destroyAllWindows()

    if downloading:
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
        # main("C:/scratch/NRG Fahzix _ Educational support-v306835334.mp4", '0:1:03', True)
        main("C:/scratch/8res.mp4", seek='0:0:20', display=True)

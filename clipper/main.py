import logging
import queue
from threading import Thread
from typing import Optional
import tensorflow as tf

import cv2
import time

from overtrack.frame import Frame
from overtrack.overwatch.collect import Game, OverwatchGameExtractor
from overtrack.overwatch.game import default_pipeline
from overtrack.performance_monitor import PerformanceMonitor
from overtrack.source.ffmpeg.ffmpeg_http_server import FFMpegHTTPServer
from overtrack.source.ffmpeg.ffmpeg_segmenter import FFMPEGSegmenter
from overtrack.util.logging_config import config_logger

SOURCE = 'https://www.twitch.tv/yeatle'
REALTIME = True
SEEK = '0:20:0'
OVERRIDE_START_TIME: Optional[int] = 20 * 60
GAME_IN_PROGRESS_FREQUENCY: Optional[int] = 30
FPS = 1
DEBUG = True


if REALTIME:
    SEEK = None


logger = logging.getLogger(__name__)


def on_game_started() -> None:
    print('game started')


def on_game_in_progress(game: Game) -> None:
    print(game)


def on_game_complete(game: Game, shutdown: bool = False) -> None:
    print('game ended:', game)


def main() -> None:
    frames: 'queue.Queue[Optional[Frame]]' = queue.Queue(25)
    ffmpeg_http_server = FFMpegHTTPServer(
        frames,
        FPS,
        debug_frames=DEBUG,
        realtime=REALTIME,
        override_start_time=OVERRIDE_START_TIME
    )
    ffmpeg = FFMPEGSegmenter(
        source=SOURCE,
        ts_destination=f'http://127.0.0.1:{ffmpeg_http_server.port}/chunk/%06d.ts',
        playlist_destination=f'http://127.0.0.1:{ffmpeg_http_server.port}/playlist.csv',
        segment_time=10,
        image_destination=f'http://127.0.0.1:{ffmpeg_http_server.port}/image/%06d.raw',
        image_fps=FPS,

        restart_on_failure=REALTIME,
        seek=SEEK,
    )
    performance = PerformanceMonitor(FPS)
    pipeline = default_pipeline.create_pipeline()

    ffmpeg_http_server.start()
    ffmpeg.start()

    game_extractor = OverwatchGameExtractor(comp_only=False)
    game_extractor.on_game_complete.append(on_game_complete)
    game_extractor.on_game_started.append(on_game_started)

    if GAME_IN_PROGRESS_FREQUENCY:
        def submit_game_in_progress():
            while True:
                try:
                    game = game_extractor.get_game_in_progress()
                    if game:
                        on_game_in_progress(game)
                except:
                    logger.exception('Failed to get game in progress')
                time.sleep(GAME_IN_PROGRESS_FREQUENCY)
        Thread(target=submit_game_in_progress, daemon=True).start()

    while True:
        start = time.time()
        frame: Optional[Frame] = frames.get()
        if not frame:
            break

        frame.timings['fetch'] = (time.time() - start) * 1000
        frame.timings['in_queue'] = (time.time() - frame.submit_timestamp) * 1000
        image = frame.get('image')
        debug_image = frame.get('debug_image')

        try:
            pipeline.process(frame)
        except:
            logger.exception(f'Got exception processing frame: ')
        finally:
            frame.strip()

        performance.submit(frame.timings, frames.qsize())
        game_extractor.on_frame(frame)

        if REALTIME and not game_extractor.have_current_game:
            ffmpeg_http_server.fix_drift()

        cv2.imshow('frame', cv2.resize(debug_image if DEBUG else image, (0, 0), fx=0.5, fy=0.5))
        cv2.waitKey(1)


if __name__ == '__main__':
    config_logger('main', logging.INFO, False)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

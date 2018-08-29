import os

import cv2
import queue
import logging
from threading import Thread

import game.frame
import stream.twitch

logger = logging.getLogger(__name__)


class FrameExtractor(Thread):

    def __init__(self, ts_queue, queuesize, extract_fps=None, max_frames_per_chunk=None, debug_frames=False):
        self.extract_fps = extract_fps
        self.debug_frames = debug_frames
        self.max_frames_per_chunk = max_frames_per_chunk

        self.ts_queue = ts_queue
        self.queue = queue.Queue(queuesize)
        self.stop_ = False
        super().__init__(name='FrameExtractor')

    def run(self):
        while not self.stop_:
            segment = self.ts_queue.get()
            if segment is None:
                self.queue.put(None)
            elif isinstance(segment, Exception):
                self.queue.put(segment)
            else:
                try:
                    self.extract_frames(segment)
                except Exception as e:
                    self.queue.put(e)
        self.queue.put(None)

    def extract_frames(self, segment: stream.twitch.TwitchLiveTSDownloader.DownloadedTSChunk):
        vid = None
        try:
            vid = cv2.VideoCapture(segment.file)
            assert vid.isOpened()
            vid_fps = vid.get(cv2.CAP_PROP_FPS)
            logger.debug('Opened video %s. FPS=%f', segment.file, vid_fps)
            frame_no = 0
            extracted_frames = 0
            while not self.stop_:
                r, frame = vid.read()
                if not r:
                    break

                if frame.shape != (1080, 1920, 3):
                    frame = cv2.resize(frame, (1920, 1080))

                timestamp = segment.chunk.timestamp + (frame_no / vid_fps)
                logger.debug('Emitting frame %d: %1.1f', frame_no, timestamp)

                frame = game.frame.Frame.create(
                    frame,
                    timestamp,
                    debug=self.debug_frames,

                    frame_no=frame_no,
                    source=segment.chunk
                )
                self.queue.put(frame)
                extracted_frames += 1
                frame_no += 1

                if self.max_frames_per_chunk and extracted_frames >= self.max_frames_per_chunk:
                    break

                if self.extract_fps:
                    skipframes = int(vid_fps / self.extract_fps)
                    logger.debug('Skipping %s frames', skipframes)

                    for _ in range(skipframes):
                        vid.grab()
                        frame_no += 1

            logger.debug('Extracted %d/%d frames. Deleting video %s', extracted_frames, frame_no, segment.file)
            vid.release()
        finally:
            if vid:
                vid.release()
            segment.delete()

    def stop(self):
        self.stop_ = True


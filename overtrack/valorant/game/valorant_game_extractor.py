import datetime
import json
import logging
import os
from collections import deque
from typing import Deque, Optional

import cv2

from overtrack_cv.frame import Frame
from overtrack.processor import Processor
from overtrack.util import frameload, uploadable_image
from overtrack.util.logging_config import intermittent_log
from overtrack.valorant.game import AgentSelectProcessor
from overtrack.valorant.game import create_pipeline


class ValorantGameExtractor:

    def __init__(
        self,
        *,
        debug_frames_path: Optional[str] = None,
        save_images: bool = False,
        imshow: bool = False,
    ):
        self.imshow = imshow

        self.ingame_pipeline = self.make_pipeline()
        self.outofgame_pipeline = self.make_outofgame_pipeline()

        self.have_game = False
        self.end_game_frames = 0
        self.frames: Deque[Frame] = deque(maxlen=10_000)

        self.debug_frames_path = debug_frames_path
        self.save_images = save_images
        if self.save_images and not self.debug_frames_path:
            raise ValueError('Cannot have save_images=True without a debug_frames_path')

        self.on_game_complete = []

        self.logger = logging.getLogger('ValorantGameExtractor')

    def make_pipeline(self) -> Processor:
        return create_pipeline(aggressive=self.imshow)

    def make_outofgame_pipeline(self) -> Processor:
        return AgentSelectProcessor()

    def process(self, frame: Frame) -> bool:
        try:
            if self.have_game:
                self.ingame_pipeline.process(frame)
            else:
                self.outofgame_pipeline.process(frame)
        except:
            self.logger.exception(f'Got exception processing frame')
            return False

        image = frame.image
        debug_image = frame.debug_image
        frame.strip()

        if self.debug_frames_path:
            ts = datetime.datetime.fromtimestamp(frame.timestamp)
            destdir = os.path.join(self.debug_frames_path, ts.strftime('%Y-%m-%d'), ts.strftime('%H'))
            os.makedirs(destdir, exist_ok=True)
            destprefix = os.path.join(destdir, ts.strftime('%M-%S-%f')[:-3]).replace('\\', '/')
            if self.save_images:
                frame.image_path = os.path.abspath(destprefix + '.image.png').replace('\\', '/')
                cv2.imwrite(frame.image_path, image)
                if debug_image is not None:
                    frame.debug_image_path = os.path.abspath(destprefix + '.debug.png').replace('\\', '/')
                    cv2.imwrite(frame.debug_image_path, debug_image)
            frame.frame_path = os.path.abspath(destprefix + '.frame.json').replace('\\', '/')
            with open(frame.frame_path, 'w') as f:
                json.dump(frameload.frames_dump(frame), f, indent=2)

        if self.imshow:
            cv2.imshow('frame', debug_image if debug_image is not None else image)

        return True

    def add(self, frame: Frame) -> None:
        if frame.get('image', None) is not None:
            self.logger.warning(f"Trying to add frame with non-stripped image - ignoring")
            return

        if len(self.frames):
            logstr = (
                f'have_game={self.have_game}, len(frames)={len(self.frames)}, '
                f'Frames: {self.frames[0].timestamp_str} -> {self.frames[-1].timestamp_str}'
            )
        else:
            logstr = f'have_game={self.have_game}, len(frames)=0'

        intermittent_log(self.logger, logstr)

        end_game = False
        start_game = False
        ignore_frame = False
        if self.have_game and frame.valorant.home_screen:
            self.logger.info(logstr)
            self.end_game_frames += 1
            if self.end_game_frames >= 3:
                self.logger.info(f'Got home screen, end_game_frames={self.end_game_frames} - ending game')
                end_game = True
                self.end_game_frames = 0
            else:
                self.logger.info(f'Got home screen, end_game_frames={self.end_game_frames} - waiting for more end-game frames')
                ignore_frame = True
        elif frame.valorant.agent_select:
            self.logger.info(logstr)
            if self.have_game:
                agent_select_ago = frame.timestamp - self.frames[0].timestamp
                self.logger.info(f'Got agent select, last agent select {agent_select_ago:.2f}s ago')
                if agent_select_ago > 100:
                    self.end_game_frames += 1
                    if self.end_game_frames >= 3:
                        self.logger.info(f'Got fresh agent select, end_game_frames={self.end_game_frames} - ending game')
                        end_game = True
                        start_game = True
                        self.end_game_frames = 0
                    else:
                        self.logger.info(f'Got fresh agent select, end_game_frames={self.end_game_frames} - waiting for more end-game frames')
                        ignore_frame = True
            else:
                self.logger.info(f'Got agent select - starting game')
                start_game = True

        if end_game:
            for ogc in self.on_game_complete:
                ogc(list(self.frames))
            for imageid, image in list(uploadable_image.active_images.items()):
                if len(self.frames) and image.timestamps[0] < self.frames[0].timestamp:
                    self.logger.info(f'Dropping uploadable image {imageid} - predates current game')
                    del uploadable_image.active_images[imageid]
                uploadable_image.active_images.clear()
            self.frames.clear()
            self.have_game = False
        if start_game:
            self.have_game = True

        if ignore_frame:
            frame.ignore = True
        if self.have_game:
            self.frames.append(frame)

    def stop(self):
        self.logger.info(f'Stopping')
        if self.have_game:
            self.logger.info(f'Calling on_game_complete for all handlers')
            for ogc in self.on_game_complete:
                ogc(list(self.frames))

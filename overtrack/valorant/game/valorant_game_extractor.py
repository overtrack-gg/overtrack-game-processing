import datetime
import json
import logging
import os
from collections import deque
from typing import Deque, Optional, List

import cv2

from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import frameload
from overtrack.util.logging_config import intermittent_log
from overtrack.valorant.game.agent_select.agent_select_processor import AgentSelectProcessor
from overtrack.valorant.game.default_pipeline import create_pipeline

logger = logging.getLogger('ValorantGameExtractor')


class ValorantGameExtractor:

    def __init__(
        self,
        *,
        debug_frames_path: Optional[str] = None,
        save_images: bool = False
    ):
        self.ingame_pipeline = self.make_pipeline()
        self.outofgame_pipeline = self.make_outofgame_pipeline()

        self.have_game = False
        self.frames: Deque[Frame] = deque(maxlen=10_000)

        self.debug_frames_path = debug_frames_path
        self.save_images = save_images
        if self.save_images and not self.debug_frames_path:
            raise ValueError('Cannot have save_images=True without a debug_frames_path')

        self.on_game_complete = []

    def make_pipeline(self) -> Processor:
        return create_pipeline()

    def make_outofgame_pipeline(self) -> Processor:
        return AgentSelectProcessor()

    def process(self, frame: Frame) -> None:
        try:
            if self.have_game:
                self.ingame_pipeline.process(frame)
            else:
                self.outofgame_pipeline.process(frame)
        except:
            logger.exception(f'Got exception processing frame')
            return

        image = frame.image
        debug_image = frame.debug_image
        frame.strip()

        if self.debug_frames_path:
            ts = datetime.datetime.fromtimestamp(frame.timestamp)
            destdir = os.path.join(self.debug_frames_path, ts.strftime('%Y-%m-%d'), ts.strftime('%H'))
            os.makedirs(destdir, exist_ok=True)
            destprefix = os.path.join(destdir, ts.strftime('%M-%S-%f')[:-3]).replace('\\', '/')
            if self.save_images:
                frame.image_path = destprefix + '.image.png'
                cv2.imwrite(frame.image_path, image)
                if debug_image is not None:
                    frame.debug_image_path = destprefix + '.debug.png'
                    cv2.imwrite(frame.debug_image_path, debug_image)
            with open(destprefix + '.frame.json', 'w') as f:
                json.dump(frameload.frames_dump(frame), f, indent=2)

        if len(self.frames):
            logstr = (
                f'have_game={self.have_game}, len(frames)={len(self.frames)}, '
                f'Frames: {self.frames[0].timestamp_str} -> {self.frames[-1].timestamp_str}'
            )
        else:
            logstr = f'have_game={self.have_game}, len(frames)=0'

        intermittent_log(logger, logstr)

        end_game = False
        start_game = False
        if self.have_game and frame.valorant.home_screen:
            logger.info(logstr)
            logger.info(f'Got home screen - ending game')
            end_game = True
        elif frame.valorant.agent_select:
            logger.info(logstr)
            if self.have_game:
                agent_select_ago = frame.timestamp - self.frames[0].timestamp
                logger.info(f'Got agent select, last agent select {agent_select_ago:.2f}s ago')
                if agent_select_ago > 100:
                    logger.info(f'Got fresh agent select - starting game')
                    end_game = True
                    start_game = True
            else:
                logger.info(f'Got agent select - starting game')
                start_game = True

        if end_game:
            for ogc in self.on_game_complete:
                ogc(list(self.frames))
            self.frames.clear()
            self.have_game = False
        if start_game:
            self.have_game = True

        if self.have_game:
            self.frames.append(frame)

from typing import NamedTuple

import numpy as np

from overtrack.game import Frame
from overtrack.source import Capture


class FramesCache:

    def __init__(self, path):
        self.out = open(path, 'w')
        self.out.write(
"""from typing import NamedTuple
from overtrack.game import Frame
from overtrack.game.killfeed.icon_parser import IconParser
from overtrack.game.killfeed.kill_extractor import KillExtractor
from overtrack.game.killfeed.killfeed_processor import KillfeedProcessor
from overtrack.game.killfeed.name_parser import NameParser
from overtrack.game.killfeed.name_parser_video import NameParserVideo
from overtrack.game.loading_map.loading_map_processor import LoadingMapProcessor
from overtrack.game.objective import ObjectiveProcessor
from overtrack.game.tab.tab_processor import TabProcessor
from overtrack.game.menu import MenuProcessor
from overtrack.source.video import VideoFrameExtractor

LoadingMap = LoadingMapProcessor.LoadingMap
Killfeed = KillfeedProcessor.Killfeed
TabScreen = TabProcessor.TabScreen
Teams = LoadingMapProcessor.Teams
KillLocation = KillExtractor.KillLocation
ParsedIcon = IconParser.ParsedIcon
ParsedName = NameParser.ParsedName
KillRow = KillfeedProcessor.KillRow
Player = KillfeedProcessor.Player
VideoFrameMetadata = VideoFrameExtractor.VideoFrameMetadata
MainMenu = MenuProcessor.MainMenu

class Objective(NamedTuple):
    probabilities: object
    is_game: bool = None
    is_koth: bool = None
    round_started: bool = None
    overtime: bool = None
    checkpoint_attacker_blue: bool = None
    checkpoint_is_payload: bool = None
    koth_map: str = None
    koth_owner: str = None

cached_frames = [
""")



    def add(self, frame: Frame):
        frame.strip()
        self.out.write(str(frame) + ',\n')

    def close(self):
        self.out.write('None\n')
        self.out.write(']')
        self.out.close()


class CachedFrameExtractor(Capture):

    def __init__(self, name):
        self.frames = []
        with open(name) as f:
            exec(f.read())
        self.frames = locals()['cached_frames']
        self.index = 0

    def get(self):
        frame = self.frames[self.index]
        self.index += 1
        # frame.debug_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        return frame

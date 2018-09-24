import numpy as np

from overtrack.game import Frame


class FramesCache:

    def __init__(self, path):
        self.out = open(path, 'w')
        self.out.write("""
from overtrack.game import Frame
from overtrack.game.killfeed.icon_parser import IconParser
from overtrack.game.killfeed.kill_extractor import KillExtractor
from overtrack.game.killfeed.killfeed_processor import KillfeedProcessor
from overtrack.game.killfeed.name_parser import NameParser
from overtrack.game.killfeed.name_parser_video import NameParserVideo
from overtrack.game.loading_map.loading_map_processor import LoadingMapProcessor
from overtrack.game.objective import ObjectiveProcessor
from overtrack.game.tab.tab_processor import TabProcessor


class AttrDict(dict):

    def __getattr__(self, k):
        return self[k]


LoadingMap = LoadingMapProcessor.LoadingMap
Killfeed = KillfeedProcessor.Killfeed
TabScreen = TabProcessor.TabScreen
Teams = LoadingMapProcessor.Teams
Objective = AttrDict
KillLocation = KillExtractor.KillLocation
ParsedIcon = IconParser.ParsedIcon
ParsedName = NameParser.ParsedName
KillRow = KillfeedProcessor.KillRow
Player = KillfeedProcessor.Player
OBSFrameMetadata = AttrDict
VideoFrameMetadata = AttrDict

cached_frames = [
""")

    def add(self, frame: Frame):
        frame.strip()
        self.out.write(str(frame) + ',\n')

    def close(self):
        self.out.write('None\n')
        self.out.write(']')
        self.out.close()


class CachedFrameExtractor:

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

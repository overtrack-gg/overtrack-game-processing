from typing import List

from overtrack.util.compat import Literal

MapName = Literal['Split', 'Bind', 'Haven']
class _Maps(list, List[MapName]):
    split: MapName = 'Split'
    bind: MapName = 'Bind'
    haven: MapName = 'Haven'
    def __init__(self):
        super().__init__([self.split, self.bind, self.haven])
maps = _Maps()

GameModeName = Literal['unrated', 'competitive', 'custom']
class _GameModes(list, List[GameModeName]):
    unrated: GameModeName = 'unrated'
    competitive: GameModeName = 'competitive'
    custom: GameModeName = 'custom'
    def __init__(self):
        super().__init__([self.unrated, self.competitive, self.custom])
game_modes = _GameModes()

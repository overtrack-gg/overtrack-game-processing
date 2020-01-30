from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING, Union

import cv2
import numpy as np
import time
from dataclasses import dataclass, field

from overtrack.util import s2ts

_init_time = time.time()


class SerializableArray:
    def __init__(self, array):
        self.array = array

    def finalize(self):
        return self.array


@dataclass
class CurrentGame:
    started: float = field(default_factory=time.time)

    def __str__(self):
        return f'CurrentGame(_id={id(self)}, started={self.started})'
    __repr__ = __str__


class Timings(Dict[str, float]):

    @property
    def total(self) -> float:
        return sum([v for k, v in self.items() if k not in ['wait', 'fetch', 'in_queue']])

    def __setitem__(self, key: str, value: float) -> None:
        super().__setitem__(key, round(value, 3))

    def __str__(self) -> str:
        return str({k: round(v, 3) for k, v in dict(TOTAL=self.total, **self).items()})

    __repr__ = __str__


class Frame(Dict[str, Any]):

    def __init__(
            self,
            timestamp: float,
            **kwargs: Any) -> None:
        super().__init__(kwargs)
        self.timestamp: float = timestamp
        if 'image' not in kwargs:
            self.image: np.ndarray = None
        if 'debug_image' not in kwargs:
            self.debug_image: Optional[np.ndarray] = None
        if '_image_yuv' not in kwargs:
            self._image_yuv: Optional[np.ndarray] = None

    # typing hints - access to fields is through object-level dict or __getattr__
    if TYPE_CHECKING:
        # image: Optional[np.ndarray]
        # timestamp: float
        relative_timestamp: float
        timestamp_str: str
        relative_timestamp_str: str

        game_time: float
        current_game: CurrentGame

        frame_no: int
        # debug_image: Optional[np.ndarray]

        import overtrack.overwatch.game.objective.models
        import overtrack.overwatch.game.objective_2.models
        import overtrack.overwatch.game.loading_map.models
        import overtrack.overwatch.game.tab.models
        import overtrack.overwatch.game.menu.models
        import overtrack.overwatch.game.killfeed_2.models
        import overtrack.overwatch.game.spectator.models
        import overtrack.overwatch.game.score.models
        import overtrack.overwatch.game.endgame.models
        import overtrack.overwatch.game.hero.models
        import overtrack.overwatch.game.endgame_sr.models
        import overtrack.overwatch.game.hero_select.models
        import overtrack.overwatch.game.overwatch_metadata
        import overtrack.overwatch.game.role_select.models
        import overtrack.overwatch.game.eliminations.models
        objective: overtrack.overwatch.game.objective.Objective
        objective2: Union[overtrack.overwatch.game.objective_2.Objective3, overtrack.overwatch.game.objective_2.Objective2]
        loading_map: overtrack.overwatch.game.loading_map.models.LoadingMap
        loading_match: float
        tab_screen: overtrack.overwatch.game.tab.models.TabScreen
        tab_match: float
        main_menu: overtrack.overwatch.game.menu.models.MainMenu
        main_menu_match: float
        play_menu: overtrack.overwatch.game.menu.models.PlayMenu
        play_menu_match: float
        killfeed_2: overtrack.overwatch.game.killfeed_2.models.Killfeed2
        killcam_match: float
        spectator_bar: overtrack.overwatch.game.spectator.models.SpectatorBar
        score_screen: overtrack.overwatch.game.score.models.ScoreScreen
        score_screen_match: float
        final_score: overtrack.overwatch.game.score.models.FinalScore
        final_score_match: float
        endgame: overtrack.overwatch.game.endgame.models.Endgame
        endgame_match: float
        hero: overtrack.overwatch.game.hero.models.Hero
        endgame_sr_match: float
        endgame_sr: overtrack.overwatch.game.endgame_sr.models.EndgameSR
        assemble_your_team_match: float
        assemble_your_team: overtrack.overwatch.game.hero_select.models.AssembleYourTeam
        role_select: overtrack.overwatch.game.role_select.models.RoleSelect
        eliminations: overtrack.overwatch.game.eliminations.models.Eliminations
        overwatch_metadata: overtrack.overwatch.game.overwatch_metadata.OverwatchClientMetadata

        import overtrack.apex.game.match_status.models
        import overtrack.apex.game.match_summary.models
        import overtrack.apex.game.menu.models
        import overtrack.apex.game.squad.models
        import overtrack.apex.game.squad_summary.models
        import overtrack.apex.game.weapon.models
        import overtrack.apex.game.your_squad
        import overtrack.apex.game.combat.models
        import overtrack.apex.game.apex_metadata
        import overtrack.apex.game.minimap.models
        from overtrack.apex.game.your_squad import YourSquad, YourSelection, ChampionSquad
        game_time: float
        match_status: overtrack.apex.game.match_status.models.MatchStatus
        match_summary_match: float
        match_summary: overtrack.apex.game.match_summary.models.MatchSummary
        apex_play_menu_match: float
        apex_play_menu: overtrack.apex.game.menu.models.PlayMenu
        squad_match: float
        squad: overtrack.apex.game.squad.models.Squad
        squad_summary_match: float
        squad_summary: overtrack.apex.game.squad_summary.models.SquadSummary
        weapons: overtrack.apex.game.weapon.models.Weapons
        your_squad_match: float
        your_squad: YourSquad
        your_selection: YourSelection
        champion_squad = ChampionSquad
        combat_log: overtrack.apex.game.combat.models.CombatLog
        minimap: overtrack.apex.game.minimap.models.Minimap
        apex_metadata: overtrack.apex.game.apex_metadata.ApexClientMetadata

        timings: Timings

        from overtrack.source.stream.ts_stream import TSSource
        from overtrack.source.display_duplication import DisplayDuplicationSource
        from overtrack.source.shmem import SharedMemorySource

        source: Union[TSSource, DisplayDuplicationSource, SharedMemorySource]

    @classmethod
    def create(
            cls,
            image: np.ndarray,
            timestamp: float,
            debug: bool=False,
            timings: Optional[Dict[str, float]]=None,
            **data: Any) -> 'Frame':
        if image.dtype != np.uint8:
            raise TypeError(f'image must have type uint8 but had type { image.dtype }')

        if image.shape[0] != 1080 or image.shape[2] != 3:
            raise TypeError(f'image must have shape (1080, *, 3) but had { image.shape }')

        f = cls.__new__(cls)
        f.image = image
        f._image_yuv: Optional[np.ndarray] = None

        f.timestamp = timestamp
        f.timestamp_str = datetime.utcfromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M:%S.') + f'{timestamp % 1 :.2f}'[2:]

        if 'relative_timestamp' in data:
            relative_timestamp = data['relative_timestamp']
        else:
            relative_timestamp = f.timestamp - _init_time
        f.relative_timestamp = relative_timestamp
        f.relative_timestamp_str = f'{s2ts(relative_timestamp)}.' + f'{relative_timestamp % 1 :.2f}'[2:]

        f.timings = Timings(**timings if timings else {})
        if debug:
            f.debug_image = image.copy()

            s = f'{f.timestamp_str}'

            if 'relative_timestamp_str' in f:
                s += f' | {f.relative_timestamp_str}'
                if 'image_no' in data:
                    s += f' ({data["image_no"]})'

            if data.get('offset_from_now') is not None:
                s += f' | offset: {s2ts(data["offset_from_now"])}'

            if 'source' in data:
                s += f' | {data["source"]}'
            if 'source_frame_no' in data:
                s += f' +{data["source_frame_no"]}'
            if 'source_timestamp' in data:
                s += f'/+{data["source_timestamp"]:1.2f}s'

            if 'offset_from_last' in data and data['offset_from_last'] is not None:
                s += f' | +{data["offset_from_last"]:1.2f}s'

            for t, c in (5, (0, 0, 0)), (1, (255, 0, 255)):
                cv2.putText(f.debug_image, s, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, c, t)
        else:
            f.debug_image = None

        f.update(data)
        return f

    @property
    def debug(self) -> bool:
        return self.get('debug_image') is not None

    def strip(self) -> 'Frame':
        """
        Remove all top-level numpy arrays
        """
        for k in 'image', 'debug_image', '_image_yuv':
            if k in self:
                del self[k]
        for k in list(self.keys()):
            if isinstance(self.get(k), np.ndarray):
                del self[k]
        return self

    def copy(self) -> 'Frame':
        return Frame(**self)

    @property
    def image_yuv(self) -> np.ndarray:
        if self._image_yuv is None:
            super().__setitem__('_image_yuv', cv2.cvtColor(self.image, cv2.COLOR_BGR2YUV))
        return self._image_yuv

    def __getattr__(self, item: str) -> Any:
        if item not in self:
            raise AttributeError('Frame does not (yet?) have attribute %r' % (item, ))
        return self[item]

    def __setattr__(self, key: str, value: Any) -> None:
        self.__setitem__(key, value)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            raise ValueError(f'Cannot add item "{ key }": already exists')
        super().__setitem__(key, value)

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

import cv2
import dataclasses
import numpy as np

from overtrack.util import s2ts


def dictify(dic: Any) -> Any:
    if isinstance(dic, dict):
        return {k: dictify(v) for k, v in dic.items()}
    elif isinstance(dic, list):
        return [dictify(e) for e in dic]
    elif callable(getattr(dic, 'to_dict', None)):
        return dictify(dic.to_dict())
    elif callable(getattr(dic, '_asdict', None)):
        # noinspection PyProtectedMember
        return dictify(dic._asdict())
    elif dataclasses.is_dataclass(dic):
        return dictify(dic.__dict__)
    elif isinstance(dic, tuple):
        return tuple(dictify(e) for e in dic)
    elif isinstance(dic, np.ndarray) and len(dic.shape) == 1:
        return [e.item() for e in dic]
    elif callable(getattr(dic, 'item', None)):  # FIXME
        return dic.item()
    elif isinstance(dic, np.ndarray) and np.prod(dic.shape) > 50:
        return f'np.ndarray<{ dic.shape }, dtype={ dic.dtype }>'
    return dic


# ¯\_(ツ)_/¯
def strify(o: Any, depth: int=0) -> str:
    if isinstance(o, str):
        return "'" + o + "'"
    if isinstance(o, float):
        return f'{ o :1.4f}'
    elif isinstance(o, dict):
        return '{' + ', '.join(f'{repr(k)}: {strify(v, depth+1)}' for k, v in o.items()) + '}'
    elif isinstance(o, list):
        return '[' + ', '.join(strify(e, depth + 1) for e in o) + ']'
    elif dataclasses.is_dataclass(o) or hasattr(o, '_fields'):
        if dataclasses.is_dataclass(o):
            fields = [f.name for f in dataclasses.fields(o)]
        else:
            # noinspection PyProtectedMember
            fields = o._fields
        if len(fields) < 4:
            return str(o.__class__.__name__ + '(' + ', '.join(f + '=' + strify(getattr(o, f), depth) for f in fields) + ')')
        else:
            spaces = '  ' * (depth+1)
            return str(o.__class__.__name__ + '(\n' + spaces + \
               (',\n' + spaces).join(
                   f + '=' + strify(getattr(o, f), depth+1)
                   for f in fields
               ) + '\n' + '  ' * depth + ')')
    elif isinstance(o, tuple):
        return '(' + ', '.join(strify(e, depth + 1) for e in o) + ')'
    elif isinstance(o, np.ndarray) and len(o.shape) == 1:
        return strify([e.item() for e in o], depth + 1)
    elif isinstance(o, np.ndarray) and np.prod(o.shape) > 50:
        return f'np.ndarray<{ o.shape }, dtype={ o.dtype }>'
    return str(o)


class Timings(Dict[str, float]):

    @property
    def total(self) -> float:
        return sum([v for k, v in self.items() if k not in ['wait', 'fetch', 'in_queue']])

    def __setitem__(self, key: str, value: float) -> None:
        super().__setitem__(key, round(value, 4))

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
        self._image_yuv: Optional[np.ndarray] = None

    # typing hints - access to fields is through object-level dict or __getattr__
    if TYPE_CHECKING:
        # image: Optional[np.ndarray]
        # timestamp: float
        relative_timestamp: float
        timestamp_str: str
        relative_timestamp_str: str

        frame_no: int
        # debug_image: Optional[np.ndarray]

        import overtrack.overwatch.game.objective
        objective: overtrack.overwatch.game.objective.Objective

        import overtrack.overwatch.game.loading_map
        loading_map: overtrack.overwatch.game.loading_map.LoadingMapProcessor.LoadingMap
        loading_match: float

        import overtrack.overwatch.game.tab
        tab_screen: overtrack.overwatch.game.tab.TabProcessor.TabScreen
        tab_match: float

        import overtrack.overwatch.game.menu
        main_menu: overtrack.overwatch.game.menu.MenuProcessor.MainMenu
        main_menu_match: float
        play_menu: overtrack.overwatch.game.menu.MenuProcessor.PlayMenu
        play_menu_match: float

        import overtrack.overwatch.game.killfeed
        killfeed: overtrack.overwatch.game.killfeed.KillfeedProcessor.Killfeed
        killcam_match: float

        import overtrack.overwatch.game.spectator
        spectator_bar: overtrack.overwatch.game.spectator.SpectatorProcessor.SpectatorBar

        import overtrack.overwatch.game.score
        score_screen: overtrack.overwatch.game.score.ScoreProcessor.ScoreScreen
        score_screen_match: float
        final_score: overtrack.overwatch.game.score.ScoreProcessor.FinalScore
        final_score_match: float

        import overtrack.overwatch.game.endgame
        endgame: overtrack.overwatch.game.endgame.EndgameProcessor.Endgame
        endgame_match: float

        import overtrack.overwatch.game.hero
        hero: overtrack.overwatch.game.hero.HeroProcessor.Hero

        timings: Timings

        # this source is used in the online version
        from overtrack.source.stream.ts_stream import TSSource
        source: TSSource

        import overtrack.apex.game.match_status
        import overtrack.apex.game.match_summary
        import overtrack.apex.game.menu
        import overtrack.apex.game.squad
        import overtrack.apex.game.weapon
        import overtrack.apex.game.your_squad
        import overtrack.apex.game.map
        match_status: overtrack.apex.game.match_status.MatchStatus
        match_summary: overtrack.apex.game.match_summary.MatchSummary
        apex_play_menu: overtrack.apex.game.menu.PlayMenu
        squad: overtrack.apex.game.squad.Squad
        weapons: overtrack.apex.game.weapon.Weapons
        your_squad: overtrack.apex.game.your_squad.YourSquad
        location: overtrack.apex.game.map.Location

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
        if image.shape != (1080, 1920, 3):
            raise TypeError(f'image must have shape (1080, 1920, 3) but had { image.shape }')

        f = cls.__new__(cls)
        f.image = image
        f._image_yuv: Optional[np.ndarray] = None

        f.timestamp = timestamp
        f.timestamp_str = datetime.utcfromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M:%S.') + f'{timestamp % 1 :.2f}'[2:]

        relative_timestamp = data.get('relative_timestamp', timestamp)
        if relative_timestamp:
            f.relative_timestamp_str = f'{s2ts(relative_timestamp)}.' + f'{relative_timestamp % 1 :.2f}'[2:]

        f.timings = Timings(**timings if timings else {})
        if debug:
            f.debug_image = image.copy()
            for t, c in (7, (0, 0, 0)), (2, (255, 0, 255)):
                s = f'{f.timestamp_str}'

                if 'relative_timestamp_str' in f:
                    s += f' | {f.relative_timestamp_str}'

                if 'offset_from_now' in data:
                    s += f' | offset: {data["offset_from_now"] :1.1f}'

                if 'source' in data:
                    s += f' | {data["source"]}'
                if 'source_frame_no' in data:
                    s += f' +{data["source_frame_no"]}'
                if 'source_timestamp' in data:
                    s += f'/+{data["source_timestamp"]:1.2f}s'

                if 'offset_from_last' in data and data['offset_from_last'] is not None:
                    s += f' | +{data["offset_from_last"]:1.2f}s'

                cv2.putText(f.debug_image, s, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, c, t)
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
        for k in 'image', 'debug_image':
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

    def _to_str(self, newlines: bool=True) -> str:
        return '%s(%s%s%s)' % (
            self.__class__.__name__,
            '\n  ' if newlines else '',
            (',\n  ' if newlines else ', ').join(
                '%s=%s' % (
                    k,
                    strify(v, 1)
                ) for (k, v) in sorted(self.items())
            ),
            '\n' if newlines else ''
        )

    def __str__(self) -> str:
        return self._to_str(newlines=True)

    def __repr__(self) -> str:
        return self._to_str(newlines=False)


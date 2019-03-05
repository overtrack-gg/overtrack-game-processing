import itertools
from typing import Any, Dict, Optional, Type, TypeVar, TYPE_CHECKING, List, Union, cast

if TYPE_CHECKING:
    from overtrack.frame import Frame

# noinspection PyUnresolvedReferences
import dataclasses
# noinspection PyUnresolvedReferences
import typedload.datadumper
# noinspection PyUnresolvedReferences
import typedload.dataloader
import numpy as np
from typedload.exceptions import Annotation

from overtrack.overwatch.collect import Game
from overtrack.source.stream.ts_stream import TSSource


class Loader(typedload.dataloader.Loader):
    # noinspection PyUnresolvedReferences
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if 'source_type' not in kwargs:
            self.source_type = TSSource

        self.referenced: Dict[object, Any] = {}

        from overtrack.frame import Frame
        import overtrack.overwatch.game.loading_map
        import overtrack.overwatch.game.killfeed
        import overtrack.overwatch.game.objective
        import overtrack.overwatch.game.endgame

        self.frefs.update({
            # 'ObjectiveExtractor.Objective': overtrack.game.objective.objective_processor.ObjectiveExtractor.Probabilities,

            'LoadingMapProcessor.Teams': overtrack.overwatch.game.loading_map.LoadingMapProcessor.Teams,
            'KillfeedProcessor.KillRow': overtrack.overwatch.game.killfeed.KillfeedProcessor.KillRow,
            'KillfeedProcessor.Player': overtrack.overwatch.game.killfeed.KillfeedProcessor.Player,
            'EndgameProcessor.Stats': overtrack.overwatch.game.endgame.EndgameProcessor.Stats
            # 'TSFrameExtractor.TSChunk': overtrack.source.stream.opencv_ts_stream.TSFrameExtractor.TSChunk
        })

        # noinspection PyTypeChecker
        self.handlers.append((lambda type_: type_ == Frame, _frameload))
        self.handlers.append((lambda type_: isinstance(type_, str), lambda l, value, type_: l.load(value, l.frefs[type_])))

        # self.handlers[8] = (self.handlers[8][0], _namedtupleload)
        # self.handlers[9] = (self.handlers[9][0], _namedtupleload)

    T = TypeVar('T')

    def load(self, value: Any, type_: Type[T], *, annotation: Optional[Annotation] = None) -> T:
        if isinstance(value, dict):
            if '_id' in value:
                _id = value['_id']
                value = dict(value)  # copy the dict so we dont erase _id from the source data
                del value['_id']
                r = super().load(value, type_)
                self.referenced[_id] = r
                return r
            elif '_ref' in value:
                return self.referenced[value['_ref']]

        return super().load(value, type_)

def _frameload(loader: Loader, value: Dict[str, object], type_: type) -> 'Frame':
    from overtrack.frame import Frame, Timings
    import overtrack.overwatch.game.objective
    import overtrack.overwatch.game.killfeed
    import overtrack.overwatch.game.tab
    import overtrack.overwatch.game.loading_map
    import overtrack.overwatch.game.spectator
    import overtrack.overwatch.game.menu
    import overtrack.overwatch.game.score
    import overtrack.overwatch.game.endgame
    import overtrack.overwatch.game.hero

    _TYPES = {
        'objective': overtrack.overwatch.game.objective.ObjectiveProcessor.Objective,
        'loading_map': overtrack.overwatch.game.loading_map.LoadingMapProcessor.LoadingMap,
        'tab_screen': overtrack.overwatch.game.tab.tab_processor.TabProcessor.TabScreen,
        'main_menu': overtrack.overwatch.game.menu.MenuProcessor.MainMenu,
        'play_menu': overtrack.overwatch.game.menu.MenuProcessor.PlayMenu,
        'killfeed': overtrack.overwatch.game.killfeed.KillfeedProcessor.Killfeed,
        'spectator_bar': overtrack.overwatch.game.spectator.SpectatorProcessor.SpectatorBar,
        'score_screen': overtrack.overwatch.game.score.ScoreProcessor.ScoreScreen,
        'final_score': overtrack.overwatch.game.score.ScoreProcessor.FinalScore,
        'endgame': overtrack.overwatch.game.endgame.EndgameProcessor.Endgame,
        'hero': overtrack.overwatch.game.hero.HeroProcessor.Hero
    }

    f = Frame.__new__(Frame)
    f.image = f.debug_image = None
    for k, v in value.items():
        if k == 'debug_image':
            continue
        elif v is None or type(v) in {int, bool, float, str}:
            f[k] = v
        elif k in _TYPES:
            f[k] = loader.load(v, _TYPES[k])
        elif k == 'timings':
            # noinspection PyTypeChecker
            f[k] = Timings(cast(Dict, v))
        elif k in ['image', 'debug_image']:
            pass
        elif k == 'source':
            f[k] = loader.load(v, loader.source_type)
        else:
            raise ValueError(f'Don\'t know how to load "{k}" (had type {type(v)})')
    return f


class Dumper(typedload.datadumper.Dumper):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        # add support for numpy scalars converting them to the equivalent python type
        self.handlers.append((
            lambda value: np.isscalar(value),
            lambda l, value: value.item()
        ))
        self.handlers.append((
            lambda value: isinstance(value, Game),
            lambda l, value: l.dump(value.__dict__)
        ))


class ReferencedDumper(Dumper):
    def __init__(self, combine_equal: bool=True, **kwargs: Any):
        super().__init__(**kwargs)
        self.combine_equal = combine_equal

        self.visited: Dict[int, Union[bool, int]] = {}
        self.dumped: Dict[int, object] = {}
        self.refs_to_add: List[int] = []

        self.equal: Dict[object, object] = {}

        self.idgen = iter(itertools.count())

    def dump(self, value: Any) -> Any:
        is_namedtuple = isinstance(value, tuple) and hasattr(value, '_fields') and hasattr(value, '_asdict')
        if type(value) in self.basictypes or np.isscalar(value):
            return super().dump(value)
        elif isinstance(value, (list, tuple, set)) and not is_namedtuple:
            if id(value) in self.visited:
                raise ValueError(f'Cannot serialise a sequence containing itself')
            self.visited[id(value)] = True
            return super().dump(value)
        elif id(value) in self.visited:
            self.refs_to_add.append(id(value))
            return {'_ref': self.visited[id(value)]}
        else:
            try:
                equal = self.equal[value]
            except TypeError:
                # not hashable
                pass
            except KeyError:
                # none equal found
                self.equal[value] = value
            else:
                # value == equal, but id(value) != equal and equal has already been added
                # instead of adding value, add a ref to equal
                self.refs_to_add.append(id(equal))
                return {'_ref': self.visited[id(equal)]}

            self.visited[id(value)] = next(self.idgen)
            result = super().dump(value)
            self.dumped[id(value)] = result
            return result


def dump(value: object) -> Dict[str, Any]:
    dumper = ReferencedDumper()
    r = dumper.dump(value)

    # add _refs for items that have been ref'd to
    for _ref in dumper.refs_to_add:
        referenced = dumper.dumped[_ref]
        if not isinstance(referenced, dict):
            raise ValueError(f'Cannot dump a {type(referenced)}, id={id(referenced)} containing itself ({referenced})')
        # print('create _id', _ref, referenced)
        referenced['_id'] = dumper.visited[_ref]

    return r


T = TypeVar('T')


def load(value: Any, type_: Type[T], **kwargs: Any) -> T:
    loader = Loader(**kwargs)
    return loader.load(value, type_)

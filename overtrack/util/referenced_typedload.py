import itertools
from typing import Any, Dict, Optional, Type, TypeVar, List, Union, cast

# noinspection PyUnresolvedReferences
import dataclasses
# noinspection PyUnresolvedReferences
import typedload.datadumper
# noinspection PyUnresolvedReferences
import typedload.dataloader
import numpy as np
from typedload.exceptions import Annotation

from overtrack.frame import Frame, Timings
from overtrack.source.display_duplication import DisplayDuplicationSource
from overtrack.source.http.http_capture import HTTPSource
from overtrack.source.stream import TSSource

import overtrack.overwatch.game.objective.models
import overtrack.overwatch.game.killfeed.models
import overtrack.overwatch.game.tab.models
import overtrack.overwatch.game.loading_map.models
import overtrack.overwatch.game.spectator.models
import overtrack.overwatch.game.menu.models
import overtrack.overwatch.game.score.models
import overtrack.overwatch.game.endgame.models
import overtrack.overwatch.game.hero.models
import overtrack.overwatch.game.endgame_sr.models

import overtrack.apex.game.match_status.models
import overtrack.apex.game.match_summary.models
import overtrack.apex.game.menu.models
import overtrack.apex.game.squad.models
import overtrack.apex.game.your_squad.models
import overtrack.apex.game.weapon.models
import overtrack.apex.game.squad_summary.models
import overtrack.apex.game.map.models
import overtrack.apex.game.combat.models
import overtrack.apex.game.apex_metadata
import overtrack.util.uploadable_image


Source = Union[TSSource, DisplayDuplicationSource, HTTPSource]

class Loader(typedload.dataloader.Loader):
    # noinspection PyUnresolvedReferences
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if 'source_type' not in kwargs:
            self.source_type = Source

        self.referenced: Dict[object, Any] = {}

        # assert self.frefs is not None
        # self.frefs.update({
        #     # 'ObjectiveExtractor.Objective': overtrack.game.objective.objective_processor.ObjectiveExtractor.Probabilities,
        #
        #     #'LoadingMapProcessor.Teams': overtrack.overwatch.game.loading_map.LoadingMapProcessor.Teams,
        #     # 'KillRow': overtrack.overwatch.game.killfeed.KillRow,
        #     # 'Player': overtrack.overwatch.game.killfeed.Player,
        #     #'EndgameProcessor.Stats': overtrack.overwatch.game.endgame.EndgameProcessor.Stats
        #     # 'TSFrameExtractor.TSChunk': overtrack.source.stream.opencv_ts_stream.TSFrameExtractor.TSChunk
        # })

        # noinspection PyTypeChecker
        cast(Any, self.handlers).append((lambda type_: type_ == Frame, _frameload))
        cast(Any, self.handlers).append((lambda type_: isinstance(type_, str), lambda l, value, type_: l.load(value, l.frefs[type_])))

        # self.handlers[8] = (self.handlers[8][0], _namedtupleload)
        # self.handlers[9] = (self.handlers[9][0], _namedtupleload)

    T = TypeVar('T')

    def load(self, value: Any, type_: Type[T], *, annotation: Optional[Annotation] = None) -> T:
        if type_ is overtrack.util.uploadable_image.UploadableImage:
            type_ = overtrack.util.uploadable_image.UploadedImage
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


_TYPES = {
    'objective': overtrack.overwatch.game.objective.models.Objective,
    'loading_map': overtrack.overwatch.game.loading_map.models.LoadingMap,
    'tab_screen': overtrack.overwatch.game.tab.models.TabScreen,
    'main_menu': overtrack.overwatch.game.menu.models.MainMenu,
    'play_menu': overtrack.overwatch.game.menu.models.PlayMenu,
    'killfeed': overtrack.overwatch.game.killfeed.models.Killfeed,
    'spectator_bar': overtrack.overwatch.game.spectator.models.SpectatorBar,
    'score_screen': overtrack.overwatch.game.score.models.ScoreScreen,
    'final_score': overtrack.overwatch.game.score.models.FinalScore,
    'endgame': overtrack.overwatch.game.endgame.models.Endgame,
    'hero': overtrack.overwatch.game.hero.models.Hero,
    'endgame_sr': overtrack.overwatch.game.endgame_sr.models.EndgameSR,

    'match_status': overtrack.apex.game.match_status.models.MatchStatus,
    'match_summary': overtrack.apex.game.match_summary.models.MatchSummary,
    'apex_play_menu': overtrack.apex.game.menu.models.PlayMenu,
    'squad': overtrack.apex.game.squad.models.Squad,
    'weapons': overtrack.apex.game.weapon.models.Weapons,
    'your_squad': overtrack.apex.game.your_squad.models.YourSquad,
    'champion_squad': overtrack.apex.game.your_squad.models.ChampionSquad,
    'squad_summary': overtrack.apex.game.squad_summary.models.SquadSummary,
    'location': overtrack.apex.game.map.models.Location,
    'combat_log': overtrack.apex.game.combat.models.CombatLog,

    'apex_metadata': overtrack.apex.game.apex_metadata.ApexClientMetadata
}


def _frameload(loader: Loader, value: Dict[str, object], type_: type) -> Frame:
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

        # from overtrack.overwatch.collect import Game
        # self.handlers.append((
        #     lambda value: isinstance(value, Game),
        #     lambda l, value: l.dump(value.__dict__)
        # ))


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

            if hasattr(value, '_typeddump') and callable(value._typeddump):
                result = value._typeddump()
            else:
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

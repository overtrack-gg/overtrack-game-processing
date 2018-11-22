import itertools
import json
import time
import typedload.datadumper
import typedload.dataloader
import dataclasses
from pprint import pprint
from typing import Dict, Any, Tuple, Type, Optional, TypeVar
import numpy as np
from typedload.exceptions import Annotation

from overtrack.collect import Game
from overtrack.source.stream.ts_stream import TSSource


class Loader(typedload.dataloader.Loader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'source_type' not in kwargs:
            self.source_type = TSSource

        self.referenced = {}

        from overtrack.game.frame import Frame
        import overtrack.game.loading_map
        import overtrack.game.killfeed
        import overtrack.game.objective
        import overtrack.game.endgame
        self.frefs.update({
            'ObjectiveExtractor.Probabilities': overtrack.game.objective.objective_processor.ObjectiveExtractor.Probabilities,

            'LoadingMapProcessor.Teams': overtrack.game.loading_map.LoadingMapProcessor.Teams,
            'KillfeedProcessor.KillRow': overtrack.game.killfeed.KillfeedProcessor.KillRow,
            'KillfeedProcessor.Player': overtrack.game.killfeed.KillfeedProcessor.Player,
            'EndgameProcessor.Stats': overtrack.game.endgame.EndgameProcessor.Stats
            # 'TSFrameExtractor.TSChunk': overtrack.source.stream.opencv_ts_stream.TSFrameExtractor.TSChunk
        })

        self.handlers.append((lambda type_: type_ == Frame, _frameload))
        self.handlers.append((lambda type_: isinstance(type_, str), lambda l, value, type_: l.load(value, l.frefs[type_])))

        self.handlers[8] = (self.handlers[8][0], _namedtupleload)
        self.handlers[9] = (self.handlers[9][0], _namedtupleload)

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


def _namedtupleload(l: Loader, value: Dict[str, Any], type_) -> Tuple:
    """
    This loads a Dict[str, Any] into a NamedTuple.
    """
    if not hasattr(type_, '__dataclass_fields__'):
        fields = set(type_._fields)
        optional_fields = set(getattr(type_, '_field_defaults', {}).keys())
        type_hints = type_._field_types
    else:
        # dataclass
        import dataclasses

        fields = set(type_.__dataclass_fields__.keys())
        optional_fields = {k for k, v in type_.__dataclass_fields__.items() if
                           not isinstance(getattr(v, 'default', dataclasses._MISSING_TYPE()), dataclasses._MISSING_TYPE)}
        type_hints = {k: v.type for k, v in type_.__dataclass_fields__.items()}
    necessary_fields = fields.difference(optional_fields)
    try:
        vfields = set(value.keys())
    except AttributeError as e:
        raise typedload.dataloader.TypedloadAttributeError(str(e), value=value, type_=type_)

    if necessary_fields.intersection(vfields) != necessary_fields:
        raise typedload.dataloader.TypedloadValueError(
            'Value does not contain fields: %s which are necessary for type %s' % (
                necessary_fields.difference(vfields),
                type_
            ),
            value=value,
            type_=type_,
        )

    fieldsdiff = vfields.difference(fields)
    if l.failonextra and len(fieldsdiff):
        extra = ', '.join(fieldsdiff)
        raise typedload.dataloader.TypedloadValueError(
            'Dictionary has unrecognized fields: %s and cannot be loaded into %s' % (extra, type_),
            value=value,
            type_=type_,
        )

    params = {}
    for k, v in value.items():
        if k not in fields:
            continue
        params[k] = l.load(
            v,
            type_hints[k],
            annotation=typedload.dataloader.Annotation(typedload.dataloader.AnnotationType.FIELD, k),
        )
    try:
        return type_(**params)
    except (TypeError, AttributeError):
        return dataclasses.make_dataclass(type_.__name__, type_hints.items())(**{n: params.get(n) for n in type_hints})


def _frameload(loader: Loader, value: Any, type_: type) -> Any:
    from overtrack.game.frame import Frame, Timings
    import overtrack.game.objective
    import overtrack.game.killfeed
    import overtrack.game.tab
    import overtrack.game.loading_map
    import overtrack.game.spectator
    import overtrack.game.menu
    import overtrack.game.score
    import overtrack.game.endgame

    _TYPES = {
        'objective': overtrack.game.objective.ObjectiveProcessor.Objective,
        'loading_map': overtrack.game.loading_map.LoadingMapProcessor.LoadingMap,
        'tab_screen': overtrack.game.tab.tab_processor.TabProcessor.TabScreen,
        'main_menu': overtrack.game.menu.MenuProcessor.MainMenu,
        'play_menu': overtrack.game.menu.MenuProcessor.PlayMenu,
        'killfeed': overtrack.game.killfeed.KillfeedProcessor.Killfeed,
        'spectator_bar': overtrack.game.spectator.SpectatorProcessor.SpectatorBar,
        'score_screen': overtrack.game.score.ScoreProcessor.ScoreScreen,
        'final_score': overtrack.game.score.ScoreProcessor.FinalScore,
        'endgame': overtrack.game.endgame.EndgameProcessor.Endgame,
    }

    f = Frame.__new__(Frame)
    f.image = f.debug_image = None
    for k, v in value.items():
        if type(v) in {int, bool, float, str, None}:
            f[k] = v
        elif k in _TYPES:
            f[k] = loader.load(v, _TYPES[k])
        elif k == 'timings':
            f[k] = Timings(v)
        elif k in ['image', 'debug_image']:
            pass
        elif k == 'source':
            f[k] = loader.load(v, loader.source_type)
        else:
            raise ValueError(f'Don\'t know how to load "{k}" (had type {type(v)})')
    return f


class Dumper(typedload.datadumper.Dumper):
    def __init__(self, **kwargs):
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
    def __init__(self, combine_equal=True, **kwargs):
        super().__init__(**kwargs)
        self.combine_equal = combine_equal

        self.visited = {}
        self.dumped = {}
        self.refs_to_add = []

        self.equal = {}

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
            # print('>', id(value), 'is visited', value)
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
                # print('>', id(value), 'is equal to', id(equal), value)
                return {'_ref': self.visited[id(equal)]}

            self.visited[id(value)] = next(self.idgen)
            # print('>', id(value), self.visited[id(value)], 'visit', value)
            result = super().dump(value)
            self.dumped[id(value)] = result
            return result


def dump(value: object) -> Dict[str, object]:
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


def load(value: Any, type_: Type[T], **kwargs) -> T:
    loader = Loader(**kwargs)
    return loader.load(value, type_)


def main():
    d = {
        "endgame": {
            "map": "LIJIANG TOWER",
            "result": "VICTORY",
            "stats": {
                "deaths": 3,
                "eliminations": 1,
                "healing_done": 0,
                "hero": "winston",
                "hero_damage_done": 475,
                "hero_specific_stats": {
                    "damage blocked": None,
                    "kill streak - best": None,
                    "melee kills": None,
                    "players knocked back": None,
                    "primal rage kills": None
                },
                "objective_kills": 1,
                "objective_time": 3
            }
        },
        "endgame_match": 0.86732,
        "frame_no": 29078,
        "relative_timestamp": 968.23333,
        "relative_timestamp_str": "00:16:08.23",
        "source": {
            "_ref": 2
        },
        "timestamp": 1542763093.9628325,
        "timestamp_str": "2018/11/21 01:18:13.96",
        "timings": {
            "VideoFrameExtractor": 100.0962
        }
    }

    from overtrack.game.endgame import EndgameProcessor

    e = load(d['endgame']['stats'], EndgameProcessor.Stats)
    print(e)

    e = load(d['endgame'], EndgameProcessor.Endgame)
    print(e)

    return

    from typing import List
    from overtrack.game.frame import Frame
    with open('./games/stream/2018-10-03-02-21/game_03-05_INGTOWER.json') as f:
        data = json.load(f)

    frames = load(data, List[Frame])


def _main():
    from overtrack.collect import Game
    from server.ingest import TSChunkHTTPServer, UploadedTSChunkFile
    # fix dill incompat
    TSChunkHTTPServer.UploadedTSChunkFile = UploadedTSChunkFile
    import dill
    with open('./games/stream/2018-09-29-11-58/game_2.dill', 'rb') as f:
        game: Game = dill.load(f)

    # with open('./games/game_15.dill', 'rb') as f:
    #     data = f.read()

    # t0 = time.time()
    # game: Game = dill.load(io.BytesIO(data))
    # t1 = time.time()
    # print(t1 - t0)

    t0 = time.time()
    dill.dumps(game)
    t1 = time.time()
    print(t1 - t0)

    t0 = time.time()
    Dumper().dump(game)
    t1 = time.time()
    print(t1 - t0)

    t0 = time.time()
    dump(game)
    t1 = time.time()
    print(t1 - t0)

    with open('full.json', 'w') as f:
        json.dump(
            Dumper().dump(game),
            f,
            indent=1
        )

    # with open('cyclic.json', 'w') as f:
    #     json.dump(ReferencedDumper().dump(game), f, indent=1)
    #

    test = {
        'list': [],
        'dict': {}
    }
    test['list'] = {
        'a': {
            'b': {
                'c': [1, 2, 3],
                1: test
            }
        }
    }
    pprint(dump(test))

    # game.frames = game.frames[100:110]
    # print(id(game.frames[0].source))
    # print(id(game.frames[1].source))
    with open('cyclic.json', 'w') as f:
        json.dump(
            dump(game),
            f,
            indent=1
        )

    print()

    # print(timeit.timeit(
    #     'dump(game)', 'pass', globals=dict(**locals(), **globals()), number=1
    # ))


if __name__ == '__main__':
    main()
    #
    # from typing import NamedTuple, List
    # from dataclasses import dataclass
    #
    # cycle = {}
    # cycle['cycle'] = cycle
    # pprint(dump(cycle))
    #
    # class CycleTuple(NamedTuple):
    #     cycle: List
    #
    # cycle2 = CycleTuple([])
    # cycle2.cycle.append(cycle2)
    # pprint(dump(cycle2))
    #
    # @dataclass
    # class CycleDataclass:
    #     cycle: 'CycleDataclass'
    #
    # cycle3 = CycleDataclass(None)
    # cycle3.cycle = cycle3
    # pprint(dump(cycle3))
    #
    # # cycle4 = []
    # # cycle4.append(cycle4)
    # # pprint(dump(cycle4))
    #
    # pprint(dump(['', '', '', '']))

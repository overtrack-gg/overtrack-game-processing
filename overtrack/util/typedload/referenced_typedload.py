from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import itertools
from dataclasses import _MISSING_TYPE, dataclass, field, fields, is_dataclass

from overtrack.util.typedload import Dumper, Loader

try:
    from typing import ForwardRef
except ImportError:
    from typing import _ForwardRef as ForwardRef

T = TypeVar('T')


def referenced_dump(value: object, ignore_default: bool = True, numpy_support: bool = False) -> Dict[str, Any]:
    return ReferencedDumper(ignore_default=ignore_default, numpy_support=numpy_support).dump(value)


dump = referenced_dump


def referenced_load(value: Any, type_: Type[T]) -> T:
    return ReferencedLoader().load(value, type_)


load = referenced_load


@dataclass
class _DepthCount:
    value: int


@dataclass
class Pointer:
    to: Any
    key: Union[str, int]
    from_: Union[dict, list]
    trace: List[Union[str, int]] = field(default_factory=list)


class ReferencedDumper(Dumper):

    def __init__(self, equality_is_identity: bool = True, **kwargs: Any):
        super().__init__(**kwargs)

        self.pointers: Dict[id, Pointer] = {}

    def _dicthash(self, o) -> int:
        if isinstance(o, dict):
            return hash(frozenset({
                k: self._dicthash(v)
                for k, v in o.items()
            }.items()))
        elif isinstance(o, list):
            return hash(tuple([self._dicthash(e) for e in o]))
        else:
            return hash(o)

    def dump(self, value: Any, *args) -> Any:
        outer_result = {}
        queue = [Pointer(value, 'return', outer_result)]
        dumped: Dict[int, dict] = {}
        ids = itertools.count()
        dumper = Dumper(numpy_support=self.numpy_support)
        dumper._dispatch = self._dispatch
        while queue:
            pointer = queue.pop(0)
            if id(pointer.to) in dumped:
                existing_dump = dumped[id(pointer.to)]
                if '_id' not in existing_dump:
                    existing_dump['_id'] = next(ids)
                pointer.from_[pointer.key] = {'_ref': existing_dump['_id']}
            elif is_dataclass(pointer.to):
                result = {}
                dumped[id(pointer.to)] = result
                for f in fields(pointer.to):
                    queue.append(Pointer(getattr(pointer.to, f.name), f.name, result, pointer.trace + [f.name]))
                pointer.from_[pointer.key] = result
            elif self._is_dict(pointer.to):
                result = {}
                dumped[id(pointer.to)] = result
                for k, v in pointer.to.items():
                    queue.append(Pointer(pointer.to[k], k, result, pointer.trace + [k]))
                pointer.from_[pointer.key] = result
            elif self._is_basic_type(pointer.to):
                # have to do strings before sequences
                pointer.from_[pointer.key] = dumper.dump(pointer.to, *args)
            elif self._is_sequence(pointer.to):
                result = [None for _ in pointer.to]
                for i, v in enumerate(pointer.to):
                    queue.append(Pointer(v, i, result, pointer.trace + [i]))
                pointer.from_[pointer.key] = result
            else:
                pointer.from_[pointer.key] = dumper.dump(pointer.to, *args)

        return outer_result['return']


class ReferencedLoader(Loader):
    _dispatch = Loader._dispatch.copy()

    def __init__(self, forward_refs: Dict[str, Type] = None):
        self.referenced: Dict[int, Any] = {}
        self.types: Dict[str, Type] = dict(forward_refs or {})

    def load(self, value: Any, type_: Type[T], push_key: Optional[str] = None, _stack=[]) -> T:
        if isinstance(value, dict) and (is_dataclass(type_) or type(type_) == ForwardRef):
            if '_id' in value:
                id_ = value['_id']

                # Copy the dict so we don't erase _id from the source data
                value = dict(value)
                del value['_id']

                if is_dataclass(type_):
                    # save the type in case it appears as a ForwardRef - this is often the case for recursive structures
                    self.types[type_.__name__] = type_
                else:
                    type_ = self.types[type_.__forward_arg__]

                # Create the dataclass and add it to referenced before deserializing its fields
                # this allows us to build recursive structures without recursing infinitely
                # noinspection PyArgumentList
                result = type_.__new__(type_)
                self.referenced[id_] = result

                try:
                    self._populate_dataclass(result, value, type_)
                except TypeError as e:
                    del self.referenced[id_]
                    raise e

                return result
            elif '_ref' in value:
                ref = value['_ref']
                return self.referenced[ref]

        return super().load(value, type_, push_key, _stack)

    def _populate_dataclass(self, result: Any, value: Dict[str, Any], type_: Type) -> Any:
        # populate (and load) fields with _id fields first in case one field references another e.g. {'a': {'_ref': 1}, 'b': {'_id': 1}}
        fields_ordered = sorted(
            fields(type_),
            key=lambda f: isinstance(value.get(f.name, None), dict) and '_id' in value[f.name],
            reverse=True
        )
        for f in fields_ordered:
            if f.name in value:
                # object.__setattr__ over setattr to bypass frozen check
                object.__setattr__(result, f.name, self.load(value[f.name], f.type, f'.{f.name}'))
            elif type(f.default) != _MISSING_TYPE:
                object.__setattr__(result, f.name, f.default)
            elif type(f.default_factory) != _MISSING_TYPE:
                object.__setattr__(result, f.name, f.default_factory())
            else:
                raise TypeError(f'Could not load {type_} from provided fields {value.keys()!r} - missing non-default {f.name}')
        return result

if __name__ == '__main__':
    def make_foo():
        @dataclass
        class Foo:
            a: int
        return Foo

    Foo = make_foo()


    @dataclass
    class Bar:
        foo1: Foo
        foo2: Foo
        foo3: Foo
        bar: Optional['Bar'] = None
        bars: Optional[List['Bar']] = None

        id: int = 0

        def __repr__(self) -> str:
            return f'Bar(' \
                   f'.id={id(self)}, ' \
                   f'foo1={self.foo1}, ' \
                   f'foo2={self.foo2}, ' \
                   f'foo3={self.foo3}, ' \
                   f'bar={f"Bar(.id={id(self.bar)}" if self.bar else None}, ' \
                   f'bars={[f"Bar(.id={id(bar)}" for bar in self.bars]}' \
                   f')'

        __str__ = __repr__

    foo = Foo(1)
    bar = Bar(
        foo,
        foo,
        Foo(1)
    )
    bar.bar = bar

    bar2 = Bar(foo, Foo(2), Foo(2), bar, [bar])
    bar2.bars.append(bar2)
    bar.bars = [bar2, bar2, bar]

    # print(bar)
    # print(bar.bars[1])

    bardata = referenced_dump(bar)
    print(bardata)
    #
    # dbar = referenced_load(bardata, Bar)
    # print(dbar)
    # print(dbar.bars[1])


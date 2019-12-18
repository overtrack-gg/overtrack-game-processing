from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, Type, TypeVar

import itertools
from dataclasses import dataclass, fields, is_dataclass, _MISSING_TYPE

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


class ReferencedDumper(Dumper):

    def __init__(self, equality_is_identity: bool = True, **kwargs: Any):
        super().__init__(**kwargs)
        self.equality_is_identity = equality_is_identity

        self.referenced: Dict[int, Dict] = {}
        self.ref_to_id: Dict[int, int] = {}
        self.ids_referenced_to: Set[int] = set()

        self.visited = set()

        self._to_resolve: List[Dict] = []

        self.equal: Dict[int, List[Tuple[Dict, int]]] = defaultdict(list)

        self.idgen = iter(itertools.count())

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

    def dump(self, value: Any, _depth=_DepthCount(0)) -> Any:
        _depth.value += 1

        ref = id(value)
        if ref in self.ref_to_id:
            self.ids_referenced_to.add(ref)
            result = {'_ref': self.ref_to_id[ref]}
        else:
            if ref in self.visited and self._is_dataclass(value):
                # `value` has already been visited, but may not have finished serializing (i.e. may be further up the call stack).
                # add a "recursive ref" that needs to be resolved to an ID once it has finished serializing
                self.ids_referenced_to.add(ref)
                result = {'_recursive_ref': ref}
                self._to_resolve.append(result)
            else:
                self.visited.add(ref)
                result = super().dump(value)

                if isinstance(result, dict):
                    if self.equality_is_identity:
                        result_hash = self._dicthash(result)
                        if result_hash in self.equal:
                            bucket = self.equal[result_hash]
                            # bucket contains a list of (dump(value), id(value)) for all previously dumpy values
                            # where _dicthash(dump(value)) == _dicthash(dump(previously_dumped_value))
                            for previously_dumped_result, ref in bucket:
                                if previously_dumped_result == result:
                                    # we have found the ref (and the dump(other_value)) of an other_value that dumps to the same as value
                                    self.ids_referenced_to.add(ref)
                                    result = {'_ref': self.ref_to_id[ref]}
                                    break
                        else:
                            self.equal[result_hash].append((result, ref))

                    if '_ref' not in result:
                        self.ref_to_id[ref] = next(self.idgen)
                        self.referenced[ref] = result

        _depth.value -= 1

        if _depth.value == 0:

            for referred_result in self._to_resolve:
                recursive_ref: int = referred_result['_recursive_ref']
                referred_result.clear()
                referred_result['_ref'] = self.ref_to_id[recursive_ref]

            # add '_id's for items that have been 'ref'd to
            for ref in self.ids_referenced_to:
                referenced = self.referenced[ref]
                if not isinstance(referenced, dict):
                    raise ValueError(f'Cannot dump a {type(referenced)}, id={id(referenced)} containing itself ({referenced})')
                referenced['_id'] = self.ref_to_id[ref]

        return result


class ReferencedLoader(Loader):

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

        def __repr__(self):
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

    print(bar)
    print(bar.bars[1])

    bardata = referenced_dump(bar)
    print(bardata)

    dbar = referenced_load(bardata, Bar)
    print(dbar)
    print(dbar.bars[1])


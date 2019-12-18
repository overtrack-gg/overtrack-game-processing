"""

Inspired by https://github.com/ltworf/typedload but written from scratch with the following improvements:
- Smaller (6 lines to load dataclass instead of 66)
- Correct handling of ClassVar in dataclasses (i.e. does not attempt to dump them)
- Can handle loading dataclasses that provide their own __init__ and __post_init__ methods
- Provides a "field" trace when a type fails to load


"""

import collections
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, TypeVar, Union

from dataclasses import Field, _MISSING_TYPE, dataclass, fields, is_dataclass

T = TypeVar('T')

def dump(value: object, ignore_default: bool = True, numpy_support: bool = False) -> Dict[str, Any]:
    return Dumper(ignore_default=ignore_default, numpy_support=numpy_support).dump(value)

def load(value: Any, type_: Type[T]) -> T:
    return Loader().load(value, type_)


class TypedDumpError(ValueError):
    pass


class Dumper:
    _dispatch = []

    def __init__(self, ignore_default: bool = True, numpy_support: bool = False):
        self.ignore_default = ignore_default
        self.numpy_support = numpy_support

    def dump(self, value) -> Dict[str, Any]:
        for check_value, dump_value in self._dispatch:
            if check_value(self, value):
                return dump_value(self, value)
        else:
            raise TypedDumpError(f"Don't know how to dump {type(value)}")

    def dump_dict(self, value: Dict[Any, Any], field_defaults: Optional[Dict[str, Any]] = None) -> Dict[Any, Any]:
        return {
            self.dump(k): self.dump(v)
            for k, v in value.items()
            if not self.ignore_default or not field_defaults or k not in field_defaults or field_defaults[k] != v
        }

    # -- Dispatch methods --

    def _is_basic_type(self, value) -> bool:
        return type(value) in [int, bool, float, str, type(None)]
    def _dump_basic_type(self, value) -> Any:
        return value
    _dispatch.append((
        _is_basic_type,
        _dump_basic_type
    ))

    def _is_dict(self, value) -> bool:
        return isinstance(value, dict)
    def _dump_dict(self, value: Dict[Any, Any]) -> Dict[Any, Any]:
        return self.dump_dict(value)

    _dispatch.append((
        _is_dict,
        _dump_dict
    ))

    # We want to dump named tuples as tuples (->sequences->lists) not dicts
    # def _is_named_tuple(self, value) -> bool:
    #     return isinstance(value, tuple) and hasattr(value, '_fields') and hasattr(value, '_asdict')
    # def _dump_named_tuple(self, value: NamedTuple) -> Dict[str, Any]:
    #     return self._dump_dict(value._asdict(), getattr(value, '_field_defaults', {}))
    # _dispatch.append((
    #     _is_named_tuple,
    #     _dump_named_tuple
    # ))

    def _is_numpy_scalar(self, value) -> bool:
        if self.numpy_support:
            import numpy as np
            return np.isscalar(value)
        return False
    def _dump_numpy_scalar(self, value) -> Any:
        return value.item()
    _dispatch.append((
        _is_numpy_scalar,
        _dump_numpy_scalar
    ))

    def _is_sequence(self, value) -> bool:
        return isinstance(value, collections.Sequence)
    def _dump_sequence(self, value: Sequence[Any]) -> List[Any]:
        return [self.dump(e) for e in value]
    _dispatch.append((
        _is_sequence,
        _dump_sequence
    ))

    def _is_dataclass(self, value) -> bool:
        return is_dataclass(value)
    def _dump_dataclass(self, value) -> Dict[str, Any]:
        f: Field
        field_defaults = {
            f.name: f.default
            for f in fields(value)
            if not isinstance(f.default, _MISSING_TYPE)
        }
        # TODO: check f.default_factory

        # Note: dataclasses.asdict doesn't work with NamedTuples inside dataclasses
        return self.dump_dict(
            {
                f.name: getattr(value, f.name)
                for f in fields(value)
            },
            field_defaults
        )
    _dispatch.append((
        _is_dataclass,
        _dump_dataclass
    ))


class TypedLoadError(ValueError):
    pass


def _is_type(type_: Type, basic_type, hinting_type):
    return getattr(type_, '__origin__', None) in (basic_type, hinting_type) or getattr(type_, '__extra__', None) == basic_type


class Loader:
    _dispatch = []

    def load(self, value: Any, type_: Type[T], push_key: Optional[str] = None, _stack=[]) -> T:
        if push_key:
            _stack.append(push_key)
        result = None
        try:
            for check_type, load_value in self._dispatch:
                if check_type(self, type_):
                    result = load_value(self, value, type_)
                    break
            else:
                raise TypedLoadError(
                    f"Don't know how to load {type_}\n"
                    f"Field trace: <base>{''.join(_stack)}\n"
                )
        except (AttributeError, TypeError) as e:
            raise TypedLoadError(
                f"Failed to load {type_} from value {value!r}\n"
                f"Field trace: <base>{''.join(_stack)}\n"
            ) from e
        if push_key:
            _stack.pop()
        return result

    # -- Dispatch methods --

    def _check_any(self, type_) -> bool:
        return type_ == Any
    def _load_any(self, value, type_) -> Any:
        return value
    _dispatch.append((
        _check_any,
        _load_any
    ))

    def _check_union(self, type_) -> bool:
        return getattr(type_, '__origin__', None) == Union
    def _load_union(self, value, type_) -> Any:
        exceptions = []
        for t_ in type_.__args__:
            try:
                return self.load(value, t_)
            except (TypeError, AttributeError, TypedLoadError) as e:
                exceptions.append(e)
        raise TypeError(f'Could not load {type_} from value {value!r}')
    _dispatch.append((
        _check_union,
        _load_union
    ))

    def _check_none_type(self, type_: Type) -> bool:
        return type_ == type(None)
    def _load_none_type(self, value: None, type_: Type) -> None:
        if value is not None:
            raise TypeError(f'Could not load {type_} from {value!r}')
        return None
    _dispatch.append((
        _check_none_type,
        _load_none_type
    ))

    def _check_basic_type(self, type_: Type) -> bool:
        return type_ in [int, bool, float, str, type(None)]
    def _load_basic_type(self, value: Any, type_: Type[T]) -> T:
        if not isinstance(value, type_) and not (type_ == int and type(value) == float) and not (type_ == float and type(value) == int):
            raise TypeError(f'Could not load {type_} from {value!r}')
        return type_(value)
    _dispatch.append((
        _check_basic_type,
        _load_basic_type
    ))

    def _check_dict(self, type_: Type) -> bool:
        return _is_type(type_, dict, Dict)
    def _load_dict(self, value: Dict[Any, Any], type_: Type[T]) -> T:
        if not isinstance(value, dict):
            raise TypeError(f'Could not load {type_} from value {value!r}')
        try:
            k_type, v_type = type_.args
        except:
            k_type = v_type = Any
        return {
            self.load(k, k_type): self.load(v, v_type, f'["{repr(k)}"]')
            for k, v in value.items()
        }
    _dispatch.append((
        _check_dict,
        _load_dict
    ))

    def _check_list(self, type_: Type) -> bool:
        return _is_type(type_, list, List)
    def _load_list(self, value: List[Any], type_: Type[T]) -> T:
        if not isinstance(value, list):
            raise TypeError(f'Could not load {type_} from value {value!r}')
        e_type = type_.__args__[0]
        return [
            self.load(e, e_type, f'[{i}]')
            for i, e in enumerate(value)
        ]
    _dispatch.append((
        _check_list,
        _load_list
    ))

    def _check_tuple(self, type_: Type) -> bool:
        return _is_type(type_, tuple, Tuple)
    def _load_tuple(self, value: List[Any], type_: Type[T]) -> T:
        if not isinstance(value, list):
            raise TypeError(f'Could not load {type_} from value {value!r}')
        if len(type_.__args__) == 2 and type_.__args__[1] == Ellipsis:
            # varardic tuple
            return tuple([
                self.load(e, type_.__args__[0], f'[{i}]')
                for i, e in enumerate(value)
            ])
        else:
            return tuple([
                self.load(e, t_, f'[{i}]')
                for i, (e, t_) in enumerate(zip(value, type_.__args__))
            ])
    _dispatch.append((
        _check_tuple,
        _load_tuple
    ))

    def _check_namedtuple(self, type_: Type) -> bool:
        return not _is_type(type_, tuple, Tuple) and issubclass(type_, tuple)
    def _load_namedtuple(self, value: List[Any], type_: Type[T]) -> T:
        if not isinstance(value, list):
            raise TypeError(f'Could not load {type_} from value {value!r}')
        return type_(*[
            self.load(e, t_, f'.{name}')
            for e, (name, t_) in zip(value, type_._field_types.items())
        ])
    _dispatch.append((
        _check_namedtuple,
        _load_namedtuple
    ))

    def _check_dataclass(self, type_) -> bool:
        return is_dataclass(type_)
    def _populate_dataclass(self, result: Any, value: Dict[str, Any], type_: Type) -> Any:
        for f in fields(type_):
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
    def _load_dataclass(self, value: Dict[str, Any], type_: Type) -> Any:
        if not isinstance(value, dict):
            raise TypeError(f'Could not load {type_} from value {value!r}')
        return self._populate_dataclass(type_.__new__(type_), value, type_)

    _dispatch.append((
        _check_dataclass,
        _load_dataclass
    ))


def main() -> None:
    @dataclass
    class Foo:
        a: int
        b: int
        c: Tuple[int, str]
        d: Dict[str, str]
        e: Dict
        f: Optional[str]
        g: Optional[Dict]
        h: Optional[int] = None

    foo = Foo(
        1,
        2,
        c=(1, 'a'),
        d={
            'abc': 'def'
        },
        e={},
        f='str',
        g=None,
    )
    from overtrack.util.prettyprint import pprint

    data = dump(foo)
    pprint(data)
    foo2 = load(data, Foo)

    pprint(foo)
    pprint(foo2)


if __name__ == '__main__':
    main()

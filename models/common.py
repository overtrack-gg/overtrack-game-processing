from typing import Iterable, TypeVar, Generic, TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Protocol

from pynamodb.attributes import ListAttribute, MapAttribute, NumberAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.models import Model


class TupleAttribute(ListAttribute):
    def __init__(self, length=None, hash_key=False, range_key=False, null=None, default=None, attr_name=None):
        super(TupleAttribute, self).__init__(hash_key=hash_key,
                                             range_key=range_key,
                                             null=null,
                                             default=default,
                                             attr_name=attr_name)
        self.length = length
        if self.default is not None and not isinstance(self.default, tuple):
            raise TypeError('Default value must be a tuple')

    def serialize(self, values):
        if self.length is not None and len(values) != self.length:
            raise TypeError('Expected tuple of length %d but had %d' % (self.length, len(values)))
        return super(TupleAttribute, self).serialize(values)

    def deserialize(self, value):
        if value is None:
            if self.null:
                return self.default
            else:
                raise TypeError('Got None but null=False')
        else:
            result = super(TupleAttribute, self).deserialize(value)
            if self.length is not None and len(result) != self.length:
                raise TypeError('Expected tuple of length %d but had %d' % (self.length, len(result)))
            return tuple(result)


# noinspection PyAbstractClass,PyUnresolvedReferences
class OverTrackModel(Model):
    def __str__(self):
        attributes = list(self._attributes.keys())
        # make `key` the first item
        key_names = [k for k, v in self._attributes.items() if v.is_hash_key]
        if len(key_names):
            key_name = key_names[0]
            attributes.remove(key_name)
            attributes.insert(0, key_name)
        items_str = ', '.join('%s=%s' % (attr, repr(getattr(self, attr))) for attr in attributes)
        return self.__class__.__name__ + '(' + items_str + ')'

    def asdict(self):
        attributes = list(self._attributes.keys())
        # make `key` the first item
        key_names = [k for k, v in self._attributes.items() if v.is_hash_key]
        if len(key_names):
            key_name = key_names[0]
            attributes.remove(key_name)
            attributes.insert(0, key_name)
        attrs = {
            attr: getattr(self, attr) for attr in attributes
        }
        return {
            k: OverTrackModel.asdict(v) if isinstance(v, MapAttribute) else v for k, v in attrs.items()
        }

    def refresh(self, consistent_read=False):
        # Fix for https://github.com/pynamodb/PynamoDB/issues/424
        # Only works on models with no range key

        hash_key_field = [k for k, v in self._attributes.items() if v.is_hash_key][0]
        assert len([k for k, v in self._attributes.items() if v.is_range_key]) == 0
        fresh = self.__class__.get(getattr(self, hash_key_field))

        for k in self._attributes:
            setattr(self, k, getattr(fresh, k))


T = TypeVar('T', bound=Model, covariant=True)

if TYPE_CHECKING:

    class UserIDIndexBase(Protocol, Generic[T]):
        def query(self, user_id: int, *args, **kwargs) -> Iterable[T]:
            ...

        def count(self, user_id: int, *args, **kwargs) -> int:
            ...
else:
    class UserIDIndexBase(Generic[T]):
        pass


def make_user_id_index():
    class UserIDIndex(GlobalSecondaryIndex):
        class Meta:
            index_name = 'user_id_index'
            projection = AllProjection()
            read_capacity_units = 1
            write_capacity_units = 1

        user_id = NumberAttribute(attr_name='user_id', hash_key=True)

        def query(self, user_id: int, *args, **kwargs):
            return super(UserIDIndex, self).query(user_id, *args, **kwargs)

        def count(self, user_id: int, *args, **kwargs) -> int:
            return super(UserIDIndex, self).count(user_id, *args, **kwargs)

    return UserIDIndex()


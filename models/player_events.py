import datetime
import os
from typing import Any, Iterable, no_type_check

from pynamodb.attributes import BooleanAttribute, JSONAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex, KeysOnlyProjection
from pynamodb.models import Model


class UserIDTimeIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user_id_time_index'
        projection = AllProjection()  # TODO: try with KeysOnlyProjection then fetch each from its key
        read_capacity_units = 1
        write_capacity_units = 1

    user_id = NumberAttribute(attr_name='user_id', hash_key=True)
    time = NumberAttribute(attr_name='time', range_key=True)

    @no_type_check
    def query(self, hash_key: str, *args: Any, newest_first: bool = False, **kwargs: Any) -> Iterable['PlayerEvent']:
        if newest_first is not None:
            kwargs['scan_index_forward'] = not newest_first
        return super(UserIDTimeIndex, self).query(hash_key, *args, **kwargs)


class GameKeyIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'game_key_index'
        projection = KeysOnlyProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    game_key = UnicodeAttribute(attr_name='game_key', hash_key=True)


class PlayerEvent(Model):
    class Meta:
        table_name = os.environ.get('PLAYER_EVENT_TABLE', 'overtrack_player_events')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_time_index = UserIDTimeIndex()
    game_key_index = GameKeyIndex()

    key = UnicodeAttribute(hash_key=True)

    user_id = NumberAttribute()
    time = NumberAttribute()

    public = BooleanAttribute(default=False)

    game_key = UnicodeAttribute()

    player = UnicodeAttribute()
    map = UnicodeAttribute()
    mode = UnicodeAttribute()

    hero = UnicodeAttribute()
    other_hero = UnicodeAttribute(null=True)
    type = UnicodeAttribute()
    data = JSONAttribute()

    video = JSONAttribute()

    @property
    def timestamp(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.time)

    def __str__(self) -> str:
        return f'PlayerEvent(key={self.key}, type={self.type}, other_hero={self.other_hero})'

    __repr__ = __str__

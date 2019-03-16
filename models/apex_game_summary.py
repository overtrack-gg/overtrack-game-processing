import datetime
import os
from typing import Any, Iterable, Optional, TYPE_CHECKING, no_type_check

from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

from models.common import TupleAttribute

if TYPE_CHECKING:
    from overtrack.apex.collect.apex_game import ApexGame
    from overtrack.apex.data import Champion


class UserIDTimeIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user_id_time_index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    user_id = NumberAttribute(attr_name='user_id', hash_key=True)
    time = NumberAttribute(attr_name='timestamp', range_key=True)

    @no_type_check
    def query(self, hash_key: str, *args: Any, newest_first: bool = False, **kwargs: Any) -> Iterable['ApexGameSummary']:
        if newest_first is not None:
            kwargs['scan_index_forward'] = not newest_first
        return super(UserIDTimeIndex, self).query(hash_key, *args, **kwargs)


# class Weapon(MapAttribute):
#     name: UnicodeAttribute()


class ApexGameSummary(Model):
    class Meta:
        table_name = os.environ.get('APEX_GAME_TABLE', 'overtrack_apex_games')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_time_index = UserIDTimeIndex()

    key = UnicodeAttribute(hash_key=True)
    user_id = NumberAttribute()

    timestamp = NumberAttribute()
    duration = NumberAttribute()
    champion = UnicodeAttribute(null=True)
    squadmates = TupleAttribute(2)
    kills = NumberAttribute()
    placed = NumberAttribute()
    landed = UnicodeAttribute(null=True)
    # weapons = ListAttribute(of=Weapon)

    @classmethod
    def create(cls, game: 'ApexGame', user_id: int) -> 'ApexGameSummary':
        def champion_name(c: Optional['Champion']) -> Optional[str]:
            if c:
                return c.name.lower()
            else:
                return None
        return cls(
            key=game.key,
            user_id=user_id,

            timestamp=game.timestamp,
            duration=game.duration,
            champion=champion_name(game.squad.champion),
            squadmates=(champion_name(game.squad.squadmates[0]), champion_name(game.squad.squadmates[1])),
            kills=game.kills,
            placed=game.placed,
            landed=game.route.landed_name
        )

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp)

    def __str__(self) -> str:
        return f'ApexGameSummary(key={self.key}, time={self.timestamp})'

    __repr__ = __str__

import datetime
import os
from typing import Any, Iterable, TYPE_CHECKING, no_type_check, Optional

from pynamodb.attributes import NumberAttribute, UnicodeAttribute, BooleanAttribute, MapAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

from models.common import TupleAttribute, OverTrackModel

if TYPE_CHECKING:
    from overtrack.apex.collect.apex_game import ApexGame


class UserIDTimeIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user_id_time_index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    user_id = NumberAttribute(attr_name='user_id', hash_key=True)
    timestamp = NumberAttribute(attr_name='timestamp', range_key=True)

    @no_type_check
    def query(self, hash_key: str, *args: Any, newest_first: bool = False, **kwargs: Any) -> Iterable['ApexGameSummary']:
        if newest_first is not None:
            kwargs['scan_index_forward'] = not newest_first
        return super(UserIDTimeIndex, self).query(hash_key, *args, **kwargs)


class SeasonTimestampIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'season-timestamp-index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    season = NumberAttribute(attr_name='season', hash_key=True)
    timestamp = NumberAttribute(attr_name='timestamp', range_key=True)


# class Weapon(MapAttribute):
#     name: UnicodeAttribute()

class Rank(MapAttribute):
    rank = UnicodeAttribute()
    tier = UnicodeAttribute(null=True)
    rp = NumberAttribute(null=True)
    rp_change = NumberAttribute(null=True)

    def __str__(self) -> str:
        return OverTrackModel.__str__(self)

    __repr__ = __str__


class ApexGameSummary(OverTrackModel):
    class Meta:
        table_name = os.environ.get('APEX_GAME_TABLE', 'overtrack_apex_games')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_time_index = UserIDTimeIndex()
    season_timestamp_index = SeasonTimestampIndex()

    key = UnicodeAttribute(hash_key=True)
    user_id = NumberAttribute()
    source = UnicodeAttribute(null=True)
    frames_uri = UnicodeAttribute(null=True)

    season = NumberAttribute(default=0)

    timestamp = NumberAttribute()
    duration = NumberAttribute()
    champion = UnicodeAttribute(null=True)
    squadmates = TupleAttribute(2)
    kills = NumberAttribute()
    knockdowns = NumberAttribute(null=True)
    placed = NumberAttribute()
    landed = UnicodeAttribute(null=True)
    squad_kills = NumberAttribute(null=True)
    # weapons = ListAttribute(of=Weapon)
    rank = Rank(null=True)

    url = UnicodeAttribute(null=True)

    @classmethod
    def create(
            cls,
            game: 'ApexGame',
            user_id: int,
            url: Optional[str] = None,
            frames_uri: Optional[str] = None,
            source: Optional[str] = None) -> 'ApexGameSummary':
        if game.rank:
            rank = Rank(rank=game.rank.rank, tier=game.rank.rank_tier, rp=game.rank.rp, rp_change=game.rank.rp_change)
        else:
            rank = None

        return cls(
            key=game.key,
            user_id=user_id,
            source=source,
            frames_uri=frames_uri,

            season=game.season,

            timestamp=game.timestamp,
            duration=game.duration,
            champion=game.squad.player.champion,
            squadmates=(
                game.squad.squadmates[0].champion if game.squad.squadmates[0] else None,
                game.squad.squadmates[1].champion if game.squad.squadmates[1] else None
            ),
            kills=game.kills,
            knockdowns=len(game.combat.knockdowns),
            placed=game.placed,
            landed=game.route.landed_name,
            squad_kills=game.squad.squad_kills,
            rank=rank,

            url=url
        )

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp)

    def __str__(self) -> str:
        return f'ApexGameSummary(key={self.key}, time={self.time}, placed={self.placed}, url={self.url})'

    __repr__ = __str__


def main() -> None:
    import time

    c = ApexGameSummary.season_time_index.count(2, ApexGameSummary.timestamp > time.time() - 24 * 60 * 60)
    print(c)


if __name__ == '__main__':
    main()

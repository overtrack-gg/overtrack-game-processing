import datetime

from pynamodb.attributes import NumberAttribute, UnicodeAttribute, JSONAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from models.common import OverTrackModel


class UserIDTimestampIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user_id-timestamp-index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    user_id = NumberAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)


class HeroTimestampIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'hero-timestamp-index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    hero = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)


class OverwatchHeroStats(OverTrackModel):
    class Meta:
        table_name = 'overtrack-hero-stats-2'
        region = 'us-west-2'

    user_id_timestamp_index = UserIDTimestampIndex()
    hero_timestamp_index = HeroTimestampIndex()

    user_id = NumberAttribute(hash_key=True)
    timestamp_hero = UnicodeAttribute(range_key=True)

    timestamp = NumberAttribute()
    season = NumberAttribute()

    hero = UnicodeAttribute()
    account = UnicodeAttribute()
    role = UnicodeAttribute(null=True)

    sr = NumberAttribute(null=True)
    rank = UnicodeAttribute(null=True)

    game_key = UnicodeAttribute()
    game_result = UnicodeAttribute()
    competitive = BooleanAttribute()
    custom_game = BooleanAttribute()
    map_name = UnicodeAttribute()
    map_type = UnicodeAttribute()

    time_played = NumberAttribute()
    from_endgame = BooleanAttribute()

    eliminations = NumberAttribute()
    objective_kills = NumberAttribute()
    objective_time = NumberAttribute()
    hero_damage_done = NumberAttribute()
    healing_done = NumberAttribute()
    deaths = NumberAttribute()
    final_blows = NumberAttribute()

    hero_specific_stats = JSONAttribute(null=True)

    def __init__(self, user_id: int, timestamp: float, hero: str, **kwargs):
        kwargs['timestamp_hero'] = (
            datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S') +
            '/' +
            hero
        )
        super().__init__(user_id=user_id, timestamp=timestamp, hero=hero, **kwargs)


def main() -> None:
    from tqdm import tqdm
    for e in tqdm(OverwatchHeroStats.scan(OverwatchHeroStats.time_played > 1e5)):
        print(e.game_key, e.time_played)
        e.delete()


if __name__ == '__main__':
    main()

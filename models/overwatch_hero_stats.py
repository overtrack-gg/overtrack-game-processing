import datetime

from pynamodb.attributes import NumberAttribute, UnicodeAttribute, JSONAttribute, BooleanAttribute

from models.common import OverTrackModel


class OverwatchHeroStats(OverTrackModel):
    class Meta:
        table_name = 'overtrack-hero-stats-2'
        region = 'us-west-2'

    user_id = NumberAttribute(hash_key=True)
    timestamp_hero = UnicodeAttribute(range_key=True)

    timestamp = NumberAttribute()
    season = NumberAttribute()

    hero = UnicodeAttribute()
    account = UnicodeAttribute()
    role = UnicodeAttribute()

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

    hero_specific_stats = JSONAttribute(null=True)

    def __init__(self, user_id: int, timestamp: float, hero: str, **kwargs):
        kwargs['timestamp_hero'] = (
            datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S') +
            '/' +
            hero
        )
        super().__init__(user_id=user_id, timestamp=timestamp, hero=hero, **kwargs)


def main() -> None:
    OverwatchHeroStats.create_table(wait=True, read_capacity_units=1, write_capacity_units=1)


if __name__ == '__main__':
    main()

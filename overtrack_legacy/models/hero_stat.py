import boto3
import os

from decimal import Decimal
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute

try:
    from .util import OverTrackModel, TupleAttribute
except SystemError:
    from util import OverTrackModel, TupleAttribute
from log_config import logger

dynamodb = boto3.resource('dynamodb')


def HeroStatIndex(index_name, attr_type=NumberAttribute):
    class Index(GlobalSecondaryIndex):
        class Meta:
            read_capacity_units = 1
            write_capacity_units = 1
            projection = AllProjection()

    setattr(Index.Meta, 'index_name', index_name + '-index')
    setattr(Index, index_name.replace('-', '_'), attr_type(attr_name=index_name, hash_key=True))
    return Index()


# noinspection PyAbstractClass
class HeroStats(OverTrackModel):

    class Meta:
        table_name = os.environ.get('HERO_STATS_TABLE', 'overtrack_hero_stats')
        region = 'us-west-2'
        table = dynamodb.Table(table_name)

    time_bucket_index = HeroStatIndex('time-bucket')
    player_id_index = HeroStatIndex('player-id')

    key = UnicodeAttribute(attr_name='key', hash_key=True, null=False)
    map_name = UnicodeAttribute(attr_name='map-name', null=False)
    time_bucket = NumberAttribute(attr_name='time-bucket', null=False)
    hero_name = UnicodeAttribute(attr_name='hero-name', null=False)

    player_id = NumberAttribute(attr_name='player-id', null=False)
    player_name = UnicodeAttribute(attr_name='player-name', null=False)

    games_played = NumberAttribute(attr_name='games-played', null=False, default=0)
    games_won = NumberAttribute(attr_name='games-won', null=False, default=0)
    time_played = NumberAttribute(attr_name='time-played', null=False, default=0)
    sr = NumberAttribute(attr_name='sr', null=False, default=0)
    sr_games = NumberAttribute(attr_name='sr-games', null=False, default=0)

    tab_health = NumberAttribute(attr_name='tab-health', null=True)

    elims = NumberAttribute(attr_name='elims', null=False, default=0)
    damage = NumberAttribute(attr_name='damage', null=False, default=0)
    objective_kills = NumberAttribute(attr_name='objective-kills', null=False, default=0)
    healing = NumberAttribute(attr_name='healing', null=False, default=0)
    objective_time = NumberAttribute(attr_name='objective-time', null=False, default=0)
    deaths = NumberAttribute(attr_name='deaths', null=False, default=0)

    hero_stat_1 = NumberAttribute(attr_name='hero-stat-1', null=False, default=0)
    hero_stat_2 = NumberAttribute(attr_name='hero-stat-2', null=False, default=0)
    hero_stat_3 = NumberAttribute(attr_name='hero-stat-3', null=False, default=0)
    hero_stat_4 = NumberAttribute(attr_name='hero-stat-4', null=False, default=0)
    hero_stat_5 = NumberAttribute(attr_name='hero-stat-5', null=False, default=0)
    hero_stat_6 = NumberAttribute(attr_name='hero-stat-6', null=False, default=0)

    @staticmethod
    def make_key(time_bucket, map_name, hero_name, player_id, player_name):
        return '%d-%s-%s-%d-%s' % (time_bucket, map_name, hero_name, player_id, player_name)

    @classmethod
    def add(cls, time_bucket, map_name, hero_name, player_id, player_name, won, sr, **kwargs):
        """
        :type time_bucket: int
        :type map_name: str
        :type hero_name: str
        :type player_id: int
        :type player_name: str
        :type won: bool
        :type sr: int | None
        """

        key = cls.make_key(time_bucket, map_name, hero_name, player_id, player_name)
        names = {}
        values = {}
        setexpr = []
        addexpr = []
        for attr_name, attr_value in [
            ('time-bucket', time_bucket),
            ('hero-name', hero_name),
            ('player-id', player_id),
            ('player-name', player_name),
            ('map_name', map_name)
        ]:
            attrkey = attr_name.replace('-', '_')
            setexpr.append('#%s = :%s' % (attrkey, attrkey))
            names['#' + attrkey] = attr_name
            values[':' + attrkey] = attr_value

        addexpr.append('#games_played :games_played')
        names['#games_played'] = 'games-played'
        values[':games_played'] = 1

        if sr:
            addexpr.append('#sr :sr')
            names['#sr'] = 'sr'
            values[':sr'] = sr
            addexpr.append('#sr_games :sr_games')
            names['#sr_games'] = 'sr-games'
            values[':sr_games'] = 1

        if won:
            addexpr.append('#games_won :games_won')
            names['#games_won'] = 'games-won'
            values[':games_won'] = 1

        for attrkey, val in kwargs.items():
            if attrkey not in [
                'tab_health',

                'time_played',
                'elims',
                'damage',
                'objective_kills',
                'healing',
                'objective_time',
                'deaths',
                'hero_stat_1',
                'hero_stat_2',
                'hero_stat_3',
                'hero_stat_4',
                'hero_stat_5',
                'hero_stat_6'
            ]:
                raise KeyError('%r is not a valid hero stat' % (attrkey, ))
            if attrkey == 'tab_health':
                val = Decimal('%f' % val)
            elif not isinstance(val, int):
                raise TypeError('%s=%r is not an integer stat' % (attrkey, val))
            attr_name = attrkey.replace('_', '-')
            addexpr.append('#%s :%s' % (attrkey, attrkey))
            names['#' + attrkey] = attr_name
            values[':' + attrkey] = val

        expression = 'SET %s ADD %s' % (', '.join(setexpr), ', '.join(addexpr))
        logger.info('Updating hero stats for %s' % (key, ))
        cls.Meta.table.update_item(
            Key={
                'key': key
            },
            UpdateExpression=expression,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values
        )

    def to_dict(self):
        return {
            k: getattr(self, k) for k in self._attributes.keys()
        }


if __name__ == '__main__':
    for stat in HeroStats.scan():
        print(stat)

import datetime
import os
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute

from models.common import OverTrackModel, TupleAttribute


class UserIDTimeIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user-id-time-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    user_id = NumberAttribute(attr_name='user-id', hash_key=True)
    time = NumberAttribute(attr_name='time', range_key=True)

    def query(self, hash_key, *args, newest_first=True, **kwargs):
        if newest_first is not None:
            kwargs['scan_index_forward'] = not newest_first
        return super(UserIDTimeIndex, self).query(hash_key, *args, **kwargs)


class HasExceptionIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'has-exception-index'
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    exception = NumberAttribute(attr_name='has-exception', hash_key=True)


# noinspection PyAbstractClass
class OverwatchGameSummary(OverTrackModel):

    class Meta:
        table_name = os.environ.get('GAMES_TABLE', 'overtrack_games')
        region = 'us-west-2'

    user_id_time_index = UserIDTimeIndex()
    has_exception_index = HasExceptionIndex()

    key = UnicodeAttribute(attr_name='key', hash_key=True, null=False)
    user_id = NumberAttribute(attr_name='user-id')
    time = NumberAttribute(attr_name='time')
    player_name = UnicodeAttribute(attr_name='player-name')
    player_battletag = UnicodeAttribute(attr_name='player-battletag', null=True)
    log_id = TupleAttribute(attr_name='log-id', length=3, null=True, default=None)

    map = UnicodeAttribute(attr_name='map', null=True)
    heroes_played = TupleAttribute(attr_name='heroes-played', null=True, default=None)
    result = UnicodeAttribute(attr_name='result', null=True)
    score = TupleAttribute(attr_name='score', length=2, null=True, default=None)
    duration = NumberAttribute(attr_name='duration', null=True)
    start_sr = NumberAttribute(attr_name='start-sr', null=True)
    end_sr = NumberAttribute(attr_name='end-sr', null=True)
    rank = UnicodeAttribute(attr_name='rank', null=True)
    custom_game = BooleanAttribute(attr_name='custom-game', null=True)
    game_type = UnicodeAttribute(attr_name='game-type', null=True)
    edited = BooleanAttribute(attr_name='edited', null=True, default=False)
    viewable = BooleanAttribute(attr_name='viewable', null=True, default=True)

    has_exception = NumberAttribute(attr_name='has-exception', default=0)
    exception = TupleAttribute(attr_name='exception', null=True, hash_key=True)

    source = UnicodeAttribute(attr_name='source', null=True)
    stream_key = UnicodeAttribute(attr_name='stream-key', null=True)
    ingest = BooleanAttribute(attr_name='ingest', null=False, default=False)

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(self.time)

    def to_dict(self):
        data = {
            'key': self.key,
            'user_id': self.user_id,
            'time': self.time
        }
        if self.map is None:
            data.update({
                'player_name': self.player_name.upper().replace('0', 'O') if self.player_name else 'UNKNOWN',
                'parsing_failed': True
            })
        else:
            for attr in ['player_name',
                         'player_battletag',
                         'map',
                         'duration',
                         'heroes_played',
                         'result',
                         'score',
                         'start_sr',
                         'end_sr',
                         'rank',
                         'viewable'
                         ]:
                data[attr] = getattr(self, attr)
            data['custom_game'] = bool(self.custom_game)
            if self.custom_game:
                data['game_type'] = 'custom'
            else:
                data['game_type'] = self.game_type or 'competitive'

        return data



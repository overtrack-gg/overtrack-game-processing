import os
import uuid
from enum import Enum
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute, BooleanAttribute

try:
    from .util import OverTrackModel, TupleAttribute
except SystemError:
    from util import OverTrackModel, TupleAttribute


class EventType(Enum):
    DISCORD_WEBHOOK = 1
    GENERIC_WEBHOOK = 2
    TWITCH_IRC_MESSAGE = 3


class DiscordWebhook:

    TYPE = EventType.DISCORD_WEBHOOK

    def __init__(self, webhook):
        self.webhook = webhook

    @classmethod
    def load(cls, data):
        return cls(data['webhook'])

    def todict(self):
        return {
            'webhook': self.webhook
        }


class GenericWebhook(DiscordWebhook):
    TYPE = EventType.GENERIC_WEBHOOK


class TwitchIRCMessage:

    TYPE = EventType.TWITCH_IRC_MESSAGE

    def __init__(self, channel, use_game_link=True):
        self.channel = channel
        self.use_game_link = use_game_link

    @classmethod
    def load(cls, data):
        return cls(data['channel'], use_game_link=data['use_game_link'])

    def todict(self):
        return {
            'channel': self.channel,
            'use_game_link': self.use_game_link
        }


event_types = {
    EventType.DISCORD_WEBHOOK: DiscordWebhook,
    EventType.GENERIC_WEBHOOK: GenericWebhook,
    EventType.TWITCH_IRC_MESSAGE: TwitchIRCMessage
}


class UserIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user-id-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    user_id = NumberAttribute(attr_name='user-id', hash_key=True)


# noinspection PyAbstractClass
class GameProcessed(OverTrackModel):
    class Meta:
        table_name = os.environ.get('GAMES_PROCESSED_EVENTS_TABLE', 'overtrack_game_processed')
        region = 'us-west-2'

    user_id_index = UserIDIndex()

    id = UnicodeAttribute(attr_name='id', hash_key=True, null=False)
    user_id = NumberAttribute(attr_name='user-id', null=False)

    player_name_filter = TupleAttribute(attr_name='player-name-filter', null=True)
    include_customs = BooleanAttribute(attr_name='include-customs', default=False)
    event_type = UnicodeAttribute(attr_name='event-type', null=False)
    event_data = JSONAttribute(attr_name='event-data', null=False)

    @classmethod
    def create(cls, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        event = None
        if 'event' in kwargs:
            event = kwargs['event']
            del kwargs['event']
        r = cls(**kwargs)
        if event:
            r.event = event
        return r

    @property
    def event(self):
        return event_types[EventType[self.event_type.split('.')[1]]].load(self.event_data)

    @event.setter
    def event(self, value):
        self.event_type = str(value.TYPE)
        self.event_data = value.todict()


if __name__ == '__main__':

    # for n in GameProcessed.scan():
    #   # print(n.event, n.include_customs)
    #   # if type(n.event) is GenericWebhook:
    #   n.include_customs = type(n.event) is GenericWebhook
    #   n.save()

    from models.user import User

    battletag = 'Widowmaker#13427'
    url = '**REMOVED**'

    user = User.get(battletag)
    print(user)
    p = GameProcessed.create(user_id=user.user_id)
    p.event = DiscordWebhook(url)
    print(p)
    p.save()


    # channel = 'keryja'
    # user_id = 100991993
    # # names = ['kephrii'.upper()]
    # # names = ['HAWKEYE', 'JORDAN', 'ROCKET']
    # # names = list('FORAIRAN/TIGOLE/SWAHELI/SUPPORTCUCK'.upper().split('/'))
    # #
    # p = GameProcessed.create(user_id=user_id)
    # # p.player_name_filter = names
    # p.event = TwitchIRCMessage(channel)
    # print(p)
    # p.save()
    #
    # p = GameProcessed.create(user_id=user_id)
    # p.event = DiscordWebhook(url)
    # # p.player_name_filter = names
    # p.save()
    # print(p)

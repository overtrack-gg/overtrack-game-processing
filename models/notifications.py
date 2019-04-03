import os

from typing import Dict, Union, Iterable
from pynamodb.attributes import UnicodeAttribute, JSONAttribute, NumberAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from models.common import OverTrackModel


class UserIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user_id_index'
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    user_id = NumberAttribute(attr_name='user_id', hash_key=True)

    def query(self, user_id: int, *args, **kwargs) -> Iterable['DiscordBotNotification']:
        return super(UserIDIndex, self).query(user_id, *args, **kwargs)


class DiscordBotNotification(OverTrackModel):
    class Meta:
        table_name = os.environ.get('DISCORD_BOT_NOTIFICATION_TABLE', 'overtrack_discord_bot_notification')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_index = UserIDIndex()

    key = UnicodeAttribute(hash_key=True, null=False)
    user_id = NumberAttribute(null=False)

    guild_id = UnicodeAttribute(null=False)
    guild_name = UnicodeAttribute(null=False)

    channel_name = UnicodeAttribute(null=False)

    notification_data = JSONAttribute(null=False)

    @classmethod
    def create(cls,
               user_id: int,
               game: str,
               channel_id: str,
               guild_id: str,
               guild_name: str,
               channel_name: str,
               notification_data: Dict[str, object]):
        return DiscordBotNotification(
            key=f'{user_id}.{game}.{channel_id}',
            user_id=user_id,
            guild_id=guild_id,
            guild_name=guild_name,
            channel_name=channel_name,
            notification_data=notification_data
        )

    @property
    def game(self) -> str:
        return self.key.split('.')[1]

    @property
    def channel_id(self) -> str:
        return self.key.split('.')[2]


# DiscordBotNotification.create_table(read_capacity_units=1, write_capacity_units=1)

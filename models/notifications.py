import os
from typing import Dict

from pynamodb.attributes import JSONAttribute, NumberAttribute, UnicodeAttribute, BooleanAttribute

from models.common import OverTrackModel, UserIDIndexBase, make_user_id_index


class DiscordBotNotification(OverTrackModel):
    class Meta:
        table_name = os.environ.get('DISCORD_BOT_NOTIFICATION_TABLE', 'overtrack_discord_bot_notification')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_index: UserIDIndexBase['DiscordBotNotification'] = make_user_id_index()

    key = UnicodeAttribute(hash_key=True, null=False)
    user_id = NumberAttribute(null=False)
    game = UnicodeAttribute()

    guild_id = UnicodeAttribute(null=False)
    guild_name = UnicodeAttribute(null=False)

    channel_name = UnicodeAttribute(null=False)

    notification_data = JSONAttribute(null=False)

    is_parent = BooleanAttribute(default=True)
    autoapprove_children = BooleanAttribute(default=False)

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
            game=game,
            guild_id=guild_id,
            guild_name=guild_name,
            channel_name=channel_name,
            notification_data=notification_data
        )

    @property
    def channel_id(self) -> str:
        return self.key.split('.')[2]


class TwitchBotNotification(OverTrackModel):
    class Meta:
        table_name = os.environ.get('TWITCH_BOT_NOTIFICATION_TABLE', 'overtrack_twitch_bot_notification')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_index: UserIDIndexBase['TwitchBotNotification'] = make_user_id_index()
    key = UnicodeAttribute(hash_key=True, null=False)
    user_id = NumberAttribute(null=False)
    game = UnicodeAttribute()

    twitch_user_id = NumberAttribute()
    twitch_channel_name = UnicodeAttribute()

    notification_data = JSONAttribute(null=False)

    @classmethod
    def create(cls,
               user_id: int,
               game: str,
               twitch_user_id: int,
               channel_name: str,
               notification_data: Dict[str, object]):
        return TwitchBotNotification(
            key=f'{user_id}.{game}.{twitch_user_id}',
            user_id=user_id,
            game=game,
            twitch_user_id=twitch_user_id,
            twitch_channel_name=channel_name,
            notification_data=notification_data
        )

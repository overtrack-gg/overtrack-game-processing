import logging
import os
from typing import Optional, List, Dict
from pprint import pformat, pprint

import requests

from overtrack.overwatch.collect.notifications import DiscordMessage
from overtrack.util import s2ts
from overtrack_models.orm.apex_game_summary import ApexGameSummary
from overtrack_models.orm.notifications import DiscordBotNotification, TwitchBotNotification
from overtrack.apex.collect.apex_game import ApexGame
from overtrack.twitch import twitch_bot

logger = logging.getLogger(__name__)

APEX_GAMES_WEBHOOK = '***REMOVED***'


class ApexDiscordMessage(DiscordMessage):
    DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
    CHANNEL_CREATE_MESSAGE = 'https://discord.com/api/channels/%s/messages'

    IMAGE_PREFIX = 'https://cdn.overtrack.gg/static/images/apex/'

    COLOR_BASE = int('992e26', base=16)
    COLOR_3 = int('0d95ff', base=16)
    COLOR_2 = int('ef20ff', base=16)
    COLOR_1 = int('ffdf00', base=16)

    colors = {
        3: COLOR_3,
        2: COLOR_2,
        1: COLOR_1
    }

    discord_bot = requests.Session()
    discord_bot.headers.update({
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
        'User-Agent': 'OverTrack.gg API'
    })

    def __init__(self, game: ApexGame, summary: ApexGameSummary, url: str, username: Optional[str] = None):
        if username is None:
            name = game.squad.player.name
        else:
            name = username

        description = f'{summary.kills} Kills'
        if summary.knockdowns is not None:
            description += f'\n{summary.knockdowns} Knockdowns'
        if summary.squad_kills is not None:
            description += f'\n{summary.squad_kills} Squad Kills'
        if summary.landed != 'Unknown':
            description += f'\nDropped {summary.landed}'
        description += '\n'
        game_embed = {
            'author': {
                'name': 'overtrack.gg',
                'url': 'https://overtrack.gg/',
                'icon_url': 'https://overtrack.gg/favicon.png'
            },
            'color': self.colors.get(game.placed, self.COLOR_BASE),
            'title': f'{name} placed #{game.placed}',
            'url': url,
            'thumbnail': {
                'url': f'{self.IMAGE_PREFIX}{game.squad.player.champion}.png'
            },
            'description': description,
            'timestamp': game.time.strftime('%Y-%m-%d %H:%M:%S'),
            'footer': {
                'text': f'Duration {s2ts(game.duration, zpad=False)}'
            }
        }

        super().__init__(game_embed)

        logger.info(f'Prepared game embed for {self}:\n{pformat(self.game_embed)}')


class TwitchMessage:
    COLOUR_MAP = {
        1: 'Goldenrod',
        2: 'BlueViolet',
        3: 'DodgerBlue'
    }

    def __init__(self, game: ApexGame, summary: ApexGameSummary, url: str, username: Optional[str] = None):
        if username is None:
            name = game.squad.player.name
        else:
            name = username

        self.message = f'{name} just placed #{game.placed} with {game.kills} kills'
        # if placed == 1:
        #     message += ' mendoEZ'
        # elif placed == 2:
        #     message += random.choice([' mendoSip', ' mendoDab'])
        # elif placed == 3:
        #     message += random.choice([' mendoGun', ' mendoSip'])

        if game.squad:
            if game.squad.squad_kills is not None:
                self.message += f' | {game.squad.squad_kills} squad kills'
        if game.route.landed_name and game.route.landed_name != 'Unknown':
            self.message += f' | Dropped {game.route.landed_name}'
        self.message += f' | {url}'

        self.color = self.COLOUR_MAP.get(game.placed)

    def send(self, channel: str) -> None:
        twitch_bot.send_message(
            channel,
            self.message,
            colour=self.color
        )


def send_notifications(user_id: int, game: ApexGame, summary: ApexGameSummary, url: str, username: str, dev_embed: Optional[Dict]) -> None:
    discord_message = ApexDiscordMessage(game, summary, url, username)
    for discord_integration in DiscordBotNotification.user_id_index.query(user_id, DiscordBotNotification.game == 'apex'):
        top3_only = discord_integration.notification_data.get('top3_only', False)
        if top3_only and summary.placed > 3:
            logger.info(f'Not sending {summary} to {discord_integration} - has top3_only')
        elif discord_integration.announce_message_id and \
                not DiscordMessage.check_message_exists(discord_integration.channel_id, discord_integration.announce_message_id):
            logger.warning(f'Could not get announce message for {discord_integration.announce_message_id!r} - ignoring')
        else:
            discord_message.send(discord_integration.channel_id)

    logger.info(f'Sending {summary} to OverTrack#apex-games')
    if dev_embed:
        discord_message.post_to_webhook(APEX_GAMES_WEBHOOK, [dev_embed])
    else:
        discord_message.post_to_webhook(APEX_GAMES_WEBHOOK)

    for twitch_integration in TwitchBotNotification.user_id_index.query(user_id, TwitchBotNotification.game == 'apex'):
        twitch_message = TwitchMessage(game, summary, url, twitch_integration.twitch_channel_name)
        top3_only = twitch_integration.notification_data.get('top3_only', False)
        if (top3_only and summary.placed <= 3) or not top3_only:
            logger.info(f'Sending {summary} to {twitch_integration}')
            twitch_message.send(twitch_integration.twitch_channel_name)
        else:
            logger.info(f'Not sending {summary} to {twitch_integration}')

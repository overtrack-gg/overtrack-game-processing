import logging
import os
from typing import Optional, List, Dict
from pprint import pformat, pprint

import requests

from models.apex_game_summary import ApexGameSummary
from models.notifications import DiscordBotNotification
from overtrack.apex.collect.apex_game import ApexGame

logger = logging.getLogger(__name__)

APEX_GAMES_WEBHOOK = '**REMOVED**'


class DiscordMessage:
    DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
    CHANNEL_CREATE_MESSAGE = '**REMOVED**'

    GAME_PREFIX = 'https://apex-beta.overtrack.gg/game/'
    IMAGE_PREFIX = 'http://apextrack-web-poc-assets.s3-us-west-2.amazonaws.com/1/images/'

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
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
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
        self.game_embed = {
            'author': {
                'name': 'overtrack.gg',
                'url': 'https://apex-beta.overtrack.gg/',
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
                'text': f'Duration {game.duration // 60:.0f}:{game.duration % 60:.0f}'
            }
        }

        logger.info(f'Prepared game embed for {self}:\n{pformat(self.game_embed)}')

    def send(self, channel_id: str) -> bool:
        logger.info(f'Sending {self} to {channel_id}')
        try:
            create_message_r = self.discord_bot.post(
                self.CHANNEL_CREATE_MESSAGE % (channel_id,),
                json={
                    'embed': self.game_embed
                },
                timeout=10
            )
            create_message = create_message_r.json()
            print(f'Create message: {create_message_r.status_code} -> ')
            pprint(create_message)
            create_message_r.raise_for_status()
        except Exception as e:
            logger.exception(f'Failed to send discord notification')
            return False
        else:
            logger.info(f'Discord notification sent: {create_message_r.status_code} - id: {create_message["id"]}')
            return True

    def post_to_webhook(self, webhook: str, extra_embeds: Optional[List[Dict]] = None) -> bool:
        embeds = [self.game_embed]
        if extra_embeds:
            embeds += extra_embeds

        logger.info(f'Posting {self} to {webhook}')
        try:
            create_message_r = requests.post(
                webhook,
                json={
                    'username': 'OverTrack',
                    'avatar_url': 'https://overtrack.gg/assets/images/OT_logo.png',
                    'embeds': embeds
                },
                timeout=10
            )
            print(f'Create message: {create_message_r.status_code} -> ')
            pprint(create_message_r.content)
            create_message_r.raise_for_status()
        except Exception as e:
            logger.exception(f'Failed to post discord notification')
            return False
        else:
            logger.info(f'Discord notification posted: {create_message_r.status_code}')
            return True


def send_notifications(user_id: int, game: ApexGame, summary: ApexGameSummary, url: str, username: str, dev_embed: Optional[Dict]) -> None:
    message = DiscordMessage(game, summary, url, username)

    for discord_integration in DiscordBotNotification.user_id_index.query(user_id):
        top3_only = discord_integration.notification_data.get('top3_only', False)
        if (top3_only and summary.placed <= 3) or not top3_only:
            logger.info(f'Sending {summary} to {discord_integration}')
            message.send(discord_integration.channel_id)
        else:
            logger.info(f'Not sending {summary} to {discord_integration}')

    logger.info(f'Sending {summary} to OverTrack#apex-games')
    if dev_embed:
        message.post_to_webhook(APEX_GAMES_WEBHOOK, [dev_embed])
    else:
        message.post_to_webhook(APEX_GAMES_WEBHOOK)
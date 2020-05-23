import itertools
from collections import Counter

import numpy as np
import logging
import os
from typing import Optional, List, Dict
from pprint import pformat, pprint

import requests
from dataclasses import dataclass
from overtrack.valorant.collect.valorant_game import ValorantGame

from overtrack_models.orm.notifications import DiscordBotNotification, TwitchBotNotification
from overtrack.twitch import twitch_bot
from overtrack_models.orm.valorant_game_summary import ValorantGameSummary

from overtrack.overwatch.collect.notifications import DiscordMessage

logger = logging.getLogger(__name__)

VALORANT_GAMES_WEBHOOK = '**REMOVED**'


def get_values(game, username):
    name = username or game.teams.firstperson.name
    result = {
        True: 'won',
        False: 'lost',
        None: 'played'
    }[game.won]
    return name, result


class ValorantDiscordMessage(DiscordMessage):

    def __init__(self, game: ValorantGame, summary: ValorantGameSummary, url: str, username: Optional[str] = None):
        name, result = get_values(game, username)

        game_embed = {
            'author': {
                'name': 'overtrack.gg',
                'url': 'https://overtrack.gg/',
                'icon_url': 'https://overtrack.gg/favicon.png'
            },
            # 'color': self.colors.get(game.placed, self.COLOR_BASE),
            'title': f'{name} {result} on {game.map}',
            'url': url,
            # 'thumbnail': {
            #     'url': f'{self.IMAGE_PREFIX}{game.squad.player.champion}.png'
            # },
            # 'description': description,
            'timestamp': game.time.strftime('%Y-%m-%d %H:%M:%S'),
            'footer': {
                'text': f'Duration {game.duration // 60:.0f}:{game.duration % 60:.0f}'
            }
        }
        super().__init__(game_embed)


@dataclass
class ValorantTwitchMessage:
    message: str
    color: Optional[str] = None

    def __init__(self, game: ValorantGame, summary: ValorantGameSummary, url: str, username: Optional[str] = None):
        name, result = get_values(game, username)

        kills_by_round = [
            [k for k in r.kills if k.killer == game.teams.firstperson]
            for r in game.rounds
        ]
        firstbloods = [
            r.kills[0]
            for r in game.rounds
            if r.kills and r.kills[0].killer == game.teams.firstperson
        ]
        weaponcounters = Counter()
        for k in itertools.chain(*kills_by_round):
            if k.weapon:
                weaponcounters[k.weapon] += 1
        bestweap, bestweap_count = weaponcounters.most_common(1)[0]

        if game.score:
            scorestr = f'{game.score[0]}-{game.score[1]} '
        else:
            scorestr = ' '

        self.message = (
            f'{name} just {result} {scorestr}on {game.map}. '
            f'{len(game.teams.firstperson.kills)} kills, {np.mean([len(ks) for ks in kills_by_round]):.1f} kills/round, {len(firstbloods)} first bloods. '
            f'Best weapon: {bestweap.title()} with {bestweap_count} kills. Best round: {np.max([len(ks) for ks in kills_by_round])} kills'
        )
        self.color = 'Goldenrod'
        logger.info(f'Prepared {self}')

    def send(self, channel: str) -> None:
        twitch_bot.send_message(
            channel,
            self.message,
            colour=self.color
        )


def send_notifications(user_id: int, game: ValorantGame, summary: ValorantGameSummary, url: str, username: str, dev_embed: Optional[Dict]) -> None:
    discord_message = ValorantDiscordMessage(game, summary, url, username)
    for discord_integration in DiscordBotNotification.user_id_index.query(user_id, DiscordBotNotification.game == 'valorant'):
        logger.info(f'Sending {summary} to {discord_integration}')
        discord_message.send(discord_integration.channel_id)

    logger.info(f'Sending {discord_message} to OverTrack#valorant-games')
    dev_embeds = []
    if dev_embed:
        dev_embeds.append(dev_embed)
    discord_message.post_to_webhook(VALORANT_GAMES_WEBHOOK, dev_embeds)

    for twitch_integration in TwitchBotNotification.user_id_index.query(user_id, TwitchBotNotification.game == 'valorant'):
        twitch_message = ValorantTwitchMessage(game, summary, url, twitch_integration.twitch_channel_name)
        logger.info(f'Sending {twitch_message} to {twitch_integration}')
        twitch_message.send(twitch_integration.twitch_channel_name)
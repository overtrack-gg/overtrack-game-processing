import bisect
from collections import Counter

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import timedelta
from overtrack.frame import Frame
from overtrack.util import s2ts
from typing import TYPE_CHECKING, List, Dict, Union, Optional

CLIP_URL = os.environ.get(
    'CLIP_URL',
    'https://m9e3shy2el.execute-api.us-west-2.amazonaws.com/{twitch_user}/clip/{time}/{duration}?pts={pts}&title={title}'
)


logger = logging.getLogger('Clips')


if TYPE_CHECKING:
    from overtrack.valorant.collect.valorant_game import ValorantGame
    from typing import TypedDict, Literal

    class KillsMetadata(TypedDict):
        kills: int
        best_weapon: str
        best_weapon_kills: int

    ClipType = Literal['multikill']

else:
    ValorantGame = object
    KillsMetadata = Dict
    ClipType = str


@dataclass
class Clip:
    url: str
    title: str
    shorttitle: str

    type: ClipType
    metadata: Union[KillsMetadata]


async def create_clip(**kwargs) -> Optional[str]:
    import requests_async
    try:
        create_clip_r = await requests_async.get(
            CLIP_URL.format(**kwargs)
        )
        logger.info(f'{create_clip_r.url} -> {create_clip_r.status_code}')
        create_clip_r.raise_for_status()
        create_clip_r.json()
    except:
        logger.error('Got exception creating clip')
        return None
    else:
        return create_clip_r.json()['clip_url']


def make_clips(game: ValorantGame, frames: Optional[List[Frame]], twitch_username: str, minimum_kills_to_clip: int = 3) -> List[Clip]:
    desired_clips = []

    multikills = []
    multikill = []
    for k in (game.teams.firstperson.kills if game.teams.firstperson else []):
        if multikill and k.timestamp - multikill[-1].timestamp > 7:
            if len(multikill) >= 2:
                multikills.append(multikill)
            multikill = []
        multikill.append(k)
    multikills.sort(key=lambda mk: len(mk), reverse=True)

    for multikill in multikills:
        if len(multikill) < minimum_kills_to_clip:
            logger.info(f'Ignoring multikill at {s2ts(multikill[0].timestamp)}: {len(multikill)} kills is below threshold')
            continue

        logger.info(f'Clipping multikill at {s2ts(multikill[0].timestamp)}: {len(multikill)} kills')

        kills = len(multikill)
        weapons = Counter([k.weapon for k in multikill if k.weapon]).most_common()
        if len(weapons):
            best_weapon, best_weapon_kills = weapons[0]
        else:
            best_weapon, best_weapon_kills = None, 0

        if best_weapon_kills == kills:
            onlyweapon = best_weapon
        else:
            onlyweapon = None

        title = twitch_username + "'s "
        shorttitle = ''
        if onlyweapon:
            title += onlyweapon + ' '
            shorttitle += onlyweapon.title() + ' '
        title += f'{kills}K with {game.teams.firstperson.agent.title()} on {game.map.title()}'
        shorttitle += f'{kills}K'

        game_offset = multikill[0].timestamp - 5
        duration = (multikill[-1].timestamp + 5) - game_offset
        time = game.time + timedelta(seconds=game_offset)
        pts = game.start_pts + game_offset
        logger.info(
            f'  '
            f'timestamp={s2ts(multikill[0].timestamp)} ({multikill[0].timestamp:.2f}), '
            f'time={game.time + timedelta(seconds=multikill[0].timestamp)}, '
            f'pts={game.start_pts + game_offset}'
        )

        if frames:
            fts = [f.timestamp - game.timestamp for f in frames]
            frame_i = bisect.bisect_left(fts, game_offset)
            frame = frames[frame_i]
            if 'frame_info' in frames[0]:
                pts = round(frame.frame_info.pts, 2)
                logger.info(f'Overriding pts with {pts} from actual frame')

        clip_type: ClipType = 'multikill'
        clip_metadata: KillsMetadata = {
            'kill_count': kills,
            'kills': [
                (k.weapon, k.killed.agent)
                for k in multikill
            ],
            'agent': game.teams.firstperson.agent,
            'best_weapon': best_weapon,
            'best_weapon_kills': best_weapon_kills,
            'round': multikill[0].round,
            'round_timestamp': multikill[0].round_timestamp,
        }
        desired_clips.append((
            {
                'twitch_user': twitch_username,
                'time': time,
                'duration': duration,
                'pts': pts,
                'title': title.replace("'", '%27'),
            },
            title,
            shorttitle,
            clip_type,
            clip_metadata,
        ))

    logger.info(f'Async fetching {len(desired_clips)} clips')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    clip_urls = loop.run_until_complete(asyncio.gather(*[
        create_clip(**clip_data[0]) for clip_data in desired_clips
    ]))
    loop.close()
    logger.info(f'Done: {clip_urls}')

    clips = []
    for clip_data, clip_url in zip(desired_clips, clip_urls):
        clip = Clip(
            clip_url,
            *clip_data[1:],
        )
        logger.info(f'Got {clip}')
        clips.append(clip)

    return clips

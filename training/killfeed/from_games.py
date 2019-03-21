import json
import logging
import os
import random
from collections import defaultdict
from typing import List

import boto3
import cv2
import numpy as np
import typedload
from tqdm import tqdm

from overtrack.overwatch.collect.killfeed import Kill, Killfeed, KillfeedProcessor
from overtrack.overwatch.collect.teams import Teams
from overtrack.frame import Frame
from overtrack.overwatch.game.endgame import EndgameProcessor
from overtrack.source.stream import HLSPlaylist
from overtrack.util import referenced_typedload
from overtrack.util.logging_config import config_logger

s3 = boto3.resource(
    's3',
    region_name='sfo2',
    endpoint_url='https://sfo2.digitaloceanspaces.com',
    aws_access_key_id=os.environ['DO_SPACES_KEY'],
    aws_secret_access_key=os.environ['DO_SPACES_SECRET']
)
playlists = s3.Bucket('overtrack-playlists')
games = s3.Bucket('overtrack-games')


logger = logging.getLogger(__name__)


TARGET = 'C:/scratch/live-killfeed'
KILL_SAVE_CHANCE = 0.25
POSITION_SAVE_CHANCE = 0.1


# def make_player_key(p: KillfeedName):
#     if p is None:
#         return ''
#     return '.'.join([
#         ['red', 'blue'][p.player.blue_team],
#         p.player.name,
#         p.hero.replace('.', '-')
#     ])
#
#
# def save_images(key: str, ts: float, image: np.ndarray, kills: List[Kill], rows: List[KillRow]):
#     dest = os.path.join(TARGET, key)
#     for row in rows:
#         matching_kills = []
#         for kill in kills:
#             if (row.left is None) != (kill.left is None):
#                 continue
#             if row.left and kill.left and row.left.hero != kill.left.hero:
#                 continue
#             if row.right.hero != kill.right.hero:
#                 continue
#             matching_kills.append(kill)
#         if len(matching_kills) != 1:
#             logger.warning(f'Got {len(matching_kills)} matching kills for {row} - {matching_kills}')
#         else:
#             kill = matching_kills[0]
#             if random.random() < KILL_SAVE_CHANCE and (kill.left is None or kill.left.player.name_correct) and kill.right.player.name_correct:
#                 kill_image = image[
#                     30 + row.y - 6: 30 + row.y + 40,
#                     1920 - 500:
#                 ]
#                 kill_key = '_'.join(make_player_key(p) for p in (kill.left, kill.right))
#                 d = dest + '/kills/' + kill_key
#                 logger.debug(f'Saving {d}')
#                 os.makedirs(d, exist_ok=True)
#                 cv2.imwrite(f'{d}/{ts:.2f}.png', kill_image)
#     if random.random() < POSITION_SAVE_CHANCE:
#         d = f'{dest}/frames'
#         os.makedirs(d, exist_ok=True)
#         killrows_str = '_'.join(f'{r.y + 30 + 16.5:1.1f}' for r in rows)
#         cv2.imwrite(f'{d}/{ts:.2f}_{killrows_str}.png', image)


def save_killframes(game_key: str, playlist: str, killfeed: Killfeed):
    kills_by_source = defaultdict(list)
    frames_by_source = {}
    for kill in killfeed.kills:
        for ts in kill.row_timestamps:
            matching = [f for f in killfeed.frames if f.timestamp - killfeed.start_timestamp == ts]
            if not len(matching):
                continue
            frame = matching[0]
            key = (frame.source.uri, frame.source_frame_no)
            frames_by_source[key] = frame
            if kill not in kills_by_source[key]:
                kills_by_source[key].append(kill)

    source = HLSPlaylist(playlist, debug_frames=False)
    try:
        while True:
            frame = source.get()
            if frame is None:
                break

            cv2.imshow('frame', cv2.resize(frame.image, (0, 0), fx=0.5, fy=0.5))
            cv2.waitKey(1)

            key = (frame.source.uri, frame.source_frame_no)
            parsed_frame = frames_by_source.get(key)
            kills = kills_by_source[key]
            if parsed_frame and len(kills):
                save_images(game_key, frame.timestamp, frame.image, kills, parsed_frame.killfeed.kills)
    finally:
        source.close()


def main() -> None:
    with open('./scanned_playlists.txt', 'a+'):
        pass
    for playlist in tqdm(playlists.objects.all()):
        if not playlist.key.endswith('vod.m3u8'):
            continue
        with open('./scanned_playlists.txt') as file:
            scanned_playlists = set([l.strip() for l in file.readlines()])
            if playlist.key in scanned_playlists:
                logger.info(f'Skipping playlist {playlist.key}')
                continue

        print(playlist.key)
        game = s3.Object('overtrack-games', playlist.key.rsplit('/', 1)[0] + '.frames.json')

        try:
            logger.info(f'Loading game {game.key}')

            data = json.loads(game.get()['Body'].read())

            # delete fields that might not be up to date
            for f in data:
                if 'objective' in f:
                    del f['objective']
                if 'hero' in f:
                    del f['hero']
                if 'tab_screen' in f:
                    f['tab_screen']['stats'] = typedload.dump(EndgameProcessor.Stats(
                        '??',
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                    ))
                #     del f['tab_screen']
            frames: List[Frame] = referenced_typedload.load(data, List[Frame])
            logger.info(f'Loaded {len(frames)} frames')

            teams = Teams(frames, frames[0].timestamp, teams_fixed=True)
            killfeed = Killfeed(frames, teams, frames[0].timestamp)
            logger.info(f'Loaded {len(killfeed.kills)} kills')

            save_killframes(
                '_'.join(playlist.key.split('/')[1:3]),
                f'https://overtrack-playlists.sfo2.digitaloceanspaces.com/{playlist.key}',
                killfeed
            )
        except Exception as e:
            logger.exception(f'Got exception processing {game.key}')
        else:
            with open('./scanned_playlists.txt', mode='a') as file:
                print(playlist.key, file=file)


if __name__ == '__main__':
    config_logger('from_games', level=logging.INFO, write_to_file=False)
    main()

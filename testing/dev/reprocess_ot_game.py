import datetime
import json
import logging
import os
from pprint import pprint
from typing import List

import boto3
import requests

from ingest.game.playlist_creator import PlaylistCreator
from overtrack.collect import Game, GameExtractor
from overtrack.collect.game_to_overtrack import GameToOvertrack
from overtrack.game import Frame
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import referenced_typedload
from overtrack.util.logging_config import config_logger

logger = logging.getLogger()

SEGMENT_BUCKET = 'overtrack-video'
PLAYLIST_BUCKET = 'overtrack-playlists'
GAMES_BUCKET = 'overtrack-games'

boto_session = boto3.session.Session()
do_spaces = boto_session.client(
    's3',
    region_name='sfo2',
    endpoint_url='https://sfo2.digitaloceanspaces.com',
    aws_access_key_id=os.environ['DO_SPACES_KEY'],
    aws_secret_access_key=os.environ['DO_SPACES_SECRET']
)
""" :type do_spaces: pyboto3.s3 """


# class MockIngest(Ingest):
#
#     def __init__(self):
#         self.logger = logger
#
#     def save_frames(self, key, frames):
#         pass


def main():
    # logging.basicConfig(level=logging.INFO)
    config_logger('reprocess_game', logging.INFO)

    frames = referenced_typedload.load(json.loads(requests.get(
        'https://overtrack-games.sfo2.digitaloceanspaces.com/Muon-1547/2019-02-09-04-31/04-32-eichenwalde.frames.json'
    ).text), List[Frame])

    import matplotlib.pyplot as plt
    plt.figure()
    timestamp = [f.timestamp for f in frames]
    for i in range(4):
        plt.scatter(timestamp, [1 - f.objective.p_game_mode[0] if 'objective' in f else 0 for f in frames], label=f'{i}')
    plt.legend()
    plt.show()

    game_extractor = GameExtractor(keep_games=True, debug=True)
    for frame in frames:
        game_extractor.on_frame(frame)
    game_extractor.finish()

    game = game_extractor.games[0]

    # import matplotlib.pyplot as plt
    # plt.figure()
    # timestamp = [f.timestamp for f in game.frames if 'objective' in f]
    # for i in range(4):
    #     plt.scatter(timestamp, [f.objective.p_koth_map[i] for f in game.frames if 'objective' in f], label=f'{i}')
    # plt.legend()
    # plt.show()

    print(game)
    print(game.teams.blue[0])
    p = game.teams.blue[0]
    print()
    pprint(game.killfeed.kills)

    print(game)
    pprint(game.stats.stats)
    print(game.stages)

    ot_game = GameToOvertrack(game, f'Muon/test')
    g = ot_game.as_dict()
    g['killfeed'] = '...'
    pprint(g)

    logger.setLevel(logging.WARNING)

    playlists = {}
    plc = PlaylistCreator(game)
    for name in 'kills', 'deaths', 'resurrects', 'ults', 'vod':
        k = f'Muon/test/{name}.m3u8'
        pl = getattr(plc, name)()
        if len(pl):
            do_spaces.put_object(
                Bucket=PLAYLIST_BUCKET,
                Key=k,
                Body=pl.as_m3u8(),
                ACL='public-read',
                ContentType='application/x-mpegURL',
            )
            playlists[name] = f'https://{PLAYLIST_BUCKET}.sfo2.digitaloceanspaces.com/{k}'
            logger.info(f'Uploaded {k} to {playlists[name]}')

    datetimestr = datetime.datetime.utcfromtimestamp(game.start).strftime('%Y-%m-%d-%H-%M')
    ot_game = GameToOvertrack(game, f'Muon/test', extra_fields={
        'playlists': playlists
    })
    ot_game.save()

    # ingest = MockIngest()
    # ingest.on_game_complete(game)

    print(f'https://overtrack.gg/game/{ot_game.key}')


if __name__ == '__main__':
    main()


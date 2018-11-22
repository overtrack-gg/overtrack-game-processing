import datetime
import logging
import os
from pprint import pprint

import boto3

from ingest.game.playlist_creator import PlaylistCreator
from overtrack.collect import Game
from overtrack.collect.game_to_overtrack import GameToOvertrack


logger = logging.getLogger(__name__)

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
    logging.basicConfig(level=logging.INFO)
    with open('./games/02-06-busan.frames.json') as f:
        game = Game.load(f)

    playlists = {}
    plc = PlaylistCreator(game)
    for name in 'kills', 'deaths', 'resurrects', 'ults', 'vod':
        k = f'Muon/{game.shortkey}/{name}.m3u8'
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
    ot_game = GameToOvertrack(game, f'Muon/{datetimestr}-test', extra_fields={
        'playlists': playlists
    })
    ot_game.save()

    # ingest = MockIngest()
    # ingest.on_game_complete(game)

    print(game)
    print(game.stages)

    pprint(ot_game.as_dict())

    print(f'https://overtrack.gg/game/{ot_game.key}')


if __name__ == '__main__':
    main()


import logging
import os
import random
import re
import time

import requests
import dateutil.parser
from pprint import pprint


from overtrack.util import dhms2timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session = requests.Session()
session.headers.update({'Client-ID': os.environ['TWITCH_CLIENT_ID']})

twitch_get_user = 'https://api.twitch.tv/helix/users?login=%s'
twitch_get_videos = 'https://api.twitch.tv/helix/videos?user_id=%s&first=%d&type=%s'

TWITCH_ACCOUNT = 'overwatchcontenders'

CUSTOM_PALETTE_INTRODUCTION_DATE = dateutil.parser.parse('2018-08-04T08:39:32Z')
REGIONS = [
    'Pacific',
    'Australia',
    'Europe',
    'North America',
    'South America'
]


class TwitchVOD:
    __slots__ = [
        'created_at',
        'description',
        'duration',
        'id',
        'language',
        'published_at',
        'thumbnail_url',
        'title',
        'type',
        'url',
        'user_id',
        'view_count',
        'viewable',
    ]

    def __init__(self, **fields):
        for k, v in fields.items():
            if k in ['created_at', 'published_at']:
                v = dateutil.parser.parse(v)
            elif k in ['view_count']:
                v = int(v)
            elif k in ['duration']:
                v = dhms2timedelta(v)
            setattr(self, k, v)

    def __str__(self):
        return f'{ self.__class__.__name__ }({ ", ".join("%s=%r" % (f, getattr(self, f)) for f in self.__slots__) })'
    __repr__ = __str__


if __name__ == "__main__":
    r = session.get(twitch_get_user % (TWITCH_ACCOUNT,))
    r.raise_for_status()
    data = r.json()['data']
    assert len(data)

    twitch_id = data[0]['id']
    logger.info('%s has twitch ID %s', TWITCH_ACCOUNT, twitch_id)

    logger.info('Searching VODs')
    vods = []
    pagination = None
    while True:
        fetch = twitch_get_videos % (twitch_id, 100, 'highlight')
        if pagination:
            fetch += '&after=' + pagination
        logger.info('Fetching %s', fetch)
        r = session.get(fetch)
        r.raise_for_status()
        data = r.json()
        for vod_dict in data['data']:
            vods.append(TwitchVOD(**vod_dict))
        logger.info('Got %d vods', len(data['data']))

        if not len(data['data']) or 'pagination' not in data or 'cursor' not in data['pagination']:
            break

        pagination = data['pagination']['cursor']
        time.sleep(3)

    logger.info('Got %d vods', len(vods))

    vods = [v for v in vods if v.created_at < CUSTOM_PALETTE_INTRODUCTION_DATE]
    logger.info('Got %d vods with red/blue pallet', len(vods))

    vods = [v for v in vods if any(s in v.title for s in REGIONS)]
    logger.info('Got %d vods with accepted regions', len(vods))

    vods = [v for v in vods if re.match(r'.*Match \d Game \d \|', v.title)]
    logger.info('Got %d single-game vods', len(vods))

    # TODO: use aws listing to remove vods already processed

    # TODO: automatically create n spot requests and split the tasks across them

    random.shuffle(vods)
    with open('contenders_games.sh', 'w') as f:
        f.write('# Contenders name extraction script\n\n')
        f.write('echo > progress.txt')
        for i, vod in enumerate(vods):
            line = f"""
            
# Title: { vod.title }
# URL: { vod.url }
# Created: { vod.created_at }
# Duration { vod.duration }
echo "{ i } / { len(vods) }" >> progress.txt
echo "Title: { vod.title }" >> progress.txt
echo "URL: { vod.url }" >> progress.txt
echo "Duration: { vod.duration }" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py { vod.url }
tar cvf /media/ephemeral0/names_{ vod.id }.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_{ vod.id }.tar s3://overtrack-training-data/vod-names/names_{ vod.id }.tar
rm /media/ephemeral0/names_{ vod.id }.tar"""
            print(line)
            f.write(line)

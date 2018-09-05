import cv2
import datetime
import logging
import os
import dateutil.parser
import requests
import bisect

from overtrack.game import Frame
from overtrack.game.processor import Processor

logger = logging.getLogger(__name__)
session = requests.Session()
session.headers.update({'Client-ID': os.environ['TWITCH_CLIENT_ID']})

twitch_get_user = 'https://api.twitch.tv/helix/users?login=%s'
twitch_get_videos = 'https://api.twitch.tv/helix/videos?user_id=%s&first=%d&type=archive'


def ot2new_hero(s: str) -> str:
    s = s.split('.')[0]
    if s == 's76':
        s = 'solider'
    elif s == 'torb':
        s = 'torbjorn'
    return s


class NamesFromOvertrack(Processor):

    def __init__(self, vod_url: str, overtrack_share_key: str) -> None:
        self.video_id = vod_url.rsplit('/', 1)[1]
        r = session.get('https://api.twitch.tv/kraken/videos/' + self.video_id)
        r.raise_for_status()
        data = r.json()

        self.channel = data['channel']['display_name']
        self.vod_start_time = dateutil.parser.parse(data['created_at'])
        logger.info('Got VOD by %s starting at %s', self.channel, self.vod_start_time)

        r = requests.get('https://api.overtrack.gg/games/' + overtrack_share_key)
        r.raise_for_status()
        self.overtrack_games = r.json()['games'][::-1]
        for game in self.overtrack_games:
            game['time'] = datetime.datetime.fromtimestamp(game['time'], datetime.timezone.utc)

        logger.info('Got %d overtrack games for share key %s', len(self.overtrack_games), overtrack_share_key)

        self.game_cache = {}

    def process(self, frame: Frame) -> bool:
        if 'killfeed' not in frame or not len(frame.killfeed.kills):
            return False

        ts = self.vod_start_time + datetime.timedelta(seconds=frame.timestamp)
        index = bisect.bisect([g['time'] for g in self.overtrack_games], ts) - 1
        if index >= len(self.overtrack_games):
            return False
        game = self.overtrack_games[index]
        end = game['time'] + datetime.timedelta(seconds=game['duration'])
        if ts > end:
            return False

        if game['key'] not in self.game_cache:
            logger.info('Downloading %s from %s', game['map'], game['key'])
            r = requests.get(game['url'])
            r.raise_for_status()
            killfeed = []
            for kill in r.json()['killfeed']:
                t = game['time'] + datetime.timedelta(milliseconds=kill[0])
                killfeed.append((t, kill[1:]))
            self.game_cache[game['key']] = killfeed

        full_game = self.game_cache[game['key']]
        kill_index = max(0, bisect.bisect([k[0] for k in full_game], ts) - 1)

        for to_match in frame.killfeed.kills:
            if not to_match.left:
                continue
            matching = None
            for offset in range(50):
                for signed_offset in -offset, offset:
                    new_index = kill_index + signed_offset
                    if new_index >= len(full_game) or new_index < 0:
                        continue
                    check_kill = full_game[new_index][1]
                    if not check_kill[1] or check_kill[0] not in [0, 1]:
                        continue

                    if ot2new_hero(check_kill[1]) == to_match.left.hero and ot2new_hero(check_kill[3]) == to_match.right.hero:
                        left_blue = to_match.left.blue_team
                        if (check_kill[0] == 1 and left_blue) or (check_kill[0] == 0 and not left_blue):
                            matching = check_kill
                            break
                if matching:
                    break
            if matching:
                self._save_name(frame.killfeed.name_images[to_match.left.index], matching[0] == 1, matching[2], frame.timestamp * 1000)
                self._save_name(frame.killfeed.name_images[to_match.right.index], matching[0] == 0, matching[4], frame.timestamp * 1000)
            else:
                logger.warning('Could not find kill matching %s in overtrack game', to_match)

    def _save_name(self, image: 'np.ndarray', blue_team: bool, name: str, ms: int):
        if '@' in name:
            return
        d = os.path.join('C:\\', 'scratch', 'names', self.channel, self.video_id, 'rb'[blue_team] + '.' + name)
        os.makedirs(d, exist_ok=True)
        cv2.imwrite(os.path.join(d, f'{ ms }.png'), image)


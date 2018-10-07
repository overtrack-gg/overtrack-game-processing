import os
from pprint import pprint

import requests

twitch_get_user = 'https://api.twitch.tv/helix/users?login=%s'
LIVE_ACTIVATED_CHANNELS = 'https://api.twitch.tv/extensions/%s/live_activated_channels'


def main():
    twitch = requests.Session()
    twitch.headers.update({'Client-ID': os.environ['TWITCH_EXTENSION_ID']})

    request = twitch.get(LIVE_ACTIVATED_CHANNELS % (os.environ['TWITCH_EXTENSION_ID'],))
    request.raise_for_status()
    data = request.json()['channels']
    pprint(data)


if __name__ == '__main__':
    main()

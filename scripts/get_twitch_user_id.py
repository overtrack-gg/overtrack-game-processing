import os
from pprint import pprint

import requests

twitch_get_user = 'https://api.twitch.tv/helix/users?login=%s'


def main(twitch_account):
    twitch = requests.Session()
    twitch.headers.update({'Client-ID': os.environ['TWITCH_EXTENSION_ID']})

    request = twitch.get(twitch_get_user % (twitch_account,))
    request.raise_for_status()
    data = request.json()['data']
    pprint(data)


if __name__ == '__main__':
    main('eeveea_')

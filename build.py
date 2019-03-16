import os
import zipfile
from typing import Tuple

import boto3


def humansize(nbytes: float, suffixes: Tuple[str, ...] = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')) -> str:
    # http://stackoverflow.com/a/14996816
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def main() -> None:
    zf = zipfile.ZipFile('./overtrack.zip', 'w')
    whitelist = [
        'overtrack',
        'overtrack_legacy',
        'ingest',
        'twitch_overlay',
        'models',

        'requirements.txt'
    ]
    blacklist = [
        '__pycache__',
        'build'
    ]

    for dirname, subdirs, files in os.walk('.'):
        parts = dirname.split(os.path.sep)
        if len(parts) > 1 and parts[1] in whitelist:
            if os.path.basename(dirname) not in blacklist:
                print(f'Adding {dirname}')
                for filename in files:
                    if os.path.basename(filename) not in blacklist:
                        zf.write(os.path.join(dirname, filename), os.path.join('overtrack', dirname, filename))
        else:
            for filename in files:
                if filename in whitelist:
                    print(f'Adding {filename}')
                    zf.write(os.path.join(dirname, filename), os.path.join('overtrack', dirname, filename))
    zf.close()

    print(f'Uploading {humansize(os.path.getsize("overtrack.zip"))}')
    do_spaces = boto3.client(
        's3',
        region_name='sfo2',
        endpoint_url='https://sfo2.digitaloceanspaces.com',
        aws_access_key_id=os.environ['DO_SPACES_KEY'],
        aws_secret_access_key=os.environ['DO_SPACES_SECRET']
    )
    do_spaces.upload_file('overtrack.zip', 'overtrack-dist', 'overtrack.zip')


if __name__ == '__main__':
    main()

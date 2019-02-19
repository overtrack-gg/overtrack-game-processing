import shortuuid

from overtrack_legacy.models.user import User


def main() -> None:
    user = User.get('Portadiam#1568')
    user.stream_key = shortuuid.uuid()
    print(f'Stream key is {user.stream_key}')
    user.save()


if __name__ == '__main__':
    main()


# rtmp://ingest.overtrack.gg/Portadiam-1568?key=UhLdKv2JGSV4MBzNGUea77
# rtmp://ingest.overtrack.gg/Muon-1547?key=uQVuHRz8MUnvf5YLxRNit4

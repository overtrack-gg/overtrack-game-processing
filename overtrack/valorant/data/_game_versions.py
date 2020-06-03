import datetime

from dataclasses import dataclass

_UTC = datetime.timezone(datetime.timedelta(hours=0))


def _parse_utc(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(
        s,
        '%b %d %Y %I:%M%p'
    ).replace(tzinfo=_UTC)


@dataclass
class GameVersion:
    name: str
    published: datetime.datetime


game_versions = [
    GameVersion(
        '00.00.0-beta',
        _parse_utc('Jan 1 2020 1:00AM')
    ),
    GameVersion(
        '01.00.0',
        _parse_utc('Jun 2 2020 1:00AM')
    )
]


def get_version(t: datetime.datetime) -> GameVersion:
    for v in reversed(game_versions):
        if t > v.published:
            return v
    else:
        return game_versions[0]

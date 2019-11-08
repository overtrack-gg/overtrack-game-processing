import datetime
from typing import Optional

from dataclasses import dataclass


@dataclass
class Season:
    index: int
    start: float
    end: float
    season_name: Optional[str] = None

    @property
    def name(self) -> str:
        return self.season_name or f'Season {self.index}'


_PDT = datetime.timezone(datetime.timedelta(hours=-7))
_season_1_start = datetime.datetime.strptime(
    # https://twitter.com/PlayApex/status/1107733497450356742
    'Mar 19 2019 10:00AM',
    '%b %d %Y %I:%M%p'
).replace(tzinfo=_PDT)
_season_2_start = datetime.datetime.strptime(
    # https://twitter.com/PlayApex/status/1107733497450356742
    'Jul 2 2019 10:00AM',
    '%b %d %Y %I:%M%p'
).replace(tzinfo=_PDT)
_season_3_start = 1569956446

SEASONS = [
    Season(0, 0, _season_1_start.timestamp()),
    Season(1, _season_1_start.timestamp(), _season_2_start.timestamp()),
    Season(2, _season_2_start.timestamp(), _season_3_start),
    Season(3, _season_3_start, float('inf')),

    Season(1002, 0, 0, season_name='Season 2 Solos'),
    Season(1003, _season_3_start, float('inf'), season_name='Season 3 Duos'),

    Season(2000, _season_3_start, float('inf'), season_name='Scrims'),
]

import datetime
from typing import Optional

from dataclasses import dataclass


@dataclass
class Season:
    index: int
    start: float
    end: float
    has_ranked: bool = True
    season_name: Optional[str] = None

    @property
    def name(self) -> str:
        return self.season_name or f'Season {self.index}'


_PDT = datetime.timezone(datetime.timedelta(hours=-7))
_PST = datetime.timezone(datetime.timedelta(hours=-8))
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
_season_4_start = datetime.datetime.strptime(
    'Feb 4 2020 10:00AM',
    '%b %d %Y %I:%M%p'
).replace(tzinfo=_PST)

seasons = [
    Season(0, 0, _season_1_start.timestamp(), has_ranked=False),
    Season(1, _season_1_start.timestamp(), _season_2_start.timestamp(), has_ranked=False),
    Season(2, _season_2_start.timestamp(), _season_3_start),
    Season(3, _season_3_start, _season_4_start.timestamp()),
    Season(4, _season_4_start.timestamp(), float('inf')),

    Season(1002, 0, 0, season_name='Season 2 Solos', has_ranked=False),
    Season(1003, _season_3_start, _season_4_start.timestamp(), season_name='Season 3 Duos', has_ranked=False),

    Season(2000, _season_3_start, float('inf'), season_name='Scrims', has_ranked=False),
]
current_season = sorted([s for s in seasons if s.index < 100], key=lambda s: s.end)[-1]

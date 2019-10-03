import datetime
import logging
import os
import re
import zipfile
from typing import List, Optional, Tuple
from urllib.parse import unquote

import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Champion:
    name: str


champions = {
    'bloodhound': Champion('Bloodhound'),
    'gibraltar': Champion('Gibraltar'),
    'lifeline': Champion('Lifeline'),
    'pathfinder': Champion('Pathfinder'),
    'wraith': Champion('Wraith'),
    'bangalore': Champion('Bangalore'),
    'mirage': Champion('Mirage'),
    'caustic': Champion('Caustic'),
    'octane': Champion('Octane'),
    'wattson': Champion('Wattson'),
    'crypto': Champion('Crypto')
}


@dataclass
class Weapon:
    name: str
    type: str
    ammo_type: str

    full_name: Optional[str] = None

    def __post_init__(self):
        if not self.full_name:
            self.full_name = self.name

    # attachments


pistols = [
    Weapon('RE-45', 'pistol', 'light', full_name='RE-45 Auto'),
    Weapon('P2020', 'pistol', 'light'),
    Weapon('Wingman', 'pistol', 'heavy'),
]
shotguns = [
    Weapon('Mozambique', 'shotgun', 'shotgun'),
    Weapon('EVA-8 Auto', 'shotgun', 'shotgun'),
    Weapon('Peacekeeper', 'shotgun', 'shotgun'),
    Weapon('Mastiff', 'shotgun', 'special'),  # is this "Mastiff Shotgun"?
]
ars = [
    Weapon('Hemlock', 'ar', 'heavy'),
    Weapon('Flatline', 'ar', 'heavy'),
    Weapon('Havoc', 'ar', 'energy'),
    Weapon('R-301', 'ar', 'light', full_name='R-301 Carbine'),
]
lmgs = [
    Weapon('Spitfire', 'lmg', 'heavy'),
    Weapon('Devotion', 'lmg', 'energy'),
    Weapon('L-STAR', 'lmg', 'special'),
]
smgs = [
    Weapon('Alternator', 'smg', 'light'),
    Weapon('Prowler', 'smg', 'heavy'),  # is this "Prowler SMG"?
    Weapon('R-99', 'smg', 'light'),
]
snipers = [
    Weapon('Triple Take', 'sniper', 'energy'),
    Weapon('Charge Rifle', 'sniper', 'energy'),
    Weapon('Longbow', 'sniper', 'heavy'),
    Weapon('G7 Scout', 'sniper', 'light'),
    Weapon('Kraber', 'sniper', 'special'),
]
weapons = \
    pistols + \
    shotguns + \
    ars + \
    lmgs + \
    smgs + \
    snipers
weapon_names = [w.name.upper() for w in weapons]


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

seasons = [
    Season(0, 0, _season_1_start.timestamp()),
    Season(1, _season_1_start.timestamp(), _season_2_start.timestamp()),
    Season(2, _season_2_start.timestamp(), 1569956446),
    Season(3, 1569956446, float('inf')),

    Season(1002, 0, 0, season_name='Season 2 Solo')
]


ranks = [
    'bronze',
    'silver',
    'gold',
    'platinum',
    'diamond',
    'apex_predator'
]

rank_tiers = [
    'IV',
    'III',
    'II',
    'I'
]

rank_rp = {
    'bronze': (0, 1200),
    'silver': (1200, 2800),
    'gold': (2800, 4800),
    'platinum': (4800, 7200),
    'diamond': (7200, 10_000),
    'apex_predator': (10_000, 99_999)
}

rank_entry_cost = {
    'bronze': 0,
    'silver': 12,
    'gold': 24,
    'platinum': 36,
    'diamond': 48,
    'apex_predator': 60
}

rank_rewards = {
    10: 10,
    9: 10,
    8: 20,
    7: 20,
    6: 30,
    5: 30,
    4: 40,
    3: 40,
    2: 60,
    1: 100,
}
for placement in range(11, 21):
    rank_rewards[placement] = 0


class MapLocations:

    def __init__(self, name: str):
        self.name = name
        self.layers: Optional[List[str, np.ndarray]] = None

    def _ensure_loaded(self) -> None:
        import cv2

        if self.layers is not None:
            return
        self.layers = []

        # TODO: workaround for https://github.com/Miserlou/Zappa/issues/1754
        source = os.path.join(os.path.dirname(__file__), self.name + '.zip')
        altsource = os.path.join(os.path.dirname(__file__), self.name + '._zip')
        if not os.path.exists(source) and os.path.exists(altsource):
            source = altsource

        with zipfile.ZipFile(source) as z:
            for f in z.namelist():
                if not f.startswith('L') or not f.endswith('.png'):
                    # not a layer
                    continue
                layer_props = f.rsplit('.', 1)[0].split(',')
                layer_name = unquote(re.sub(r'%00(\d\d)', r'%\1', layer_props[3]))
                if layer_name.lower() != 'background' and not layer_name.startswith('.'):
                    with z.open(f, 'r') as fobj:
                        logger.debug(f'Loading location {layer_name}')
                        layer = cv2.imdecode(np.frombuffer(fobj.read(), dtype=np.uint8), -1)
                        mask = layer[:, :, 3] > 0
                        self.layers.append((layer_name, mask))

    def get_location_name(self, location: Tuple[int, int]) -> str:
        self._ensure_loaded()
        for name, mask in self.layers:
            if mask[location[1], location[0]]:
                # logger.info(f'Resolving {location} -> {name}')
                return name
        # logger.warning(f'Unable to resolve {location}')
        return 'Unknown'

    def __getitem__(self, location: Tuple[int, int]) -> str:
        return self.get_location_name(location)


kings_canyon_locations = MapLocations('map_locations')
worlds_edge_locations = MapLocations('worlds_edge_locations')

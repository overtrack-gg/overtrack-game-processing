import cv2
import logging
import os
import re
import zipfile
from typing import Optional, Tuple
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
    # 'pathfinder': Champion('Pathfinder'),
    'wraith': Champion('Wraith'),
    'bangalore': Champion('Bangalore'),
    'mirage': Champion('Mirage'),
    # 'caustic': Champion('Caustic')
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
    Weapon('Devotion', 'lmg', 'energy')
]
smgs = [
    Weapon('Alternator', 'smg', 'light'),
    Weapon('Prowler', 'smg', 'heavy'),  # is this "Prowler SMG"?
    Weapon('R-99', 'smg', 'light'),
]
snipers = [
    Weapon('Triple Take', 'sniper', 'energy'),
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


class MapLocations:

    def __init__(self):
        self.layers = []
        with zipfile.ZipFile(os.path.join(os.path.dirname(__file__), 'map_locations.zip')) as z:
            for f in z.namelist():
                if not f.startswith('L') or not f.endswith('.png'):
                    # not a layer
                    continue
                layer_props = f.rsplit('.', 1)[0].split(',')
                layer_name = unquote(re.sub(r'%00(\d\d)', r'%\1', layer_props[3]))
                if layer_name.lower() != 'background':
                    with z.open(f, 'r') as fobj:
                        logger.debug(f'Loading location {layer_name}')
                        layer = cv2.imdecode(np.frombuffer(fobj.read(), dtype=np.uint8), -1)
                        mask = layer[:, :, 3] > 0
                        self.layers.append((layer_name, mask))

    def get_location_name(self, location: Tuple[int, int]) -> str:
        for name, mask in self.layers:
            if mask[location[1], location[0]]:
                # logger.info(f'Resolving {location} -> {name}')
                return name
        # logger.warning(f'Unable to resolve {location}')
        return 'Unknown'

    def __getitem__(self, location: Tuple[int, int]) -> str:
        return self.get_location_name(location)


map_locations = MapLocations()

from dataclasses import dataclass
from typing import Optional, Tuple, List

from overtrack.util.uploadable_image import UploadableImage


@dataclass
class PlayerStats:
    agent: Optional[str]
    name: Optional[str]
    friendly: bool
    avg_combat_score: Optional[int]
    kills: Optional[int]
    deaths: Optional[int]
    assists: Optional[int]
    econ_rating: Optional[int]
    first_bloods: Optional[int]
    plants: Optional[int]
    defuses: Optional[int]


@dataclass
class Postgame:
    victory: bool
    score: Tuple[Optional[int], Optional[int]]
    map: Optional[str]

    game_mode: Optional[str] = None

    image: Optional[UploadableImage] = None


@dataclass
class Scoreboard:
    player_stats: List[PlayerStats]

    image: Optional[UploadableImage] = None

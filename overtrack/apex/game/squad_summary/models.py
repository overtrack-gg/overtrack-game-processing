from typing import Optional, Tuple

from dataclasses import dataclass

from overtrack.util.uploadable_image import UploadableImage


@dataclass
class PlayerStats:
    name: str

    kills: Optional[int]
    damage_dealt: Optional[int]
    survival_time: Optional[int]
    players_revived: Optional[int]
    players_respawned: Optional[int]


@dataclass
class SquadSummary:
    champions: bool
    squad_kills: Optional[int]
    player_stats: Tuple[PlayerStats, PlayerStats, PlayerStats]

    placed: Optional[int] = None

    image: Optional[UploadableImage] = None

    elite: Optional[bool] = False


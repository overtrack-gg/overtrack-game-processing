from typing import Optional, Tuple

from dataclasses import dataclass


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
    # placed: Optional[int]
    squad_kills: Optional[int]
    player_stats: Tuple[PlayerStats, PlayerStats, PlayerStats]


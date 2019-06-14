from typing import Optional

from dataclasses import dataclass


@dataclass
class MatchStatus:
    squads_left: int
    players_alive: Optional[int]
    kills: Optional[int]

    streak: Optional[int] = None

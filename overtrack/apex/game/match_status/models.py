from typing import Optional, Tuple

from dataclasses import dataclass


@dataclass
class MatchStatus:
    squads_left: Optional[int]
    players_alive: Optional[int]
    kills: Optional[int]

    streak: Optional[int] = None

    rank_badge_matches: Optional[Tuple[float, ...]] = None
    rank_text: Optional[str] = None

    solos_players_left: Optional[int] = None


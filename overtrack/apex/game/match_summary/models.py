from typing import Optional

from dataclasses import dataclass


@dataclass
class XPStats:
    won: bool = False
    top3_finish: bool = False
    time_survived: Optional[int] = None
    kills: Optional[int] = None
    damage_done: Optional[int] = None
    revive_ally: Optional[int] = None
    respawn_ally: Optional[int] = None


@dataclass
class MatchSummary:
    placed: int
    xp_stats: XPStats


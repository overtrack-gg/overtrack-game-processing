from typing import List

from dataclasses import dataclass

EventTypes = [
    'ELIMINATED',
    'KNOCKED DOWN',
    'ASSIST, ELIMINATION',
    'ASSIST, KNOCK DOWN'
]


@dataclass
class Event:
    type: str
    width: int
    # name: str
    # damage: Optional[int]

    match: float


@dataclass
class CombatLog:
    events: List[Event]

from dataclasses import dataclass
from typing import Optional, Tuple

from overtrack.valorant.data import AgentName

OAgent = Optional[AgentName]
TeamComp = Tuple[OAgent, OAgent, OAgent, OAgent, OAgent]
Obool = Optional[bool]
FiveOBool = Tuple[Obool, Obool, Obool, Obool, Obool]

@dataclass
class TopHud:
    score: Tuple[Optional[int], Optional[int]]
    teams: Tuple[TeamComp, TeamComp]
    has_ult: Optional[Tuple[FiveOBool, FiveOBool]] = None
    has_spike: Optional[FiveOBool] = None

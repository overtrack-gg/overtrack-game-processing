from dataclasses import dataclass
from typing import Optional, Tuple

from overtrack.valorant.data import AgentName

OAgent = Optional[AgentName]
TeamComp = Tuple[OAgent, OAgent, OAgent, OAgent, OAgent]

@dataclass
class TopHud:
    score: Tuple[Optional[int], Optional[int]]
    teams: Tuple[TeamComp, TeamComp]


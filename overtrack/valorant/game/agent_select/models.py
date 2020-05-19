from dataclasses import dataclass
from typing import Optional

from overtrack.valorant.data import AgentName


@dataclass
class AgentSelect:
    agent: AgentName
    locked_in: bool

    map: Optional[str]
    game_mode: Optional[str] = None
    # TODO: other player names? - include which one is first person?
    # TODO: other agents?

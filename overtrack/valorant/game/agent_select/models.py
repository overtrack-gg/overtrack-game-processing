from dataclasses import dataclass
from typing import Optional, List, Tuple

from overtrack.util.uploadable_image import UploadableImage
from overtrack.valorant.data import AgentName


@dataclass
class AgentSelect:
    agent: AgentName
    locked_in: bool

    map: Optional[str]
    game_mode: Optional[str] = None

    player_names: Optional[List[str]] = None
    agents: Optional[List[Optional[str]]] = None
    ranks: Optional[List[Tuple[str, float]]] = None

    image: Optional[UploadableImage] = None

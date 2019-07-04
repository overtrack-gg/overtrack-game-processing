from typing import Optional, Tuple

from dataclasses import dataclass


@dataclass
class PlayMenu:
    player_name: str
    squadmates: Tuple[Optional[str], Optional[str]]
    ready: bool

    rank_text: Optional[str] = None
    rp_text: Optional[str] = None

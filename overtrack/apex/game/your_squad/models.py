from typing import Tuple, Optional

from dataclasses import dataclass


@dataclass
class YourSquad:
    names: Tuple[Optional[str], Optional[str], Optional[str]]

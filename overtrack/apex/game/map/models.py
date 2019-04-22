from typing import Tuple, Optional

from dataclasses import dataclass


@dataclass
class Location:
    coordinates: Tuple[int, int]
    match: float

    bearing: Optional[int] = None
    rotated_map: Optional[bool] = None

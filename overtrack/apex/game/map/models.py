from typing import Tuple

from dataclasses import dataclass


@dataclass
class Location:
    coordinates: Tuple[int, int]
    match: float

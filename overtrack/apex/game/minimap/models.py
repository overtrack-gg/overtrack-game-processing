from typing import Optional, Tuple

from dataclasses import dataclass

from overtrack.util import round_floats


@dataclass(frozen=True)
@round_floats
class Circle:
    coordinates: Tuple[float, float]
    r: float

    residual: Optional[float] = None
    points: Optional[int] = None


@dataclass(frozen=True)
@round_floats
class Location:
    coordinates: Tuple[int, int]
    match: float
    bearing: Optional[int]

    zoom: Optional[float] = None

    @property
    def x(self):
        return self.coordinates[0]

    @property
    def y(self):
        return self.coordinates[1]


@dataclass(frozen=True)
class Minimap:
    location: Location
    inner_circle: Optional[Circle]
    outer_circle: Optional[Circle]
    spectate: bool = False
    version: int = 0

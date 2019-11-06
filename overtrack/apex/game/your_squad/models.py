from typing import Optional, Tuple

from dataclasses import dataclass

from overtrack.util.uploadable_image import UploadableImage


@dataclass(frozen=True)
class YourSquad:
    names: Tuple[Optional[str], ...]
    mode: Optional[str] = None
    images: Optional[UploadableImage] = None


@dataclass(frozen=True)
class ChampionSquad:
    names: Tuple[Optional[str], ...]
    images: Optional[UploadableImage] = None


@dataclass(frozen=True)
class YourSelection:
    name: str
    image: Optional[UploadableImage] = None

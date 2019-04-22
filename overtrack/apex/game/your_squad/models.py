from typing import Optional, Tuple

from dataclasses import dataclass

from overtrack.util.uploadable_image import UploadableImage


@dataclass
class YourSquad:
    names: Tuple[Optional[str], Optional[str], Optional[str]]
    images: Optional[UploadableImage] = None


@dataclass
class ChampionSquad:
    names: Tuple[Optional[str], Optional[str], Optional[str]]
    images: Optional[UploadableImage] = None

from typing import List, Optional, Tuple

import numpy as np
from dataclasses import dataclass

from overtrack.util import arrayops


@dataclass(frozen=True)
class Weapons:
    weapon_names: List[str]
    selected_weapons: Tuple[int, int]
    clip: Optional[int]
    ammo: Optional[int]

    @property
    def selected_weapon_index(self) -> Optional[int]:
        if np.max(self.selected_weapons) > 190 and np.min(self.selected_weapons) < 100:
            return arrayops.argmin(self.selected_weapons)
        else:
            return None

from typing import List, Optional, Tuple

import numpy as np
from dataclasses import dataclass

from overtrack.apex import data
from overtrack.util import arrayops


@dataclass
class Squad:
    name: Optional[str]
    champion: List[float]
    squadmate_names: Tuple[Optional[str], Optional[str]]
    squadmate_champions: Tuple[List[float], List[float]]

    @property
    def champion_name(self) -> str:
        return list(data.champions.keys())[arrayops.argmax(self.champion)]

    @property
    def squadmate_champions_names(self) -> Tuple[str, str]:
        # noinspection PyTypeChecker
        return tuple(list(data.champions.keys())[arrayops.argmax(arr)] for arr in self.squadmate_champions)

    def __str__(self) -> str:
        return f'Squad(' \
               f'champion={self.champion_name}({np.argmax(self.champion):1.4f}), ' \
               f'squadmate_champions=' \
               f'{self.squadmate_champions_names[0]}({np.max(self.squadmate_champions[0])}), ' \
               f'{self.squadmate_champions_names[1]}({np.max(self.squadmate_champions[1])}))'

    __repr__ = __str__

from typing import Sequence, Union

import numpy as np

Num = Union[int, float]


def argmin(seq: Union[Sequence[Num], np.ndarray]) -> int:
    return int(np.argmin(seq))


def argmax(seq: Union[Sequence[Num], np.ndarray]) -> int:
    return int(np.argmax(seq))


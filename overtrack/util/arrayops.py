from typing import Sequence, Union

import numpy as np

Num = Union[int, float]


def argmin(seq: Union[Sequence[Num], np.ndarray]) -> int:
    return int(np.argmin(seq))


def argmax(seq: Union[Sequence[Num], np.ndarray]) -> int:
    return int(np.argmax(seq))


def monotonic(seq: Union[Sequence[Num], np.ndarray], increasing: bool = True):
    arr = np.array(seq)
    diff = arr[1:] - arr[:-1]
    if increasing:
        return np.all(diff > 0)
    else:
        return np.all(diff < 0)

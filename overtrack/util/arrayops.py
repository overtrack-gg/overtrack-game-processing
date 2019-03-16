from typing import Sequence, Union, Tuple

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


def mode(arr: np.ndarray, axis: int = 0) -> Tuple[np.ndarray, int]:
    if arr.size == 1:
        return arr[0], 1
    elif arr.size == 0:
        raise ValueError('Attempted to find mode on an empty array')
    try:
        axis = [i for i in range(arr.ndim)][axis]
    except IndexError:
        raise ValueError('Axis %i out of range for array with %i dimension(s)' % (axis, arr.ndim))
    srt = np.sort(arr, axis=axis)
    dif = np.diff(srt, axis=axis)
    shape = [i for i in dif.shape]
    shape[axis] += 2
    indices = np.indices(shape)[axis]
    index = tuple([slice(None) if i != axis else slice(1, -1) for i in range(dif.ndim)])
    indices[index][dif == 0] = 0
    indices.sort(axis=axis)
    bins = np.diff(indices, axis=axis)
    location = np.argmax(bins, axis=axis)
    mesh = np.indices(bins.shape)
    index = tuple([slice(None) if i != axis else 0 for i in range(dif.ndim)])
    index = [mesh[i][index].ravel() if i != axis else location.ravel() for i in range(bins.ndim)]
    counts = bins[tuple(index)].reshape(location.shape)
    index[axis] = indices[tuple(index)]
    modals = srt[tuple(index)].reshape(location.shape)
    return modals, counts


def modefilt(seq: Union[Sequence[Num], np.ndarray], filtersize: int) -> np.ndarray:
    if not isinstance(seq, np.ndarray):
        seq = np.array(seq)
    if filtersize < 3 or filtersize % 2 == 0:
        raise ValueError(f'Mode filter length ({filtersize}) must be odd')
    if seq.ndim != 1:
        raise ValueError('Input must be one-dimensional')
    if len(seq) < filtersize:
        return seq

    k = (filtersize - 1) // 2
    y = np.zeros((len(seq), filtersize), dtype=seq.dtype)
    y[:, k] = seq
    for i in range(k):
        j = k - i
        y[j:, i] = seq[:-j]
        y[:j, i] = seq[0]
        y[:-j, -(i + 1)] = seq[j:]
        y[-j:, -(i + 1)] = seq[-1]
    return mode(y, axis=1)[0]

import itertools
import logging
import string
from collections import Counter

import editdistance
from typing import List, Iterable, Optional, TypeVar, overload

import numpy as np

logger = logging.getLogger(__name__)


def matches(to_match: str, possible_matches: List[str], ignore_spaces=True, ignore_case=True, ignore_symbols=True) -> List[float]:
    r = []
    for s in possible_matches:
        if s:
            # mean_len = (len(to_match) + len(s)) / 2
            # min_len = min(len(to_match), len(s))
            s1, s2 = s, to_match
            if ignore_symbols:
                s1 = ''.join(c for c in s1 if c in string.ascii_letters + string.digits + ' ')
                s2 = ''.join(c for c in s2 if c in string.ascii_letters + string.digits + ' ')
            if ignore_spaces:
                s1 = s1.replace(' ', '')
                s2 = s2.replace(' ', '')
            if ignore_case:
                s1 = s1.upper()
                s2 = s2.upper()
            r.append(editdistance.eval(s1, s2))
        else:
            r.append(float('inf'))
    return r


def matches_product(seq1: List[str], seq2: List[str]):
    return [
        editdistance.eval(s1, s2)
        for (s1, s2)
        in itertools.product(seq1, seq2)
    ]


def charcountmatch(s1: str, s2: str) -> int:
    cnt = Counter()
    for c in s1:
        cnt[c] += 1
    for c in s2:
        cnt[c] -= 1

    return sum(abs(v) for (c, v) in cnt.items())


def mmss_to_seconds(mmss: int) -> int:
    mm = mmss // 100
    ss = mmss % 100
    return mm * 60 + ss


T = TypeVar('T')
@overload
def best_match(text: str, options: Iterable[str], threshold=2, level: Optional[int]=logging.INFO) -> Optional[str]:
    ...
@overload
def best_match(text: str, options: Iterable[str], default: str, threshold=2, level: Optional[int]=logging.INFO) -> str:
    ...
@overload
def best_match(text: str, options: Iterable[str], choose_from: List[T], threshold=2, level: Optional[int]=logging.INFO) -> Optional[T]:
    ...
@overload
def best_match(text: str, options: Iterable[str], choose_from: List[T], default: T, threshold=2, level: Optional[int]=logging.INFO) -> T:
    ...
def best_match(text: str, options, choose_from=None, default=None, threshold=2, level=logging.INFO, **kwargs):
    options = list(options)
    if choose_from is None:
        choose_from = options
    m = matches(text, options, **kwargs)
    index: int = np.argmin(m)
    if m[index] <= threshold:
        if level:
            logging.log(level, f'Matched "{text}" to "{options[index]}"->{repr(choose_from[index])} - match={m[index]}')
        return choose_from[index]
    else:
        logger.warning(f'Failed to find match for "{text}" in {options} - closest="{options[index]} with match={m[index]} - using default="{default}"')
        return default

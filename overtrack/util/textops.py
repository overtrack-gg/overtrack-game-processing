import itertools
import logging
import string
import typing
from collections import Counter
import Levenshtein as levenshtein
from typing import Any, Iterable, List, Optional, Sequence, Tuple, TypeVar, Union, no_type_check, overload

# import editdistance
import numpy as np

logger = logging.getLogger(__name__)


def matches(to_match: str, possible_matches: List[str], ignore_spaces: bool=True, ignore_case: bool=True, ignore_symbols: bool=True) -> List[float]:
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
            r.append(levenshtein.distance(s1, s2))
        else:
            r.append(float('inf'))
    return r

def matches_ratio(to_match: str, possible_matches: List[str]) -> Tuple[float, str]:
    best = 0, possible_matches[0]
    for s in possible_matches:
        if s:
            ratio = levenshtein.ratio(to_match, s)
            if ratio > best[0]:
                best = ratio, s
    return best


def matches_product(seq1: List[str], seq2: List[str]) -> List[List[str]]:
    return [
        levenshtein.distance(s1, s2)
        for (s1, s2)
        in itertools.product(seq1, seq2)
    ]


def charcountmatch(s1: str, s2: str) -> int:
    cnt: typing.Counter[str] = Counter()
    for c in s1:
        cnt[c] += 1
    for c in s2:
        cnt[c] -= 1

    return sum(abs(v) for (c, v) in cnt.items())


def mmss_to_seconds(mmss: int) -> int:
    mm = mmss // 100
    ss = mmss % 100
    return mm * 60 + ss


def strip_string(s: str, alphabet: str=string.digits + string.ascii_letters + '_') -> str:
    return ''.join(c for c in s if c in alphabet)


T = TypeVar('T')
@overload
def best_match(
        text: str,
        options: Iterable[str],
        default: str,
        threshold: int = 0,
        level: Optional[int] = 0) -> str:
    ...
@overload
def best_match(
        text: str,
        options: Iterable[str],
        threshold: int = 0,
        level: Optional[int] = 0) -> Optional[str]:
    ...
@overload
def best_match(
        text: str,
        options: Iterable[str],
        choose_from: Sequence[T],
        default: T,
        threshold: int = 0,
        level: Optional[int] = 0) -> T:
    ...
@overload
def best_match(
        text: str,
        options: Iterable[str],
        choose_from: Sequence[T],
        threshold: int = 0,
        level: Optional[int] = 0) -> Optional[T]:
    ...
@no_type_check
def best_match(
        text: str,
        options: Iterable[str],
        choose_from: Optional[Sequence[T]]=None,
        default: Union[str, T, None]=None,
        threshold: int=2,
        level: Optional[int]=logging.INFO,
        **kwargs: Any) -> Optional[Union[T, str]]:
    options = list(options)
    m = matches(text, options, **kwargs)
    index: int = np.argmin(m)
    if m[index] <= threshold:
        if level:
            logging.log(level, f'Matched "{text}" to "{options[index]}"->{repr((choose_from or options)[index])} - match={m[index]}')
        if choose_from is not None:
            return choose_from[index]
        else:
            return options[index]
    else:
        logger.warning(f'Failed to find match for "{text}" in {options} - closest="{options[index]} with match={m[index]} - using default="{default}"')
        return default

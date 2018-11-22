import itertools
from collections import Counter

import editdistance
from typing import List


def matches(to_match: str, possible_matches: List[str]) -> List[float]:
    r = []
    for s in possible_matches:
        if s:
            # mean_len = (len(to_match) + len(s)) / 2
            # min_len = min(len(to_match), len(s))
            r.append(editdistance.eval(to_match, s))
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

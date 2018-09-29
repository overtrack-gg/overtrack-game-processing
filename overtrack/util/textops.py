import editdistance
from typing import List


def matches(to_match: str, possible_matches: List[str]) -> List[float]:
    r = []
    for s in possible_matches:
        if s:
            mean_len = (len(to_match) + len(s)) / 2
            min_len = min(len(to_match), len(s))
            r.append(editdistance.eval(to_match, s) / 1)
        else:
            r.append(float('inf'))
    return r
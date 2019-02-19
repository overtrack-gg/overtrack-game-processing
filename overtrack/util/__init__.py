import datetime
import string
import time
from functools import wraps
from typing import Any, Callable, List, Iterable, Tuple

import numpy as np


def humansize(nbytes, suffixes=('B', 'KB', 'MB', 'GB', 'TB', 'PB')):
    # http://stackoverflow.com/a/14996816
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def s2ts(s, ms=False, zpad=True):
    sign = ''
    if s < 0:
        sign = '-'
        s = -s
    m = s / 60
    h = m / 60
    if zpad or int(h):
        ts = '%s%02d:%02d:%02d' % (sign, h, m % 60, s % 60)
    else:
        ts = '%s%02d:%02d' % (sign, m % 60, s % 60)
    if ms:
        return ts + f'{s % 1 :1.3f}'[1:]
    else:
        return ts


def ms2ts(ms):
    return s2ts(ms / 1000)


def ts2s(ts):
    h, m, s = ts.split(':')
    h, m, s = int(h), int(m), int(s)
    m = m + 60 * h
    s = m * 60 + s
    return s


def ts2ms(ts):
    return ts2s(ts) * 1000


def dhms2timedelta(s):
    td = datetime.timedelta()
    current = ''
    for c in s:
        if c.isdigit():
            current += c
        else:
            if c == 'd':
                td += datetime.timedelta(days=int(current))
            elif c == 'h':
                td += datetime.timedelta(hours=int(current))
            elif c == 'm':
                td += datetime.timedelta(minutes=int(current))
            elif c == 's':
                td += datetime.timedelta(seconds=int(current))
            else:
                raise ValueError('Unknown timedelta specifier "%s"', c)
            current = ''
    return td


def time_processing(process: Callable[[Any, Any, ], bool]):
    @wraps(process)
    def timed_process(self: Any, frame: Any) -> bool:
        t0 = time.time()
        result = process(self, frame)
        t1 = time.time()
        frame.timings[self.__class__.__name__] = (t1 - t0) * 1000
        return result
    return timed_process


def strip_string(s, alphabet=string.digits+string.ascii_letters+'_'):
    return ''.join(c for c in s if c in alphabet)


def argmax(a: Iterable[float]) -> int:
    return int(np.argmax(a))


def html2bgr(code: str) -> Tuple[int, int, int]:
    r1, r2, g1, g2, b1, b2 = code[1:]
    return int(b1 + b2, 16), int(g1 + g2, 16), int(r1 + r2, 16)


def bgr2html(color: Tuple[int, int, int]):
    return '#' + ''.join(f'{c:02x}' for c in color[::-1])

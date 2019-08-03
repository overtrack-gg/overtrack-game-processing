import datetime
import logging
import time
from functools import wraps
from typing import Callable, Tuple, TypeVar, TYPE_CHECKING
if TYPE_CHECKING:
    from overtrack.frame import Frame

logger = logging.getLogger(__name__)


def humansize(nbytes: float, suffixes: Tuple[str, ...]=('B', 'KB', 'MB', 'GB', 'TB', 'PB')) -> str:
    # http://stackoverflow.com/a/14996816
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def s2ts(s: float, ms: bool=False, zpad: bool=True) -> str:
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


def ms2ts(ms: float) -> str:
    return s2ts(ms / 1000)


def ts2s(ts: str) -> int:
    hs, ms, ss = ts.split(':')
    h, m, s = int(hs), int(ms), int(ss)
    m = m + 60 * h
    s = m * 60 + s
    return s


def ts2ms(ts: str) -> int:
    return ts2s(ts) * 1000


def dhms2timedelta(s: str) -> datetime.timedelta:
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


T = TypeVar('T')


def time_processing(process: Callable[[T, 'Frame'], bool]) -> Callable[[T, 'Frame'], bool]:
    @wraps(process)
    def timed_process(self: T, frame: 'Frame') -> bool:
        t0 = time.time()
        result = process(self, frame)
        t1 = time.time()
        name = self.__class__.__name__
        if name in frame.timings:
            name = name + '.2'
        frame.timings[name] = (t1 - t0) * 1000
        return result
    return timed_process


def bgr2html(color: Tuple[int, int, int]) -> str:
    return '#' + ''.join(f'{c:02x}' for c in color[::-1])


def html2bgr(hex_str: str) -> Tuple[int, int, int]:
    if hex_str[0] == '#':
        hex_str = hex_str[1:]
    return int(hex_str[4:6], 16), int(hex_str[2:4], 16), int(hex_str[0:2], 16)


def test_processor(directory: str, proc, *fields: str) -> None:
    import glob
    import cv2
    from pprint import pprint
    from overtrack.frame import Frame

    logging.basicConfig(level=logging.DEBUG)

    for p in glob.glob(f"C:/Users/simon/overtrack_2/overwatch_images/{directory}/*.png") + \
             glob.glob("C:/Users/simon/overtrack_2/overwatch_images/*/*.png", recursive=True):

        im = cv2.imread(p)
        im = cv2.resize(im, (1920, 1080))
        f = Frame.create(im, 0, debug=True)
        proc.process(f)
        for n in fields:
            print(f.get(n))
        pprint(f.timings)
        cv2.imshow('debug', f.debug_image)
        cv2.waitKey(0)

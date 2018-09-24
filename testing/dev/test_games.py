import sys

import cv2
import os
import logging
from pprint import pprint
from typing import NamedTuple, List
import tensorflow as tf

from overtrack.collect.game import Game
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.loading_map import LoadingMapProcessor
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import ts2s, s2ts
from overtrack.util.frames_cache import CachedFrameExtractor, FramesCache


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Kill(NamedTuple):
    ts: str
    left_name: str
    right_name: str
    res: bool = False


class ExpectedGame(NamedTuple):
    path: str
    killfeed: List[Kill]
    start: str = None
    stop: str = None


MUON = 'MUON'
ORITHETOAST = 'ORITHETOAST'
GINJERSPICE = 'GINJERSPICE'
NIPPLEBUTTER = 'NIPPLEBUTTER'
SUBD = 'SUBD'
THEILLEGAL = 'THEILLEGAL'
ZIPPERWEASEL = 'ZIPPERWEASEL'
JANGLEZ = 'JANGLEZ'
YXNOH = 'YXNOH'
BOOP = 'BOOP'
IHOOKYOUSOOK = 'IHOOKYOUSOOK'
MERRIS = 'MERRIS'

HEROES = {
    MUON: ['mercy'],
    ORITHETOAST: ['doomfist'],
    GINJERSPICE: ['widowmaker', 'hanzo'],
    NIPPLEBUTTER: ['junkrat'],
    SUBD: ['brigitte'],
    THEILLEGAL: ['soldier'],

    ZIPPERWEASEL: ['lucio', 'hammond'],
    JANGLEZ: ['genji', 'hanzo', 'sombra'],
    YXNOH: ['soldier'],
    BOOP: ['dva', 'dva.mech'],
    IHOOKYOUSOOK: ['symmetra', 'symmetra.teleporter'],
    MERRIS: ['mercy']
}

expected = ExpectedGame(
    path="C:/scratch/8res.mp4",
    killfeed=[
        Kill('0:00:00',     MERRIS,             ORITHETOAST),
        Kill('0:00:00',     MUON,               ORITHETOAST, True),
        Kill('0:00:15',     NIPPLEBUTTER,       IHOOKYOUSOOK),
        Kill('0:00:20',     GINJERSPICE,        ZIPPERWEASEL),
        Kill('0:00:22',     IHOOKYOUSOOK,       MUON),
        Kill('0:00:22',     ORITHETOAST,        IHOOKYOUSOOK),
        Kill('0:00:32',     MERRIS,             ZIPPERWEASEL, True),
        Kill('0:00:32',     BOOP,               GINJERSPICE),
        Kill('0:00:32',     BOOP,               THEILLEGAL),
        Kill('0:00:33',     NIPPLEBUTTER,       JANGLEZ),
        Kill('0:00:39',     BOOP,               NIPPLEBUTTER),

        Kill('0:01:00',     ORITHETOAST,        YXNOH),
        Kill('0:01:13',     IHOOKYOUSOOK,       ORITHETOAST),
        Kill('0:01:17',     MUON,               ORITHETOAST, True),
        Kill('0:01:20',     GINJERSPICE,        JANGLEZ),
        Kill('0:01:21',     IHOOKYOUSOOK,       NIPPLEBUTTER),
        Kill('0:01:33',     THEILLEGAL,         YXNOH),
        Kill('0:01:43',     MERRIS,             YXNOH, True),
        Kill('0:01:49',     SUBD,               IHOOKYOUSOOK),
        Kill('0:01:51',     THEILLEGAL,         YXNOH),

        Kill('0:02:00',     GINJERSPICE,        JANGLEZ),
        Kill('0:02:01',     BOOP,               THEILLEGAL),
        Kill('0:02:01',     BOOP,               MUON),
        Kill('0:02:10',     IHOOKYOUSOOK,       ORITHETOAST),
        Kill('0:02:17',     IHOOKYOUSOOK,       NIPPLEBUTTER),
        Kill('0:02:19',     IHOOKYOUSOOK,       GINJERSPICE),
        Kill('0:02:26',     MUON,               NIPPLEBUTTER, True),
        Kill('0:02:29',     YXNOH,              MUON),
        Kill('0:02:29',     BOOP,               SUBD),
        Kill('0:02:29',     YXNOH,              THEILLEGAL),
        Kill('0:02:34',     YXNOH,              ORITHETOAST),
        Kill('0:02:34',     NIPPLEBUTTER,       YXNOH),
        Kill('0:02:34',     NIPPLEBUTTER,       JANGLEZ),
        Kill('0:02:37',     MERRIS,             YXNOH, True),
        Kill('0:02:40',     BOOP,               NIPPLEBUTTER),
        Kill('0:02:55',     THEILLEGAL,         ZIPPERWEASEL),
        Kill('0:02:59',     ORITHETOAST,        YXNOH),

        Kill('00:03:09',    MERRIS,             YXNOH, True),
        Kill('00:03:17',    ORITHETOAST,        JANGLEZ),
        Kill('00:03:17',    GINJERSPICE,        IHOOKYOUSOOK),
        Kill('00:03:19',    THEILLEGAL,         BOOP),
        Kill('00:03:31',    ORITHETOAST,        BOOP),
        Kill('00:03:33',    ORITHETOAST,        YXNOH),
        Kill('00:03:36',    MERRIS,             GINJERSPICE),
        Kill('00:03:41',    THEILLEGAL,         ZIPPERWEASEL),
        Kill('00:03:46',    JANGLEZ,            NIPPLEBUTTER),
        Kill('00:03:46',    MUON,               GINJERSPICE, True),
        Kill('00:03:47',    THEILLEGAL,         IHOOKYOUSOOK),
        Kill('00:03:48',    IHOOKYOUSOOK,       THEILLEGAL),

        Kill('00:04:17',    THEILLEGAL,         YXNOH),
        Kill('00:04:29',    GINJERSPICE,        ZIPPERWEASEL),
        Kill('00:04:33',    BOOP,               NIPPLEBUTTER),
        Kill('00:04:34',    ORITHETOAST,        IHOOKYOUSOOK),
        Kill('00:04:37',    YXNOH,              ORITHETOAST),
        Kill('00:04:39',    MERRIS,             IHOOKYOUSOOK, True),
        Kill('00:04:40',    SUBD,               MERRIS),
        Kill('00:04:42',    MUON,               ORITHETOAST, True),
        Kill('00:04:43',    YXNOH,              GINJERSPICE),
        Kill('00:04:45',    YXNOH,              SUBD),
        Kill('00:04:47',    THEILLEGAL,         IHOOKYOUSOOK),
        Kill('00:04:48',    ORITHETOAST,        YXNOH),

        Kill('00:05:14',    YXNOH,              GINJERSPICE),
        Kill('00:05:22',    SUBD,               ZIPPERWEASEL),
        Kill('00:05:27',    MERRIS,             ZIPPERWEASEL, True),
        Kill('00:05:32',    ORITHETOAST,        YXNOH),
        Kill('00:05:34',    THEILLEGAL,         JANGLEZ),
        Kill('00:05:39',    SUBD,               IHOOKYOUSOOK),
        Kill('00:05:53',    THEILLEGAL,         BOOP),
        Kill('00:05:55',    THEILLEGAL,         BOOP),

        Kill('00:06:22',    NIPPLEBUTTER,       IHOOKYOUSOOK),
        Kill('00:06:28',    ORITHETOAST,        JANGLEZ),
        Kill('00:06:31',    NIPPLEBUTTER,       MERRIS),
        Kill('00:06:31',    NIPPLEBUTTER,       ZIPPERWEASEL),
        Kill('00:06:33',    SUBD,               YXNOH),
        Kill('00:06:38',    ORITHETOAST,        IHOOKYOUSOOK),

        Kill('00:07:04',    GINJERSPICE,        BOOP),
        Kill('00:07:06',    YXNOH,              NIPPLEBUTTER),
        Kill('00:07:06',    ORITHETOAST,        ZIPPERWEASEL),
        Kill('00:07:10',    YXNOH,              THEILLEGAL),
        Kill('00:07:14',    MUON,               THEILLEGAL, True),
        Kill('00:07:17',    MERRIS,             ZIPPERWEASEL, True),
        Kill('00:07:19',    JANGLEZ,            SUBD),
        Kill('00:07:19',    ORITHETOAST,        YXNOH),
        Kill('00:07:19',    IHOOKYOUSOOK,       ORITHETOAST),
        Kill('00:07:23',    IHOOKYOUSOOK,       THEILLEGAL),
        Kill('00:07:27',    JANGLEZ,            MUON),
        Kill('00:07:40',    YXNOH,              NIPPLEBUTTER),
        Kill('00:07:49',    THEILLEGAL,         BOOP),
        Kill('00:07:52',    YXNOH,              ORITHETOAST),
        Kill('00:07:54',    IHOOKYOUSOOK,       SUBD),
        Kill('00:07:55',    MUON,               ORITHETOAST, True),
        Kill('00:07:56',    IHOOKYOUSOOK,       THEILLEGAL),

        Kill('00:08:01',    YXNOH,              GINJERSPICE),
        Kill('00:08:08',    YXNOH,              NIPPLEBUTTER),
        Kill('00:08:09',    BOOP,               MUON),
        Kill('00:08:10',    ORITHETOAST,        YXNOH),
        Kill('00:08:20',    JANGLEZ,            ORITHETOAST),
        Kill('00:08:20',    MERRIS,             YXNOH, True),
        Kill('00:08:35',    IHOOKYOUSOOK,       NIPPLEBUTTER),
        Kill('00:08:38',    MUON,               NIPPLEBUTTER, True),
        Kill('00:08:40',    JANGLEZ,            ORITHETOAST),
        Kill('00:08:47',    YXNOH,              MUON),
        Kill('00:08:50',    NIPPLEBUTTER,       YXNOH),
        Kill('00:08:52',    BOOP,               SUBD),
        Kill('00:08:53',    MERRIS,             YXNOH, True),
        Kill('00:08:57',    YXNOH,              THEILLEGAL),
        Kill('00:09:01',    NIPPLEBUTTER,       BOOP),
        Kill('00:09:01',    ORITHETOAST,        ZIPPERWEASEL),
        Kill('00:09:03',    YXNOH,              NIPPLEBUTTER),
        Kill('00:09:07',    BOOP,               GINJERSPICE),
    ]
    # stop='0:04:0'
)


def errout(s='', *args):
    if len(args):
        s = str(s) % args
    else:
        s = str(s)
    sys.stderr.write(s + '\n')


def main(debug=False):
    extractor = None
    pipeline = []
    cache = None
    if os.path.exists('cache.py') and not debug:
        try:
            extractor = CachedFrameExtractor('./cache.py')
        except Exception as e:
            logger.exception('Unable to load cached frames', exc_info=e)
    if not extractor:
        extractor = VideoFrameExtractor(expected.path, debug_frames=debug, seek=s2ts(expected.start) if expected.start else None)
        pipeline = [KillfeedProcessor()]
        cache = FramesCache('./cache.py')

    frames = []
    while True:
        frame = extractor.get()
        if frame is None:
            break
        for p in pipeline:
            p.process(frame)

        if debug:
            im = cv2.resize(frame.debug_image, (1280, 720))

        frame.strip()
        if cache:
            cache.add(frame)
        frames.append(frame)
        if cache:
            print(frame.timestamp_str)
        if expected.stop and frame.relative_timestamp > ts2s(expected.stop):
            break

        if debug:
            cv2.imshow('frame', im)
            # cv2.waitKey(0)
            if cv2.waitKey(0) == 27:
                break

    cv2.destroyAllWindows()

    if cache:
        cache.close()

    game = Game(frames, LoadingMapProcessor.Teams(
        [MUON, ORITHETOAST, GINJERSPICE, NIPPLEBUTTER, SUBD, THEILLEGAL],
        [ZIPPERWEASEL, JANGLEZ, YXNOH, BOOP, IHOOKYOUSOOK, MERRIS],
        None
    ), required_rows=1)
    pprint((game.stats.blue, game.stats.red))

    print()
    for kill in game.killfeed:
        print(s2ts(kill.timestamp), '-', kill)
    print()
    sys.stdout.flush()
    sys.stderr.flush()

    def get_match(actual_kill: Game.Kill, expected_kill: Kill):
        mismatch = 0
        if actual_kill.right_name != expected_kill.right_name:
            mismatch += 50
        if actual_kill.right_hero not in HEROES[actual_kill.right_name]:
            mismatch += 10

        if expected_kill.left_name and not actual_kill.suicide:
            if actual_kill.left_name != expected_kill.left_name:
                mismatch += 50
            if actual_kill.left_hero not in HEROES[actual_kill.left_name]:
                mismatch += 10

        if actual_kill.resurrect != expected_kill.res:
            mismatch += 5

        # use an offset of less than 10s as less-than-1 mismatch
        offset = abs(ts2s(expected_kill.ts) - actual_kill.timestamp)
        mismatch += min(offset / 10, 15)

        return mismatch

    # check for kills that were not seen by the parser
    missed_kills = 0
    for kill in expected.killfeed:
        matches = sorted([(get_match(k, kill), k) for k in game.killfeed], key=lambda e: e[0])
        mismatch, best = matches[0]
        if mismatch > 1:
            missed_kills += 1
            errout('Could not find %s in video - possible matches: ', kill)
            for i in range(3):
                reason = ''
                if best.left_hero not in HEROES[kill.left_name]:
                    reason = f'left hero was {best.left_hero}, but {kill.left_name} only played {HEROES[kill.left_name]} - '
                elif best.right_hero not in HEROES[kill.right_name]:
                    reason = f'right hero was {best.right_hero}, but {kill.right_name} only played {HEROES[kill.right_name]} - '
                errout(f'\t{s2ts(matches[i][1].timestamp)} - {reason}match={matches[i][0] :1.1f} - {matches[i][1]}')
    if missed_kills:
        errout('Missed %d kills', missed_kills)
    else:
        errout('No missed kills')

    errout()
    # check for extra kills that should not be there
    extra_kills = 0
    seen = {}
    for i, kill in enumerate(game.killfeed):
        matches = sorted([(get_match(kill, e), e) for e in expected.killfeed], key=lambda e: e[0])
        mismatch, best = matches[0]
        matches_notseen = [e for e in matches if e[1] not in seen]
        if len(matches_notseen):
            mismatch_notseen, best_notseen = matches_notseen[0]
        else:
            mismatch_notseen, best_notseen = mismatch, None

        if mismatch_notseen > 1:
            extra_kills += 1
            errout('Found kill that should not exist at %s - %s', s2ts(kill.timestamp), kill)
            if best != best_notseen:
                state = 'matches'
                if mismatch > 1:
                    state = 'was similar'
                errout(f'\tkill at {best.ts} {state} ({mismatch :1.1f}), but this kill was already matched: {best} -> {s2ts(seen[best].timestamp)} - {seen[best]}')
        else:
            seen[best_notseen or best] = kill
    if extra_kills:
        errout('%d extra kills', extra_kills)
    else:
        errout('No extra kills')

    errout()

    for kill in game.killfeed:
        if len(kill.rows) < 4:
            errout(f'kill at {s2ts(kill.timestamp)} only had {len(kill.rows)} rows seen: {kill}')


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()

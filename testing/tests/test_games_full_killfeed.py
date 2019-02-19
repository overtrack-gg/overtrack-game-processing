import logging
import os
import sys
from pprint import pprint
from typing import List, NamedTuple, Optional

import cv2
import pytest
import tensorflow as tf

from overtrack.collect.game import Frame, Game
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.loading_map import LoadingMapProcessor
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import s2ts, ts2s

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ExpectedKill(NamedTuple):
    ts: str
    left_name: str
    right_name: str
    res: bool = False


class ExpectedGame(NamedTuple):
    path: str
    killfeed: List[ExpectedKill]
    start: Optional[str] = None
    stop: Optional[str] = None


def errout(s='', *args):
    if len(args):
        s = str(s) % args
    else:
        s = str(s)
    sys.stderr.write(s + '\n')


@pytest.fixture(scope='module', autouse=True)
def setup_tf():
    sess = tf.InteractiveSession(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0}))
    sess.as_default()
    global pipeline
    pipeline = KillfeedProcessor(output_icon_images=False, output_name_images=False)


from testing.tests.full_games import qp_8res, edgy_name


@pytest.mark.slow
@pytest.mark.parametrize('game_source', [
    qp_8res, edgy_name
], ids=lambda v: os.path.basename(v.game.path))
def test_full_game(game_source, debug=False):
    expected: ExpectedGame = game_source.game

    # extractor = None
    cache = None
    # if os.path.exists('cache.py') and not debug:
    #     try:
    #         extractor = CachedFrameExtractor('./cache.py')
    #     except Exception as e:
    #         logger.exception('Unable to load cached frames', exc_info=e)
    # if not extractor:
    extractor = VideoFrameExtractor(expected.path, debug_frames=debug, seek=s2ts(expected.start) if expected.start else None)
    #     cache = FramesCache('./cache.py')

    frames = []
    while True:
        frame = extractor.get()
        if frame is None:
            break
        # if cache:
        #     pipeline.process(frame)
        pipeline.process(frame)

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

    frames = [Frame(
        timestamp=-1,
        loading_map=LoadingMapProcessor.LoadingMap(
            'UNKNOWN',
            'TEST',
            LoadingMapProcessor.Teams(
                game_source.teams[0],
                game_source.teams[1],
                None
            ),
            None
        )
    )] + frames
    game = Game(frames)
    sys.stdout.flush()
    sys.stderr.flush()
    print('-' * 30)

    pprint((game.teams.blue, game.teams.red))

    print()
    for kill in game.killfeed:
        print(s2ts(kill.timestamp), '-', kill)
    print()
    sys.stdout.flush()
    sys.stderr.flush()

    def get_match(actual_kill, expected_kill: ExpectedKill):
        mismatch = 0
        if actual_kill.right.name != expected_kill.right_name:
            mismatch += 50
        if actual_kill.right.hero not in game_source.heroes[actual_kill.right.name]:
            mismatch += 10

        if expected_kill.left_name and not actual_kill.suicide:
            if actual_kill.suicide:
                mismatch += 100
            else:
                if actual_kill.left.name != expected_kill.left_name:
                    mismatch += 50
                if actual_kill.left.hero not in game_source.heroes[actual_kill.left.name]:
                    mismatch += 10

        if actual_kill.resurrect != expected_kill.res:
            mismatch += 5

        # use an offset of less than 10s as less-than-1 mismatch
        offset = abs(ts2s(expected_kill.ts) - actual_kill.timestamp)
        mismatch += min(offset / 10, 15)

        return mismatch

    # check for kills that were not seen by the parser
    missed_kills = 0
    for expected_kill in expected.killfeed:
        matches = sorted([(get_match(k, expected_kill), k) for k in game.killfeed], key=lambda e: e[0])
        mismatch, best = matches[0]
        if mismatch > 1:
            missed_kills += 1
            errout('Could not find %s in video - possible matches: ', expected_kill)
            for i in range(3):
                reason = ''
                if best.left.hero not in game_source.heroes[expected_kill.left_name]:
                    reason = f'left hero was {best.left.hero}, but {expected_kill.left_name} only played {game_source.heroes[expected_kill.left_name]} - '
                elif best.right.hero not in game_source.heroes[expected_kill.right_name]:
                    reason = f'right hero was {best.right.hero}, but {expected_kill.right_name} only played {game_source.heroes[expected_kill.right_name]} - '
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
                errout(
                    f'\tkill at {best.ts} {state} ({mismatch :1.1f}), '
                    f'but this kill was already matched: {best} -> {s2ts(seen[best].timestamp)} - {seen[best]}'
                )
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

    assert 0 == missed_kills
    assert 0 == extra_kills


# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#
#     logger.setLevel(logging.INFO)
#     with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
#         main()


if __name__ == '__main__':
    test_full_game(qp_8res)

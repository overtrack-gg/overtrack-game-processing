import os
import sys
from pprint import pprint

import pytest
import tensorflow as tf
from typing import NamedTuple, List

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.loading_map import LoadingMapProcessor
from overtrack.live_game import LiveGameStats
from overtrack.source.video import VideoFrameExtractor


class KillDeathCount(NamedTuple):
    name: str
    blue_team: bool
    hero: str = None
    kills: int = 0
    deaths: int = 0
    resurrects: int = 0


class ExpectedResult(NamedTuple):
    counts: List[KillDeathCount]


class VideoTest(NamedTuple):
    path: str
    expected: ExpectedResult
    fps: int = None
    add_other_side: bool = False


videos = [
    # test kills
    VideoTest(
        'killfeed_videos/winston_6k.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'winston', 6, 0),

            KillDeathCount('REAPER', False, 'reaper', 0, 1),
            KillDeathCount('ZARYA', False, 'zarya', 0, 1),
            KillDeathCount('ZENYATTA', False, 'zenyatta', 0, 1),
            KillDeathCount('SOLDIER76', False, 'soldier', 0, 1),
            KillDeathCount('ROADHOG', False, 'roadhog', 0, 1),
            KillDeathCount('LUCIO', False, 'lucio', 0, 1),
        ])
    ),

    # test killcam
    VideoTest(
        'killfeed_videos/killcam.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 0, 1),
            KillDeathCount('ZARYA', False, 'zarya', 1, 0),
        ]),
        add_other_side=True,
        fps=5  # Make sure the killcam frames are caught
    ),
    VideoTest(
        'killfeed_videos/death_killcam.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 0, 1),
            KillDeathCount('SOLDIER76', False, 'soldier', 1, 0),
        ]),
        add_other_side=True,
        fps=5
    ),
    VideoTest(
        'killfeed_videos/kill_death_killcam.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 1, 1),

            KillDeathCount('ZENYATTA', False, 'zenyatta', 1, 0),
            KillDeathCount('ROADHOG', False, 'roadhog', 0, 1),
        ]),
        add_other_side=True,
        fps=5
    ),
    VideoTest(
        'killfeed_videos/killcam_only.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 0, 1),
            KillDeathCount('PORTADIAM', True, 'brigitte', 0, 1),

            KillDeathCount('ROADHOG', False, 'roadhog', 1, 0),
            KillDeathCount('ZARYA', False, 'zarya', 1, 0),
        ]),
        add_other_side=True,
        fps=5
    ),

    # test res
    VideoTest(
        'killfeed_videos/res_bastion.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 0, 0, 0),
            KillDeathCount('PORTADIAM', True, 'mercy', 0, 0, 1),
        ])
    ),

    # test kill and res
    VideoTest(
        'killfeed_videos/killed_res_bastion.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 0, 1),
            KillDeathCount('PORTADIAM', True, 'mercy', 0, 0, 1),
            KillDeathCount('LUCIO', False, 'lucio', 1, 0),
        ])
    ),

    # test suicides
    VideoTest(
        'killfeed_videos/suicide_bastion.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 0, 1, 0),
        ])
    ),
    VideoTest(
        'killfeed_videos/double_suicide.mp4',
        ExpectedResult([
            KillDeathCount('MINININJA', True, 'bastion', 0, 1),
            KillDeathCount('PORTADIAM', True, 'mercy', 0, 1),
        ])
    )

    # TODO: suicide when killcam has info
    # this will result in kills detected on the killcam, but without the usual team perspective flip
]


def extract_stats(videofile, teams, fps=2):
    path = os.path.join(os.path.dirname(__file__), videofile)
    extractor = VideoFrameExtractor(path, extract_fps=fps)
    stats = LiveGameStats(teams=teams)
    while True:
        frame = extractor.get()
        if not frame:
            break
        elif isinstance(frame, Exception):
            raise frame

        pipeline.process(frame)
        if 'killfeed' in frame and len(frame.killfeed.kills):
            for kill in frame.killfeed.kills:
                print(' ' * 2, end='')
                if kill.left:
                    print('blue' if kill.left.blue_team else 'red ', kill.left.hero.ljust(10), kill.left.name.ljust(16), end=' | ')
                print('blue' if kill.right.blue_team else 'red ', kill.right.hero.ljust(10), kill.right.name, end='')
                if kill.from_killcam:
                    print(' *', end='')
                print()
            print()
        frame.strip()
        stats.feed(frame)

    return stats.get_stats()


@pytest.fixture(scope='module', autouse=True)
def setup_tf():
    sess = tf.InteractiveSession(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0}))
    sess.as_default()
    global pipeline
    pipeline = KillfeedProcessor(output_icon_images=False, output_name_images=False)


@pytest.mark.parametrize('video_test', videos, ids=lambda v: os.path.basename(v.path))
def test_killfeed_video(video_test: VideoTest):
    # video_test = videos[0]
    assert tf.get_default_session()

    blue_team = []
    red_team = []
    for player in video_test.expected.counts:
        if player.blue_team:
            blue_team.append(player.name)
        else:
            red_team.append(player.name)

    if video_test.add_other_side:
        # add the names from each side to the other
        # this will uncover kills being attributed to the wrong side
        # make the other teams names come first so a) the explicit "wrong team" bug is the first one reported
        # and b) code that could allow kills to bind to either team may be more likely to select the wrong team
        temp = blue_team
        blue_team = red_team + blue_team
        red_team = temp + red_team

    blue_team += [''] * (6 - len(blue_team))
    red_team += [''] * (6 - len(red_team))
    teams = LoadingMapProcessor.Teams(blue_team, red_team, None)

    print()
    print('Video:')
    print(os.path.basename(video_test.path))

    print('Kills:')
    blue_stats, red_stats = extract_stats(video_test.path, teams, fps=video_test.fps or 2)

    print('Stats:')
    f = lambda s: s.name
    pprint((blue_stats, red_stats))

    print('Expected stats:')
    pprint(video_test.expected.counts)
    print('-' * 32)

    for player in video_test.expected.counts:
        stats_containing_player = blue_stats if player.blue_team else red_stats
        assert player.name in [s.name for s in stats_containing_player]

    # check there are no stats returned that are not expected
    actual_stat: LiveGameStats.PlayerStats
    expected_player_names = [r.name for r in video_test.expected.counts]
    for blue_team, stats in (True, blue_stats), (False, red_stats):
        for actual_stat in stats:
            if not actual_stat.name:
                # ignore empty players
                continue

            assert actual_stat.name in expected_player_names, f'Did not expect to see stats for {actual_stat.name}'

            team_name = 'blue' if blue_team else 'red'

            matching_expected_players = [p for p in video_test.expected.counts if p.name == actual_stat.name and p.blue_team == blue_team]
            if not len(matching_expected_players) and video_test.add_other_side:
                # this was a fake player added to test if kills would me missatributed to the wrong team during killcams
                assert 0 == actual_stat.kills, \
                    f'Attributed kill(s) to the wrong team: said {actual_stat.name} on {team_name} team ' \
                    f'playing {actual_stat.current_hero} had {actual_stat.kills} kill, but {actual_stat.name} was not on this team'
                assert 0 == actual_stat.deaths, \
                    f'Attributed deaths(s) to the wrong team: said {actual_stat.name} on {team_name} team ' \
                    f'playing {actual_stat.current_hero} had {actual_stat.deaths} death, but {actual_stat.name} was not on this team'
                assert 0 == actual_stat.deaths, \
                    f'Attributed resurrects(s) to the wrong team: said {actual_stat.name} on {team_name} team ' \
                    f'playing {actual_stat.current_hero} had {actual_stat.resurrects} resurrects, but {actual_stat.name} was not on this team'
            else:
                if len(matching_expected_players) != 1:
                    assert False, f'Found {team_name} player {actual_stat.name} in stats, but was not in expected stats: ' \
                                  f'{[("blue" if e.blue_team else "red") + " player " + e.name for e in video_test.expected.counts]}'

                expected_stat = matching_expected_players[0]

                name = 'blue' if expected_stat.blue_team else 'red'
                name += ' player ' + expected_stat.name
                assert expected_stat.kills == actual_stat.kills, \
                    f'Expected {name} to have {expected_stat.kills} kills but had {actual_stat.kills}'
                assert expected_stat.deaths == actual_stat.deaths, \
                    f'Expected {name} to have {expected_stat.deaths} deaths but had {actual_stat.deaths}'
                assert expected_stat.resurrects == actual_stat.resurrects, \
                    f'Expected {name} to have {expected_stat.resurrects} resurrects but had {actual_stat.resurrects}'
                assert expected_stat.hero == actual_stat.current_hero, \
                    f'Expected {name} to have hero {expected_stat.hero} but saw {actual_stat.current_hero}'

    # check each expected stat is accounted for
    expected_kd: KillDeathCount
    for expected_kd in video_test.expected.counts:
        team_containing_player = blue_stats if expected_kd.blue_team else red_stats
        assert expected_kd.name in [p.name for p in team_containing_player]

        expected_stats = [p for p in team_containing_player if p.name == expected_kd.name]
        assert 1 == len(expected_stats)
        expected = expected_stats[0]

        assert expected_kd.kills == expected.kills
        assert expected_kd.deaths == expected.deaths
        assert expected_kd.hero == expected.current_hero


if __name__ == '__main__':
    raise RuntimeError('Run with py.test')

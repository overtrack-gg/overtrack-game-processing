import datetime
import hashlib
import logging
import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, Union

import Levenshtein as levenshtein
import numpy as np
import shortuuid
import typedload
from dataclasses import dataclass

from overtrack.apex import data
from overtrack.apex.collect.apex_game.combat import Combat
from overtrack.apex.collect.apex_game.rank import Rank
from overtrack.apex.collect.apex_game.route import Route
from overtrack.apex.collect.apex_game.squad import Squad
from overtrack.apex.collect.apex_game.weapons import Weapons
from overtrack.frame import Frame
from overtrack.util import arrayops, s2ts


class ApexGame:
    logger = logging.getLogger('ApexGame')

    def __init__(
            self,
            frames: List[Frame],
            key: str = None,
            stats_before: Optional[List[Tuple[str, Dict[str, Dict]]]] = None,
            stats_after: Optional[List[Tuple[str, Dict[str, Dict]]]] = None,
            champion: Optional[Dict] = None,
            scrims: Optional[str] = None,
            debug: Union[bool, str] = False):

        self.scrims = scrims
        self.champion = champion

        game_times = [f for f in frames if 'game_time' in f]
        if len(game_times):
            self.match_started = int(game_times[0].timestamp)
        else:
            self.match_started = int(frames[0].timestamp + 180)
        if self.champion:
            match_started_offset = self.match_started % 60

            rounded_match_started = int(self.match_started / 60 + 0.5) * 60
            alt_match_started = rounded_match_started + (1 if match_started_offset > 30 else -1) * 60

            started_datetime = datetime.datetime.utcfromtimestamp(rounded_match_started)
            self.match_id = started_datetime.strftime('%Y-%m-%d-%H-%M') + '/' + self.champion['ocr_name']
            self.match_ids = [
                self.match_id,
                datetime.datetime.utcfromtimestamp(alt_match_started).strftime('%Y-%m-%d-%H-%M') + '/' + self.champion['ocr_name']
            ]
        else:
            self.match_id = None
            self.match_ids = [None, None]

        your_squad_first_index = 0
        your_squad_last_index = 0
        for i, f in enumerate(frames):
            if 'your_squad' in f or 'your_selection' in f:
                if not your_squad_first_index:
                    your_squad_first_index = i
                your_squad_last_index = i

        self.solo = any('your_selection' in f for f in frames)
        if self.solo and any('your_squad' in f for f in frames):
            self.logger.error(f'Got game with both "your_selection" and "your_squad"')

        duos_frames = len([f for f in frames if ('your_squad' in f and f.your_squad.mode == 'duos') or ('champion_squad' in f and f.champion_squad.mode == 'duos')])
        selection_frames = len([f for f in frames if 'your_squad' in f or 'champion_squad' in f])
        self.logger.info(f'Got {duos_frames}/{selection_frames} confirming game as duos')
        self.duos = duos_frames > selection_frames * 0.5

        self.squad_count = 20
        if self.solo:
            self.logger.info(f'Game is solos game')
            self.squad_count = 60
        elif self.duos:
            self.logger.info(f'Game is duos game')
            self.squad_count = 30

        self.menu_frames = [f.apex_play_menu for f in frames if 'apex_play_menu' in f]
        menu_names = [apex_play_menu.player_name for apex_play_menu in self.menu_frames]
        self.logger.info(f'Processing game from {len(frames) - your_squad_first_index} frames and {len(menu_names)} menu frames')

        self.player_name = levenshtein.median(menu_names)
        self.logger.info(f'Resolved player name={repr(self.player_name)} from menu frames')

        game_end_index = len(frames) - 1
        for i in range(game_end_index, 0, -1):
            if 'match_status' in frames[i]:
                self.logger.info(
                    f'Found last match_status at {i} -> {s2ts(frames[i].timestamp - frames[your_squad_first_index].timestamp)}: '
                    f'pulling end back from {game_end_index} -> {s2ts(frames[-1].timestamp - frames[your_squad_first_index].timestamp)}. '
                    f'{(game_end_index + 10) - i} frames dropped'
                )
                game_end_index = i
                break
        else:
            self.logger.warning(f'Did not see match_status - not trimming')

        self.frames = frames[your_squad_first_index:game_end_index]
        self.all_frames = frames[your_squad_first_index:]
        self.timestamp = round(frames[your_squad_last_index].timestamp, 2) + 10.  # CHAMPION SQUAD takes 10s after YOUR SQUAD, then dropship launches
        self.duration = round(self.frames[-1].timestamp - self.frames[0].timestamp, 2)
        self.logger.info(
            f'Relative start: {s2ts(self.frames[0].timestamp - frames[0].timestamp)}, '
            f'relative end: {s2ts(self.frames[-1].timestamp - frames[0].timestamp)}'
        )
        self.logger.info(f'Started={self.time}, duration={s2ts(self.duration)}')

        if key:
            self.key = key
        else:
            datetimestr = datetime.datetime.utcfromtimestamp(self.timestamp).strftime('%Y-%m-%d-%H-%M')
            self.key = f'{datetimestr}-{shortuuid.uuid()[:6]}'

        self.match_status_frames = [
            f.match_status
            for f in self.frames
            if 'match_status' in f and (f.match_status.squads_left is not None or f.match_status.solos_players_left is not None)
        ]
        self.squad_summary_frames = [f.squad_summary for f in self.all_frames if 'squad_summary' in f]
        self.match_summary_frames = [f.match_summary for f in self.all_frames if 'match_summary' in f]

        self.placed = self._get_placed(debug)

        config_name: Optional[str] = None
        for frame in self.frames:
            if 'apex_metadata' in frame:
                config_name = frame.apex_metadata.player_config_name
                self.player_name = config_name
                self.logger.info(f'Got player name from config: "{config_name}"')

        self.squad = Squad(self.all_frames, menu_names, config_name, stats_before, stats_after, solo=self.solo, duos=self.duos, debug=debug)
        self.combat = Combat(self.frames, self.placed, self.squad, debug=debug)
        self.weapons = Weapons(self.frames, self.combat, debug=debug)
        self.route: Route = Route(self.frames, self.weapons, self.combat, season=self.season, debug=debug)
        # self.stats = Stats(frames, self.squad)  # TODO: stats using match summary

        if self.squad.player and self.squad.player.stats and self.squad.player.stats.kills is not None:
            self.kills = self.squad.player.stats.kills
            self.logger.info(f'Using kills from stats: kills={self.kills}')
        else:
            self.kills = max(
                self._get_match_state_kills(debug) or 0,
                len(self.combat.eliminations),
            )

        if len(self.match_status_frames):
            rank_matches = sum(match_status.rank_text is not None for match_status in self.match_status_frames)
            rank_matches_p = rank_matches / len(self.match_status_frames)
        else:
            rank_matches = 0
            rank_matches_p = 0
        self.logger.info(f'Got {rank_matches_p * 100:.0f}% ({rank_matches}/{len(self.match_status_frames)}) of match status frames claiming ranked')
        if rank_matches_p > 0.8 and rank_matches > 10:
            self.rank: Optional[Rank] = Rank(
                self.menu_frames,
                self.match_status_frames,
                self.placed,
                self.kills,
                self.squad.player.name,
                stats_before,
                stats_after,
                debug=debug
            )
        else:
            self.rank: Optional[Rank] = None

        self.mode = 'unranked'
        if self.rank is not None:
            self.mode = 'ranked'
        elif self.solo:
            self.mode = 'solo'
        elif self.duos:
            self.mode = 'duos'

        self.images = {}
        for f in frames:
            if 'your_squad' in f and f.your_squad.images:
                self.images['your_squad'] = f.your_squad.images.url
            if 'your_selection' in f and f.your_selection.image:
                self.images['your_selection'] = f.your_selection.image.url
            if 'champion_squad' in f and f.champion_squad.images:
                self.images['champion_squad'] = f.champion_squad.images.url
            if 'match_summary' in f and f.match_summary.image:
                self.images['match_summary'] = f.match_summary.image.url
            if 'squad_summary' in f and f.squad_summary.image:
                self.images['squad_summary'] = f.squad_summary.image.url

    def _get_placed(self, debug: Union[bool, str] = False) -> int:
        self.logger.info(f'Getting squad placement from '
                         f'{len(self.match_summary_frames)} summary frames, '
                         f'{len(self.squad_summary_frames)} squad summary frames, '
                         f'{len(self.match_status_frames)} match status frames')

        match_summary_placed: Optional[int] = None
        match_summary_count = 0
        if len(self.match_summary_frames):
            placed_values = [s.placed for s in self.match_summary_frames]
            placed_counter = Counter(placed_values)
            placed_counter_dict = dict(placed_counter.most_common())
            self.logger.info(f'Got match_summary.placed={placed_counter}')
            count = None
            for e in placed_values[::-1]:
                if 1 <= e <= self.squad_count:
                    match_summary_placed = e
                    count = placed_counter_dict[match_summary_placed]
                    break
                else:
                    self.logger.warning(f'Ignoring match_summary.placed={e} - not in range')
            if match_summary_placed:
                if count != len(self.match_summary_frames):
                    self.logger.warning(f'Got disagreeing match summary placed counts: {placed_counter}')
                self.logger.info(f'Got match summary > placed={match_summary_placed} from summary')
                match_summary_count = count
        if not match_summary_placed:
            self.logger.info(f'Did not get (valid) match summary placement')

        squad_summary_placed: Optional[int] = None
        squad_summary_count = 0
        if len(self.squad_summary_frames) and not self.solo:
            # TODO: support solo (change crop regions and use the squad kills as placed_
            champions = np.mean([s.champions for s in self.squad_summary_frames])
            if champions > 0.75:
                self.logger.info(f'Got champions={champions:1.1f} from squad summary - using placed = 1')
                return 1

            placed_vals = [s.placed for s in self.squad_summary_frames if s.placed]
            if len(placed_vals):
                placed_counter = Counter(placed_vals)
                self.logger.info(f'Got squad_summary.placed={placed_counter}')
                count = None
                for e in placed_counter.most_common():
                    if e[0] == 1 and champions < 0.25:
                        self.logger.warning(f'Ignoring squad_summary.placed=1 - champion={champions:.2f}')
                    elif 1 <= e[0] <= self.squad_count:
                        squad_summary_placed, count = e
                        break
                    else:
                        self.logger.warning(f'Ignoring squad_summary.placed={e[0]} - not in range')
                if squad_summary_placed:
                    if count != len(self.squad_summary_frames):
                        self.logger.warning(f'Got disagreeing squad summary placed counts: {placed_counter}')
                    self.logger.info(f'Got squad summary > placed = {squad_summary_placed}')
                    squad_summary_count = count
        if not squad_summary_placed:
            self.logger.info(f'Did not get (valid) squad summary placement')

        if len(self.match_status_frames) > 10:
            # TODO: record this plot as edges
            squads_alive = arrayops.modefilt([s.squads_left if s.squads_left is not None else s.solos_players_left for s in self.match_status_frames], 5)
            last_squads_alive = int(squads_alive[-1])
            if 1 <= last_squads_alive <= self.squad_count:
                self.logger.info(f'Got last seen squads alive = {last_squads_alive}')
            else:
                self.logger.info(f'Did not get valid last seen squads alive: {last_squads_alive}')
                last_squads_alive = None
        else:
            self.logger.warning(f'Did not get any match summaries - last seen squads alive = 20')
            last_squads_alive = self.squad_count

        if debug in [True, 'Placed']:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.title('Squads Alive')
            plt.plot(squads_alive)
            plt.show()

        if match_summary_placed and squad_summary_placed and match_summary_placed != squad_summary_placed:
            self.logger.warning(
                f'Got match summary > placed: {match_summary_placed} ({match_summary_count}) != '
                f'squad summary > placed: {squad_summary_placed} ({squad_summary_count})'
            )
            # # self.logger.warning(f'Got match summary > placed != squad summary > placed', exc_info=True)
            # if squad_summary_count > 3:
            #     return squad_summary_placed
            # elif match_summary_count > 3:
            #     return ma

        if match_summary_count > 3:
            self.logger.info(f'Using placed from match summary: {match_summary_placed} ({match_summary_count})')
            return match_summary_placed
        elif squad_summary_count > 3:
            self.logger.info(f'Using placed from squad summary: {squad_summary_placed} ({squad_summary_count})')
            return squad_summary_placed
        elif match_summary_count > 1:
            self.logger.info(f'Using placed from match summary: {match_summary_placed} ({match_summary_count})')
            return match_summary_placed
        elif squad_summary_count > 1:
            self.logger.info(f'Using placed from squad summary: {squad_summary_placed} ({squad_summary_count})')
            return squad_summary_placed
        elif match_summary_count:
            self.logger.info(f'Using placed from match summary: {match_summary_placed} ({match_summary_count})')
            return match_summary_placed
        elif squad_summary_count:
            self.logger.info(f'Using placed from squad summary: {squad_summary_placed} ({squad_summary_count})')
            return squad_summary_placed
        else:
            self.logger.info(f'Using placed from last squads alive: {last_squads_alive}')
            return last_squads_alive

    def _get_match_state_kills(self, debug: Union[bool, str] = False) -> int:
        kills_seen = [s.kills for s in self.match_status_frames if s.kills]
        self.logger.info(
            f'Getting kills from {len(self.match_status_frames)} match status frames with {len(kills_seen)} killcounts seen'
        )

        if len(kills_seen) > 10:
            kills_seen = arrayops.modefilt(kills_seen, 5)

            if debug is True or debug == self.__class__.__name__:
                import matplotlib.pyplot as plt

                plt.figure()
                plt.title('Kills')
                plt.plot(kills_seen)
                plt.show()

            final_kills = kills_seen[-1]
            self.logger.info(f'Got final_kills={final_kills}')

            last_killcount = int(final_kills)
        else:
            self.logger.info(f'Only saw {len(kills_seen)} killcounts - using last_killcount=0')
            last_killcount = 0

        return last_killcount

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp)

    @property
    def won(self) -> bool:
        return self.placed == 1

    @property
    def season(self) -> int:
        for season in data.SEASONS:
            if season.start < self.timestamp < season.end:
                return season.index
        self.logger.error(f'Could not get season for {self.timestamp} - using {len(data.SEASONS)}', exc_info=True)
        return len(data.SEASONS)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
            f'key={self.key}, ' \
            f'season={self.season}, ' \
            f'solo={self.solo}, ' \
            f'duration={s2ts(self.duration)}, ' \
            f'frames={len(self.frames)}, ' \
            f'squad={self.squad}, ' \
            f'landed={self.route.landed_name}, ' \
            f'placed={self.placed}, ' \
            f'kills={self.kills}' \
            f'rank={self.rank}' \
            f')'

    __repr__ = __str__

    def to_dict(self) -> Dict[str, Any]:
        return {
            'key': self.key,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'season': self.season,
            'solo': self.solo,
            'scrims': self.scrims,
            'match_started': self.match_started,
            'match_id': self.match_id,
            'match_ids': self.match_ids,

            # 'player_name': self.player_name,
            'kills': self.kills,
            'placed': self.placed,

            'squad': self.squad.to_dict(),
            'combat': self.combat.to_dict(),
            'route': self.route.to_dict(),
            'weapons': self.weapons.to_dict(),
            'rank': self.rank.to_dict() if self.rank else None,

            'champion': self.champion,

            'images': self.images,
        }


def main() -> None:
    import json
    from pprint import pprint
    from overtrack.util import referenced_typedload
    from overtrack.util.logging_config import config_logger

    config_logger('apex_game', logging.INFO, False)

    # data = requests.get('https://overtrack-games.sfo2.digitaloceanspaces.com/EeveeA-1716/2019-03-20-00-40-apex-8vSqu2.frames.json')
    with open('../../../dev/ERRORS/EeveeA-1716_2019-03-20-02-58-apex-ntTJtP.frames.json') as f:
        frames = referenced_typedload.load(json.load(f), List[Frame])

    game = ApexGame(frames)
    print(game)
    pprint(game.to_dict())

    from overtrack_models.apex_game_summary import ApexGameSummary

    g = ApexGameSummary.create(game, -1)
    print(g)


if __name__ == '__main__':
    main()

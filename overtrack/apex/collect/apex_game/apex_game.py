import datetime
import logging
from collections import Counter
from typing import Any, ClassVar, Dict, List, Optional, Union

import Levenshtein as levenshtein
import numpy as np
import shortuuid
from dataclasses import dataclass

from overtrack.apex import data
from overtrack.apex.collect.apex_game.combat import Combat
from overtrack.apex.collect.apex_game.rank import Rank
from overtrack.apex.collect.apex_game.route import Route
from overtrack.apex.collect.apex_game.squad import APIOriginUser, Squad
from overtrack.apex.collect.apex_game.weapons import Weapons
from overtrack.frame import Frame
from overtrack.util import arrayops, s2ts, validate_fields, typedload


@dataclass
@validate_fields
class ApexGame:
    key: str
    timestamp: float

    duration: float
    season: int
    match_started: float
    valid: bool

    solo: bool
    scrims: Optional[str]

    match_id: Optional[str]
    match_ids: List[Optional[str]]

    kills: int
    placed: int

    squad: Squad
    combat: Combat
    route: Route
    weapons: Weapons
    rank: Optional[Rank]

    player_name: str
    champion: Optional[Dict]
    images: Dict[str, str]

    frames_count: int

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(
        self,
        frames: List[Frame],
        key: str = None,
        squad_before: Optional[List[Optional[APIOriginUser]]] = None,
        squad_after: Optional[List[Optional[APIOriginUser]]] = None,
        champion: Optional[APIOriginUser] = None,
        scrims: Optional[str] = None,
        debug: Union[bool, str] = False
    ):

        self.scrims = scrims
        self.valid = True

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
            self.valid = False

        squad_frames = sum('squad' in f for f in frames)
        match_status_frames = sum('match_status' in f for f in frames)
        if squad_frames == 0 and match_status_frames == 0:
            self.logger.warning(f'Match had 0 squad/match status frames - detecting as invalid')
            self.valid = False
        else:
            self.logger.info(f'Match had {squad_frames} squad frames and {match_status_frames} match status frames')

        selection_frames = [f for f in frames if 'your_squad' in f or 'champion_squad' in f]
        self.duos = self._get_is_duos(frames, selection_frames)

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

        if len(selection_frames):
            self.logger.info(
                f'Match start from selection frame ({"your_squad" if "your_squad" in selection_frames[-1] else "your_champion"}) => '
                f'{selection_frames[-1].timestamp_str}'
            )
            self.match_started = round(selection_frames[-1].timestamp, 2)
        else:
            self.logger.warning(f'Got game with missing selection frames - using end of menu frames as game start')
            self.match_started = round(frames[len(self.menu_frames)].timestamp, 2)
            your_squad_first_index = len(self.menu_frames)
            your_squad_last_index = len(self.menu_frames)

        self.match_ids = self._generate_match_id(champion)
        self.match_id = self.match_ids[0]

        self.player_name = levenshtein.median(menu_names)
        self.logger.info(f'Resolved player name={repr(self.player_name)} from menu frames')

        game_end_index = self._get_end_index(frames, your_squad_first_index)

        self.frames = frames[your_squad_first_index:game_end_index]
        self.frames_count = len(self.frames)
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

        self.mode = 'unranked'
        if self._get_is_ranked(squad_before, squad_after, debug):
            self.mode = 'ranked'
        elif self.solo:
            self.mode = 'solo'
        elif self.duos:
            self.mode = 'duos'

        self.season = self._get_season()

        config_name: Optional[str] = None
        for frame in self.frames:
            if 'apex_metadata' in frame:
                config_name = frame.apex_metadata.player_config_name
                self.player_name = config_name
                self.logger.info(f'Got player name from config: {config_name!r}')

        self.squad = Squad(self.all_frames, menu_names, config_name, self.mode == 'ranked', squad_before, squad_after, solo=self.solo, duos=self.duos, debug=debug)
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

        if self.mode == 'ranked':
            self.rank = Rank(
                self.menu_frames,
                self.match_status_frames,
                self.placed,
                self.kills,
                self.squad.player.name,
                squad_before,
                squad_after,
                debug=debug
            )
        else:
            self.rank = None

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

        if champion:
            self.champion = {
                'name': champion['name'],
                'ocr_name': champion['ocr_name'],

                'champion': champion.get('stats', {}).get('champion'),

                'kills': champion.get('stats', {}).get('kills'),
                'wins': champion.get('stats', {}).get('wins'),
            }
            if self.mode == 'ranked':
                self.champion['rp'] = champion.get('stats', {}).get('rank_score')
        else:
            self.champion = None

    def _get_is_duos(self, frames: List[Frame], selection_frames: List[Frame]) -> bool:
        duos_frames = [f for f in frames if ('your_squad' in f and f.your_squad.mode == 'duos') or ('champion_squad' in f and f.champion_squad.mode == 'duos')]
        self.logger.info(f'Got {len(duos_frames)}/{len(selection_frames)} confirming game as duos')
        return len(duos_frames) > len(selection_frames) * 0.5

    def _get_is_ranked(self, squad_before: Optional[List[Optional[APIOriginUser]]], squad_after: Optional[List[Optional[APIOriginUser]]], debug: bool) -> Optional[Rank]:
        if len(self.match_status_frames):
            rank_matches = sum(match_status.rank_text is not None for match_status in self.match_status_frames)
            rank_matches_p = rank_matches / len(self.match_status_frames)
        else:
            rank_matches = 0
            rank_matches_p = 0
        self.logger.info(f'Got {rank_matches_p * 100:.0f}% ({rank_matches}/{len(self.match_status_frames)}) of match status frames claiming ranked')

        return rank_matches_p > 0.8 and rank_matches > 10

    def _generate_match_id(self, champion: Optional[APIOriginUser]) -> List[Optional[str]]:
        if champion:
            rounded_match_started = int(self.match_started / 60 + 0.5) * 60
            match_started_offset = self.match_started - rounded_match_started
            alt_match_started = rounded_match_started + (1 if match_started_offset > 0 else -1) * 60

            started_datetime = datetime.datetime.utcfromtimestamp(rounded_match_started)
            alt_started_datetime = datetime.datetime.utcfromtimestamp(alt_match_started)

            self.logger.info(
                f'Start time is {datetime.datetime.utcfromtimestamp(self.match_started)} -> '
                f'{started_datetime} with offset={match_started_offset:.0f} ({("positive" if match_started_offset > 0 else "negative")}), '
                f'alt start={alt_started_datetime}'
            )

            match_ids = [
                started_datetime.strftime('%Y-%m-%d-%H-%M') + '/' + champion['ocr_name'].upper(),
                alt_started_datetime.strftime('%Y-%m-%d-%H-%M') + '/' + champion['ocr_name'].upper()
            ]
            self.logger.info(f'Match IDs: {match_ids}')
            return match_ids
        else:
            self.logger.warning(f'Match does not have champion - not setting match ID')
            return [None, None]

    def _get_end_index(self, frames: List[Frame], your_squad_first_index: int) -> int:
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
        return game_end_index

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

    def _get_season(self) -> int:
        for season in data.SEASONS:
            if season.start < self.timestamp < season.end:
                return season.index
        self.logger.error(f'Could not get season for {self.timestamp} (valid={self.valid}) - using {len(data.SEASONS)}', exc_info=True)
        return len(data.SEASONS)

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp)

    @property
    def won(self) -> bool:
        return self.placed == 1

    def asdict(self) -> Dict[str, Any]:
        return typedload.dump(self, ignore_default=False)


def main() -> None:
    import json
    # from overtrack.util import __referenced_typedload
    from overtrack.util.typedload import frameload
    from overtrack.util.logging_config import config_logger
    from overtrack.util.prettyprint import pprint
    import time

    config_logger('apex_game', logging.INFO, False)

    with open("C:/Users/simon/AppData/Local/Temp/mendokusaii_2019-12_15-01-32-PF4QC4tKg4sy6JgmAEwJW4.frames.json") as f:
        data = json.load(f)

    t0 = time.perf_counter()
    frames = frameload.frames_load(data, List[Frame])
    print(f'Loaded {len(frames)} in {time.perf_counter()-t0}s')
    t0 = time.perf_counter()
    frames_ = __referenced_typedload.load(data, List[Frame])
    print(f'Loaded {len(frames_)} in {time.perf_counter() - t0}s')

    game = ApexGame(frames)
    print(game)

    # data = game.asdict()
    # # data['route']['locations'][6] = 'a'
    # game2 = typedload.load(data, ApexGame)
    #
    # pprint(game)
    # pprint(game2)
    #
    # print(game == game2)
    #
    # from overtrack.util.typedload import referenced_typedload
    #
    # t0 = time.perf_counter()
    # frames_data = frameload.frames_dump(frames)
    # print(time.perf_counter() - t0)
    #
    # t0 = time.perf_counter()
    # frames_data = __referenced_typedload.dump(frames)
    # print(time.perf_counter() - t0)

    #
    # frames2 = frameload.frames_load(frames_data, List[Frame])
    # pprint(frames2)


if __name__ == '__main__':
    main()

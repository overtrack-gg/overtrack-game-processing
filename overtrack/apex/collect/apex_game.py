import bisect 
import datetime
import itertools
import logging
import string
from collections import deque, Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import Levenshtein as levenshtein
import numpy as np
import shortuuid
import tabulate
import typedload
from dataclasses import dataclass, fields

from overtrack.apex import data
from overtrack.apex.game.match_status import MatchStatus
from overtrack.apex.game.match_summary.models import MatchSummary
from overtrack.apex.game.menu import PlayMenu
from overtrack.apex.game.squad_summary.models import PlayerStats as SquadSummaryStats
from overtrack.frame import Frame
from overtrack.util import arrayops, s2ts, textops


def norm_name(s: str) -> str:
    rs = s
    for c1, c2 in '0O', 'lI', '1I':
        rs = rs.replace(c1, c2)
    for dc in '_-':
        while dc * 2 in rs:
            rs = rs.replace(dc * 2, dc)
    return rs


@dataclass
class PlayerStats:
    kills: Optional[int] = None
    damage_dealt: Optional[int] = None
    survival_time: Optional[int] = None
    players_revived: Optional[int] = None
    players_respawned: Optional[int] = None

    def merge(self, other: 'PlayerStats'):
        for f in fields(self):
            name = f.name
            own_value = getattr(self, name)
            other_value = getattr(other, name)
            if own_value is None and other_value is not None:
                setattr(self, name, other_value)
            elif own_value is not None and other_value is not None and own_value != other_value:
                logging.getLogger('PlayerStats').warning(f'Got PlayerStats.{name} {own_value} != {other_value}')


class Player:
    """
    A Player from a Squad.
    Each game (usually) has 3 Players forming a `Squad`.

    The initial name is provided, then player data from other sources (i.e. in frames)
    is derived by assigning data based on finding the best matching player from each other
    source based on the edit distance/ratio of names from those sources.

    Attributes
    -----------
    name: str
        The name of the player. May be corrected from the supplied if a higher-accuracy source is found.
    champion: str
        The champion that the player is playing.
    stats: Optional[PlayerStats]
        The stats for this player.
    is_owner: bool
        Whether the player is the first-person player of the game
    name_from_config: bool
        Whether `name` is provided ahead of time from *config* (instead of OCR).
        If True, the name is assumed fully accurate.
    name_matches_api: bool
        Whether `name` matches (or was updated to match) data provided from the Apex API.
        If True, the name can likely be assumed to be fully accurate.

    Parameters
    ----------
    :param name:
        The (estimated) name of the player.
    :param champion:
        The champion of the player.
    :param stats:
        The stats of this player as per the squad summary frames
    :param frames:
        All frames of the game
    :param is_owner:
        Whether the player is the first person player of the game i.e. if the match summary (XP) stats belong to this player
    :param name_from_config:
        Whether `name` is provided ahead of time from *config* (instead of OCR).
    """

    logger = logging.getLogger('Player')

    def __init__(self,
                 name: Optional[str],
                 champion: str,
                 stats: List[SquadSummaryStats],
                 frames: List[Frame],
                 is_owner: bool = False,
                 name_from_config: bool = False):

        squad_summaries = [f.squad_summary for f in frames if 'squad_summary' in f]

        self.logger.info( 
            f'Resolving player with estimated name="{name}", champion={champion} '
            f'from {len(squad_summaries)} squad summary frames | '
            f'use_match_summary={is_owner}, name_from_config={name_from_config}'
        )
        self.name = name
        self.champion = champion
        self.is_owner = is_owner
        self.name_from_config = name_from_config
        self.name_matches_api = False

        if len(stats):
            # use name from stats screen as this is easier to OCR
            names = [s.name for s in stats]
            own_stats_name = levenshtein.median(names)
            if not name_from_config and len(names) > 3 and own_stats_name != self.name and len(own_stats_name) > 3:
                self.logger.warning(f'Updating name from game name to stats name: "{self.name}" -> "{own_stats_name}"')
                self.name = own_stats_name

            self.stats = self._get_mode_stats(stats)
        else:
            self.stats = None

        if is_owner:
            summaries = [f.match_summary for f in frames if 'match_summary' in f]
            self.logger.info(f'Resolving stat from {len(summaries)} match summary (XP) frames')
            summary_stats = self._make_summary_stats(summaries)
            mode_summary_stats = self._get_mode_stats(summary_stats)
            if stats:
                if self.stats is None:
                    self.logger.info(f'Using stats from summary: {mode_summary_stats}')
                    self.stats = mode_summary_stats
                elif self.stats != mode_summary_stats:
                    self.logger.warning(f'Merging squad stats {self.stats} with summary stats {mode_summary_stats}')
                    self.stats = self._get_mode_stats(stats + summary_stats)
                else:
                    self.logger.info(f'Squad stats and summary stats agree')

        if self.stats:
            self.stats = self._sanity_clip(self.stats)

        self.logger.info(f'Resolved to: {self}')

    def _get_mode_stats(self, stats: List[SquadSummaryStats]) -> PlayerStats:
        mode = {}
        for name in 'kills', 'damage_dealt', 'survival_time', 'players_revived', 'players_respawned':
            values = [getattr(s, name) for s in stats]
            counter = Counter([v for v in values if v is not None])
            if len(counter):
                mode[name] = counter.most_common(1)[0][0]
            else:
                mode[name] = None
            self.logger.info(f'{self.name} > {name} : {counter} > {mode[name]}')
        return PlayerStats(
            **mode
        )

    def _make_summary_stats(self, summaries: List[MatchSummary]) -> List[SquadSummaryStats]:
        return [
            SquadSummaryStats(
                name='',
                kills=s.xp_stats.kills,
                damage_dealt=s.xp_stats.damage_done,
                survival_time=s.xp_stats.time_survived,
                players_revived=s.xp_stats.revive_ally,
                players_respawned=s.xp_stats.respawn_ally,
            ) for s in summaries if s.xp_stats
        ] + [
            SquadSummaryStats(
                name='',
                kills=s.score_report.kills,
                damage_dealt=None,
                survival_time=None,
                players_revived=None,
                players_respawned=None,
            ) for s in summaries if s.score_report
        ]

    def _sanity_clip(self, stats: PlayerStats) -> PlayerStats:
        def _sanity_clip(x: Optional[int], lb: int, ub: int, name: str) -> Optional[int]:
            if x is None:
                return x
            elif lb <= x <= ub:
                return x
            else:
                self.logger.warning(f'Rejecting {self.name} > {name}={x} - outside of sane bounds')
                return None

        return PlayerStats(
            kills=_sanity_clip(stats.kills, 0, 30, 'kills'),
            damage_dealt=_sanity_clip(stats.damage_dealt, 0, 10000, 'damage_dealt'),
            survival_time=_sanity_clip(stats.survival_time, 15, 60 * 45, 'survival_time'),
            players_revived=_sanity_clip(stats.players_revived, 0, 20, 'players_revived'),
            players_respawned=_sanity_clip(stats.players_respawned, 0, 10, 'players_respawned'),
        )

    def update_from_api(self, name: str, before: Dict[str, Any], after: Dict[str, Any]) -> None:
        self.logger.info(f'Matched {name} {before["champion"]} for {self}')
        self.logger.info(f'Banners before: {before["banners"]}')
        self.logger.info(f'Banners after: {after["banners"]}')

        if self.name != name:
            self.logger.warning(f'Name for {self.name} does not match stats API - updating to {name}')
            self.name = name

        self.name_matches_api = True

        if before['champion'] and self.champion != before['champion'].lower():
            self.logger.warning(f'Champion for {self.name} does not match stats API - {self.champion} > {before["champion"]}')
            self.champion = before['champion'].lower()

        for stat_name, stat_value in before['banners'].items():
            for stat_key, stat_field in ('_KILL', 'kills'), ('_DAMAGE', 'damage_dealt'):
                if stat_key in stat_name and stat_name in after['banners']:
                    if self.stats is None:
                        self.stats = PlayerStats()
                    ocr_value = getattr(self.stats, stat_field)
                    api_value = after['banners'][stat_name] - before['banners'][stat_name]
                    if ocr_value is None:
                        self.logger.info(f'{stat_field} for {self.name} not provided by OCR, API={api_value} - using API')
                        setattr(self.stats, stat_field, api_value)
                    elif ocr_value != api_value:
                        self.logger.info(f'{stat_field} for {self.name} from OCR does not match API: OCR={ocr_value} > API={api_value} - using API')
                        setattr(self.stats, stat_field, api_value)
                    else:
                        self.logger.info(f'{stat_field} for {self.name} from OCR matches stats API: {stat_field}={api_value}')

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'name={repr(self.name)}, ' \
               f'champion={self.champion}, ' \
               f'stats={self.stats}' \
               f')'

    __repr__ = __str__

    def to_dict(self) -> Dict[str, Any]:
        stats = None
        if self.stats:
            stats = typedload.dump(self.stats, hidedefault=False)
        return {
            'name': self.name,
            'champion': self.champion,
            'stats': stats,
            'name_from_config': self.name_from_config
        }


class Squad:
    logger = logging.getLogger('Squad')

    def __init__(
            self,
            frames: List[Frame],
            menu_names: List[str],
            config_name: Optional[str],
            stats_before: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
            stats_after: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
            solo: bool = False,
            debug: Union[bool, str] = False):
        self.squad = [f.squad for f in frames if 'squad' in f]
        self.logger.info(f'Processing squad from {len(self.squad)} squad frames')

        if debug is True or debug == self.__class__.__name__:
            self._debug_champions(frames)

        if solo:
            names = [
                self._get_name(menu_names) if not config_name else config_name
            ]
        else:
            names = [
                self._get_name(menu_names) if not config_name else config_name,
                self._get_squadmate_name(0),
                self._get_squadmate_name(1)
            ]

        champions = [
            self._get_champion(debug)
        ]

        squadmate_champion_0_valid = self._get_champion_valid_count(0)
        squadmate_champion_1_valid = self._get_champion_valid_count(1)

        if squadmate_champion_0_valid > squadmate_champion_1_valid:
            champions.append(self._get_squadmate_champion(0, debug, champions))
            champions.append(self._get_squadmate_champion(1, debug, champions))
        else:
            champions.append(self._get_squadmate_champion(1, debug, champions))
            champions.insert(1, self._get_squadmate_champion(0, debug, champions))

        self.logger.info(f'Resolved names and champions: {list(zip(names, champions))}')

        squad_summaries = [f.squad_summary for f in frames if 'squad_summary' in f]
        if len(squad_summaries):
            self.logger.info(f'Resolving players from {len(squad_summaries)} squad summary frames')
            all_player_stats: List[List[SquadSummaryStats]] = [[], [], []]
            for summary in squad_summaries:
                for i in range(3):
                    if solo and i != 1:
                        continue
                    all_player_stats[i].append(summary.player_stats[i])

            self.player = None
            self.squadmates = (None, None)
            matches = []
            for name in names:
                matches.append([])
                for player_stats in all_player_stats:
                    if name:
                        matches[-1].append(levenshtein.setratio([norm_name(name)] * len(player_stats), [norm_name(s.name) for s in player_stats]))
                    else:
                        matches[-1].append(0)

            table = [[names[i]] + matches[i] for i in range(3 if not solo else 1)]
            headers = [levenshtein.median([s.name for s in stats]) for stats in all_player_stats]
            self.logger.info(f'Got name/stat matches:\n{tabulate.tabulate(table, headers=[""] + headers)}')

            matches = np.array(matches)
            for i in range(3 if not solo else 1):
                names_index, stats_index = np.unravel_index(np.argmax(matches), matches.shape)
                match = matches[names_index, stats_index]
                name = names[names_index]
                champion = champions[names_index]
                stats = all_player_stats[stats_index]
                reject = False
                if match > 0.75:
                    self.logger.info(f'Matched {name} <-> {headers[stats_index]}: {match:1.2f} - champion={champion}')
                elif champion:
                    self.logger.warning(
                        f'Got potentially bad match {name}<->{[Counter(s.name for s in stats)]}: {match:1.2f} - '
                        f'champion={champion} ({2-i} other options)'
                    )
                else:
                    self.logger.warning(
                        f'Got potentially bad match {name}<->{[Counter(s.name for s in stats)]}: {match:1.2f} and champion was not seen - '
                        f'champion=None ({2 - i} other options)'
                    )
                    reject = True

                matches[names_index, :] = -1
                matches[:, stats_index] = -1

                if not reject:
                    player = Player(
                        name,
                        champion,
                        stats,
                        frames,
                        is_owner=bool(names_index == 0),
                        name_from_config=bool(names_index == 0 and config_name is not None)
                    )
                else:
                    player = None
                if names_index == 0:
                    self.player = player
                elif names_index == 1:
                    self.squadmates = (player, self.squadmates[1])
                else:
                    self.squadmates = (self.squadmates[0], player)
        else:
            self.logger.info(f'Did not get any squad summary frames')

            self.player = Player(
                names[0],
                champions[0],
                [],
                frames,
                is_owner=True,
                name_from_config=config_name is not None
            )
            if solo:
                self.squadmates = (None, None)
            else:
                self.squadmates = (
                    Player(names[1], champions[1], [], frames) if champions[1] else None,
                    Player(names[2], champions[2], [], frames) if champions[2] else None,
                )

        if stats_before and stats_after:
            self._update_players_stats_from_api(stats_before, stats_after)

        if not solo:
            self.squad_kills = self._get_squad_kills(frames)
        else:
            self.squad_kills = None

    def _update_players_stats_from_api(
            self,
            stats_before: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
            stats_after: Optional[List[Tuple[str, Dict[str, Any]]]] = None):
        
        stats = [(sb[0], sb[1], sa[1]) if sb and sb[1] and sa and sa[1] else None for sb, sa in zip(stats_before, stats_after)]
        squadnames = [s[0] for s in stats if s]
        if not len(squadnames):
            return None

        name_similarities = [levenshtein.ratio(*c) for c in itertools.combinations(squadnames, 2)]
        self.logger.info(f'Resolving player stats using API stats')

        if len(name_similarities) and np.max(name_similarities) > 0.9:
            self.logger.warning(f'Squadmates (names={squadnames}) had the same name(s) - refusing to use API stats')
            return

        for player in list(self.squadmates) + [self.player]:
            if player and player.name and any(s for s in stats):
                best = textops.best_match(
                    player.name,
                    [s[0] for s in stats if s],
                    [s for s in stats if s],
                    threshold=0.75
                )
                if best:
                    stats.remove(best)
                    player.update_from_api(*best)

    def _get_champion_valid_count(self, squadmate_index: int) -> int:
        arr = np.array([s.squadmate_champions[squadmate_index] for s in self.squad])
        if not len(arr):
            return 0
        inds = np.argsort(arr).T
        best_match = np.array([arr[i, inds[-1][i]] for i in range(inds.shape[1])])
        best_match[np.isnan(best_match) | (best_match == 0)] = 0.01
        secondbest_match = np.array([arr[i, inds[-2][i]] for i in range(inds.shape[1])])
        secondbest_match[np.isnan(secondbest_match)] = 0
        ratio = secondbest_match / best_match
        return int(np.sum((best_match > 0.9) & (ratio < 0.95)))

    def _debug_champions(self, frames):
        import matplotlib.pyplot as plt

        ts = [frame.timestamp - frames[0].timestamp for frame in frames if 'squad' in frame]

        def make_champion_plot(vals):
            for i, (s, c) in enumerate(data.champions.items()):
                plt.plot(ts, [v[i] for v in vals], label=s)
            plt.legend()

        plt.figure()
        plt.title('Player Champion')
        make_champion_plot([s.champion for s in self.squad])
        plt.figure()
        plt.title('Squadmate 1 Champion')
        make_champion_plot([s.squadmate_champions[0] for s in self.squad])
        plt.figure()
        plt.title('Squadmate 2 Champion')
        make_champion_plot([s.squadmate_champions[1] for s in self.squad])
        plt.show()

    def _median_name(self, names: List[str]):
        name = levenshtein.median(names)
        self.logger.info(f'Resolving median name {Counter(names)}/{len(names)} -> {name}')
        return name

    def _get_name(self, menu_names: List[str]) -> Optional[str]:
        return self._median_name([s.name for s in self.squad if s.name] + menu_names)

    def _get_champion(self, debug: Union[bool, str] = False) -> Optional[str]:
        return self._get_matching_champion([s.champion for s in self.squad], debug)

    def _get_squadmate_name(self, index: int) -> Optional[str]:
        return self._median_name([s.squadmate_names[index] for s in self.squad if s.squadmate_names[index]])

    def _get_squadmate_champion(self, index: int, debug: Union[bool, str] = False, other_champions: Optional[List[str]] = None) -> Optional[str]:
        return self._get_matching_champion([s.squadmate_champions[index] for s in self.squad], debug, other_champions)

    def _get_matching_champion(self, arr: List[List[float]], debug: Union[bool, str] = False, other_champions: Optional[List[str]] = None) -> Optional[str]:
        champions = list(data.champions.keys())
        if other_champions:
            other_champion_inds = [champions.index(c) for c in other_champions if c]
        else:
            other_champion_inds = []

        if not len(arr):
            self.logger.warning(f'Could not identify champion - no data')
            return None

        arr = np.array(arr)
        inds = np.argsort(arr).T
        best_match = np.nanpercentile(np.array([arr[i, inds[-1][i]] for i in range(inds.shape[1])]), 75)
        secondbest_match = np.nanpercentile(np.array([arr[i, inds[-2][i]] for i in range(inds.shape[1])]), 75)
        ratio = secondbest_match / best_match
        if best_match < 0.9:
            self.logger.warning(f'Rejecting champion match={best_match:1.2f}')
            return None
        # elif ratio > 0.92:
        #     self.logger.warning(f'Rejecting champion ratio={ratio:1.2f}')
        #     return None
        else:
            self.logger.info(f'Got champion match={best_match:1.2f}, ratio={ratio:1.2f}')

        current_champ = np.full((len(arr), ), fill_value=np.nan, dtype=np.float)
        for i, vals in enumerate(arr):
            inds = np.argsort(vals)
            ratio = vals[inds[-2]] / vals[inds[-1]]
            if vals[inds[-1]] > 0.9 and ratio < 0.95 and inds[-1] not in other_champion_inds:
                current_champ[i] = inds[-1]

        current_champ_where_known = current_champ[~np.isnan(current_champ)].astype(np.int)

        if len(current_champ_where_known) <= 3:
            self.logger.warning(f'Could not identify champion - average matches={np.nanmedian(arr, axis=0)}')
            return None

        current_champ_where_known = arrayops.modefilt(current_champ_where_known, 9)

        if debug is True or debug == self.__class__.__name__:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.title('Champion Index')
            plt.plot(current_champ_where_known)
            plt.show()

        champion_changed = np.where(current_champ_where_known[1:] != current_champ_where_known[:-1])[0]
        if len(champion_changed) and 1 < champion_changed[0] < len(current_champ_where_known):
            before = champions[arrayops.most_common(current_champ_where_known[:champion_changed[0] - 1])]
            count_before = champion_changed[0]

            after = champions[arrayops.most_common(current_champ_where_known[champion_changed[0] + 1:])]
            count_after = len(current_champ_where_known) - count_before

            if before != after:
                if count_before > count_after:
                    self.logger.warning(
                        f'Champion changed from {before} -> {after} at {count_before} / {len(current_champ_where_known)} - '
                        f'using first champion'
                    )
                    return before
                else:
                    self.logger.warning(
                        f'Champion changed from {before} -> {after} at {count_before} / {len(current_champ_where_known)} - '
                        f'using second champion'
                    )
                    return after

        champion, count = Counter(current_champ_where_known).most_common(1)[0]
        champion = champions[champion]
        self.logger.info(f'Got champion={champion} ~ {count}')
        return champion

    def _get_matching_stats(self, name: str, player_summary_stats: List[List[SquadSummaryStats]]) -> List[SquadSummaryStats]:
        self.logger.info(
            f'Trying to match player name {name} against {len(player_summary_stats)} sets of stats: '
            f'{[levenshtein.median([s.name for s in stats]) for stats in player_summary_stats]}'
        )

        matches = [levenshtein.setratio([norm_name(name)] * len(stats), [norm_name(s.name) for s in stats]) for stats in player_summary_stats]
        best = arrayops.argmax(matches)
        match = player_summary_stats[best]
        if matches[best] < 0.85:
            self.logger.warning(
                f'Got potentially bad match {name}<->{[Counter(s.name for s in stat) for stat in player_summary_stats]} ~ '
                f'{best}: {matches[best]:1.2f}'
            )
        else:
            self.logger.info(f'Got stats for {name} = {Counter(s.name for s in player_summary_stats[best])}')
        player_summary_stats.remove(match)
        return match

    def _get_squad_kills(self, frames: List[Frame]) -> Optional[int]:
        if self.player.stats and self.player.stats.kills is not None \
                and self.squadmates[0] and self.squadmates[0].stats is not None and self.squadmates[0].stats.kills is not None \
                and self.squadmates[1] and self.squadmates[1].stats is not None and self.squadmates[1].stats.kills is not None:
            derived_squad_kills = self.player.stats.kills + self.squadmates[0].stats.kills + self.squadmates[1].stats.kills
            self.logger.info(f'Deriving squad kills from stats: {derived_squad_kills}')
        else:
            derived_squad_kills = None

        squad_summary = [f.squad_summary for f in frames if 'squad_summary' in f]
        self.logger.info(f'Parsing squad kills from {len(squad_summary)} squad summary frames')
        squad_kills_counter = Counter([s.squad_kills for s in squad_summary if s.squad_kills is not None])
        if not len(squad_kills_counter):
            if derived_squad_kills:
                self.logger.warning(f'Using derived squad kills from stats')
            else:
                self.logger.warning(f'No squad kills parsed')
            return derived_squad_kills
        else:
            squad_kills, count = squad_kills_counter.most_common(1)[0]
            if count != len(squad_summary):
                self.logger.warning(f'Got disagreeing squad kills: {Counter(s.squad_kills for s in squad_summary)}')
            self.logger.info(f'Got squad_kills from summary: {squad_kills}')
            if derived_squad_kills and squad_kills != derived_squad_kills:
                self.logger.warning(f'Got disagreeing squad kills: from stats={derived_squad_kills}, from summary= {squad_kills} - using stats')
                return derived_squad_kills
            return squad_kills

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'player={self.player}, ' \
               f'squadmates=({self.squadmates[0]}, {self.squadmates[1]})' \
               f')'

    __repr__ = __str__

    def to_dict(self) -> Dict[str, Any]:
        return {
            'player': self.player.to_dict(),
            'squadmates': (
                self.squadmates[0].to_dict() if self.squadmates[0] else None,
                self.squadmates[1].to_dict() if self.squadmates[1] else None
            ),
            'squad_kills': self.squad_kills
        }


@dataclass
class CombatEvent:
    timestamp: float
    type: str
    inferred: bool = False
    weapon: Optional[str] = None
    location: Optional[Tuple[int, int]] = None

    def __str__(self):
        r = f'CombatEvent(ts={s2ts(self.timestamp)}, type={self.type}'
        if self.inferred:
            r += f', inferred=True'
        if self.weapon:
            r += f', weapon={self.weapon}'
        if self.location:
            r += f', location={self.location}'
        return r + ')'

    __repr__ = __str__


class Combat:

    logger = logging.getLogger('Combat')

    def __init__(self, frames: List[Frame], placed: int, squad: Squad, debug: Union[bool, str]= False):
        self.combat_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'combat_log' in f]
        self.combat_data = [f.combat_log for f in frames if 'combat_log' in f]
        self.logger.info(f'Resolving combat from {len(self.combat_data)} combat frames')

        if debug is True or debug == self.__class__.__name__:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.title('Combat Log Widths')
            for t, l in zip(self.combat_timestamp, self.combat_data):
                plt.scatter([t]*len(l.events), [e.width for e in l.events])
            plt.show()

        self.events = []

        self.eliminations = []
        self.knockdowns = []
        self.elimination_assists = []
        self.knockdown_assists = []

        seen_events = []
        combatevent_to_event = {}
        for ts, combat in zip(self.combat_timestamp, self.combat_data):
            for event in combat.events:
                matching = [
                    other_ts for other_ts, other in seen_events if
                    ts - other_ts < 10 and event.type == other.type and abs(event.width - other.width) < 10
                ]
                if not len(matching):
                    # new event
                    self.logger.info(f'Got new event @ {ts:.1f}s: {event}')
                    combat_event = None
                    if event.type == 'ELIMINATED':
                        # If we see an ELIMINATED, it means we have also scored a knockdown on that player
                        # Because knocking and eliminating the last player is equivalent, only ELIMINATED will show
                        # Insert the missing knock down if needed
                        matching_knockdowns = [
                            (ts, other) for other_ts, other in seen_events if
                            ts - other_ts < 30 and other.type == 'KNOCKED DOWN' and abs(event.width - other.width) < 7
                        ]
                        if not len(matching_knockdowns):
                            # don't have a matching knockdown for this elim - create one now
                            knockdown = CombatEvent(ts, 'downed', inferred=True)
                            self.logger.info(f'Could not find knockdown for {event} - inserting {knockdown}')
                            self.knockdowns.append(knockdown)
                            self.events.append(knockdown)

                        # add after inferred event
                        combat_event = CombatEvent(ts, 'eliminated')
                        self.eliminations.append(combat_event)

                    elif event.type == 'KNOCKED DOWN':
                        combat_event = CombatEvent(ts, 'downed')
                        self.knockdowns.append(combat_event)
                    elif event.type == 'ASSIST, ELIMINATION':
                        combat_event = CombatEvent(ts, 'assist.eliminated')
                        self.elimination_assists.append(combat_event)
                    elif event.type == 'ASSIST, KNOCK DOWN':
                        combat_event = CombatEvent(ts, 'assist.downed')
                        self.knockdown_assists.append(combat_event)

                    assert combat_event

                    # add last so inferred events are inserted first
                    self.events.append(combat_event)
                    combatevent_to_event[id(combat_event)] = event

                else:
                    self.logger.info(f'Already seen event @ {ts:.1f}s: {event} {ts - matching[-1]:.1f}s ago')

                seen_events.append((ts, event))

        if placed == 1 and squad.player.stats and squad.player.stats.kills and squad.player.stats.kills > len(self.eliminations):
            match_status_frames = [f for f in frames if 'match_status' in f]
            if len(match_status_frames):
                last_timestamp = [f.timestamp - frames[0].timestamp for f in match_status_frames][-1]
                self.logger.warning(
                    f'Got won game with {squad.player.stats.kills} kills, but only saw {len(self.eliminations)} eliminations from combat - '
                    f'Trying to resolve final fight (ended {s2ts(last_timestamp)})'
                )
                # detect recent knockdowns that don't have elims after them, and add the elim as it should be a final elim
                for knock in self.knockdowns:
                    if last_timestamp - knock.timestamp < 60:
                        elims_following = [e for e in self.eliminations if e.timestamp > knock.timestamp]
                        if not len(elims_following):
                            final_elim = CombatEvent(last_timestamp, 'eliminated', inferred=True)
                            self.eliminations.append(final_elim)
                            self.logger.warning(f'Adding elim for final fight knockdown @{s2ts(knock.timestamp)}: {final_elim}')

                while squad.player.stats.kills > len(self.eliminations):
                    # still lacking on elims - this player got the final kill
                    self.knockdowns.append(CombatEvent(last_timestamp, 'downed'))
                    self.eliminations.append(CombatEvent(last_timestamp, 'eliminated'))
                    self.logger.warning(f'Adding down+elim for final kill(s) of the match: {self.knockdowns[-1]}, {self.eliminations[-1]}')

            # if len(self.eliminations) > len(self.knockdowns):
            #     self.logger.warning(
            #         f'Still have outstanding knockdowns: elims={len(self.eliminations)}, knockdowns={len(self.knockdowns)} - '
            #         f'Adding down for final kill of the match'
            #     )

        self.logger.info(
            f'Resolved combat:\n'
            f'Eliminations: {self.eliminations}\n'
            f'Knockdowns: {self.knockdowns}\n'
            f'Elimination_assists: {self.elimination_assists}\n'
            f'Knockdown_assists: {self.knockdown_assists}\n'
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'eliminations': typedload.dump(self.eliminations, hidedefault=False),
            'knockdowns': typedload.dump(self.knockdowns, hidedefault=False),
            'elimination_assists': typedload.dump(self.elimination_assists, hidedefault=False),
            'knockdown_assists': typedload.dump(self.knockdown_assists, hidedefault=False),
        }


@dataclass
class WeaponStats:
    weapon: str
    time_held: float = 0
    time_active: float = 0

    knockdowns: int = 0


class Weapons:
    logger = logging.getLogger('Weapons')

    def __init__(self, frames: List[Frame], combat: Combat, debug: Union[bool, str]= False):
        self.weapon_timestamp = [round(f.timestamp - frames[0].timestamp, 2) for f in frames if 'weapons' in f]
        self.weapon_data = [f.weapons for f in frames if 'weapons' in f]
        self.logger.info(f'Resolving weapons from {len(self.weapon_data)} weapon frames')

        weapon1 = self._get_weapon_map(0)
        weapon1_selected_vals = np.array([w.selected_weapons[0] for w in self.weapon_data])
        if len(weapon1_selected_vals):
            weapon1_selected = (arrayops.medfilt(weapon1_selected_vals, 3) < 200) & np.not_equal(weapon1, -1)
        else:
            weapon1_selected = np.array((0, ), dtype=np.bool)
        # ammo1 = [wep.clip if sel else np.nan for sel, wep in zip(weapon1_selected, self.weapon_data)]

        weapon2 = self._get_weapon_map(1)
        weapon2_selected_vals = np.array([w.selected_weapons[1] for w in self.weapon_data])
        if len(weapon2_selected_vals):
            weapon2_selected = (arrayops.medfilt(weapon2_selected_vals, 3) < 200) & np.not_equal(weapon2, -1)
        else:
            weapon2_selected = np.array((0,), dtype=np.bool)
        # ammo2 = [wep.clip if sel else np.nan for sel, wep in zip(weapon2_selected, self.weapon_data)]

        if len(weapon1) and len(weapon2):
            have_weapon = np.convolve(np.not_equal(weapon1, -1) + np.not_equal(weapon2,  -1), np.ones((10,)), mode='valid')
            self.first_weapon_timestamp = self._get_firstweapon_pickup_time(have_weapon)
        else:
            have_weapon = np.array((0,), dtype=np.bool)
            self.first_weapon_timestamp = frames[-1].timestamp

        self.weapon_stats: List[WeaponStats] = []
        self.selected_weapon_at: List[Optional[WeaponStats]] = [None for _ in self.weapon_timestamp]
        self._add_weapon_stats(weapon1, weapon1_selected)
        self._add_weapon_stats(weapon2, weapon2_selected)
        self._add_combat_weaponstats(combat)
        self.weapon_stats = sorted(self.weapon_stats, key=lambda stat: (stat.knockdowns, stat.time_active), reverse=True)
        self.weapon_stats = [w for w in self.weapon_stats if w.time_held > 15 or w.knockdowns > 0]
        self.logger.info(f'Resolved weapon stats: {self.weapon_stats}')

        if debug is True or debug == self.__class__.__name__:
            self._debug(combat, have_weapon, weapon1, weapon1_selected, weapon1_selected_vals, weapon2, weapon2_selected, weapon2_selected_vals)

    def _debug(self, combat, have_weapon, weapon1, weapon1_selected, weapon1_selected_vals, weapon2, weapon2_selected, weapon2_selected_vals):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.title('Selected Weapon')
        plt.plot(self.weapon_timestamp, weapon1_selected_vals)
        plt.plot(self.weapon_timestamp, weapon2_selected_vals)

        # plt.figure()
        # plt.title('Ammo')
        # plt.plot(self.weapon_timestamp, ammo1)
        # plt.plot(self.weapon_timestamp, ammo2)

        def make_weaponplot():
            for event in combat.events:
                c = None
                if event.type == 'KNOCKED DOWN':
                    c = 'red'
                elif event.type == 'ASSIST, ELIMINATION':
                    c = 'orange'
                if c:
                    plt.axvline(event.timestamp, color=c)
            for i, n in enumerate(data.weapon_names):
                plt.text(0, i + 0.25, n)

        plt.figure()
        plt.title('Weapon 1')
        plt.scatter(self.weapon_timestamp, weapon1)
        plt.plot(self.weapon_timestamp, weapon1_selected * 5)
        make_weaponplot()
        plt.figure()

        plt.title('Weapon 2')
        plt.scatter(self.weapon_timestamp, weapon2)
        plt.plot(self.weapon_timestamp, weapon2_selected * 5)
        make_weaponplot()

        plt.figure('Have Weapon')
        plt.plot(have_weapon)
        plt.axhline(6, color='r')
        plt.show()

    def _get_weapon_map(self, index: int) -> np.ndarray:
        def stripname(s: str) -> str:
            return textops.strip_string(s, string.ascii_uppercase + string.digits + '- ')

        weapon = np.full((len(self.weapon_data, )), fill_value=-1, dtype=np.int)
        name2index = {stripname(n): i for i, n in enumerate(data.weapon_names)}
        for i, weapons in enumerate(self.weapon_data):
            name = weapons.weapon_names[index]
            ratio, match = textops.matches_ratio(
                stripname(name),
                data.weapon_names
            )
            if ratio > 0.75:
                weapon[i] = name2index[match]
        return weapon

    def _get_firstweapon_pickup_time(self, have_weapon: np.ndarray) -> Optional[float]:
        have_weapon_inds = np.where(have_weapon > 4)[0]
        if len(have_weapon_inds):
            first_weapon_index = have_weapon_inds[0] + 5
            if 0 <= first_weapon_index < len(self.weapon_timestamp):
                ts = self.weapon_timestamp[first_weapon_index]
                self.logger.info(f'Got first weapon pickup at {s2ts(ts)}')
                return ts
            else:
                self.logger.warning(f'Got weapon pickup at invalid index: {first_weapon_index}')
                return None
        else:
            self.logger.warning(f'Did not see any weapons')
            return None

    def _add_weapon_stats(self, weapon: Sequence[int], weapon_selected: Sequence[bool]) -> None:
        weapon_stats_lookup = {
            s.weapon: s for s in self.weapon_stats
        }

        last: Optional[Tuple[float, int, bool]] = None
        for i, (ts, weapon_index, selected) in enumerate(zip(self.weapon_timestamp, weapon, weapon_selected)):
            if weapon_index == -1:
                continue
            if last is not None:
                weapon_name = data.weapons[weapon_index].name
                weapon_stats = weapon_stats_lookup.get(weapon_name)
                if not weapon_stats:
                    weapon_stats = WeaponStats(weapon_name)
                    self.weapon_stats.append(weapon_stats)
                    weapon_stats_lookup[weapon_name] = weapon_stats

                if last[1] == weapon_index:
                    weapon_stats.time_held += ts - last[0]

                if selected:
                    self.selected_weapon_at[i] = weapon_stats
                    if last[2]:
                        weapon_stats.time_active += ts - last[0]

            last = ts, weapon_index, selected

    def _add_combat_weaponstats(self, combat: Combat):
        # n.b. the weapon is only relevant for knockdowns and elimination_assists, and only useful for knockdowns of these
        # knockdowns: we knocked someone down - don't know who will finish or how
        # elimination_assists: we eliminated someone ourselves with a weapon
        for event in combat.knockdowns:
            weapon_stats = self._get_weapon_at(event.timestamp)
            if weapon_stats:
                weapon_stats.knockdowns += 1
                event.weapon = weapon_stats.weapon
                self.logger.info(f'Found weapon={weapon_stats.weapon} for {event}')

    def _get_weapon_at(self, timestamp: float, max_distance: float = 10) -> Optional[WeaponStats]:
        index = bisect.bisect(self.weapon_timestamp, timestamp) - 1
        if not (0 <= index < len(self.weapon_timestamp)):
            self.logger.error(f'Got invalid index trying to find weapon @ {timestamp:.1f}s', exc_info=True)
            return None

        self.logger.debug(
            f'Trying to resolve weapon at {timestamp:.1f}s - '
            f'got weapon index={index} -> {self.weapon_timestamp[index]:.1f}s'
        )
        for ofs in range(-5, 6):
            check = index + ofs
            if 0 <= check < len(self.weapon_timestamp):
                weap = self.selected_weapon_at[check]
                self.logger.debug(f'ofs={ofs:+d} > ind={check} ts={self.weapon_timestamp[check]:.1f} > weap={weap.weapon if weap else None}')

        for fan_out in range(20):
            for sign in -1, 1:
                check = index + sign * fan_out
                if 0 <= check < len(self.weapon_timestamp):
                    ts = self.weapon_timestamp[check]
                    distance = abs(timestamp - ts)
                    if distance < max_distance:
                        stat = self.selected_weapon_at[check]
                        if stat:
                            self.logger.debug(f'Found {stat} at {ts:.1f}s - distance {distance}')
                            return stat

        self.logger.warning(f'Could not find weapon for ts={timestamp:.1f}s')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'weapon_stats': typedload.dump(self.weapon_stats, hidedefault=False)
        }


class Route:
    logger = logging.getLogger('Route')

    def __init__(self, frames: List[Frame], weapons: Weapons, combat: Combat, season: int, debug: Union[bool, str] = False):
        self.season = season
        alive = np.array([
            ('squad' in f or 'match_status' in f) for f in frames
        ])
        alive = np.convolve(alive, np.ones(10, ), mode='valid')
        alive_at = np.zeros(int((frames[-1].timestamp - frames[0].timestamp) / 10) + 5, dtype=np.bool)
        alive_at[:20] = True
        alive_at[-20:] = True
        for f, a in zip(frames, alive):
            alive_at[int((f.timestamp - frames[0].timestamp) / 10)] |= (a > 2)

        if debug is True or debug == self.__class__.__name__:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.title('alive')
            plt.plot([f.timestamp for f in frames[:-9]], alive)

            plt.figure()
            plt.title('alive at')
            plt.scatter(np.linspace(0, 10 * alive_at.shape[0], alive_at.shape[0]), alive_at)
            plt.show()

        self.locations = []
        recent = deque(maxlen=5)

        # map processor v1
        for i, frame in enumerate([f for f in frames if 'location' in f or 'minimap' in f]):
            if 'minimap' in frame:
                ts, location = frame.timestamp, frame.minimap.location
                coordinates = location.coordinates
                if season <= 2:
                    coordinates = (
                        int(coordinates[0] * 0.987 + 52),
                        int(coordinates[1] * 0.987 + 48)
                    )
            else:
                ts, location = frame.timestamp, frame.location
                coordinates = location.coordinates

            rts = round(ts - frames[0].timestamp, 2)
            if location.match > 0.7:
                continue

            if len(recent):
                last = np.mean(recent, axis=0)
                dist = np.sqrt(np.sum((np.array(last) - np.array(coordinates)) ** 2))
                if not alive_at[int(rts / 10)]:
                    # ignore route - not from this player
                    self.logger.debug(f'Ignoring location {i}: {location} - not alive')
                elif dist < 250:
                    self.locations.append((rts, coordinates))
                else:
                    self.logger.warning(
                        f'Ignoring location {i}: {location} - {dist:.1f} away from average {np.round(last, 1)}'
                    )
            recent.append(coordinates)

        self.logger.info(f'Processing route from {len(self.locations)} locations')
        if not len(self.locations):
            self.logger.warning(f'Got no locations')
            self.time_landed = None
            self.landed_location_index = None
            self.landed_location = None
            self.landed_name = None
            self.locations_visited = []
        else:

            x = np.array([l[1][0] for l in self.locations])
            y = np.array([l[1][1] for l in self.locations])
            ts = np.array([l[0] for l in self.locations])
            if len(ts) < 3:
                self.logger.warning(f'Only got {len(ts)} locations - assuming drop location = last location seen')
                self.landed_location_index = len(ts) - 1
                self.time_landed = float(ts[self.landed_location_index])
            else:
                time_offset = np.array(ts[1:] - ts[:-1])
                speed = np.sqrt((x[1:] - x[:-1]) ** 2 + (y[1:] - y[:-1]) ** 2) / time_offset
                speed_smooth = np.convolve(speed, np.ones(3) / 3, mode='same')
                # accel = np.diff(speed_smooth)
                self.landed_location_index = int(np.argmax(speed_smooth < 6)) + 1
                self.time_landed = float(ts[self.landed_location_index])
                self.logger.info(f'Speed dropped below 4 @ {s2ts(self.time_landed)}, index={self.landed_location_index}')

            # average location of first 5 locations
            mean_location = np.mean([
                l[1] for l
                in self.locations[
                   max(0, self.landed_location_index - 2):
                   min(self.landed_location_index + 3, len(self.locations))
                   ]],
                axis=0
            )
            self.landed_location = int(mean_location[0]), int(mean_location[1])
            if season <= 2:
                self.landed_name = data.kings_canyon_locations[self.landed_location]
            else:
                self.landed_name = data.worlds_edge_locations[self.landed_location]

            self._process_locations_visited()

        for event in combat.events:
            event.location = self._get_location_at(event.timestamp)
            if season <= 2:
                lname = data.kings_canyon_locations[event.location] if event.location else "???"
            else:
                lname = data.worlds_edge_locations[event.location] if event.location else "???"
            self.logger.info(f'Found location={lname} for {event}')

        if debug is True or debug == self.__class__.__name__:
            self._debug(frames)

    def _debug(self, frames):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        plt.figure()
        plt.title('Location Match')
        plt.plot([f.location.match for f in frames if 'location' in f])

        import cv2
        from overtrack.apex.game.map.map_processor import MapProcessor
        from colorsys import hsv_to_rgb
        image = MapProcessor.MAP.copy()
        for frame in [f for f in frames if 'location' in f]:
            h = 240 - 240 * frame.location.match
            c = np.array(hsv_to_rgb(h / 255, 1, 1))
            cv2.circle(
                image,
                frame.location.coordinates,
                1,
                c * 255,
                -1
            )
        plt.figure()
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), interpolation='none')

        plt.figure()
        plt.imshow(cv2.cvtColor(self.make_image(), cv2.COLOR_BGR2RGB), interpolation='none')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x = np.array([l[1][0] for l in self.locations])
        y = np.array([l[1][1] for l in self.locations])
        t = [l[0] for l in self.locations]
        ax.scatter(x, y, t, c='green', marker='o')

        ts = np.array([l[0] for l in self.locations])
        plt.figure()
        plt.title('time offsets')
        time_offset = np.array(ts[1:] - ts[:-1])
        plt.plot(time_offset)

        plt.figure()
        plt.title('speed')
        speed = np.sqrt((x[1:] - x[:-1])**2 + (y[1:] - y[:-1])**2) / time_offset
        plt.plot(speed)
        #q
        # plt.figure()
        # plt.title('speed2')
        # speed2 = speed / time_offset
        # plt.plot(speed2)

        speed_smooth = np.convolve(speed, np.ones(3)/3, mode='valid')
        plt.figure()
        plt.title('speed_smooth')
        plt.plot(speed_smooth)

        plt.figure()
        plt.title('accel')
        accel = np.diff(speed_smooth)
        plt.plot(accel)

        plt.show()

    def _process_locations_visited(self):
        self.locations_visited = [self.landed_name]
        last_location = self.locations[self.landed_location_index][0], self.landed_name
        for ts, location in self.locations[self.landed_location_index + 1:]:
            if self.season <= 2:
                location_name = data.kings_canyon_locations[location]
            else:
                location_name = data.worlds_edge_locations[location]
            if location_name == 'Unknown':
                continue
            if location_name == last_location[1] and ts - last_location[0] > 30:
                if self.locations_visited[-1] != location_name:
                    self.locations_visited.append(location_name)
            elif location_name != last_location[1]:
                self.logger.info(f'Spent {ts - last_location[0]:.1f}s in {last_location[1]}')
                last_location = ts, location_name

    def make_image(self, combat: Optional[Combat] = None) -> np.ndarray:
        import cv2
        from overtrack.apex.game.map.map_processor import MapProcessor
        image = MapProcessor.MAP.copy()

        if len(self.locations):
            last = self.locations[self.landed_location_index][1]
            for ts, l in self.locations[self.landed_location_index + 1:]:
                dist = np.sqrt(np.sum((np.array(last) - np.array(l)) ** 2))
                cv2.line(
                    image,
                    last,
                    l,
                    (0, 255, 0) if dist < 60 else (0, 0, 255),
                    1,
                )
                last = l

            if self.landed_location:
                for t, c in (10, (0, 0, 0)), (2, (180, 0, 200)):
                    cv2.putText(
                        image,
                        'Landed',
                        self.landed_location,
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        1.2,
                        c,
                        t
                    )

            if combat:
                for event in combat.events:
                    location = self._get_location_at(event.timestamp)
                    if location:
                        cv2.putText(
                            image,
                            'x',
                            location,
                            cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            1.2,
                            (0, 0, 255),
                            1
                        )

        return image

    def _get_location_at(self, timestamp: float, max_distance: float = 120) -> Optional[Tuple[int, int]]:
        ts = [l[0] for l in self.locations]
        xy = [l[1] for l in self.locations]
        index = min(max(0, bisect.bisect(ts, timestamp) - 1), len(ts))
        if not (0 <= index < len(ts)):
            self.logger.error(f'Got invalid index {index} trying to find location @ {timestamp:.1f}s', exc_info=True)
            return None

        self.logger.debug(
            f'Trying to resolve location at {timestamp:.1f}s - '
            f'got location index={index} -> {ts[index]:.1f}s'
        )
        for fan_out in range(100):
            for sign in -1, 1:
                check = index + sign * fan_out
                if 0 <= check < len(ts):
                    ats = ts[check]
                    distance = abs(timestamp - ats)
                    if distance < max_distance:
                        loc = xy[check]
                        if distance < 30:
                            level = logging.DEBUG
                        else:
                            level = logging.WARNING
                        self.logger.log(level, f'Found {loc} at {ats:.1f}s - distance {distance}s')
                        return loc

        self.logger.warning(f'Could not find location for ts={timestamp:.1f}s')
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'locations': self.locations,

            'time_landed': self.time_landed,
            'landed_location_index': self.landed_location_index,
            'landed_location': self.landed_location,
            'landed_name': self.landed_name,
            'locations_visited': self.locations_visited
        }


class Rank:
    """
    Ranked data for a game.

    Attributes
    -----------
    rank: Optional[str]
        The rank if known
    rank_tier: Optional[str]
        The rank tier if known, and if not Apex Predator
    rp: Optional[int]
        The amount of RP before and during the game
    rp_change: Optional[int]
        The RP change from this match, computed from entry cost, placement, and kills

    Parameters
    ----------
    :param menu_frames:
    :param match_status_frames:
    :param placement:
    :param kills:
    :param debug:
    """

    logger = logging.getLogger(__qualname__)

    def __init__(
            self,
            menu_frames: List[PlayMenu],
            match_status_frames: List[MatchStatus],
            placement: int,
            kills: int,
            player_name: str,
            stats_before: Optional[List[Tuple[str, Dict[str, Any]]]],
            stats_after: Optional[List[Tuple[str, Dict[str, Any]]]],
            debug: bool = False):

        self.rank: Optional[str] = None
        self.rank_tier: Optional[str] = None
        self.rp: Optional[int] = None

        self._resolve_match_status_rank(match_status_frames)
        self._resolve_menu_rank(menu_frames, debug=debug)
        # TODO: resolve RP and change from match summary > score summary
        # NOTE: score summary current RP is an animation - take the last frame and use IFF there are enough frames for it to have finished animating

        if self.rank:
            self.rp_change = -data.rank_entry_cost[self.rank] + min(kills, 5) + data.rank_rewards[placement]
            self.logger.info(f'Got rp_change={self.rp_change:+}: rank={self.rank}, placement={placement}, kills={kills}')
            if self.rp and self.rp + self.rp_change < data.rank_rp[self.rank][0]:
                self.logger.info(f'RP {self.rp} {self.rp_change} would drop rank - setting RP change to 0')
                self.rp_change = 0
        else:
            self.rp_change = None

        if stats_before and stats_after:
            self._resolve_api_rank(player_name, stats_after, stats_before)

    def _resolve_match_status_rank(self, match_status_frames: List[MatchStatus], debug: bool = False) -> None:
        rank_matches = np.array([
            match_status.rank_badge_matches
            for match_status in match_status_frames
            if match_status.rank_badge_matches is not None
        ])
        rank_matches_avg = np.median(rank_matches, axis=0)

        self.logger.info(f'Found ranked matches:\n{tabulate.tabulate([(data.ranks[i], rank_matches_avg[i]) for i in range(len(data.ranks))])}')
        self.rank = data.ranks[arrayops.argmin(rank_matches_avg)]
        self.logger.info(f'Got rank={self.rank}')

        if self.rank != 'apex_predator':
            rank_text = [match_status.rank_text for match_status in match_status_frames if match_status.rank_text]
            rank_text_counter = Counter(rank_text)
            self.logger.info(f'Found rank tier texts: {rank_text_counter}')

            for text, count in rank_text_counter.most_common():
                if text in data.rank_tiers:
                    self.rank_tier = text
                    self.logger.info(f'Got rank tier={self.rank_tier} - seen {(count / len(rank_text)) * 100:.0f}% {count}/{len(rank_text)}')
                    break
                else:
                    self.logger.warning(f'Ignoring {text} (count={count}) - invalid tier')

        if debug is True or debug == self.__class__.__name__:
            import matplotlib.pyplot as plt

            # plt.figure()
            # plt.imshow(rank_matches)

            plt.figure()
            plt.title('Rank Badges')
            for i, rank in enumerate(data.ranks):
                from pprint import pprint

                plt.plot(
                    rank_matches[:, i],
                    label=rank
                )
            plt.legend()
            plt.show()

    def _resolve_menu_rank(self, menu_frames: List[PlayMenu], debug: bool = False) -> None:
        menu_rank_text = [menu.rank_text for menu in menu_frames]
        if not len(menu_rank_text):
            self.logger.warning(f'Got 0 rank texts from menu')
            self.rp = None
            return

        menu_rank_counter = Counter(menu_rank_text)
        self.logger.info(f'Got menu ranked text: {menu_rank_counter}')

        options, choose_from = [], []
        for rank in data.ranks:
            if rank != 'apex_predator':
                for tier in data.rank_tiers:
                    options.append(rank + tier)
                    choose_from.append((rank, tier))
            else:
                options.append(rank)
                choose_from.append((rank, None))

        rank_text = menu_rank_counter.most_common()[0][0]
        if rank_text:
            rank_tier = textops.best_match(
                rank_text,
                options,
                choose_from,
                threshold=0.9
            )
            if not rank_tier:
                self.logger.warning(f'Could not identify rank for {rank_text}')
            else:
                rank, tier = rank_tier
                self.logger.info(f'Got rank={rank}, tier={tier}')
                if rank != self.rank:
                    self.logger.warning(f'Rank from ingame badge={self.rank}, but menu got {rank}')
                    self.rank = rank
                if tier != self.rank_tier:
                    self.logger.warning(f'Rank from ingame text={self.rank_tier}, but menu got {tier}')
                    self.rank_tier = tier
                if rank != self.rank or tier != self.rank_tier:
                    self.logger.error(f'Ingame rank does not match menu rank', exc_info=True)

        menu_rp_text = [menu.rp_text for menu in menu_frames]
        menu_rp_counter = Counter(menu_rp_text)
        self.logger.info(f'Got menu RP text: {menu_rp_counter}')
        try:
            rp_str = menu_rp_counter.most_common()[0][0].split('/')[0]
            self.rp = int(rp_str)
        except Exception as e:
            self.logger.warning(f'Failed to parse menu RP: {e}')
            self.rp = None
        else:
            rp_lower_limit, rp_upper_limit = data.rank_rp[self.rank]
            if not rp_lower_limit <= self.rp < rp_upper_limit:
                self.logger.warning(f'RP: {self.rp} is not within {rp_lower_limit}, {rp_upper_limit} from rank {self.rank} - ignorng')
                self.rp = None
            else:
                self.logger.info(f'Got RP={self.rp}')

        if self.rp is None:
            self.logger.warning(f'Menu RP invalid')

    def _resolve_api_rank(self, player_name, stats_after, stats_before):
        self.logger.info(f'Trying to resolve RP from API stats for "{player_name}"')
        player_stats_before_l = [n_s[1] for n_s in stats_before if n_s and n_s[0] == player_name and n_s[1]]
        player_stats_after_l = [n_s[1] for n_s in stats_after if n_s and n_s[0] == player_name and n_s[1]]
        if len(player_stats_before_l) == 1 and len(player_stats_after_l) == 1:
            player_stats_before = player_stats_before_l[0]
            player_stats_after = player_stats_after_l[0]
            if 'rank_score' in player_stats_before and 'rank_score' in player_stats_after:
                rp_before = player_stats_before['rank_score']
                rp_after = player_stats_after['rank_score']

                if not rp_before or not rp_after:
                    self.logger.warning(f'API RP before={rp_before}, after={rp_after} - may be invalid: ignoring API RP')
                    return

                rp_change = rp_after - rp_before
                error = False

                if rp_before != self.rp:
                    self.logger.warning(f'Had RP={self.rp}, but API said RP={rp_before} - using API')
                    error |= self.rp is not None  # if RP *was* parsed from OCR but disagrees, then something is wrong
                else:
                    self.logger.info(f'API RP={rp_before} agrees with OCR')

                if rp_change != self.rp_change:
                    self.logger.warning(f'Had RP change={self.rp_change}, but API said RP after={rp_after}, change={rp_change} - using API')
                    error |= self.rp_change is not None
                else:
                    self.logger.info(f'API RP change={rp_change:+} agrees with OCR')

                self.rp = rp_before
                self.rp_change = rp_change

                derived_rank = None
                derived_tier = None
                for rank, (lower, upper) in data.rank_rp.items():
                    if lower <= self.rp < upper:
                        derived_rank = rank
                        if rank != 'apex_predator':
                            division = (upper - lower) // 4
                            tier_ind = (self.rp - lower) // division
                            derived_tier = data.rank_tiers[tier_ind]
                        break
                else:
                    self.logger.warning(f'API RP={self.rp} did not correspond to a valid rank')
                    error = True

                if derived_rank:
                    if derived_rank != self.rank:
                        self.logger.warning(f'Had rank={self.rank}, but API said rank={derived_rank} - using API')
                        error |= self.rank is not None
                    else:
                        self.logger.info(f'API rank={derived_rank} agrees with OCR')

                    if derived_tier != self.rank_tier:
                        self.logger.warning(f'Had rank tier={self.rank_tier}, but API said rank={derived_tier} - using API')
                        error |= derived_tier is not None and self.rank_tier is not None
                    else:
                        self.logger.info(f'API rank tier={derived_tier} agrees with API')

                    self.rank = derived_rank
                    self.rank_tier = derived_tier

                if error:
                    self.logger.warning(f'Got disagreeing RP/RP change/rank from OCR and API', exc_info=True)
                    #self.logger.error(f'Got disagreeing RP/RP change/rank from OCR and API', exc_info=True)

        else:
            self.logger.error(f'API stats invalid', exc_info=True)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
            f'rank={self.rank}, ' \
            f'rank_tier={self.rank_tier}, ' \
            f'rp={self.rp}' \
            f'rp_change={self.rp_change}' \
            f')'

    __repr__ = __str__

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rank': self.rank,
            'rank_tier': self.rank_tier,
            'rp': self.rp,
            'rp_change': self.rp_change
        }


class ApexGame:
    logger = logging.getLogger('ApexGame')

    def __init__(
            self,
            frames: List[Frame],
            key: str = None,
            stats_before: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
            stats_after: Optional[List[Tuple[str, Dict[str, Any]]]] = None,
            debug: Union[bool, str] = False):

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
        self.squad_count = 20 if not self.solo else 60

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

        self.squad = Squad(self.all_frames, menu_names, config_name, stats_before, stats_after, solo=self.solo, debug=debug)
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
        self.logger.info(f'Got {rank_matches_p*100:.0f}% ({rank_matches}/{len(self.match_status_frames)}) of match status frames claiming ranked')
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
                    self.logger.warning(f'Ignoring match_summary.placed={e[0]} - not in range')
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

    def _get_match_state_kills(self, debug: Union[bool, str]= False) -> int:
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
        for season in data.seasons:
            if season.start < self.timestamp < season.end:
                return season.index
        self.logger.error(f'Could not get season for {self.timestamp} - using {len(data.seasons)}', exc_info=True)
        return len(data.seasons)

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

            # 'player_name': self.player_name,
            'kills': self.kills,
            'placed': self.placed,

            'squad': self.squad.to_dict(),
            'combat': self.combat.to_dict(),
            'route': self.route.to_dict(),
            'weapons': self.weapons.to_dict(),
            'rank': self.rank.to_dict() if self.rank else None,

            'images': self.images
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

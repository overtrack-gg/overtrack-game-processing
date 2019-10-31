import logging
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, Union

import Levenshtein as levenshtein
import itertools
import numpy as np
import tabulate
import typedload
from dataclasses import dataclass, fields

from overtrack.apex import data
from overtrack.apex.game.match_summary.models import MatchSummary
from overtrack.apex.game.squad_summary.models import PlayerStats as SquadSummaryStats
from overtrack.frame import Frame
from overtrack.util import arrayops, textops


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
            if before['champion'].lower() != 'bangalore':
                self.logger.warning(f'Champion for {self.name} does not match stats API - {self.champion} > {before["champion"]}')
                self.champion = before['champion'].lower()
            else:
                self.logger.warning(f'Champion for {self.name} does not match stats API - {self.champion} > {before["champion"]} - ignoring bangalore')

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
                        f'champion={champion} ({2 - i} other options)'
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
            for i, (s, c) in enumerate(data.CHAMPIONS.items()):
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
        champions = list(data.CHAMPIONS.keys())
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

        current_champ = np.full((len(arr),), fill_value=np.nan, dtype=np.float)
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

import logging
from collections import Counter
from typing import ClassVar, List, Optional

import numpy as np
import tabulate
from dataclasses import dataclass

from overtrack.apex import data
from overtrack.apex.collect.apex_game.squad import APIOriginUser, APIStats
from overtrack.apex.game.match_status import MatchStatus
from overtrack.apex.game.menu import PlayMenu
from overtrack.util import arrayops, textops, validate_fields


@dataclass
@validate_fields
class Rank:
    """
    Ranked data for a game.

    Parameters
    ----------
    :param menu_frames:
    :param match_status_frames:
    :param placement:
    :param kills:
    :param debug:
    """

    rank: Optional[str]
    rank_tier: Optional[str]
    rp: Optional[int]
    rp_change: Optional[int]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(
            self,
            menu_frames: List[PlayMenu],
            match_status_frames: List[MatchStatus],
            placement: int,
            kills: int,
            player_name: str,
            players_before: Optional[List[Optional[APIOriginUser]]],
            players_after: Optional[List[Optional[APIOriginUser]]],
            debug: bool = False):

        self.rank: Optional[str] = None
        self.rank_tier: Optional[str] = None
        self.rp: Optional[int] = None

        self._resolve_match_status_rank(match_status_frames)
        self._resolve_menu_rank(menu_frames, debug=debug)
        # TODO: resolve RP and change from match summary > score summary
        # NOTE: score summary current RP is an animation - take the last frame and use IFF there are enough frames for it to have finished animating


        if players_before and players_after:
            self._resolve_api_rank(player_name, players_before, players_after)

    def _resolve_match_status_rank(self, match_status_frames: List[MatchStatus], debug: bool = False) -> None:
        rank_matches = np.array([
            match_status.rank_badge_matches
            for match_status in match_status_frames
            if match_status.rank_badge_matches is not None
        ])
        rank_matches_avg = np.median(rank_matches, axis=0)

        rank_names = data.ranks.copy()
        if len(rank_matches_avg) == 6:
            rank_names.remove('master')
        self.logger.info(f'Found ranked matches:\n{tabulate.tabulate([(rank_names[i], rank_matches_avg[i]) for i in range(len(rank_names))])}')
        self.rank = rank_names[arrayops.argmin(rank_matches_avg)]
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

            plt.figure()
            plt.title('Rank Badges')
            for i, rank in enumerate(rank_names):
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

    def _resolve_api_rank(self, player_name: str, players_before: List[Optional[APIOriginUser]], players_after: List[Optional[APIOriginUser]]) -> None:
        self.logger.info(f'Trying to resolve RP from API stats for {player_name!r}')
        player_stats_before_l: List[APIStats] = [p['stats'] for p in players_before if p and p['name'] == player_name and p.get('stats')]
        player_stats_after_l: List[APIStats] = [p['stats'] for p in players_after if p and p['name'] == player_name and p.get('stats')]
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
                    # self.logger.error(f'Got disagreeing RP/RP change/rank from OCR and API', exc_info=True)

        else:
            self.logger.error(f'API stats invalid', exc_info=True)

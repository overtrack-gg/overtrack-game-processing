import itertools
from collections import Counter

import logging
import numpy as np
import re
from dataclasses import dataclass
from overtrack.util.arrayops import modefilt
from overtrack.valorant.collect.valorant_game.valorant_game import InvalidGame
from typing import List, Optional, ClassVar, Union, Tuple

from overtrack.frame import Frame
from overtrack.util import ts2s, s2ts
from overtrack.valorant.collect.valorant_game.kills import Kills

ROUND_ACTIVE_PHASE_DURATION = 100
FIRST_BUY_PHASE_DURATION = 43
BUY_PHASE_DURATION = 30
INTER_PHASE_DURATION = 6

COUNTDOWN_PATTERN = re.compile(r'^[01]:\d\d$')


class NoRounds(InvalidGame):
    pass


@dataclass
class Round:
    index: int

    buy_phase_start: float
    start: float
    end: float

    won: Optional[bool]

    kills: Kills


@dataclass
class Rounds:

    rounds: List[Round]
    final_score: Optional[Tuple[int, int]]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, frames: List[Frame], debug: Union[bool, str] = False):
        timestamp = frames[0].timestamp
        self.rounds, score_from_rounds = self._parse_rounds_from_scores(
            frames,
            timestamp,
            debug,
        )
        # TODO: check against count of rounds, final score seen
        self.final_score = score_from_rounds

        if not self.final_score:
            self.logger.error('Could not derive final score')
        elif not (self.final_score[0] == 13 or self.final_score[1] == 13):
            self.logger.error('Final score did not have team with 13 wins')

        if debug in [True, self.__class__.__qualname__]:
            import matplotlib.pyplot as plt
            plt.show()

    def _parse_rounds_from_scores(
        self,
        frames: List[Frame],
        timestamp: float,
        debug: Union[bool, str] = False
    ) -> Tuple[List[Round], Optional[Tuple[int, int]]]:
        score_timestamps = []
        frame_scores_data = []
        for f in frames:
            if f.valorant.top_hud:
                scores = [None, None]
                for side in range(2):
                    if f.valorant.top_hud.score[side] is not None and f.valorant.top_hud.score[side] <= 13:
                        scores[side] = f.valorant.top_hud.score[side]
                if any(s is not None for s in scores):
                    score_timestamps.append(f.timestamp - timestamp)
                    frame_scores_data.append(scores)

        frame_scores = np.array(frame_scores_data, dtype=np.float).T
        scores_filt = np.array([
            modefilt(frame_scores[i], 7)
            for i in range(2)
        ])

        rounds = []
        score = [0, 0]

        self.logger.info(f'Searching for round ends:')
        last_round_end_index = 0
        for round_index in range(25):
            # Find all potential round ends where score increases by one for one team
            edges = [
                list(np.where(
                    (scores_filt[i, last_round_end_index    : -1] == score[i]) &
                    (scores_filt[i, last_round_end_index + 1:] == score[i] + 1)
                )[0] + last_round_end_index) if score[i] <= 12 else []
                for i in range(2)
            ]
            # For each teams edges, rank these by how well they match a score increase
            # i.e. [0, 0, 1, 1, 1] will match a score of 0-> better than [0, 0, 1, 0, 0]
            edgematch_ranks = [
                [
                    (
                        np.mean(np.concatenate((
                            scores_filt[i, last_round_end_index:e] == score[i],
                            scores_filt[i, e+1:] >= score[i] + 1
                        ))),
                        e,
                        i,
                    ) for e in edges[i]
                ] for i in range(2)
            ]
            # For each team, find the best matching edge by the above criteria
            edgematch_best = [
                sorted(edgematch_ranks[i], reverse=True)
                for i in range(2)
            ]
            best_edges = list(sorted(
                itertools.chain(*edgematch_best),
                key=lambda e: e[1],
            ))
            if not len(best_edges):
                break
            edgematch, edge, winner_index = best_edges[0]

            last_round_end_timestamp = score_timestamps[last_round_end_index]
            found_round = Round(
                round_index,
                round(float(last_round_end_timestamp + INTER_PHASE_DURATION), 1),
                round(float(last_round_end_timestamp + INTER_PHASE_DURATION + (FIRST_BUY_PHASE_DURATION if round_index == 0 else BUY_PHASE_DURATION)), 1),
                round(float(score_timestamps[edge]), 1),
                winner_index == 0,
                None,
            )
            rounds.append(found_round)
            self.logger.info(
                f'    {s2ts(score_timestamps[edge])}, match={edgematch:.3f}, winner={["Team1", "Team2"][winner_index]}, '
                f'score={score[winner_index]}->{score[winner_index] + 1}: '
                f'{found_round}'
            )

            score[winner_index] += 1
            last_round_end_index = edge

        self.logger.info(f'Trying to identify final round winner')
        final_round_won = None

        # Attempt to derive final round winner (and game winner) by if one team was up by more than 1 point
        if score[0] == 12 and score[1] != 12:
            self.logger.info(f'Deriving final round win=True from score={score[0]}-{score[1]}')
            final_round_won = True
        elif score[0] != 12 and score[1] == 12:
            self.logger.info(f'Deriving final round win=False from score={score[0]}-{score[1]}')
            final_round_won = False
        else:
            self.logger.warning(f'Could not resolve final round winner from {score[0]}-{score[1]}')

        # Attempt to derive final round winner by postgame game winner
        final_scores_observed = [Counter(), Counter()]
        game_results_observed = Counter()
        for f in frames:
            if f.valorant.postgame:
                for i in range(2):
                    if f.valorant.postgame.score[i] is not None:
                        final_scores_observed[i][f.valorant.postgame.score[i]] += 1
                game_results_observed[f.valorant.postgame.victory] += 1
        if sum(game_results_observed.values()):
            postgame_result_game_won = game_results_observed.most_common(1)[0][0]
            self.logger.info(f'Got final game result: {game_results_observed} -> win={postgame_result_game_won}')
            if final_round_won is not None:
                if postgame_result_game_won != final_round_won:
                    self.logger.error('Got inconsistent game result from final round derived result')
            else:
                final_round_won = postgame_result_game_won
        else:
            self.logger.warning(f'Unable to get final game result - no game result')

        if not len(rounds):
            raise NoRounds()

        # Add the final round
        final_round = Round(
            len(rounds),
            round(float(rounds[-1].end + INTER_PHASE_DURATION), 1),
            round(float(rounds[-1].end + INTER_PHASE_DURATION + BUY_PHASE_DURATION), 1),
            round(float(score_timestamps[-1]), 1),
            final_round_won,
            None
        )
        self.logger.info(f'Adding final round: {final_round}')
        rounds.append(final_round)

        # Update the score using the final round
        # If the final round result is unknown, so is the final score
        if final_round_won is not None:
            score[not final_round_won] += 1
            score = score[0], score[1]
        else:
            score = None

        if debug in [True, self.__class__.__qualname__]:
            import matplotlib.pyplot as plt
            from matplotlib import patches, lines

            plt.figure()

            def draw_rounds(y, height):
                print(y, height)
                for r in rounds:
                    plt.gca().add_patch(patches.Rectangle(
                        (r.buy_phase_start, y),
                        r.start - r.buy_phase_start,
                        height,
                        linewidth=1,
                        edgecolor='blue',
                        color='blue',
                        alpha=0.25,
                    ))
                    plt.gca().add_patch(patches.Rectangle(
                        (r.start, y),
                        r.end - r.start,
                        height,
                        linewidth=1,
                        edgecolor='green',
                        color='green',
                        alpha=0.25,
                    ))

            draw_rounds(-1, np.nanmax(frame_scores) + 1)
            plt.plot(score_timestamps, frame_scores[0], color='b', linestyle='--')
            plt.plot(score_timestamps, scores_filt[0], color='b')
            plt.plot(score_timestamps, frame_scores[1], color='orange', linestyle='--')
            plt.plot(score_timestamps, scores_filt[1], color='orange')

        return rounds, score

    def __iter__(self):
        return iter(self.rounds)

    def __len__(self):
        return len(self.rounds)

    def __getitem__(self, item):
        return self.rounds[item]

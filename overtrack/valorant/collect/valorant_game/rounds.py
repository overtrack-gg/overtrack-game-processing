import bisect
import heapq
import logging
import re
from collections import Counter
from typing import List, Optional, ClassVar, Union, Tuple

import itertools
import numpy as np
from dataclasses import dataclass
from overtrack.frame import Frame
from overtrack.util import s2ts
from overtrack.valorant.collect.valorant_game.kills import Kills, Kill
from overtrack.valorant.collect.valorant_game.valorant_game import InvalidGame

ROUND_ACTIVE_PHASE_DURATION = 100
FIRST_BUY_PHASE_DURATION = 43
BUY_PHASE_DURATION = 30
INTER_PHASE_DURATION = 6

COUNTDOWN_PATTERN = re.compile(r'^[01]:\d\d$')


def isotonic_regression(y, _=None, __=None, ___=None):
    """Finds a non-decreasing fit for the specified `y` under L1 norm.

    The O(n log n) algorithm is described in:
    "Isotonic Regression by Dynamic Programming", Gunter Rote, SOSA@SODA 2019.

    Args:
    y: The values to be fitted, 1d-numpy array.
    w: The loss weights vector, 1d-numpy array.

    Returns:
    An isotonic fit for the specified `y` which minimizies the weighted
    L1 norm of the fit's residual.

    Copyright 2020 Google LLC.
    SPDX-License-Identifier: Apache-2.0
    """
    w = np.ones(y.shape)

    h = []  # max heap of values
    p = np.zeros_like(y)  # breaking position
    for i in range(y.size):
        a_i = y[i]
        w_i = w[i]
        heapq.heappush(h, (-a_i, 2 * w_i))
        s = -w_i
        b_position, b_value = h[0]
        while s + b_value <= 0:
            s += b_value
            heapq.heappop(h)
            b_position, b_value = h[0]
        b_value += s
        h[0] = (b_position, b_value)
        p[i] = -b_position
    z = np.flip(np.minimum.accumulate(np.flip(p)))  # right_to_left_cumulative_min
    return z


class InvalidRounds(InvalidGame):
    pass
class NoRounds(InvalidRounds):
    pass
class BadRoundMatch(InvalidRounds):
    pass


@dataclass
class Round:
    index: int

    buy_phase_start: float
    start: float
    end: float

    attacking: bool
    won: Optional[bool]

    kills: Kills


@dataclass
class Rounds:

    rounds: List[Round]
    final_score: Optional[Tuple[int, int]]

    attacking_first: bool
    attack_wins: int
    defence_wins: int

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    @property
    def all_kills(self) -> List[Kill]:
        return list(itertools.chain(*[r.kills for r in self.rounds]))

    def firstbloods(self, for_team: Optional[bool] = None) -> List[Kill]:
        fbs = [r.kills.firstblood(for_team) for r in self.rounds]
        return [fb for fb in fbs if fb]

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

        if len(self.rounds) < 13:
            self.logger.error('Had game with less than 13 rounds')
        elif len(self.rounds) > 25:
            self.logger.error('Had game with more than 25 rounds')
        else:
            spike_carriers_per_side = [0, 0]
            for f in frames:
                if f.valorant.top_hud and (len(self.rounds) < 25 or f.timestamp - timestamp < self.rounds[24].start):
                    spike_carriers_per_side[f.timestamp - timestamp > self.rounds[11].end] += any(f.valorant.top_hud.has_spike)
            self.logger.info(f'Had {spike_carriers_per_side[0]} spikes seen in first half, and {spike_carriers_per_side[1]} in second')
            attacker_match = spike_carriers_per_side[0] / 12, spike_carriers_per_side[1] / (len(self.rounds) - 12)
            self.attacking_first = attacker_match[0] > attacker_match[1]
            self.logger.info(f'Attack match: {attacker_match[0]:.2f} / {attacker_match[1]:.2f} -> attacking_first={self.attacking_first}')
            if self.attacking_first:
                self.logger.info(f'Marking first 12 rounds as attack')
                for r in self.rounds[:12]:
                    r.attacking = True
            else:
                self.logger.info(f'Marking round 13->24 as attack')
                for r in self.rounds[12:24]:
                    r.attacking = True
            if len(self.rounds) >= 25:
                self.logger.info(f'Game has sudden death round (round 25) - resolving attack defend')
                spike_carriers_sudden_death = 0
                for f in frames:
                    if f.valorant.top_hud and f.timestamp - timestamp > self.rounds[24].start:
                        spike_carriers_sudden_death += any(f.valorant.top_hud.has_spike)
                self.logger.info(f'Sudden death round had {spike_carriers_sudden_death} spikes seen')
                if spike_carriers_sudden_death > 0:
                    self.logger.info(f'Marking round 25 as attack')
                    self.rounds[24].attacking = True
                    if spike_carriers_sudden_death < 3:
                        self.logger.error(f'Sudden death round has low (but nonzero) spike carriers observed')

        self.attack_wins = sum(r.won is True for r in self.rounds if r.attacking)
        self.defence_wins = sum(r.won is True for r in self.rounds if not r.attacking)

        if debug in [True, self.__class__.__qualname__]:
            import matplotlib.pyplot as plt
            from matplotlib import patches

            for r in self.rounds:
                if r.attacking:
                    plt.gca().add_patch(patches.Rectangle(
                        (r.buy_phase_start, 14.5),
                        r.end - r.buy_phase_start,
                        0.4,
                        color='orange',
                        fill=True,
                        alpha=0.75,
                    ))

            hs = [[], []]
            for f in frames:
                if f.valorant.top_hud and any(f.valorant.top_hud.has_spike):
                    hs[0].append(f.timestamp - timestamp)
                    hs[1].append(-0.5)
            plt.scatter(*hs)

            if len(self.rounds) >= 13:
                plt.axvline(self.rounds[11].end)

            plt.show()

    def _parse_rounds_from_scores(
        self,
        frames: List[Frame],
        start: float,
        debug: Union[bool, str] = False
    ) -> Tuple[List[Round], Optional[Tuple[int, int]]]:

        score_timestamps = []
        frame_scores_data = []
        for f in frames:
            if f.valorant.top_hud and sum(e is not None for e in itertools.chain(*f.valorant.top_hud.teams)) >= 2:
                scores = [None, None]
                for side in range(2):
                    if f.valorant.top_hud.score[side] is not None and f.valorant.top_hud.score[side] <= 13:
                        scores[side] = f.valorant.top_hud.score[side]
                if any(s is not None for s in scores):
                    score_timestamps.append(f.timestamp - start)
                    frame_scores_data.append(scores)

        score_timestamps = np.array(score_timestamps)
        frame_scores = np.array(frame_scores_data, dtype=np.float).T

        valid_timestamps = []
        valid_scores = []
        score_matches = []
        for i in range(2):
            isvalid = ~np.isnan(frame_scores[i])
            filtered = isotonic_regression(frame_scores[i, isvalid].astype(np.int), 0, 13)
            valid_timestamps.append(score_timestamps[isvalid])
            valid_scores.append(filtered)
            score_matches.append(np.mean(frame_scores[i, isvalid] == filtered))
        score_match = np.mean(score_matches)
        valid_timestamps = np.array(valid_timestamps)

        self.logger.info(f'Score match is {score_match:.3f}')

        # TODO: find places where score incremented by more than one
        # Possibly best option is to use multiple methods to find round ends
        # (score increase, buy phase hud started, bomb planted hud ended) then resolve scores from the isotonic

        rounds = []
        score = [0, 0]

        self.logger.info(f'Searching for round ends:')
        round_start_timestamp = 0
        for round_index in range(25):
            round_start_index = [
                bisect.bisect_left(valid_timestamps[i], round_start_timestamp)
                for i in range(2)
            ]

            # Find all potential round ends where score increases by one for one team
            edges = [
                list(np.where(
                    (valid_scores[i][s    : -1] == score[i]) &
                    (valid_scores[i][s + 1:   ] == score[i] + 1)
                )[0] + s) if score[i] <= 12 else []
                for i, s in enumerate(round_start_index)
            ]

            # For each teams edges, rank these by how well they match a score increase
            # i.e. [0, 0, 1, 1, 1] will match a score of 0-> better than [0, 0, 1, 0, 0]
            edgematch_ranks = [
                [
                    (
                        np.mean(np.concatenate((
                            valid_scores[i][s  :e] == score[i],
                            valid_scores[i][e+1: ] >= score[i] + 1
                        ))),
                        e,
                        i,
                    ) for e in edges[i]
                ] for i, s in enumerate(round_start_index)
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

            round_end_timestamp = valid_timestamps[winner_index][edge]
            found_round = Round(
                index=round_index,
                buy_phase_start=round(float(round_start_timestamp + INTER_PHASE_DURATION), 1),
                start=round(float(round_start_timestamp + INTER_PHASE_DURATION + (FIRST_BUY_PHASE_DURATION if round_index == 0 else BUY_PHASE_DURATION)), 1),
                end=round(float(round_end_timestamp), 1),
                attacking=False,
                won=winner_index == 0,
                kills=None,
            )
            rounds.append(found_round)
            self.logger.info(
                f'    {s2ts(score_timestamps[edge])} ({score_timestamps[edge]:.0f}s i={edge}), match={edgematch:.3f}, '
                f'winner={["Team1", "Team2"][winner_index]}, score={score[winner_index]}->{score[winner_index] + 1}: '
                f'{found_round}'
            )
            self.logger.info(f'        New score: {valid_scores[winner_index][edge + 1]} - {valid_scores[winner_index][edge: edge + 2]}')

            round_end_index = [
                bisect.bisect_left(valid_timestamps[i], round_end_timestamp)
                for i in range(2)
            ]
            prior_score = [
                Counter(valid_scores[i][round_start_index[i] + 1:round_end_index[i]])
                for i in range(2)
            ]
            self.logger.info(f'        Previous score: {prior_score[0]}, {prior_score[1]}')

            score[winner_index] += 1
            round_start_timestamp = round_end_timestamp

        if score[0] == 13 or score[1] == 13:
            # Captured final score transition
            self.logger.info(f'Final round score transition was captured - final round was included, final score={score[0]}-{score[1]}')
            score = score[0], score[1]
        else:
            self.logger.info(f'Final round score transition was not captured - resolving final round')

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
                index=len(rounds),
                buy_phase_start=round(float(rounds[-1].end + INTER_PHASE_DURATION), 1),
                start=round(float(rounds[-1].end + INTER_PHASE_DURATION + BUY_PHASE_DURATION), 1),
                end=round(float(score_timestamps[-1]), 1),
                attacking=False,
                won=final_round_won,
                kills=None
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
            from matplotlib import patches

            plt.figure()

            def draw_rounds(y, height):
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
                    plt.gca().add_patch(patches.Rectangle(
                        (r.buy_phase_start, height + 0.5),
                        r.end - r.buy_phase_start,
                        0.4,
                        color='green' if r.won else 'red',
                        fill=True,
                        alpha=0.75,
                    ))

            draw_rounds(-0.5, np.nanmax(frame_scores) + 0.5)
            plt.scatter(score_timestamps, frame_scores[0], color='b', marker='v')
            plt.plot(valid_timestamps[0], valid_scores[0], color='b', label='team1')
            plt.scatter(score_timestamps, frame_scores[1], color='orange', marker='^')
            plt.plot(valid_timestamps[1], valid_scores[1], color='orange', label='team2')
            plt.legend()

        return rounds, score

    def __iter__(self):
        return iter(self.rounds)

    def __len__(self):
        return len(self.rounds)

    def __getitem__(self, item):
        return self.rounds[item]


if __name__ == '__main__':

    dat = np.arange(10).astype(np.float)
    dat += 2 * np.random.randn(10)  # add noise

    dat_hat = isotonic_regression(dat)

    import pylab as pl
    pl.close('all')
    pl.plot(dat, 'ro')
    pl.plot(dat_hat, 'b')
    pl.show()

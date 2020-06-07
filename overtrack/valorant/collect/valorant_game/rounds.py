import bisect
import heapq
import logging
import re
from collections import Counter

from overtrack.util.arrayops import modefilt
from typing import List, Optional, ClassVar, Union, Tuple

import itertools
import numpy as np
from dataclasses import dataclass, field
from overtrack.frame import Frame
from overtrack.util import s2ts, arrayops
from overtrack.valorant.collect.valorant_game.kills import Kills, Kill
from overtrack.valorant.collect.valorant_game.teams import Ult
from overtrack.valorant.collect.valorant_game.valorant_game import InvalidGame
from overtrack.valorant.data import GameModeName, game_modes

ROUND_ACTIVE_PHASE_DURATION = 100
FIRST_BUY_PHASE_DURATION = 43
BUY_PHASE_DURATION = 30
INTER_PHASE_DURATION = 6

COUNTDOWN_PATTERN = re.compile(r'^[01]:\d\d$')
HAS_SPIKE_THRESHOLD = 0.6


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
class NoScoresSeen(InvalidRounds):
    pass
class BadRoundMatch(InvalidRounds):
    pass
class BadRoundCount(InvalidRounds):
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
    ults_used: List[Ult] = field(default_factory=list)


@dataclass
class Rounds:
    rounds: List[Round]
    final_score: Optional[Tuple[int, int]]

    attacking_first: bool
    attack_wins: int
    defence_wins: int

    has_game_resets: bool = False

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    @property
    def all_kills(self) -> List[Kill]:
        return list(itertools.chain(*[r.kills for r in self.rounds]))

    def firstbloods(self, for_team: Optional[bool] = None) -> List[Kill]:
        fbs = [r.kills.firstblood(for_team) for r in self.rounds]
        return [fb for fb in fbs if fb]

    def __init__(self, frames: List[Frame], game_mode: GameModeName, debug: Union[bool, str] = False):
        timestamp = frames[0].timestamp
        self.rounds, score_from_rounds, self.has_game_resets = self._parse_rounds_from_scores(
            frames,
            timestamp,
            game_mode,
            debug,
        )

        rounds_per_side = 12
        score_to_win = 13
        max_rounds = 25
        if game_mode == game_modes.spike_rush:
            rounds_per_side = 3
            score_to_win = 4
            max_rounds = 7

        # TODO: check against count of rounds, final score seen
        self.final_score = None
        if not self.has_game_resets:
            self.final_score = score_from_rounds

            if not self.final_score:
                self.logger.error('Could not derive final score')
            elif not (self.final_score[0] == score_to_win or self.final_score[1] == score_to_win):
                self.logger.error(f'Final score did not have team with {score_to_win} wins')

        if not self.final_score:
            self.logger.info(f'Deriving score from sum of won rounds (fallback)')
            self.final_score = (
                sum(r.won is True for r in self.rounds),
                sum(r.won is False for r in self.rounds),
            )

        if len(self.rounds) < score_to_win and not self.has_game_resets:
            raise BadRoundCount(f'Had game with less than {score_to_win} rounds')
        elif game_mode != game_modes.spike_rush and len(self.rounds) > max_rounds and not self.has_game_resets:
            raise BadRoundCount(f'Had standard game with more than {max_rounds} rounds')
        else:
            spike_carriers_per_side = [0, 0]
            for f in frames:
                if f.valorant.top_hud and (len(self.rounds) < max_rounds or f.timestamp - timestamp < self.rounds[max_rounds - 1].start):
                    if f.valorant.top_hud.has_spike_match:
                        any_has_spike = any([
                            m and m > HAS_SPIKE_THRESHOLD for m in f.valorant.top_hud.has_spike_match
                        ])
                    elif f.valorant.top_hud.has_spike:
                        any_has_spike = any(f.valorant.top_hud.has_spike)
                    else:
                        any_has_spike = False
                    spike_carriers_per_side[f.timestamp - timestamp > self.rounds[rounds_per_side - 1].end] += any_has_spike

            self.logger.info(f'Had {spike_carriers_per_side[0]} spikes seen in first half, and {spike_carriers_per_side[1]} in second')
            attacker_match = spike_carriers_per_side[0] / rounds_per_side, spike_carriers_per_side[1] / (len(self.rounds) - rounds_per_side)
            self.attacking_first = attacker_match[0] > attacker_match[1]
            self.logger.info(f'Attack match: {attacker_match[0]:.2f} / {attacker_match[1]:.2f} -> attacking_first={self.attacking_first}')
            if self.attacking_first:
                self.logger.info(f'Marking first {rounds_per_side} rounds as attack')
                for r in self.rounds[:rounds_per_side]:
                    r.attacking = True
            else:
                self.logger.info(f'Marking round {rounds_per_side}->{max_rounds - 1} as attack')
                for r in self.rounds[rounds_per_side:max_rounds - 1]:
                    r.attacking = True
            if len(self.rounds) >= 25:
                self.logger.info(f'Game has sudden death round (round 25) - resolving attack defend')
                spike_carriers_sudden_death = 0
                for f in frames:
                    if f.valorant.top_hud and f.timestamp - timestamp > self.rounds[24].start:
                        if f.valorant.top_hud.has_spike_match:
                            spike_carriers_sudden_death += any([
                                m and m > HAS_SPIKE_THRESHOLD for m in f.valorant.top_hud.has_spike_match
                            ])
                        elif f.valorant.top_hud.has_spike:
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
            sm = [[], []]
            for f in frames:
                if f.valorant.top_hud:
                    if f.valorant.top_hud.has_spike and any(f.valorant.top_hud.has_spike):
                        hs[0].append(f.timestamp - timestamp)
                        hs[1].append(-0.5)
                    if f.valorant.top_hud.has_spike_match:
                        sm[0].append(f.timestamp - timestamp)
                        sm[1].append(-(1 + max(v or 0 for v in f.valorant.top_hud.has_spike_match)))

            if len(hs[0]) > 10:
                plt.scatter(*hs)
            else:
                plt.plot(*sm)
                plt.axhline(-(1 + HAS_SPIKE_THRESHOLD), linestyle='--', color='r')

            if len(self.rounds) >= 13:
                plt.axvline(self.rounds[11].end)

            plt.show()

    def _parse_rounds_from_scores(
        self,
        frames: List[Frame],
        start: float,
        game_mode: GameModeName,
        debug: Union[bool, str] = False
    ) -> Tuple[List[Round], Optional[Tuple[int, int]], bool]:

        score_to_win = 13
        if game_mode == game_modes.spike_rush:
            score_to_win = 4

        score_timestamps = []
        frame_scores_data = []
        last_invalid = 0
        end = 0
        for f in frames:
            if f.valorant.top_hud and not f.valorant.postgame and not f.valorant.agent_select:
                if sum(e is not None for e in itertools.chain(*f.valorant.top_hud.teams)) >= 2:
                    last_invalid = 0
                    end = f.timestamp - start
                else:
                    last_invalid += 1

                scores = [None, None]
                for side in range(2):
                    if f.valorant.top_hud.score[side] is not None and f.valorant.top_hud.score[side] <= 13:
                        scores[side] = f.valorant.top_hud.score[side]
                if any(s is not None for s in scores) and last_invalid < 10:
                    score_timestamps.append(f.timestamp - start)
                    frame_scores_data.append(scores)

        score_timestamps = np.array(score_timestamps)
        frame_scores = np.array(frame_scores_data, dtype=np.float).T

        if not len(frame_scores) or frame_scores.shape[1] < 30:
            raise NoScoresSeen()

        isvalid = []
        valid_timestamps = []
        valid_scores = []
        score_matches = []
        for i in range(2):
            isvalid.append(~np.isnan(frame_scores[i]))
            valid_timestamps.append(score_timestamps[isvalid[i]])
            valid_scores.append(isotonic_regression(frame_scores[i, isvalid[i]].astype(np.int), 0, 13))
            score_matches.append(np.mean(frame_scores[i, isvalid[i]] == valid_scores[i]))
        validcounts = (sum(isvalid[0]), sum(isvalid[1]))
        score_match = np.mean(score_matches)
        valid_timestamps = np.array(valid_timestamps)

        self.logger.info(f'Scores observed: {len(score_timestamps)}')
        self.logger.info(f'Valid scores per side: {validcounts}')
        self.logger.info(f'Score match for default game is {score_match:.3f}')

        if np.isnan(score_match):
            raise BadRoundMatch()

        if min(validcounts) < 30:
            raise NoScoresSeen()

        score_resets = None
        has_score_resets = False
        if game_mode == game_modes.custom and score_match < 0.9:
            self.logger.info(f'Checking for score resets')
            score_resets = [max(valid_timestamps[0][0], valid_timestamps[0][1])]
            for i in range(2):
                is_firstround = modefilt(frame_scores[i, isvalid[i]], 15) == 0
                firstround_edges = arrayops.contiguous_regions(is_firstround)
                firstround_edges_t = valid_timestamps[i][firstround_edges]
                for firstround_start, firstround_end in sorted(
                    firstround_edges_t,
                    key=lambda pair: pair[1] - pair[0],
                    reverse=True
                ):
                    if firstround_end - firstround_start < 60:
                        # too short - ignore
                        continue

                    offset_from_closest = min(abs(firstround_start - existing_split) for existing_split in score_resets)
                    if offset_from_closest < 240:
                        # too close to existing split
                        continue

                    self.logger.info(f'  Found score reset at {s2ts(firstround_start)} - closest reset is {s2ts(offset_from_closest)} away')
                    score_resets.append(firstround_start)

            # remove first reset
            score_resets = score_resets[1:]

            if len(score_resets):
                self.logger.warning(f'Detected score resets - attempting modified isotonic fit with {len(score_resets)} score resets')
                valid_scores_split = []
                score_matches_split = []
                for i in range(2):
                    valid_scores_partial = []
                    last_score_reset = 0
                    for score_reset_t in sorted(score_resets + [valid_timestamps[i][-1]]):
                        score_reset_i = bisect.bisect_right(valid_timestamps[i], score_reset_t)
                        scores_in_half = frame_scores[i, isvalid[i]][last_score_reset:score_reset_i]
                        valid_scores_partial.append(isotonic_regression(scores_in_half.astype(np.int), 0, 13))
                        last_score_reset = score_reset_i
                    valid_scores_split.append(np.concatenate(valid_scores_partial))
                    assert len(valid_scores_split[i]) == len(frame_scores[i, isvalid[i]])
                    score_matches_split.append(np.mean(valid_scores_split[i] == frame_scores[i, isvalid[i]]))
                score_match_split = np.mean(score_matches_split)
                self.logger.info(f'Score match for game with resets is {score_match_split:.3f}')
                if score_match_split > score_match:
                    self.logger.warning(f'Assuming score resets')
                    valid_scores = valid_scores_split
                    score_match = score_match_split
                    has_score_resets = True
                else:
                    self.logger.warning(f'Assuming no score resets')

        if score_match < 0.75:
            raise BadRoundMatch()

        # TODO: find places where score incremented by more than one
        # Possibly best option is to use multiple methods to find round ends
        # (score increase, buy phase hud started, bomb planted hud ended) then resolve scores from the isotonic

        rounds = []
        score = [0, 0]

        self.logger.info(f'Searching for round ends:')
        round_start_timestamp = 0
        for round_index in range(99):
            if has_score_resets and len(score_resets) and round_start_timestamp > score_resets[0] - 30:
                self.logger.info(f'Got score reset for round starting at {s2ts(round_start_timestamp)}')
                score = [0, 0]
                score_resets.pop(0)

            round_start_index = [
                bisect.bisect_left(valid_timestamps[i], round_start_timestamp)
                for i in range(2)
            ]

            # Find all potential round ends where score increases by one for one team
            self.logger.info(
                f'  Checking for score transition from {score} '
                f'starting at {round_start_index} / {(len(valid_timestamps[0]), len(valid_timestamps[1]))}'
            )
            edges = [
                list(np.where(
                    (valid_scores[i][s    : -1] == score[i]) &
                    (valid_scores[i][s + 1:   ] != score[i])
                )[0] + s) if score[i] <= 12 else []
                for i, s in enumerate(round_start_index)
            ]
            self.logger.info(
                f'    Got edges: {edges} -> '
                f'{valid_timestamps[0][edges[0]] if len(edges[0]) else "-"}, '
                f'{valid_timestamps[1][edges[1]] if len(edges[1]) else "-"}'
            )

            all_edges = []
            for i in range(2):
                if edges[i]:
                    all_edges.append((edges[i][0], i))
            all_edges.sort()
            if not all_edges:
                break

            edge, winner_index = all_edges[0]

            round_end_timestamp = valid_timestamps[winner_index][edge]
            latest_round = Round(
                index=len(rounds),
                buy_phase_start=round(float(round_start_timestamp + INTER_PHASE_DURATION), 1),
                start=round(float(round_start_timestamp + INTER_PHASE_DURATION + (FIRST_BUY_PHASE_DURATION if round_index == 0 else BUY_PHASE_DURATION)), 1),
                end=round(float(round_end_timestamp), 1),
                attacking=False,
                won=winner_index == 0,
                kills=None,
            )
            self.logger.info(
                f'    {s2ts(score_timestamps[edge])} ({score_timestamps[edge]:.0f}s i={edge}), '
                f'winner={["Team1", "Team2"][winner_index]}, '
                f'score={valid_scores[winner_index][edge]}->{valid_scores[winner_index][edge + 1]}, '
                f'duration={s2ts(score_timestamps[edge] - round_start_timestamp)}: '
                f'{latest_round}'
            )
            if valid_scores[winner_index][edge + 1] != valid_scores[winner_index][edge] + 1:
                time_until_end = valid_timestamps[0][-1] - round_end_timestamp
                self.logger.warning(f'Had round with bad score increase {time_until_end:.1f}s before end')
                if time_until_end < 120:
                    self.logger.error(
                        f'Had round with bad score increase less than 60s before end - '
                        f'assuming round is final round - ignoring here, will be picked up by final round detection'
                    )
                    break
                elif not has_score_resets:
                    raise InvalidRounds('Had round with bad score increase')
                else:
                    self.logger.warning(f'Ignoring round with no score increase - likely game was reset (has_score_resets=True)')
            else:
                rounds.append(latest_round)

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

            if not has_score_resets and (score[0] == score_to_win or score[1] == score_to_win):
                self.logger.info(f'    Score limit {score_to_win} reached')
                break

        if has_score_resets:
            self.logger.info(f'Not checking for final round for scrims/score reset game')
        elif score[0] == score_to_win or score[1] == score_to_win:
            # Captured final score transition
            self.logger.info(f'Final round score transition was captured - final round was included, final score={score[0]}-{score[1]}')
            score = score[0], score[1]
        else:
            self.logger.info(f'Final round score transition was not captured - resolving final round')

            self.logger.info(f'Trying to identify final round winner')
            final_round_won = None

            # Attempt to derive final round winner (and game winner) by if one team was up by more than 1 point
            if score[0] == score_to_win - 1 and score[1] != score_to_win - 1:
                self.logger.info(f'Deriving final round win=True from score={score[0]}-{score[1]}')
                final_round_won = True
            elif score[0] != score_to_win - 1 and score[1] == score_to_win - 1:
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

        if end < rounds[-1].end:
            self.logger.info(f'Pulling round end {s2ts(rounds[-1].end)} -> {s2ts(end)}')
            rounds[-1].end = end

        if debug in [True, self.__class__.__qualname__]:
            import matplotlib.pyplot as plt
            from matplotlib import patches

            plt.figure()
            plt.title(self.__class__.__qualname__)

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

        return rounds, score, has_score_resets

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

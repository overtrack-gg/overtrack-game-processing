from collections import Counter

import logging
import numpy as np
import re
from dataclasses import dataclass
from scipy.signal import find_peaks
from typing import List, Optional, ClassVar, Union

from overtrack.frame import Frame
from overtrack.util import ts2s

ROUND_ACTIVE_PHASE_DURATION = 100
FIRST_BUY_PHASE_DURATION = 43
BUY_PHASE_DURATION = 30
INTER_PHASE_DURATION = 6

COUNTDOWN_PATTERN = re.compile(r'^[01]:\d\d$')

@dataclass
class Round:
    index: int

    buy_phase_start: float
    start: float
    end: float

    won: Optional[bool]


@dataclass
class Rounds:

    rounds: List[Round]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, frames: List[Frame], debug: Union[bool, str] = False):
        timestamp = frames[0].timestamp
        duration = frames[-1].timestamp - timestamp

        self.rounds, \
        countdown_frames, \
        countdown_values, \
        round_started_accumulator, \
        round_started_accumulator_filt = self._parse_rounds(
            frames,
            timestamp,
            duration,
        )

        self._resolve_round_results(
            frames,
            timestamp,
        )

        if debug is True or debug == self.__class__.__qualname__:
            self._show_debug(
                countdown_frames,
                countdown_values,
                duration,
                frames,
                round_started_accumulator,
                round_started_accumulator_filt,
                timestamp
            )

    def _parse_rounds(self, frames: List[Frame], timestamp: float, duration: float):
        countdown_frames = []
        countdown_values = []
        for f in frames:
            if f.valorant.timer and f.valorant.timer.countdown and COUNTDOWN_PATTERN.match(f.valorant.timer.countdown) and not f.valorant.timer.spike_planted:
                countdown = ts2s(f.valorant.timer.countdown)
                if countdown > ROUND_ACTIVE_PHASE_DURATION:
                    continue
                countdown_frames.append(f)
                countdown_values.append(countdown)

        self.logger.info(f'Parsing rounds from {len(countdown_values)} valid countdown strings')

        round_started_accumulator = np.zeros((int(duration + 0.5),))
        for f, countdown in zip(countdown_frames, countdown_values):
            if f.valorant.timer.buy_phase:
                round_start = (f.timestamp - timestamp) + countdown
                round_started_accumulator[int(round_start + 0.5)] += 1
            else:
                first_buy_phase = f.timestamp - countdown_frames[0].timestamp < FIRST_BUY_PHASE_DURATION
                buy_phase_duration = [BUY_PHASE_DURATION, FIRST_BUY_PHASE_DURATION][first_buy_phase]

                # This could be either an active round, or a round's buy phase...
                if countdown > buy_phase_duration:
                    # but by restricting to only caring if the countdown is high enough to be in a round, we only get rounds themselves.
                    # Compute the intersect of when this round would end, the from that calculate when it started, and increment accumulator
                    round_end = (f.timestamp - timestamp) + countdown
                    round_start = round_end - ROUND_ACTIVE_PHASE_DURATION
                    round_started_accumulator[int(round_start + 0.5)] += 1

        # Blur the accumulator so the countdown being a few seconds off expected still counts (although weighted less)
        round_started_accumulator_filt = np.convolve(round_started_accumulator, [0.125, 0.5, 1, 0.5, 0.125], mode='same')
        round_starts, details = find_peaks(
            round_started_accumulator,
            height=4,
            distance=FIRST_BUY_PHASE_DURATION
        )

        rounds = []
        final_round_end = (countdown_frames[-1].timestamp - timestamp) - INTER_PHASE_DURATION
        for i, start in enumerate(round_starts):
            if len(rounds):
                rounds[-1].end = int(start - (BUY_PHASE_DURATION + INTER_PHASE_DURATION))
                self.logger.info(f'Updating previous round end={rounds[-1].end}')

            round_ = Round(
                index=i,
                buy_phase_start=int(start - [BUY_PHASE_DURATION, FIRST_BUY_PHASE_DURATION][len(rounds) == 0]),
                start=int(start),
                end=int(final_round_end + 0.5),
                won=None,
            )
            rounds.append(round_)
            self.logger.info(f'Got {round_}')
        return rounds, countdown_frames, countdown_values, round_started_accumulator, round_started_accumulator_filt

    def _resolve_round_results(self, frames, timestamp):
        last_known_score = [0, 0]
        last_known_score_round = [0, 0]
        round_end_scores = {
            -1: [0, 0],
        }
        have_unknown_rounds = False
        for i, r in enumerate(self.rounds):
            self.logger.info(f'Round {i + 1}')
            if i == 0:
                continue

            frame_scores = [[], []]
            for f in frames:
                if f.valorant.top_hud and r.buy_phase_start <= f.timestamp - timestamp <= r.end:
                    for side in range(2):
                        if f.valorant.top_hud.score[side] is not None and f.valorant.top_hud.score[side] <= 12:
                            frame_scores[side].append(f.valorant.top_hud.score[side])

            score_during = [None, None]
            for side in range(2):
                observed_scores = Counter()
                observed_valid_scores = Counter()
                observed_invalid_scores = 0
                min_possible_score = last_known_score[side]
                score_known_rounds_ago = i - last_known_score_round[side]
                max_possible_score = last_known_score[side] + score_known_rounds_ago
                for observed_score in frame_scores[side]:
                    observed_scores[observed_score] += 1
                    if (
                            observed_score is not None and
                            min_possible_score <= observed_score <= max_possible_score
                    ):
                        observed_valid_scores[observed_score] += 1
                    else:
                        observed_invalid_scores += 1
                if len(observed_valid_scores):
                    observed_score, observations = observed_valid_scores.most_common(1)[0]
                    invalid_observations = observed_invalid_scores + sum(observed_valid_scores.values()) - observations
                    if observations * 0.5 > invalid_observations:
                        self.logger.info(
                            f'    Team {side} had score={observed_score} (during round) | '
                            f'valid range {min_possible_score}-{max_possible_score} | '
                            f'{observed_scores}'
                        )
                        last_known_score[side] = observed_score
                        score_during[side] = observed_score
                        last_known_score_round[side] = i
                    else:
                        self.logger.warning(
                            f'    Team {side} maybe had score={observed_score} (during round) but did not have sufficient data | '
                            f'valid range {min_possible_score}-{max_possible_score} | '
                            f'{observed_scores}'
                        )
                else:
                    self.logger.warning(
                        f'    Team {side} had no valid scores observed during round | '
                        f'valid range {min_possible_score}-{max_possible_score} | '
                        f'{observed_scores}'
                    )
            round_end_scores[i - 1] = score_during

        final_scores_observed = [Counter(), Counter()]
        game_results_observed = Counter()
        for f in frames:
            # if 'top_hud' in f and f.timestamp - timestamp > self.rounds[-1].end:
            #     for side, counter, score in zip(range(2), final_scores_observed, f.top_hud.score):
            #         min_possible_score = last_known_score[side]
            #         score_known_rounds_ago = len(self.rounds) - last_known_score_round[side]
            #         max_possible_score = last_known_score[side] + score_known_rounds_ago
            #         if score is not None and min_possible_score <= score <= max_possible_score:
            #             counter[score] += 1
            if f.valorant.postgame:
                for counter, score in zip(final_scores_observed, f.valorant.postgame.score):
                    if score is not None:
                        counter[score] += 1
                game_results_observed[f.valorant.postgame.victory] += 1
        if sum(game_results_observed.values()):
            game_won = game_results_observed.most_common(1)[0][0]
            self.logger.info(f'Got final game result: {game_results_observed} -> {["LOSS", "WIN"][game_won]}')
        else:
            game_won = None
            self.logger.info(f'Unable to get final game result - no game result')

        final_score = []
        for i, counter in enumerate(final_scores_observed):
            if sum(counter.values()):
                score, count = counter.most_common(1)[0]
                # TODO: dont use if not supermajority
                final_score.append(score)
                self.logger.info(f'Got final score for team {i}: {counter} -> {score}')
            else:
                self.logger.info(f'Unable to resolve final score for team {i}: {counter}')
                final_score.append(None)
        self.logger.info(f'Got final score: {final_score}')
        round_end_scores[len(self.rounds) - 1] = [final_score[0], final_score[1]]

        self.logger.info(f'Resolving round wins')
        for r in self.rounds:
            won = [None, None]
            score_during = round_end_scores[r.index - 1]
            score_after = round_end_scores[r.index]
            self.logger.info(f'Round {r.index + 1} had score change {score_during}->{score_after}')
            for side in range(2):
                if score_during[side] is not None and score_after[side] is not None:
                    won[side] = score_after[side] > score_during[side]
                else:
                    self.logger.warning(
                        f'    Team {side} had no incomplete scores: {score_during}->{score_after}'
                    )
            if not any(won) or all(won):
                have_unknown_rounds = True
                self.logger.warning(
                    f'    Could not infer winner for previous round'
                )
            elif won[0] is not None:
                self.logger.info(f'    Previous round result: {["LOSS", "WIN"][won[0]]}')
                r.won = won[0]
            elif won[1] is not None:
                self.logger.info(f'    Previous round result: {["LOSS", "WIN"][not won[1]]}')
                r.won = not won[1]

        if game_won is not None:
            if self.rounds[-1].won is None:
                self.rounds[-1].won = game_won
            elif game_won != self.rounds[-1].won:
                self.logger.error('Game result disagreed with final round result')
                have_unknown_rounds = False  # Only emit the one error

        # TODO: infer unknown rounds from number of rounds e.g. if 12-5 and 1 more unknown its obvious who won...

        if have_unknown_rounds:
            self.logger.error('Had rounds with unknown results')

    def _show_debug(
        self,
        countdown_frames,
        countdown_values,
        duration,
        frames,
        round_started_accumulator,
        round_started_accumulator_filt,
        timestamp
    ):
        from matplotlib import pyplot as plt
        from matplotlib import patches, lines

        def draw_rounds(y, height):
            for r in self.rounds:
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

        plt.figure()
        plt.title('Rounds (HUD Timer)')
        draw_rounds(-5, 110)

        for x, y in enumerate(round_started_accumulator_filt):
            if y:
                plt.gca().add_line(lines.Line2D(
                    (x, x),
                    (0, 100),
                    linestyle='--',
                    color='red',
                    alpha=0.2,
                    linewidth=1,
                ))
                plt.gca().add_line(lines.Line2D(
                    (x, x + 70),
                    (100, 30),
                    linestyle='--',
                    color='red',
                    alpha=0.2,
                    linewidth=1,
                ))

        blues = [], []
        greens = [], []
        for f, v in zip(countdown_frames, countdown_values):
            addto = blues
            if 'buy_phase' in f:
                addto = greens
            addto[0].append(f.timestamp - timestamp)
            addto[1].append(v)

        plt.scatter(*blues)
        plt.scatter(*greens, color='green')
        plt.plot(np.linspace(0, duration, len(round_started_accumulator)), round_started_accumulator, color='red', linestyle='--')
        plt.plot(np.linspace(0, duration, len(round_started_accumulator)), round_started_accumulator_filt, color='red')

        plt.figure()
        plt.title('HUD Score')
        draw_rounds(-1, 14)
        t0, s0 = [], []
        t1, s1 = [], []
        for f in frames:
            if 'top_hud' in f and any(r.buy_phase_start <= f.timestamp - timestamp <= r.end for r in self.rounds):
                if f.top_hud.score[0] is not None and f.top_hud.score[0] <= 12:
                    t0.append(f.timestamp - timestamp)
                    s0.append(f.top_hud.score[0])
                if f.top_hud.score[1] is not None and f.top_hud.score[1] <= 12:
                    t1.append(f.timestamp - timestamp)
                    s1.append(f.top_hud.score[1])
        plt.scatter(t0, s0)
        plt.scatter(t1, s1)
        plt.show()

    def __iter__(self):
        return iter(self.rounds)

    def __len__(self):
        return len(self.rounds)

    def __getitem__(self, item):
        return self.rounds[item]

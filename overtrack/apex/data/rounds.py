from dataclasses import dataclass
from typing import Optional

ROUND_START_DELAY = 4.0
CLOSING_DELAY = 5.0

COUNTDOWN = 10
FIRST_RING_SPAWN = 55

@dataclass
class Round:
    index: int

    ring_countdown: float
    close_time: Optional[float]

    radius: Optional[int]

    start_time: float = -1
    end_time: float = -1

    @property
    def final_outer_radius(self) -> Optional[int]:
        if self.radius:
            return self.radius + 3
        else:
            return None


ROUNDS = [
    Round(
        0,
        ring_countdown=COUNTDOWN,
        close_time=FIRST_RING_SPAWN - CLOSING_DELAY,

        radius=None
    ),

    Round(
        1,
        ring_countdown=180,
        close_time=166.66,
        radius=332,
    ),
    Round(
        2,
        ring_countdown=150,
        close_time=58.33,
        radius=218,
    ),
    Round(
        3,
        ring_countdown=135,
        close_time=41.66,
        radius=132,
    ),
    Round(
        4,
        ring_countdown=120,
        close_time=33.66,
        radius=65,
    ),
    Round(
        5,
        ring_countdown=90,
        close_time=25.0,
        radius=24,
    ),
    Round(
        6,
        ring_countdown=90,
        close_time=7.5,
        radius=10,
    ),
    Round(
        7,
        ring_countdown=120,
        close_time=8.0,
        radius=2,
    ),
    Round(
        8,
        ring_countdown=20,
        close_time=None,
        radius=None,
    ),
]

current_time = 0
for current_round in ROUNDS:
    current_round.start_time = current_time
    if current_round.close_time:
        current_time += current_round.ring_countdown + CLOSING_DELAY + current_round.close_time + ROUND_START_DELAY
        current_round.end_time = current_time
    else:
        current_round.end_time = 2000

@dataclass(frozen=True)
class RoundState:
    round: int
    ring_moving: bool

    ring_radius: Optional[int]
    next_ring_radius: Optional[int]
    ring_closing: bool

    time_into: float
    time_to_next: float


def get_round_state(t: float):
    current_time = 0
    current_ring_radius = None
    for current_round in ROUNDS:
        next_state_time = current_time + current_round.ring_countdown + CLOSING_DELAY
        if t <= next_state_time or current_round.close_time is None:
            return RoundState(
                round=current_round.index,
                ring_moving=False,

                ring_radius=current_ring_radius,
                next_ring_radius=current_round.radius,
                ring_closing=False,

                time_into=t - current_time,
                time_to_next=next_state_time - t,
            )

        current_time = next_state_time
        next_state_time = current_time + current_round.close_time + ROUND_START_DELAY

        if current_ring_radius and current_round.radius:
            frac = (t - current_time) / current_round.close_time
            ring_radius = max(current_round.radius + (current_ring_radius - current_round.radius) * (1 - frac), current_round.radius + 3)
        else:
            ring_radius = None
        if t <= next_state_time:
            return RoundState(
                round=current_round.index,
                ring_moving=True,

                ring_radius=ring_radius,
                next_ring_radius=current_round.radius,
                ring_closing=True,

                time_into=t - current_time,
                time_to_next=next_state_time - t,
            )

        current_time = next_state_time
        if current_round.radius:
            current_ring_radius = current_round.radius + 3
        else:
            current_ring_radius = None


if __name__ == '__main__':
    current = 0
    for r in ROUNDS:
        if r is None:
            current += COUNTDOWN + FIRST_RING_SPAWN
        else:
            print(f'Round {r.index} start: {current:.1f}')
            current += ROUND_START_DELAY + r.ring_countdown
            print(f'Round {r.index} closing: {current:.1f}')
            if r.close_time:
                current += CLOSING_DELAY + r.close_time

    import matplotlib.pyplot as plt

    ts, irr, orr, rin = [], [], [], []
    for t in range(1500):
        state = get_round_state(t)
        ts.append(t)
        irr.append(state.next_ring_radius)
        orr.append(state.ring_radius)
        rin.append(state.round * 10)

    plt.figure()
    plt.scatter(ts, orr, label='outer')
    plt.scatter(ts, irr, label='inner')
    plt.scatter(ts, rin, label='index')
    plt.legend()
    plt.show()


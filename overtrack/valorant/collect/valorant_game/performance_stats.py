import numpy as np
from typing import List, Optional, TYPE_CHECKING

from dataclasses import dataclass, InitVar, field

from overtrack_cv_private.games.valorant.processors.killfeed.models import Kill

if TYPE_CHECKING:
    from overtrack.valorant.collect.valorant_game.rounds import Rounds


@dataclass
class Stat:
    total: int
    per_round: float = field(init=False)
    of_total: float = field(init=False)

    num_rounds: InitVar[int]
    num_total: InitVar[int]

    def __post_init__(self, num_rounds: int, num_total: int):
        self.per_round = round(self.total / num_rounds, 3)
        self.of_total = round(self.total / num_total, 3) if num_total else 0


@dataclass
class WinCorrelatedStat:
    total: int
    per_round: float
    of_total: float

    led_to_win: int
    led_to_win_ratio: Optional[float]

    led_to_loss: int
    led_to_loss_ratio: Optional[float]

    def __init__(
        self,
        events: List[bool],
        round_won: List[bool],
        num_total: int,
    ):
        event_occurrence = np.array(events, dtype=np.bool)
        win_occurrence = np.array(round_won, dtype=np.bool)

        self.total = int(np.sum(event_occurrence))
        self.per_round = round(float(np.mean(event_occurrence)), 3)
        self.of_total = round(self.total / num_total, 3) if num_total else 0

        self.led_to_win = int(np.sum(event_occurrence & win_occurrence))
        self.led_to_win_ratio = round(self.led_to_win / self.total, 3) if self.total else None

        self.led_to_loss = int(np.sum(event_occurrence & ~win_occurrence))
        self.led_to_loss_ratio = round(self.led_to_loss / self.total, 3) if self.total else None


@dataclass
class PerformanceStats:
    kills: Stat
    deaths: Stat
    kills_per_death: Optional[float]

    team_firstbloods: WinCorrelatedStat
    team_firstdeaths: WinCorrelatedStat

    firstbloods: WinCorrelatedStat
    firstdeaths: WinCorrelatedStat

    def __init__(self, friendly_team: bool, kills: List[Kill], deaths: List[Kill], rounds: 'Rounds', match_team: Optional[bool]):
        self.kills = Stat(
            len(kills),
            len(rounds),
            len(rounds.all_kills) if match_team is None else len([
                k for k in rounds.all_kills if k.killer.friendly == match_team
            ]),
        )
        self.deaths = Stat(
            len(deaths),
            len(rounds),
            len(rounds.all_kills) if match_team is None else len([
                k for k in rounds.all_kills if k.killed.friendly == match_team
            ]),
        )
        self.kills_per_death = round(self.kills.total / self.deaths.total, 3) if self.deaths.total else None

        self.team_firstbloods = WinCorrelatedStat(
            [r.kills.firstblood(friendly_team) in kills for r in rounds],
            [r.won is True for r in rounds],
            len(rounds.firstbloods(friendly_team)),
        )
        self.team_firstdeaths = WinCorrelatedStat(
            [r.kills.firstblood(not friendly_team) in deaths for r in rounds],
            [r.won is True for r in rounds],
            len(rounds.firstbloods(not friendly_team)),
        )
        self.firstbloods = WinCorrelatedStat(
            [r.kills.firstblood() in kills for r in rounds],
            [r.won is True for r in rounds],
            len(rounds.firstbloods()),
        )
        self.firstdeaths = WinCorrelatedStat(
            [r.kills.firstblood() in deaths for r in rounds],
            [r.won is True for r in rounds],
            len(rounds.firstbloods()),
        )

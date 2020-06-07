import string
from collections import Counter

import Levenshtein as levenshtein
import itertools
import logging
import numpy as np
from dataclasses import dataclass, fields, Field, field
from typing import List, Optional, Union, ClassVar, Tuple, TYPE_CHECKING, Dict

from overtrack.frame import Frame
from overtrack.valorant.collect.valorant_game.performance_stats import PerformanceStats
from overtrack.util import textops, arrayops
from overtrack.valorant.collect.valorant_game.invalid_game import InvalidGame
from overtrack.valorant.data import AgentName
from overtrack.valorant.game.postgame import PlayerStats as PlayerStatsFrame
from overtrack.valorant.game.top_hud.models import TeamComp

if TYPE_CHECKING:
    from overtrack.valorant.collect.valorant_game.kills import Kill
    from overtrack.valorant.collect.valorant_game.rounds import Rounds
else:
    Kill = 'Kill'
    Rounds = 'Rounds'


class MissingAgents(InvalidGame):
    pass


@dataclass
class PlayerStats:
    avg_combat_score: Optional[int]
    kills: Optional[int]
    deaths: Optional[int]
    assists: Optional[int]
    econ_rating: Optional[int]
    first_bloods: Optional[int]
    plants: Optional[int]
    defuses: Optional[int]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, stats: List[PlayerStatsFrame]):
        f: Field
        for f in fields(self):
            counter = Counter()
            for stat in stats:
                raw_value = getattr(stat, f.name)
                if raw_value is not None and 0 <= raw_value <= 999:
                    counter[raw_value] += 1
                else:
                    self.logger.warning(f'Ignoring {f.name} value {raw_value}')

            if len(counter):
                value = counter.most_common(1)[0][0]
            else:
                value = None
            setattr(self, f.name, value)
            self.logger.info(f'    {f.name}: {counter} -> {value}')


ULT_MERGE_WINDOW = 80


@dataclass
class Ult:
    player: 'Player'
    index: int

    gained: float
    lost: float
    used: bool

    round_gained: int
    round_gained_timestamp: float

    round_lost: int
    round_lost_timestamp: float

    @property
    def held(self) -> Optional[float]:
        if self.used:
            return self.lost - self.gained
        else:
            return None


@dataclass
class Player:
    agent: Optional[AgentName]
    name: Optional[str]
    index: int
    friendly: bool

    ults: List[Ult] = field(default_factory=list)
    stats: Optional[PlayerStats] = field(repr=False, default=None)

    kills: List[Kill] = field(repr=False, default_factory=list)
    deaths: List[Kill] = field(repr=False, default_factory=list)
    weaponkills: Dict[Optional[str], List[Kill]] = field(repr=False, default_factory=dict)

    performance: Optional[PerformanceStats] = field(repr=False, default=None)

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def resolve_name_from_killfeed(self, frames: List[Frame]):
        names = []
        for f in frames:
            if f.valorant.killfeed:
                for k in f.valorant.killfeed.kills:
                    if self.friendly == k.killer_friendly:
                        killfeed_player = k.killer
                    else:
                        killfeed_player = k.killed
                    if killfeed_player.agent == self.agent and killfeed_player.name and len(killfeed_player.name) > 2:
                        names.append(killfeed_player.name)
        name = levenshtein.median(names)
        self.logger.info(f'Resolving {self} name={name!r} from {Counter(names)}')
        self.name = name

    def resolve_ults(self, frames: List[Frame], rounds: Rounds, debug: Union[bool, str] = False):
        self.logger.info(f'Resolving ults for {["Enemy", "Friendly"][self.friendly]} {self.agent}')

        ts, ult_match = [], []
        start = frames[0].timestamp
        for f in frames:
            if f.valorant.top_hud and f.valorant.top_hud.has_ult_match:
                team: List[Optional[AgentName]] = f.valorant.top_hud.teams[not self.friendly]
                try:
                    index = team.index(self.agent)
                except ValueError:
                    pass
                else:
                    val = f.valorant.top_hud.has_ult_match[not self.friendly][index]
                    if val is not None:
                        ts.append(f.timestamp - start)
                        ult_match.append(val)

        if len(ult_match) > 3:
            self.logger.info(f' Resolving ult periods')
            ult_match_f = np.convolve(ult_match, np.array([1, 1, 1], dtype=np.float) / 3, mode='same')
            has_ult = ult_match_f > 0.8
            has_ult_regions = arrayops.contiguous_regions(has_ult)

            ults_tss = []
            for si, ei in has_ult_regions:
                counts = np.sum(has_ult[si:ei])

                st, et = ts[si], ts[ei]
                if len(ults_tss):
                    prev_ult = ults_tss[-1]
                    if st - prev_ult[1] < ULT_MERGE_WINDOW:
                        self.logger.info(f'    Merging ult {prev_ult[0]:.1f}s->{prev_ult[1]:.1f}s with {st:.1f}s->{et:.1f}s ({counts} counts)')
                        prev_ult[1] = et
                        continue
                self.logger.info(f'  Got ult period {st:.1f}s->{et:.1f}s ({counts} counts)')
                ults_tss.append([st, et])

            self.logger.info(f' Resolving actual ults')
            for i, (st, et) in enumerate(ults_tss):
                round_gained = int(np.argmax([st < r.end for r in rounds]))
                round_lost = int(np.argmax([et < r.start for r in rounds])) - 1
                if round_lost == -1:
                    round_lost = len(rounds) - 1

                used = True
                round_lost_timestamp = et - rounds[round_lost].start
                round_duration = min(rounds[round_lost].end, ts[-1]) - rounds[round_lost].start

                infostr = ''
                if (round_lost == len(rounds) - 1 or round_lost == 11) and round_duration - round_lost_timestamp < 15:
                    infostr = f' - Ult was lost by side switch/end: round {round_lost}, ' \
                              f'{round_duration - round_lost_timestamp}s before round end'
                    used = False
                    round_lost_timestamp = round_duration

                ult = Ult(
                    player=self,
                    index=i,

                    gained=st,
                    lost=et,
                    used=used,

                    round_gained=round_gained,
                    round_gained_timestamp=st - rounds[round_gained].start,

                    round_lost=round_lost,
                    round_lost_timestamp=round_lost_timestamp,
                )
                self.logger.info(f'  {ult}{infostr}')
                self.ults.append(ult)
                if used:
                    rounds[round_lost].ults_used.append(ult)

            if debug is True or debug == 'Ults':
                import matplotlib.pyplot as plt
                from matplotlib import patches

                ofs = (self.friendly * 5.5 + self.index * 1.1)
                plt.text(-100, ofs, f'{"Enemy" if not self.friendly else ""} {self.agent}')
                plt.plot(ts, ult_match_f + ofs, label=f'{"Enemy" if not self.friendly else ""} {self.agent}')
                for si, ei in has_ult_regions:
                    plt.gca().add_patch(patches.Rectangle(
                        (ts[si], ofs + 0.1),
                        ts[ei] - ts[si],
                        0.8,
                        linewidth=1,
                        edgecolor='red',
                        color='red',
                        alpha=0.25,
                    ))
                for u in self.ults:
                    plt.gca().add_patch(patches.Rectangle(
                        (u.gained, ofs + 0.3),
                        u.lost - u.gained,
                        0.4,
                        linewidth=1,
                        edgecolor='blue',
                        color='blue',
                        alpha=0.25,
                    ))

    def resolve_performance(self, rounds: Rounds):
        self.logger.info(f'Resolving performance for {self.name}')
        self.performance = PerformanceStats(self.friendly, self.kills, self.deaths, rounds, self.friendly)
        self.logger.info(f'    {self.performance}')

    def __str__(self):
        s = f'Player(agent={self.agent}, friendly={self.friendly}'
        if self.name:
            s += f', name={self.name!r}'
        return s + ')'
    __repr__ = __str__


@dataclass
class Team:
    players: List[Player]
    friendly: bool

    performance: Optional[PerformanceStats] = None

    def resolve_performance(self, rounds: Rounds):
        self.performance = PerformanceStats(
            self.friendly,
            list(itertools.chain(*[
                p.kills for p in self.players
            ])),
            list(itertools.chain(*[
                p.deaths for p in self.players
            ])),
            rounds,
            None,
        )
        for p in self.players:
            p.resolve_performance(rounds)

    def __iter__(self):
        return iter(self.players)

    def __len__(self):
        return len(self.players)

    def __getitem__(self, item):
        return self.players[item]


@dataclass
class Teams:
    team1: Team
    team2: Team

    firstperson: Optional[Player]
    have_scoreboard: bool

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, frames: List[Frame], rounds: Rounds, debug: Union[bool, str] = False):
        # Resolve agents from top HUD
        teams = [], []
        for i, teamcomp in enumerate(self._parse_teamcomps(frames, rounds)):
            for j, agent in enumerate(teamcomp):
                teams[i].append(Player(
                    agent=agent,
                    name=None,
                    friendly=i == 0,
                    index=j,
                ))
        self.team1 = Team(teams[0], True)
        self.team2 = Team(teams[1], False)

        self.logger.info(f'Resolving player names')
        for p in self.players:
            p.resolve_name_from_killfeed(frames)

        self.logger.info(f'Resolving ults')
        if debug is True or debug == 'Ults':
            import matplotlib.pyplot as plt
            plt.figure()
        for p in self.players:
            p.resolve_ults(frames, rounds, debug)
        if debug is True or debug == 'Ults':
            import matplotlib.pyplot as plt
            from matplotlib import patches

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

            draw_rounds(-0.1, 0.1)
            plt.legend()
            plt.show()

        # Work out which is the firstperson player by matching agent selected at game start against team1
        agent_select_frames = [
            f
            for f in frames
            if f.valorant.agent_select and f.valorant.agent_select.agent
        ]
        valid_agent_select_frames = [
            f
            for f in agent_select_frames
            if f.valorant.agent_select.locked_in
        ]
        if not len(valid_agent_select_frames) and len(agent_select_frames):
            self.logger.warning(f'Got no locked in agent select frames - using {len(agent_select_frames)} not-locked-in frames')
            valid_agent_select_frames = agent_select_frames

        if len(agent_select_frames):
            agent_select = [f.valorant.agent_select.agent for f in valid_agent_select_frames]
            self.logger.info(f'Resolving firstperson agent from agent select: {agent_select}')
            agent_select_counter = Counter(agent_select)
            if agent_select_counter[agent_select[0]] != len(agent_select):
                self.logger.warning(f'Got multiple agents selected')
            done = set()
            for firstperson_agent in reversed(agent_select):
                if firstperson_agent in done:
                    continue
                done.add(firstperson_agent)
                self.logger.info(f'Checking agent select {firstperson_agent}')
                firstperson_match = [p for p in self.team1 if p.agent == firstperson_agent]
                if not len(firstperson_match):
                    self.logger.warning(f'{firstperson_agent} selected, but not observed on team - trying next most recent')
                    continue
                else:
                    self.logger.info(f'Using firstperson agent={firstperson_agent} from last observed agent')
                    self.firstperson = firstperson_match[0]
                    break
            else:
                self.logger.error(f'Could not find agent matching agent select frames')
                self.firstperson = None
        else:
            self.logger.error(f'Got no agent select frames - assuming game has no firstperson data')
            self.firstperson = None

        self.have_scoreboard = False
        self.resolve_scoreboards(frames)

    def resolve_scoreboards(self, frames):
        # Resolve names and stats from scoreboard
        scoreboards = [f.valorant.scoreboard for f in frames if f.valorant.scoreboard]
        if len(scoreboards):
            self.logger.info(f'Resolving player stats from {len(scoreboards)} scoreboard frames')
            for player in self.players:
                matching_stats = []
                for scoreboard in scoreboards:
                    for stats in scoreboard.player_stats:
                        if stats.agent == player.agent and stats.friendly == player.friendly:
                            matching_stats.append(stats)
                if len(matching_stats):
                    self.logger.info(
                        f'Resolving team {int(not player.friendly) + 1} {player.agent} from {len(matching_stats)} scoreboard frames'
                    )
                    raw_names = [textops.strip_string(s.name.upper(), alphabet=string.ascii_uppercase + string.digits + '#') for s in matching_stats]
                    resolved_name = levenshtein.median(raw_names).upper()
                    self.logger.info(f'  Got name: {Counter(raw_names)} -> {resolved_name!r} - not overriding {player.name!r}')
                    self.logger.info('  Resolving stats')
                    player.stats = PlayerStats(matching_stats)
                    self.have_scoreboard = True

        else:
            self.logger.info(f'Got no scoreboard frames - not resolving stats')

    def resolve_performance(self, rounds: Rounds):
        for t in self.teams:
            t.resolve_performance(rounds)

    def _parse_teamcomps(self, frames: List[Frame], rounds: Rounds) -> Tuple[TeamComp, TeamComp]:
        timestamp = frames[0].timestamp
        team_agents_seen = [Counter() for _ in range(2)]
        for f in frames:
            if f.valorant.top_hud:
                for side in range(2):
                    for agent in f.valorant.top_hud.teams[side]:
                        if agent:
                            team_agents_seen[side][agent] += 1

        teams = []
        error_agents = False
        for side in range(2):
            self.logger.info(f'Team {side} had agents: {team_agents_seen[side]}')

            agents = team_agents_seen[side].most_common()
            if len(agents) < 3:
                raise MissingAgents(f'Team {side} had less than 3 agents')
            elif len(agents) < 5:
                self.logger.warning(f'Team {side} had less than 5 agents - some agents will be unknown')
                agents = [a for a in agents] + [(None, 0) for _ in range(5 - len(agents))]

            team = []
            for i, (agent, count) in enumerate(agents):
                if i < 5:
                    self.logger.info(f'Team {side} agent {i} was {agent} ({count} occurrences)')
                    team.append(agent)
                else:
                    self.logger.warning(f'Team {side} had {i + 1}th agent {agent} ({count} occurrences)')
                    error_agents |= count > 10

            assert len(team) == len(set(team)), f'Teamcomp had duplicate agents'
            teams.append((team[0], team[1], team[2], team[3], team[4]))

        if error_agents:
            self.logger.error('Got additional agents seen on teams')

        return teams[0], teams[1]

    @property
    def teams(self) -> Tuple[Team, Team]:
        return self.team1, self.team2

    @property
    def players(self) -> List[Player]:
        return self.team1.players + self.team2.players

    def __iter__(self):
        return iter(self.teams)

    def __len__(self):
        return len(self.teams)

    def __getitem__(self, item):
        return self.teams[item]

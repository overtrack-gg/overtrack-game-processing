import string

import itertools
import logging
from collections import Counter

from overtrack.util import textops
from typing import List, Optional, Union, ClassVar, Tuple, TYPE_CHECKING, Dict
import Levenshtein as levenshtein
from dataclasses import dataclass, fields, Field, field, InitVar

from overtrack.frame import Frame
from overtrack.valorant.collect.valorant_game.performance_stats import PerformanceStats
from overtrack.valorant.collect.valorant_game.rounds import Rounds
from overtrack.valorant.data import AgentName
from overtrack.valorant.game.top_hud.models import TeamComp
from overtrack.valorant.game.postgame import PlayerStats as PlayerStatsFrame


if TYPE_CHECKING:
    from overtrack.valorant.collect.valorant_game.kills import Kill
else:
    Kill = 'Kill'


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


@dataclass
class Player:
    agent: Optional[AgentName]
    name: Optional[str]
    friendly: bool

    stats: Optional[PlayerStats] = field(repr=False, default=None)

    kills: List[Kill] = field(repr=False, default_factory=list)
    deaths: List[Kill] = field(repr=False, default_factory=list)
    weaponkills: Dict[str, List[Kill]] = field(repr=False, default_factory=dict)

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
            for agent in teamcomp:
                teams[i].append(Player(
                    agent,
                    None,
                    i == 0,
                ))
        self.team1 = Team(teams[0], True)
        self.team2 = Team(teams[1], False)

        self.logger.info(f'Resolving player names')
        for p in self.players:
            p.resolve_name_from_killfeed(frames)

        # Work out which is the firstperson player by matching agent selected at game start against team1
        agent_select_frames = [f for f in frames if f.valorant.agent_select and f.valorant.agent_select.agent and f.valorant.agent_select.locked_in]
        if len(agent_select_frames):
            agent_select = [f.valorant.agent_select.agent for f in agent_select_frames]
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
            self.logger.info(f'Got no agent select frames - assuming game has no firstperson data')
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
        team_agents_seen = [[Counter() for _ in range(5)] for _ in range(2)]
        for f in frames:
            # Only look at buy phase comps because the players get reordered when death spectating
            # Actually, we use the first 10s of a round to get extra data because players are dead here infrequently enough
            if f.valorant.top_hud and any(r.buy_phase_start <= f.timestamp - timestamp <= r.start + 10 for r in rounds):
                for side in range(2):
                    for i in range(5):
                        agent = f.valorant.top_hud.teams[side][i]
                        if agent:
                            team_agents_seen[side][i][agent] += 1

        teams = []
        for side in range(2):
            team = []
            for i in range(5):
                counter = team_agents_seen[side][i]
                if sum(counter.values()) > 5:
                    agent: AgentName = counter.most_common(1)[0][0]
                    team.append(agent)
                    self.logger.info(f'Team {side} agent {i} was {counter} -> {agent}')
                else:
                    self.logger.info(f'Team {side} agent {i} unknown with {counter}')
                    team.append(None)
            teams.append((team[0], team[1], team[2], team[3], team[4]))
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

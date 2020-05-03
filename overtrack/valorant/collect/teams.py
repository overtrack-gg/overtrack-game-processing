import logging
from collections import Counter
from typing import List, Optional, Union, ClassVar, Tuple
import Levenshtein as levenshtein
from dataclasses import dataclass, fields, Field

from overtrack.frame import Frame
from overtrack.valorant.collect.rounds import Rounds
from overtrack.valorant.data import AgentName
from overtrack.valorant.game.top_hud.models import TeamComp
from overtrack.valorant.game.postgame import PlayerStats as PlayerStatsFrame


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

    stats: Optional[PlayerStats] = None

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

    def __str__(self):
        s = f'Player(agent={self.agent}, friendly={self.friendly}'
        if self.name:
            s += f', name={self.name!r}'
        return s + ')'
    __repr__ = __str__


@dataclass
class Kill:
    round_timestamp: float
    timestamp: float

    killer: Player
    killed: Player
    weapon: str


@dataclass
class Kills:
    kills: List[Kill]

    def __iter__(self):
        return iter(self.kills)
    def __len__(self):
        return len(self.kills)
    def __getitem__(self, item):
        return self.kills[item]


@dataclass
class Teams:
    team1: List[Player]
    team2: List[Player]

    firstperson: Optional[Player]
    have_scoreboard: bool

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, frames: List[Frame], rounds: Rounds, debug: Union[bool, str] = False):
        # Resolve agents from top HUD
        self.team1, self.team2 = [], []
        for i, teamcomp in enumerate(self._parse_teamcomps(frames, rounds)):
            for agent in teamcomp:
                self.teams[i].append(Player(
                    agent,
                    None,
                    i == 0,
                    ))

        self.logger.info(f'Resolving player names')
        for p in self.players:
            p.resolve_name_from_killfeed(frames)

        # Work out which is the firstperson player by matching agent selected at game start against team1
        agent_select_frames = [f for f in frames if f.valorant.agent_select and f.valorant.agent_select.agent and f.valorant.agent_select.locked_in]
        if len(agent_select_frames):
            firstperson_agent, count = Counter([f.valorant.agent_select.agent for f in agent_select_frames]).most_common(1)[0]
            self.logger.info(f'Got firstperson agent={firstperson_agent!r} with {count} observations')
            self.firstperson = [p for p in self.team1 if p.agent == firstperson_agent][0]
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
                    raw_names = [s.name for s in matching_stats]
                    player.name = levenshtein.median(raw_names).upper()
                    self.logger.info(f'  Resolved name: {Counter(raw_names)} -> {player.name}')
                    self.logger.info('  Resolving stats')
                    player.stats = PlayerStats(matching_stats)
                    self.have_scoreboard = True

        else:
            self.logger.info(f'Got no scoreboard frames - not resolving stats')

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
            teams.append((team[0], team[1], team[2], team[3], team[4]))
        return teams[0], teams[1]

    @property
    def teams(self) -> List[List[Player]]:
        return [self.team1, self.team2]

    @property
    def players(self) -> List[Player]:
        return self.team1 + self.team2

    def __iter__(self):
        return iter(self.teams)

    def __len__(self):
        return len(self.teams)

    def __getitem__(self, item):
        return self.teams[item]

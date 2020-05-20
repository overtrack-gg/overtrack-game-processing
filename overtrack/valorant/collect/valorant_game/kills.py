
import logging
from typing import List, TYPE_CHECKING, ClassVar, Optional

import Levenshtein as levenshtein
import numpy as np
from dataclasses import dataclass, field

from overtrack.frame import Frame
from overtrack.util import s2ts, arrayops
from overtrack.valorant.game.killfeed import Kill as FrameKill

if TYPE_CHECKING:
    from overtrack.valorant.collect.valorant_game.teams import Teams, Player, AgentName
else:
    Teams = 'Teams'
    Player = 'Player'
    AgentName = 'AgentName'


@dataclass
class Kill:
    round: int
    round_timestamp: float
    timestamp: float

    killer: Player
    killed: Player
    weapon: Optional[str]

    wallbang: bool = False
    headshot: bool = False

    def __str__(self):
        return (
            f'Kill('
                f'round={self.round}, '
                f'{s2ts(self.round_timestamp)}, '
                f'{["Enemy", "Ally"][self.killer.friendly]} {self.killer.agent} {self.killer.name!r} > '
                f'{self.weapon} {"- " if self.wallbang else ""}{"* " if self.headshot else ""}> '
                f'{self.killed.agent} {self.killed.name!r}'
            f')'
        )
    __repr__ = __str__


@dataclass(frozen=True)
class KillKey:
    killer_friendly: bool
    killer_agent: AgentName
    killed_agent: AgentName


@dataclass
class UnresolvedKill:
    key: KillKey
    timestamps: List[float] = field(default_factory=list)
    raw_kills: List[FrameKill] = field(default_factory=list)

    def __len__(self):
        return len(self.raw_kills)

    def __str__(self):
        s = f'UnresolvedKill('
        if len(self.timestamps):
            s += s2ts(self.timestamps[0]) + ', '
        s += (
            ['Enemy', 'Ally'][self.key.killer_friendly] +
            ' ' +
            self.key.killer_agent +
            ' > ' +
            self.key.killed_agent
        )
        s += f', {len(self)} observations'
        return s
    __repr__ = __str__

@dataclass
class Kills:
    SAME_KILL_WINDOW = 7

    kills: List[Kill]

    def firstblood(self, for_team: Optional[bool] = None) -> Optional[Kill]:
        km = [k for k in self.kills if for_team is None or k.killer.friendly == for_team]
        if not len(km):
            return None
        else:
            return km[0]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, frames: List[Frame], teams: Teams, round: int, base_timestamp: float, round_start: float, round_end: float):
        self.logger.info(f'Resolving kills for round staring at {s2ts(round_start)}')

        unresolved_kills = []
        recent_kills = {}
        _k2f = {}
        for f in frames:
            game_timestamp = int(f.timestamp - base_timestamp)
            if round_start < game_timestamp < round_end + 15 and f.valorant.killfeed:
                for raw_kill in f.valorant.killfeed:
                    key = KillKey(raw_kill.killer_friendly, raw_kill.killer.agent, raw_kill.killed.agent)
                    kill = recent_kills.get(key)
                    if kill and game_timestamp - kill.timestamps[-1] > self.SAME_KILL_WINDOW:
                        self.logger.warning(
                            f'Found matching kill {raw_kill.killer.agent} > {raw_kill.killed.agent} after being unobserved for '
                            f'{game_timestamp - kill.timestamps[-1]}s  - '
                            f'considering as distinct'
                        )
                        kill = None
                    if not kill:
                        kill = UnresolvedKill(key)
                        unresolved_kills.append(kill)
                        recent_kills[key] = kill

                    kill.timestamps.append(game_timestamp)
                    kill.raw_kills.append(raw_kill)

                    _k2f[id(kill)] = f

        self.kills = []
        self.logger.debug(f'Got {len(unresolved_kills)} kills to resolve:')
        for unresolved_kill in unresolved_kills:
            self.logger.debug(f'  {s2ts(unresolved_kill.timestamps[0])} {unresolved_kill}')

            killer_player = self._get_player_by_agent(
                teams[not unresolved_kill.key.killer_friendly],
                unresolved_kill.key.killer_agent
            )
            if not killer_player:
                killer_player = self._get_player_by_names(
                    teams[not unresolved_kill.key.killer_friendly],
                    [r.killer.name for r in unresolved_kill.raw_kills]
                )

            killed_player = self._get_player_by_agent(
                teams[unresolved_kill.key.killer_friendly],
                unresolved_kill.key.killed_agent
            )
            if not killed_player:
                killed_player = self._get_player_by_names(
                    teams[unresolved_kill.key.killer_friendly],
                    [r.killed.name for r in unresolved_kill.raw_kills]
                )

            weapon = arrayops.most_common([r.weapon for r in unresolved_kill.raw_kills if r.weapon])
            wallbang = sum(r.wallbang for r in unresolved_kill.raw_kills) > 0.25 * len(unresolved_kill.raw_kills)
            headshot = sum(r.headshot for r in unresolved_kill.raw_kills) > 0.25 * len(unresolved_kill.raw_kills)

            self.logger.debug(f'    Killer: {[r.killer.name for r in unresolved_kill.raw_kills]} > {killer_player}')
            self.logger.debug(f'    Killed: {[r.killed.name for r in unresolved_kill.raw_kills]} > {killed_player}')
            self.logger.debug(f'    Weapon: {[r.weapon for r in unresolved_kill.raw_kills]} > {weapon}')

            # if not weapon or (killer_player and not killed_player) or (not killer_player and killed_player):
            #     # import cv2
            #     # print(unresolved_kill.key)
            #     # print(unresolved_kill.raw_kills[0])
            #     # print(_k2f[id(unresolved_kill)].debug_image_path)
            #     # cv2.imshow('kill', cv2.imread(_k2f[id(unresolved_kill)].debug_image_path))
            #     # cv2.waitKey(0)
            #     import shutil, os
            #     f = _k2f[id(unresolved_kill)]
            #     shutil.copy(f.image_path, os.path.join(f"D:/overtrack/valorant_stream_client/unknownkills/{f.timestamp}.png"))

            if not killer_player or not killed_player:
                self.logger.warning(f'      > Unable to resolve kill {unresolved_kill.key}')
                continue

            # killer_player_match = np.mean([levenshtein.ratio(r.killer.name, killer_player.name) for r in unresolved_kill.raw_kills])
            # killed_player_match = np.mean([levenshtein.ratio(r.killed.name, killed_player.name) for r in unresolved_kill.raw_kills])
            kill = Kill(
                round,
                unresolved_kill.timestamps[0] - round_start,
                unresolved_kill.timestamps[0],
                killer_player,
                killed_player,
                weapon,
                wallbang=wallbang,
                headshot=headshot,
            )
            self.kills.append(kill)
            killer_player.kills.append(kill)
            killer_player.weaponkills.setdefault(kill.weapon, []).append(kill)
            killed_player.deaths.append(kill)

            self.logger.info(f'      > {kill}')

    def _get_player_by_agent(self, team: List[Player], agent: AgentName) -> Optional[Player]:
        match = [p for p in team if p.agent == agent]
        if not len(match):
            self.logger.warning(f'Unable to find {agent} on team {team}')
            return None
        elif len(match) > 1:
            self.logger.warning(f'Found multiple players playing {agent} on team {team}')
        return match[0]

    def _get_player_by_names(self, team: List[Player], names: List[str]) -> Optional[Player]:
        matches = [
            np.mean([levenshtein.ratio(p.name, n) for n in names])
            for p in team
        ]
        am = arrayops.argmax(matches)
        if matches[am] > 0.9:
            return team[am]
        else:
            self.logger.warning(f'Could not resolve player from names {names} on team {team}')
        return None

    def __str__(self):
        return str(self.kills)
    def __repr__(self):
        return repr(self.kills)

    def __iter__(self):
        return iter(self.kills)
    def __len__(self):
        return len(self.kills)
    def __getitem__(self, item):
        return self.kills[item]

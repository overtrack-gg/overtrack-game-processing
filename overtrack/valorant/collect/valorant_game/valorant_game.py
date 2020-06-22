import copy
import itertools

import os

import datetime
import logging
from collections import Counter

import requests
from overtrack.source.twitch_source import TwitchSource
from overtrack.valorant.collect.valorant_game.performance_stats import PerformanceStats
from typing import List, ClassVar, Tuple, Union, Optional, Dict, Any, cast

import shortuuid
from dataclasses import dataclass, fields

from overtrack.frame import Frame, ValorantData
from overtrack.util import textops
from overtrack.util.prettyprint import DataclassPrettyPrinter
from overtrack.valorant import data
from overtrack.valorant.collect.valorant_game.invalid_game import InvalidGame
from overtrack.valorant.collect.valorant_game.kills import Kills, Kill
from overtrack.valorant.collect.valorant_game.rounds import Rounds
from overtrack.valorant.collect.valorant_game.teams import Teams, Player, Ult
from overtrack.valorant.collect.valorant_game.clips import Clip, make_clips
from overtrack.valorant.data import MapName, GameModeName, game_modes
from overtrack_models.dataclasses.typedload import referenced_typedload, typedload

VERSION = '1.2.0'
GET_VOD_URL = os.environ.get('GET_VOD_URL', 'https://m9e3shy2el.execute-api.us-west-2.amazonaws.com/{twitch_user}/vod/{time}?pts={pts}')


class NoMap(InvalidGame):
    pass
class InvalidMode(InvalidGame):
    pass
class NoMode(InvalidMode):
    pass
class UnsupportedMode(InvalidMode):
    pass


@dataclass
class ValorantGame:
    key: str
    timestamp: float
    duration: float

    spectated: bool

    won: Optional[bool]

    map: MapName
    game_mode: GameModeName
    rounds: Rounds
    teams: Teams

    start_pts: Optional[float]
    vod: Optional[str]
    clips: Optional[List[Clip]]

    season_mode_id: int
    frames_count: int
    game_version: str

    version: str

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    @property
    def score(self) -> Optional[Tuple[int, int]]:
        return self.rounds.final_score

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=0)))

    @property
    def kills(self) -> List[Kill]:
        return list(itertools.chain.from_iterable([
            r.kills for r in self.rounds
        ]))

    def __init__(
        self,
        frames: List[Frame],
        key: Optional[str] = None,
        resolve_vod: bool = True,
        twitch_username: Optional[str] = None,
        debug: Union[bool, str] = False
    ):
        self.logger.info(f'Resolving valorant game from {len(frames)} frames')
        self.logger.info(f'Resolving frames {frames[0].timestamp_str} -> {frames[-1].timestamp_str}')

        if 'frame_info' in frames[0]:
            self.start_pts = round(frames[0].frame_info.pts, 2)
            self.logger.info(f'Got game pts_timestamp={self.start_pts}')
        else:
            self.start_pts = None

        framemakeup = Counter()
        for frame in frames:
            for f in fields(ValorantData):
                if getattr(frame.valorant, f.name):
                    framemakeup[f.name] += 1
        self.logger.info(f'Frame data seen: {framemakeup}')

        self.timestamp = frames[0].timestamp
        if key:
            self.key = key
        else:
            slug = shortuuid.uuid()[:6]
            self.key = f'VALORANT/{self.time.strftime("%Y-%m-%d-%H-%M")}-{slug}'

        self.spectated = False

        self.map = self._resolve_map(frames)
        self.game_mode = self._resolve_game_mode(frames)

        self.rounds = Rounds(frames, self.game_mode, debug)
        self.duration = self.rounds[-1].end
        self.teams = Teams(frames, self.rounds, debug)

        for r in self.rounds:
            r.resolve_kills_spike_win(frames, self.teams, self.timestamp, self.game_mode)

        self.teams.resolve_performance(self.rounds)

        if self.rounds.has_game_resets:
            self.won = None
        elif self.rounds[-1].won is not None:
            self.won = self.rounds[-1].won
        elif self.score and self.score[0] == 13:
            self.won = True
        elif self.score and self.score[1] == 13:
            self.won = False
        else:
            self.won = None

        if self.game_mode == game_modes.custom:
            self.season_mode_id = -1
        elif self.game_mode == game_modes.unrated:
            self.season_mode_id = 0
        else:
            self.season_mode_id = 1

        self.frames_count = len(frames)

        self.vod = None
        self.clips = []
        if resolve_vod:
            vod_username = self.resolve_vod(frames, twitch_username)
            if vod_username:
                self.vod, twitch_username = vod_username
                self.clips = make_clips(self, frames, twitch_username)

        self.game_version = data.get_version(self.time).name

        self.version = VERSION

    def _resolve_map(self, frames: List[Frame]) -> Optional[MapName]:
        mapcounter = Counter()
        map_texts = []
        for f in frames:
            if f.valorant.agent_select and f.valorant.agent_select.map:
                map_texts.append(f.valorant.agent_select.map)
            elif f.valorant.postgame and f.valorant.postgame.map:
                map_texts.append(f.valorant.postgame.map)
        for map_text in map_texts:
            map_ = textops.best_match(
                map_text,
                [f'MAP - {m.upper()}' for m in data.maps] + data.maps,
                data.maps + data.maps,
                threshold=0.75,
                disable_log=False,
                )
            if map_:
                mapcounter[map_] += 1
        if not len(mapcounter):
            raise NoMap()
        bestmap, count = mapcounter.most_common(1)[0]
        self.logger.info(f'Resolving map {mapcounter} -> {bestmap}')
        if len(mapcounter) > 1 and mapcounter.most_common(2)[1][1] > 0.25 * count:
            self.logger.error('Got multiple matching maps')
        return bestmap

    def _resolve_game_mode(self, frames: List[Frame]) -> Optional[GameModeName]:
        modecounter = Counter()
        mode_texts = []
        for f in frames:
            if f.valorant.agent_select and f.valorant.agent_select.game_mode:
                mode_texts.append(f.valorant.agent_select.game_mode)
            elif f.valorant.postgame and f.valorant.postgame.game_mode:
                mode_texts.append(f.valorant.postgame.game_mode)
        mode_texts = mode_texts[-50:]
        for mode_text in mode_texts:
            mode = textops.best_match(
                mode_text,
                [f'STANDARD - {m.upper()}' for m in data.game_modes[:-1]] +
                data.game_modes[:-1] + [data.game_modes.spike_rush.upper(), 'spike rush - custom'.upper()],
                data.game_modes[:-1] + data.game_modes + ['spike rush - custom'],
                threshold=0.75,
                disable_log=False,
            )
            if mode:
                modecounter[mode] += 1
        if not len(modecounter):
            raise NoMode()
        bestmode, _ = modecounter.most_common(1)[0]
        self.logger.info(f'Resolving mode {modecounter} -> {bestmode}')
        if bestmode == 'spike rush - custom':
            raise UnsupportedMode()
        return bestmode

    def resolve_vod(self, frames: List[Frame], twitch_username: Optional[str]) -> Optional[Tuple[str, str]]:
        source = frames[0].source
        if isinstance(source, TwitchSource):
            self.logger.info(f'Resolving twitch username from {source}')
            twitch_username = source.username

        if not twitch_username:
            return None

        self.logger.info(f'Resolving VODs/clips for twitch user {twitch_username}')

        try:
            vod_r = requests.get(
                GET_VOD_URL.format(
                    twitch_user=twitch_username,
                    time=self.time,
                    pts=self.start_pts,
                ),
                timeout=30,
            )
            self.logger.info(f'{vod_r.url} -> {vod_r.status_code}: {vod_r.text[:100]}')
            if vod_r.status_code == 404:
                self.logger.warning(f'Could not resolve twitch user')
                return None
            else:
                vod_r.raise_for_status()
                vod_r.json()
        except:
            self.logger.exception('Got exception resolving vod')
            return None

        vod_url = vod_r.json()['vod_timestamp_url']
        self.logger.info(f'Resolved vod_url={vod_url}')

        return vod_url, twitch_username

    @property
    def summary(self) -> str:
        _printed = set()
        _entered = set()
        _printed_players = set()
        oself = self
        class ValorantGamePrettyPrinter(DataclassPrettyPrinter):

            def force_use_repr(self, object):
                return isinstance(object, Kill)

            def allow_use_repr(self, object):
                return id(oself.teams) not in _entered

            def _pprint_list(self, object, stream, indent, allowance, context, level):
                if len(object) > 1:
                    stream.write('[\n' + (' ' * (indent + 4)))
                    self._format_items(object, stream, indent + 3, allowance + 1, context, level)
                    stream.write('\n' + (' ' * (indent)) + ']')
                else:
                    super()._pprint_list(object, stream, indent, allowance, context, level)

            def _pprint_dataclass(self, object, stream, *args, **kwargs):
                _entered.add(id(object))

                done = False
                if id(oself.teams) in _entered:
                    # processing teams
                    if isinstance(object, Player):
                        # Print all fields even if repr=False
                        super()._pprint_dataclass(object, stream, *args, **kwargs, respect_repr_hint=id(object) in _printed_players)
                        _printed_players.add(id(object))
                        done = True
                    elif isinstance(object, Kill):
                        stream.write(repr(object))
                        done = True

                if isinstance(object, PerformanceStats):
                    stream.write('...')
                elif isinstance(object, Ult):
                    ult_copy = copy.copy(object)
                    ult_copy.player = repr(ult_copy.player)
                    super()._pprint_dataclass(ult_copy, stream, *args)
                elif not done:
                    super()._pprint_dataclass(object, stream, *args)

                _entered.remove(id(object))
                _printed.add(id(object))

        printer = ValorantGamePrettyPrinter(width=220)
        return printer.pformat(self)

    def print_summary(self) -> None:
        print(self.summary)

    def to_dict(self) -> Dict:
        convert: ValorantGame = copy.deepcopy(self)
        if convert.teams.firstperson:
            convert.teams.firstperson = convert.teams.firstperson.agent

        for k in convert.kills:
            cast(Any, k).killer = (k.killer.friendly, k.killer.agent)
            cast(Any, k).killed = (k.killed.friendly, k.killed.agent)

        for r in convert.rounds:
            cast(Any, r).ults_used = [((u.player.friendly, u.player.agent), u.index) for u in r.ults_used]
            if r.spike_planter:
                cast(Any, r).spike_planter = (r.spike_planter.friendly, r.spike_planter.agent)

        for p in convert.teams.players:
            cast(Any, p).kills = [
                (k.round, k.index) for k in p.kills
            ]
            cast(Any, p).deaths = [
                (k.round, k.index) for k in p.deaths
            ]
            p.weaponkills = {
                w: [
                    (k.round, k.index) for k in ks
                ]
                for w, ks in p.weaponkills.items()
            }
            for u in p.ults:
                cast(Any, u).player = None

        rdata = typedload.dump(convert)
        for p in rdata['teams']['team1']['players'] + rdata['teams']['team2']['players']:
            for u in p.get('ults', []):
                del u['player']
        return rdata


def main():
    from overtrack.util.logging_config import config_logger
    config_logger('valorant_game', level=logging.INFO, write_to_file=False)

    import json
    from overtrack.util import frameload

    frames_path = "C:/tmp/08-09-07-TnHnFjMR45rf4XoUVLNRTz.frames.json"

    with open(frames_path) as frame:
        frames = frameload.frames_load(json.load(frame), List[Frame])

    game = ValorantGame(frames, debug=False)
    game.print_summary()

    data = game.asdict()
    from overtrack_models.dataclasses.valorant import ValorantGame as DataclassValorantGame
    game2 = referenced_typedload.load(data, DataclassValorantGame)
    print(game2)

    from overtrack_models.orm.valorant_game_summary import ValorantGameSummary
    summary = ValorantGameSummary.create(
        game,
        0,
        0,
        'http://example.com',
    )
    print(summary)

    import os
    os.environ['DISCORD_BOT_TOKEN'] = ''
    from overtrack.valorant.collect.notifications import ValorantTwitchMessage
    msg = ValorantTwitchMessage(game, summary, 'http://example.com', 'USER')
    print(msg)


if __name__ == '__main__':
    main()

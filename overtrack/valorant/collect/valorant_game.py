import copy
import datetime
import logging
from collections import Counter
from typing import List, ClassVar, Tuple, Union, Optional, Dict, Any

import shortuuid
from dataclasses import dataclass, Field, fields

from overtrack.frame import Frame
from overtrack.util import textops, humansize
from overtrack.util.prettyprint import pprint, DataclassPrettyPrinter
from overtrack.valorant import data
from overtrack.valorant.collect.kills import Kills, Kill
from overtrack.valorant.collect.rounds import Rounds
from overtrack.valorant.collect.teams import Teams, Player
from overtrack_models.dataclasses.typedload import referenced_typedload
from overtrack_models.dataclasses.valorant import MapName

VERSION = '0.9.0'


class GameParseError(Exception):
    pass


class NoMapError(GameParseError):
    pass


@dataclass
class ValorantGame:
    key: str
    timestamp: float
    duration: float

    spectated: bool

    won: Optional[bool]

    map: MapName
    rounds: Rounds
    teams: Teams

    version: str

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    @property
    def score(self) -> Optional[Tuple[int, int]]:
        return self.rounds.final_score

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp)

    def __init__(self, frames: List[Frame], key: Optional[str] = None, debug: Union[bool, str] = False):
        self.logger.info(f'Resolving valorant game from {len(frames)} frames')
        self.logger.info(f'Resolving frames {frames[0].timestamp_str} -> {frames[-1].timestamp_str}')

        self.timestamp = frames[0].timestamp
        if key:
            self.key = key
        else:
            slug = shortuuid.uuid()[:6]
            self.key = f'VALORANT/{self.time.strftime("%Y-%m-%d-%H-%M")}-{slug}'

        self.spectated = False

        map_ = self._resolve_map(frames)
        self.map = map_

        self.rounds = Rounds(frames, debug)
        self.duration = self.rounds[-1].end
        self.teams = Teams(frames, self.rounds, debug)

        for r in self.rounds:
            r.kills = Kills(frames, self.teams, r.index, self.timestamp, r.start, r.end)

        if self.rounds[-1].won is not None:
            self.won = self.rounds[-1].won
        elif self.score:
            self.won = self.score[0] > self.score[1]
        else:
            self.won = None

        self.version = VERSION

    def _resolve_map(self, frames):
        mapcounter = Counter()
        map_texts = []
        for f in frames:
            if f.valorant.agent_select and f.valorant.agent_select.map:
                map_texts.append(f.valorant.agent_select.map)
            elif f.valorant.postgame and f.valorant.postgame.map:
                map_texts.append(f.valorant.postgame.map)
        map_texts = map_texts[-50:]
        map_ = None
        for map_text in map_texts:
            map_ = textops.best_match(
                map_text,
                data.maps,
                threshold=0.75,
                disable_log=True,
            )
            if map_:
                mapcounter[map_] += 1
        if not map_:
            raise NoMapError()
        self.logger.info(f'Resolving map {mapcounter} -> {map_}')
        return map_

    def asdict(self) -> Dict[str, Any]:
        return referenced_typedload.dump(self)

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

                if not done:
                    super()._pprint_dataclass(object, stream, *args)

                _entered.remove(id(object))
                _printed.add(id(object))

        printer = ValorantGamePrettyPrinter()
        return printer.pformat(self)

    def print_summary(self) -> None:
        print(self.summary)


def main():
    from overtrack.util.logging_config import config_logger
    config_logger('valorant_game', level=logging.INFO, write_to_file=False)

    import json
    from overtrack.util import frameload

    frames_path = "D:/overtrack/valorant_stream_client/games/2020-05-04-02-49-24.frames.json"

    with open(frames_path) as frame:
        frames = frameload.frames_load(json.load(frame), List[Frame])

    # import cv2
    # from overtrack.valorant.game.default_pipeline import create_pipeline
    # from overtrack.frame import ValorantData
    # from tqdm import tqdm
    #
    # proc = create_pipeline(aggressive=True)
    # for frame in tqdm(frames):
    #     del frame['image']
    #     del frame['debug_image']
    #     frame.image = cv2.imread(frame.image_path)
    #     frame.debug_image = frame.image.copy()
    #     del frame['valorant']
    #     frame.valorant = ValorantData()
    #
    #     proc.process(frame)
    #     cv2.waitKey(1)
    #
    #     cv2.imwrite(frame.debug_image_path, frame.debug_image)
    #     cv2.imshow('frame', frame.debug_image)
    #
    #     frame.strip()
    #     with open(frame.frame_path, 'w') as f:
    #         json.dump(frameload.frames_dump(frame), f, indent=2)
    #
    # with open(frames_path, 'w') as f:
    #     json.dump(frameload.frames_dump(frames), f, indent=2)

    game = ValorantGame(frames, debug=False)
    game.print_summary()

    data = game.asdict()
    from overtrack_models.dataclasses.valorant import ValorantGame as DataclassValorantGame
    game2 = referenced_typedload.load(data, DataclassValorantGame)
    print(game2)

    # mendokills_round = []
    # firstbloods = 0
    # weapons = Counter()
    # for r in game.rounds:
    #     if r.kills[0].killer.name == 'MENDO':
    #         firstbloods += 1
    #     mendokills_round.append([
    #         k for k in r.kills
    #         if k.killer.name == 'MENDO'
    #     ])
    #     for k in r.kills:
    #         if k.killer.name == 'MENDO' and k.weapon:
    #             weapons[k.weapon] += 1
    # print([len(ks) for ks in mendokills_round])
    # print(firstbloods)
    # from overtrack.twitch import twitch_bot
    # import numpy as np
    # if len(weapons):
    #     weapon, count = weapons.most_common(1)[0]
    #     twitch_bot.send_message(
    #         'mendo',
    #         f"Mendo got {np.mean([len(ks) for ks in mendokills_round]):.2f} kills/round, and {firstbloods} first bloods. "
    #         f"Best weapon: {weapon.title()} with {count} kills. Best round: {np.max([len(ks) for ks in mendokills_round])} kills"
    #     )

    from overtrack_models.orm.valorant_game_summary import ValorantGameSummary
    summary = ValorantGameSummary.create(
        game,
        0,
        0,
        'http://example.com',
    )
    print(summary)



if __name__ == '__main__':
    main()

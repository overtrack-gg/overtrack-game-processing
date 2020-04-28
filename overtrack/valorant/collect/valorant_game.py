import datetime
import logging
from collections import Counter
from typing import List, ClassVar, Tuple, Union, Optional, Dict, Any

import shortuuid
from dataclasses import dataclass

from overtrack.frame import Frame
from overtrack.util import textops
from overtrack.util.prettyprint import pprint
from overtrack.valorant import data
from overtrack.valorant.collect.rounds import Rounds
from overtrack.valorant.collect.teams import Teams
from overtrack_models.dataclasses.typedload import referenced_typedload
from overtrack_models.dataclasses.valorant import MapName

VERSION = '1.0.0'


class GameParseError(Exception):
    pass


class NoMapError(GameParseError):
    pass


@dataclass
class ValorantGame:

    timestamp: float
    duration: float

    spectated: bool

    map: MapName
    rounds: Rounds
    teams: Teams
    score: Tuple[Optional[int], Optional[int]]

    version: str = VERSION

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, frames: List[Frame], key: Optional[str] = None, debug: Union[bool, str] = False):
        self.timestamp = frames[0].timestamp
        if key:
            self.key = key
        else:
            slug = shortuuid.uuid()[:6]
            self.key = f'VALORANT/{self.time.strftime("%Y-%m-%d-%H-%M")}-{slug}'

        self.spectated = False

        mapcounter = Counter()
        map_texts = []
        for f in frames:
            if f.valorant.agent_select:
                map_texts.append(f.valorant.agent_select.map)
            elif f.valorant.postgame:
                map_texts.append(f.valorant.postgame.map)
        map_texts = map_texts[-50:]
        for map_text in map_texts:
            map_ = textops.best_match(
                map_text,
                data.maps,
                threshold=0.75,
                disable_log=True,
            )
            if map_:
                mapcounter[map_] += 1
        if not len(mapcounter):
            raise NoMapError()
        self.map = mapcounter.most_common(1)[0][0]
        self.logger.info(f'Resolving map {mapcounter} -> {self.map}')

        self.rounds = Rounds(frames, debug)
        self.duration = self.rounds[-1].end
        self.teams = Teams(frames, self.rounds, debug)

        score = [0, 0]
        if self.won is not None:
            score[self.won - 1] = 13
            score[self.won] = len(self.rounds) - 13
            self.logger.info(
                f'Resolved score={score} from known winning team (team {int(not self.won) + 1}) '
                f'and number of rounds ({len(self.rounds)})'
            )
        else:
            for round_ in self.rounds:
                if round_.won is not None:
                    score[1 - round_.won] += 1
            self.logger.warning(f'Game winner unknown - resolved score={score} from round win totals')
        self.score = score[0], score[1]

    @property
    def won(self) -> Optional[bool]:
        return self.rounds[-1].won

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.timestamp)

    def asdict(self) -> Dict[str, Any]:
        return referenced_typedload.dump(self)


def main():
    from overtrack.util.logging_config import config_logger
    config_logger('valorant_game', level=logging.INFO, write_to_file=False)

    import json
    from overtrack.util import frameload

    # with open("C:/Users/simon/overtrack_2/overtrack_2/overtrack/valorant/frames.json") as f:
    #     frames = frameload.frames_load(json.load(f), List[Frame])
    #
    # filt_frames = []
    # started = False
    # for f in frames:
    #     if 'agent_select' in f:
    #         if len(filt_frames) and f.timestamp - filt_frames[0].timestamp > 120:
    #             print('stopping after', filt_frames[-1].timestamp - filt_frames[0].timestamp)
    #             break
    #         started = True
    #     # if started:
    #     #     filt_frames.append(f)
    #     if started and (not len(filt_frames) or f.timestamp - filt_frames[-1].timestamp >= 2):
    #         filt_frames.append(f)
    # with open('./game-frames.json', 'w') as f:
    #     json.dump(frameload.frames_dump(filt_frames), f, indent=2)

    with open("C:/Users/simon/overtrack_2/overtrack_2/overtrack/valorant/frames.json") as f:
        frames = frameload.frames_load(json.load(f), List[Frame])

    # frames = []
    # started = False
    # for p in tqdm(sorted(glob.glob("D:/overtrack/valorant_stream/*.json"))):
    #     with open(p) as f:
    #         frame = frameload.frames_load(json.load(f), Frame)
    #     if 'agent_select' in frame:
    #         started = True
    #         if len(frames) and frame.timestamp - frames[0].timestamp > 90:
    #             break
    #     if started:
    #         frames.append(frame)

    game = ValorantGame(frames, debug=False)
    pprint(game)

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

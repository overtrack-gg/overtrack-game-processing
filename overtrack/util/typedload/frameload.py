from typing import Dict, Any, Type, Union, TypeVar

from overtrack.frame import Frame, Timings
from overtrack.source.display_duplication import DisplayDuplicationSource
from overtrack.source.shmem import SharedMemorySource
from overtrack.util.typedload.referenced_typedload import ReferencedLoader, ReferencedDumper

import overtrack.overwatch.game.objective.models
import overtrack.overwatch.game.objective_2.models
import overtrack.overwatch.game.killfeed_2.models
import overtrack.overwatch.game.tab.models
import overtrack.overwatch.game.loading_map.models
import overtrack.overwatch.game.spectator.models
import overtrack.overwatch.game.menu.models
import overtrack.overwatch.game.score.models
import overtrack.overwatch.game.endgame.models
import overtrack.overwatch.game.hero.models
import overtrack.overwatch.game.endgame_sr.models
import overtrack.overwatch.game.hero_select.models
import overtrack.overwatch.game.role_select.models
import overtrack.overwatch.game.eliminations.models
import overtrack.overwatch.game.overwatch_metadata

import overtrack.apex.game.match_status.models
import overtrack.apex.game.match_summary.models
import overtrack.apex.game.menu.models
import overtrack.apex.game.squad.models
import overtrack.apex.game.your_squad.models
import overtrack.apex.game.weapon.models
import overtrack.apex.game.squad_summary.models
import overtrack.apex.game.combat.models
import overtrack.apex.game.minimap.models
import overtrack.apex.game.apex_metadata
from overtrack.util.uploadable_image import UploadableImage, UploadedImage

T = TypeVar('T')

def frames_dump(value: object, ignore_default: bool = True, numpy_support: bool = True) -> Dict[str, Any]:
    return FrameDumper(ignore_default=ignore_default, numpy_support=numpy_support).dump(value)


def frames_load(value: Any, type_: Type[T]) -> T:
    return FrameLoader().load(value, type_)


class FrameDumper(ReferencedDumper):
    _dispatch = ReferencedDumper._dispatch.copy()

    def _is_uploadable_image(self, value) -> bool:
        return isinstance(value, UploadableImage)
    def _dump_uploadable_image(self, value: UploadableImage) -> Dict[Any, Any]:
        return value._typeddump()
    _dispatch.append((
        _is_uploadable_image,
        _dump_uploadable_image
    ))

_Source = Union[SharedMemorySource, DisplayDuplicationSource]

try:
    from overtrack.source.ffmpeg.ffmpeg_http_server import UploadedTSSource
    _Source = Union[_Source, UploadedTSSource]
except ImportError:
    pass
try:
    from overtrack.source.http.http_capture import HTTPSource
    _Source = Union[_Source, HTTPSource]
except ImportError:
    pass
try:
    from overtrack.source.stream import TSSource
    _Source = Union[_Source, TSSource]
except ImportError:
    pass


_TYPES = {
    'objective': overtrack.overwatch.game.objective.models.Objective,
    'objective2': Union[overtrack.overwatch.game.objective_2.Objective3, overtrack.overwatch.game.objective_2.Objective2],
    'loading_map': overtrack.overwatch.game.loading_map.models.LoadingMap,
    'tab_screen': overtrack.overwatch.game.tab.models.TabScreen,
    'main_menu': overtrack.overwatch.game.menu.models.MainMenu,
    'play_menu': overtrack.overwatch.game.menu.models.PlayMenu,
    'killfeed_2': overtrack.overwatch.game.killfeed_2.models.Killfeed2,
    'spectator_bar': overtrack.overwatch.game.spectator.models.SpectatorBar,
    'score_screen': overtrack.overwatch.game.score.models.ScoreScreen,
    'final_score': overtrack.overwatch.game.score.models.FinalScore,
    'endgame': overtrack.overwatch.game.endgame.models.Endgame,
    'hero': overtrack.overwatch.game.hero.models.Hero,
    'endgame_sr': overtrack.overwatch.game.endgame_sr.models.EndgameSR,
    'assemble_your_team': overtrack.overwatch.game.hero_select.models.AssembleYourTeam,
    'role_select': overtrack.overwatch.game.role_select.models.RoleSelect,
    'eliminations': overtrack.overwatch.game.eliminations.models.Eliminations,
    'overwatch_metadata': overtrack.overwatch.game.overwatch_metadata.OverwatchClientMetadata,

    'match_status': overtrack.apex.game.match_status.models.MatchStatus,
    'match_summary': overtrack.apex.game.match_summary.models.MatchSummary,
    'apex_play_menu': overtrack.apex.game.menu.models.PlayMenu,
    'squad': overtrack.apex.game.squad.models.Squad,
    'weapons': overtrack.apex.game.weapon.models.Weapons,
    'your_squad': overtrack.apex.game.your_squad.models.YourSquad,
    'your_selection': overtrack.apex.game.your_squad.models.YourSelection,
    'champion_squad': overtrack.apex.game.your_squad.models.ChampionSquad,
    'squad_summary': overtrack.apex.game.squad_summary.models.SquadSummary,
    'minimap': overtrack.apex.game.minimap.models.Minimap,
    'combat_log': overtrack.apex.game.combat.models.CombatLog,
    'apex_metadata': overtrack.apex.game.apex_metadata.ApexClientMetadata,

    'source': _Source,
}

class FrameLoader(ReferencedLoader):

    _dispatch = ReferencedLoader._dispatch.copy()

    def _is_frame(self, type_: Type) -> bool:
        return type_ == Frame
    def _load_frame(self, value: Dict[str, Any], type_: Type[Frame]) -> Frame:
        if not isinstance(value, dict):
            raise TypeError(f'Could not load {type_} from value {value!r}')
        result = Frame.__new__(Frame)
        result.image = result.debug_image = result._image_yuv = None
        for k, v in value.items():
            if k in ['image', 'debug_image']:
                continue
            if v is None or type(v) in {int, bool, float, str}:
                result[k] = v
            elif k in _TYPES:
                result[k] = self.load(v, _TYPES[k])
            elif k == 'timings':
                result[k] = Timings(v)
            else:
                raise TypeError(f'Don\'t know how to load Frame field {k!r}')
        return result
    _dispatch.append((
        _is_frame,
        _load_frame
    ))

    def _is_uploadable_image(self, type_: Type) -> bool:
        return type_ == UploadableImage
    def _load_uploadable_image(self, image: UploadableImage, type_: Type[UploadableImage]) -> UploadedImage:
        # Convert UploadableImage -> UploadedImage
        return self.load(image, UploadedImage)
    _dispatch.insert(0, (
        _is_uploadable_image,
        _load_uploadable_image
    ))

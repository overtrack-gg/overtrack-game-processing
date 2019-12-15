from overtrack.apex.game.combat.combat_processor import CombatProcessor
from overtrack.apex.game.map.map_processor import MapProcessor
from overtrack.apex.game.minimap.minimap_processor import MinimapProcessor
from overtrack.apex.game.match_status.match_status_processor import MatchStatusProcessor
from overtrack.apex.game.match_summary.match_summary_processor import MatchSummaryProcessor
from overtrack.apex.game.menu.menu_processor import MenuProcessor
from overtrack.apex.game.squad.squad_processor import SquadProcessor
from overtrack.apex.game.squad_summary.squad_summary_processor import SquadSummaryProcessor
from overtrack.apex.game.weapon.weapon_processor import WeaponProcessor
from overtrack.apex.game.your_squad.your_squad_processor import YourSquadProcessor
from overtrack.processor import OrderedProcessor, ShortCircuitProcessor, ConditionalProcessor, EveryN, Processor


def create_pipeline(interleave_processors: bool = True) -> Processor:
    pipeline = OrderedProcessor(
        ShortCircuitProcessor(
            MenuProcessor(),

            YourSquadProcessor(),
            MatchSummaryProcessor(),
            SquadSummaryProcessor(),

            OrderedProcessor(
                EveryN(MatchStatusProcessor(), 4 if interleave_processors else 1),
                ConditionalProcessor(
                    EveryN(MinimapProcessor(), 3 if interleave_processors else 1),
                    condition=lambda f: 'match_status' in f or 'game_time' not in f or f.game_time < 60,
                    lookbehind=20,
                    lookbehind_behaviour=any,
                    default_without_history=True,
                ),
            ),
            order_defined=False
        ),

        ConditionalProcessor(
            OrderedProcessor(
                EveryN(
                    SquadProcessor(),
                    4 if interleave_processors else 1,
                    offset=0
                ),
                CombatProcessor(),
                EveryN(
                    WeaponProcessor(),
                    4 if interleave_processors else 1,
                    offset=1,
                    override_condition=lambda f: 'combat_log' in f
                ),
            ),
            condition=lambda f: ('location' in f) or ('match_status' in f),
            lookbehind=15,
            lookbehind_behaviour=any,
            default_without_history=True,
        ),
    )
    return pipeline


def create_lightweight_pipeline() -> Processor:
    pipeline = OrderedProcessor(
        ShortCircuitProcessor(
            EveryN(MenuProcessor(), 2),

            YourSquadProcessor(),
            EveryN(MatchSummaryProcessor(), 5),
            SquadSummaryProcessor(),

            EveryN(
                OrderedProcessor(
                    EveryN(MatchStatusProcessor(), 2),
                    MapProcessor(),
                ), 2
            ),

            order_defined=False
        ),

        ConditionalProcessor(
            OrderedProcessor(
                EveryN(SquadProcessor(), 7),
                EveryN(WeaponProcessor(), 3),
                CombatProcessor()
            ),
            condition=lambda f: ('location' in f) or ('match_status' in f),
            lookbehind=15,
            lookbehind_behaviour=any,
            default_without_history=True,
        ),
    )
    return pipeline


def main() -> None:
    from overtrack import util

    util.test_processor('squad', create_pipeline(), 'frame', 'minimap', game='apex')


if __name__ == '__main__':
    main()

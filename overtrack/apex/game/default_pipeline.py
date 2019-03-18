from overtrack.apex.game.map.map_processor import MapProcessor
from overtrack.apex.game.match_status.match_status_processor import MatchStatusProcessor
from overtrack.apex.game.match_summary.match_summary_processor import MatchSummaryProcessor
from overtrack.apex.game.menu.menu_processor import MenuProcessor
from overtrack.apex.game.squad.squad_processor import SquadProcessor
from overtrack.apex.game.squad_summary import SquadSummaryProcessor
from overtrack.apex.game.weapon.weapon_processor import WeaponProcessor
from overtrack.apex.game.your_squad.your_squad_processor import YourSquadProcessor
from overtrack.processor import OrderedProcessor, ShortCircuitProcessor, ConditionalProcessor, Processor


def create_pipeline() -> Processor:
    pipeline = OrderedProcessor(
        ShortCircuitProcessor(
            MenuProcessor(),

            YourSquadProcessor(),
            MatchSummaryProcessor(),
            SquadSummaryProcessor(),

            OrderedProcessor(
                MatchStatusProcessor(),
                MapProcessor(),
            ),

            order_defined=False
        ),

        ConditionalProcessor(
            OrderedProcessor(
                SquadProcessor(),
                WeaponProcessor(),
            ),
            condition=lambda f: ('location' in f) or ('match_status' in f),
            lookbehind=15,
            lookbehind_behaviour=any,
            default_without_history=True,
        ),
    )
    return pipeline


def main() -> None:
    from overtrack.util.logging_config import config_logger
    import logging

    config_logger('map_processor', logging.INFO, write_to_file=False)

    pipeline = create_pipeline()

    import glob
    from overtrack.frame import Frame
    import cv2

    for p in glob.glob('../../../dev/apex_images/squad/*.png') + glob.glob('../../../dev/apex_images/**/*.png'):
        frame = Frame.create(
            cv2.resize(cv2.imread(p), (1920, 1080)),
            0,
            True
        )
        pipeline.process(frame)
        print(frame)
        cv2.imshow('debug', frame.debug_image)
        cv2.waitKey(0)


if __name__ == '__main__':
    main()

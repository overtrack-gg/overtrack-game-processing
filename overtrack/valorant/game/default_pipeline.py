from typing import Sequence

from overtrack.processor import Processor, OrderedProcessor, ShortCircuitProcessor, EveryN, ConditionalProcessor
from overtrack.valorant.game.agent_select.agent_select_processor import AgentSelectProcessor
from overtrack.valorant.game.home_screen.home_screen_processor import HomeScreenProcessor
from overtrack.valorant.game.killfeed.killfeed_processor import KillfeedProcessor
from overtrack.valorant.game.postgame.postgame_processor import PostgameProcessor
from overtrack.valorant.game.timer.timer_processor import TimerProcessor
from overtrack.valorant.game.top_hud.top_hud_processor import TopHudProcessor


def create_pipeline(extra_processors: Sequence[Processor] = (), aggressive=False) -> Processor:
    pipeline = OrderedProcessor(
        ShortCircuitProcessor(
            AgentSelectProcessor(),
            TimerProcessor(),
            PostgameProcessor(),
            order_defined=False,
        ),
        ConditionalProcessor(
            HomeScreenProcessor(),
            condition=lambda f: (
                not (f.valorant.timer and f.valorant.timer.valid) and
                not (f.valorant.top_hud and f.valorant.top_hud.score and f.valorant.top_hud.score[0] is not None and f.valorant.top_hud.score[1] is not None) and
                not f.valorant.postgame
            ),
            log=False,
        ),
        ConditionalProcessor(
            OrderedProcessor(
                EveryN(TopHudProcessor(), 2 if not aggressive else 1),
                KillfeedProcessor(),
            ),
            condition=lambda f: lambda f: (
                aggressive or
                (f.valorant.timer and f.valorant.timer.valid) or
                f.valorant.top_hud
            ),
            lookbehind=7,
            lookbehind_behaviour=any,
            default_without_history=True,
        )
    )
    if extra_processors:
        pipeline.processors = tuple(list(pipeline.processors) + list(extra_processors))
    return pipeline

from typing import Sequence

from overtrack.processor import Processor, OrderedProcessor, ShortCircuitProcessor, EveryN, ConditionalProcessor
from overtrack.valorant.game.agent_select.agent_select_processor import AgentSelectProcessor
from overtrack.valorant.game.home_screen.home_screen_processor import HomeScreenProcessor
from overtrack.valorant.game.postgame.postgame_processor import PostgameProcessor
from overtrack.valorant.game.timer.timer_processor import TimerProcessor
from overtrack.valorant.game.top_hud.top_hud_processor import TopHudProcessor


def create_pipeline(extra_processors: Sequence[Processor] = (), aggressive=False) -> Processor:
    pipeline = OrderedProcessor(
        ShortCircuitProcessor(
            ShortCircuitProcessor(
                AgentSelectProcessor(),
                TimerProcessor(),
                PostgameProcessor(),
                order_defined=False,
            ),
            EveryN(
                HomeScreenProcessor(),
                3 if not aggressive else 1,
            ),
            order_defined=False,
        ),
        ConditionalProcessor(
            OrderedProcessor(
                EveryN(TopHudProcessor(), 5 if not aggressive else 1),
            ),
            condition=lambda f: lambda f: aggressive or ('timer' in f and f.timer.valid) or 'top_hud' in f,
            lookbehind=7,
            lookbehind_behaviour=any,
            default_without_history=True,
        )
    )
    if extra_processors:
        pipeline.processors = tuple(list(pipeline.processors) + list(extra_processors))
    return pipeline

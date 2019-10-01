from collections import deque
from typing import Callable, Iterable, Any, Optional

from overtrack.frame import Frame


class Processor:

    def process(self, frame: Frame) -> bool:
        return False

    def eager_load(self):
        pass

    def update(self):
        pass

class OrderedProcessor(Processor):
    """
    Run all processors in the predefined order
    """
    def __init__(self, *processors: Processor):
        self.processors = processors

    def process(self, frame: Frame) -> bool:
        """
        :param frame: the current frame
        :return: True if _any_ of the processors returned True
        """
        return any([p.process(frame) for p in self.processors])

    def eager_load(self):
        for p in self.processors:
            p.eager_load()


class ConditionalProcessor(Processor):
    """
    Run the processor IFF the provided condition evaluates to True

    If this is a lookbehind ConditionalProcessor, run the processor if the condition was true for any of the frames in the lookbehind window.
    Note that condition evaluation is cached
    """
    def __init__(
            self,
            processor: Processor,
            condition: Callable[[Frame], object],  # condition may return falsey objects
            lookbehind: Optional[int] = None,
            lookbehind_behaviour: Callable[[Iterable[Any]], bool] = any,
            default_without_history: bool = True):

        self.processor = processor
        self.condition = condition
        self.lookbehind = lookbehind
        self.lookbehind_behaviour = lookbehind_behaviour
        if lookbehind:
            self.history = deque(
                [default_without_history] * lookbehind,
                maxlen=lookbehind
            )

    def process(self, frame: Frame) -> bool:
        """
        :param frame: the current frame
        :return: The result of the processor, if it ran, otherwise False
        """
        if self.lookbehind:
            self.history.popleft()
            self.history.append(bool(self.condition(frame)))
            result = self.lookbehind_behaviour(self.history)
        else:
            result = bool(self.condition(frame))
        if result:
            return self.processor.process(frame)
        else:
            return False

    def eager_load(self):
        self.processor.eager_load()

    def update(self):
        self.processor.update()

class ShortCircuitProcessor(Processor):
    """
    Run the processors until one of them returns True

    If order_defined=False then the processor that returned True on the previous frame is run first
    """
    def __init__(self, *processors: Processor, order_defined: bool, invert: bool=False):
        self.processors = processors
        self.order_defined = order_defined
        self.invert = invert
        if not self.order_defined:
            self.last_processor = processors[0]

    def should_bail(self, result: bool) -> bool:
        if self.invert:
            return not result
        else:
            return result

    def process(self, frame: Frame) -> bool:
        """
        :param frame: the frame
        :return: True if _any_ of the processors returned True
        """
        if self.order_defined:
            # use any's short circuiting
            return self.should_bail(any(self.should_bail(p.process(frame)) for p in self.processors))
        else:
            # first check the last processor
            if self.should_bail(self.last_processor.process(frame)):
                return True
            else:
                # if the "last_processor" did not return True this frame, check all the others
                for processor in self.processors:
                    if processor is self.last_processor:
                        continue
                    elif self.should_bail(processor.process(frame)):
                        # save the previous processor
                        self.last_processor = processor
                        return True
                self.last_processor = self.processors[0]
                return False

    def eager_load(self):
        for p in self.processors:
            p.eager_load()

    def update(self):
        for p in self.processors:
            p.eager_load()

class EveryN(Processor):

    def __init__(self, processor: Processor, n: int, return_last: bool = True, override_condition: Callable[[Frame], bool] = lambda f: False):
        self.processor = processor
        self.return_last = return_last
        self.override_condition = override_condition
        self.n = n
        self.i = -1
        self.last = False

    def process(self, frame: Frame) -> bool:
        self.i += 1
        if self.i % self.n == 0 or self.override_condition(frame):
            self.last = self.processor.process(frame)
            return self.last
        if self.return_last:
            return self.last
        else:
            return False

    def eager_load(self):
        self.processor.eager_load()

    def update(self):
        self.processor.update()

# class RepeatProcessor(Processor):
#
#     def process(self, frame: Frame) -> bool:
#         if do process:
#             f = Frame(frame)
#             result = self.processor.process(frame)
#             if self.only_cache_on_positive:
#                 if result:
#                     self.cached = frame - f
#                 else:
#                     self.cached = None
#             else:
#
#         else:
#             frame.update(self.cached)

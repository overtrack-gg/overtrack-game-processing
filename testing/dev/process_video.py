import json
import os

import tensorflow as tf

from overtrack.game import OrderedProcessor, ShortCircuitProcessor, ConditionalProcessor
from overtrack.game.killfeed import KillfeedProcessor
from overtrack.game.loading_map import LoadingMapProcessor
from overtrack.game.menu import MenuProcessor
from overtrack.game.objective import ObjectiveProcessor
from overtrack.game.tab import TabProcessor
from overtrack.source.video import VideoFrameExtractor
from overtrack.util import referenced_typedload


def main():
    p = "D:/overwatch_vids/switch_heroes_2_badnames.mp4"
    source = VideoFrameExtractor(p, extract_fps=2)

    frames = []
    while True:
        frame = source.get()
        if not frame:
            break
        print(frame.timestamp_str)
        pipeline.process(frame)
        frame.strip()
        frames.append(frame)

    with open(f'../../games/{os.path.basename(p).rsplit(".", 1)[0]}.json', 'w') as f:
        json.dump(referenced_typedload.dump(frames), f, indent=2)


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        pipeline = OrderedProcessor(
            ShortCircuitProcessor(
                MenuProcessor(),
                LoadingMapProcessor(),
                ObjectiveProcessor(save_probabilities=False),
                order_defined=False
            ),

            TabProcessor(),

            ConditionalProcessor(
                OrderedProcessor(
                    KillfeedProcessor(output_icon_images=False, output_name_images=False),
                ),
                condition=lambda f: 'objective' in f and f.objective.is_game,
                lookbehind=5,
                lookbehind_behaviour=any,
                default_without_history=True,
            ),
        )
        main()

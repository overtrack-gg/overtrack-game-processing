import logging
import time

import cv2
import tensorflow as tf

from overtrack.game.default_pipeline import create_pipeline
from overtrack.game.hero import HeroProcessor
from overtrack.source.obs import OBSFrameExtractor
from overtrack.util import ms2ts

logger = logging.getLogger(__name__)


def main(display=True):
    logging.basicConfig(level=logging.INFO)
    cap = OBSFrameExtractor('Overwatch', debug=True)
    start = time.time()
    pipeline = create_pipeline()
    pipeline = HeroProcessor()
    # if display:
    #     fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    #     writer = cv2.VideoWriter('out.mp4', fourcc, 10, (1280, 720))

    # outdir = None
    # for i in range(100):
    #     outdir = os.path.join('C:\\scratch\\frames', str(i))
    #     if not os.path.exists(outdir):
    #         os.makedirs(outdir)
    #         break

    i = 0
    while True:
        time.sleep(0.5)
        frame = cap.get()
        if isinstance(frame, Exception):
            raise frame
        if frame is None:
            break

        pipeline.process(frame)

        if not i % 10:
            print(ms2ts((frame.timestamp - start) * 1000))

        # cv2.imwrite(os.path.join(outdir, f'%d.png' % (frame.timestamp * 1000, )), frame.image)

        if display:
            im = cv2.resize(frame.debug_image, (1280, 720))
            frame.strip()
            print(frame)
            # writer.write(im)
            cv2.imshow('frame', im)
            # cv2.imshow('alpha', frame.alpha_image)

            if cv2.waitKey(1) == 27:
                break
            i += 1

    # if display:
    #     writer.release()
    #     cv2.destroyAllWindows()


if __name__ == "__main__":
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main(True)

import cv2
import logging
import os
import string
from typing import List, Optional

import numpy as np
import tensorflow as tf

from overtrack.util import imageops

logger = logging.getLogger(__name__)


class Classifier:
    IMSIZE = (20, 16)
    CHARACTERS = np.array(list(string.digits + '_'))

    _instance = None

    @classmethod
    def get_instance(cls, session=None):
        if cls._instance:
            return cls._instance
        if not session:
            session = tf.get_default_session()
        cls._instance = cls(session)
        return cls._instance

    def __init__(self, session):
        self.sess = session
        with tf.variable_scope('DigitClassifier') as v:
            with np.load(os.path.join(os.path.dirname(__file__), 'data', 'tab_ocr.npz')) as data:
                w1 = tf.Variable(data['tab_ocr/W_fc_:0'], name='W_fc_1')
                b1 = tf.Variable(data['tab_ocr/b_fc_:0'], name='b_fc_1')
            self.sess.run(tf.variables_initializer([w1, b1]))

            self.digit_images = tf.placeholder(tf.float32, shape=[None, self.IMSIZE[0], self.IMSIZE[1]], name='digit_images')
            self.logits = tf.matmul(
                tf.cast(tf.reshape(self.digit_images, [-1, np.prod(self.IMSIZE)]), tf.float32),
                w1
            ) + b1
            self.probs = tf.nn.softmax(self.logits)
            self.clas = tf.argmax(self.logits, axis=1)

    def classify(self, images: List[np.ndarray], scale=1., debug=False) -> List[Optional[int]]:
        if not len(images):
            return []

        digit_images = []
        digit_buckets = []

        logger.debug(f'Parsing images {", ".join("{1}*{0}".format(*i.shape) for i in images)}')

        for index, im in enumerate(images):
            _, im = cv2.threshold(im, 150, 255, cv2.BORDER_CONSTANT)
            labels, components = imageops.connected_components(im, connectivity=4)

            for c in sorted(components[1:], key=lambda c: c.x):
                num_overlapping = sum(
                    (c.x <= o.x <= c.x + c.w or
                     c.x <= o.x + o.w <= c.x + c.w) and
                    o.area > 5 and
                    o.h * scale > 7
                    for o in components[1:]
                ) - 1
                if num_overlapping:
                    # percent sign
                    continue
                if not 4 < c.w * scale < 18:
                    # too wide (could just be comma)
                    if c.area > 100:
                        logger.warning(f'Found bad digit component {c} (incorrect width)')
                    continue
                if not 15 < c.h * scale < 19:
                    logger.warning(f'Found bad digit component {c} (incorrect height)')
                    continue

                digit_image = (labels[c.y:c.y + c.h, c.x:c.x + c.w] == c.label).astype(np.uint8) * 255
                digit_image = cv2.resize(digit_image, (0, 0), fx=scale, fy=scale)[:self.IMSIZE[0] - 2, :self.IMSIZE[1] - 1]
                digit_image = cv2.copyMakeBorder(
                    digit_image,
                    2,
                    self.IMSIZE[0] - (digit_image.shape[0] + 2),
                    1,
                    self.IMSIZE[1] - (digit_image.shape[1] + 1),
                    cv2.BORDER_CONSTANT
                )
                digit_images.append(digit_image)
                digit_buckets.append(index)

        if not len(digit_images):
            logger.warning('Did not get any digits to classify')
            return [None for _ in images]

        probs, parses = self.sess.run((self.probs, self.clas), {self.digit_images: digit_images})
        str_results = [[] for _ in images]
        p_groups = [[] for _ in images]
        for stat_bucket, clas, p in zip(digit_buckets, parses, probs):
            str_results[stat_bucket].append(str(clas))
            p_groups[stat_bucket].append(np.max(p))

        rstr, pstr = [], []
        for r, ps in zip(str_results, p_groups):
            rstr.append('[ ' + ''.join(d + '   ' for d in r) + ' ]')
            pstr.append('[ ' + ''.join(f'{p:1.1f} ' for p in ps) + ' ]')

        logger.debug(f'OCR RESULT: {" ".join(rstr)}')
        logger.debug(f'OCR PROBS:  {" ".join(pstr)}')

        results = []
        for r in str_results:
            try:
                r = int(''.join(r))
            except ValueError:
                logger.warning(f'Could not parse {r} as a number - ignoring')
                results.append(None)
            else:
                results.append(r)

        return results


def ocr_images(images, scale=1.):
    return Classifier.get_instance().classify(
        [np.min(im, axis=2) for im in images],
        scale=scale
    )


def ocr(image, scale=1.):
    return ocr_images([image], scale=scale)[0]

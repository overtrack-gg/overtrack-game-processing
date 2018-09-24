import os
import string
from typing import List

import cv2
import logging
import numpy as np
import tensorflow as tf

from overtrack.util import imageops

logger = logging.getLogger(__name__)


class Decoder:
    IMAGE_HEIGHT = 20
    IMAGE_WIDTH = 300
    CONV1_SIZE = (5, 5)
    CONV1_LAYERS = 2
    CONV2_WIDTH = 10
    MAXPOOL_WIDTH = 1
    MERGE_REPEATED = True
    CHARACTERS = string.digits + string.ascii_uppercase

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
        with tf.variable_scope('BigNoodleDecoder') as v:
            # Create inputs
            # self.input_count = tf.placeholder(tf.int32, ())
            self.input_image = tf.placeholder(tf.uint8, shape=(None, self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3), name='input_image')
            self.width = tf.placeholder(tf.int32, (None,), name='width')

            # Normalise values to [-0.5, 0.5]
            image_float = tf.cast(self.input_image, tf.float32) / 255 - 0.5
            # image_float_reshape = tf.reshape(image_float, (self.input_count, self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3))

            # Prepare layers
            conv1 = tf.layers.conv2d(
                image_float,
                self.CONV1_LAYERS,
                self.CONV1_SIZE,
                strides=(1, 1),
                activation=tf.nn.relu,
                padding='same',
                name='conv1'
            )
            conv2 = tf.layers.conv2d(
                tf.pad(
                    conv1,
                    ((0, 0), (0, 0), (0, self.CONV2_WIDTH - 1), (0, 0))
                ),
                len(self.CHARACTERS) + 1,
                (self.IMAGE_HEIGHT - 2, self.CONV2_WIDTH),
                strides=(1, 1),
                activation=None,
                padding='valid',
                name='conv2'
            )[:, :, :-(self.CONV2_WIDTH - 2), :]
            conv2_mxd = tf.reduce_max(conv2, axis=1)
            if self.MAXPOOL_WIDTH > 1:
                self.logits = tf.layers.max_pooling1d(
                    conv2_mxd,
                    self.MAXPOOL_WIDTH,
                    self.MAXPOOL_WIDTH
                )
            else:
                self.logits = conv2_mxd

            seq_len = tf.cast((self.width - (self.CONV2_WIDTH - 2)) / self.MAXPOOL_WIDTH, tf.int32)
            self.decoded = tf.nn.ctc_greedy_decoder(
                tf.transpose(self.logits, perm=[1, 0, 2]),
                seq_len,
                merge_repeated=self.MERGE_REPEATED
            )[0][0]
            self.decoded_dense = tf.sparse_tensor_to_dense(self.decoded, default_value=-1)

            var_prefix = v.name + '/'
            ctc_vars = v.global_variables()

        p = os.path.join(os.path.dirname(__file__), 'data', 'big_noodle_ctc.npz')
        logger.info('Loading BigNoodleDecoder weights from %s', p)
        restore_dict = dict(np.load(p))
        for v in ctc_vars:
            # strip off the scope prefix as the saved vars do not include this
            self.sess.run(v.assign(restore_dict[v.name[len(var_prefix):]]))

    def decode(self, images: List[np.ndarray]) -> List[str]:
        if not len(images):
            return []
        print([i.shape if i is not None else None for i in images])
        inds = self.sess.run(
            self.decoded_dense,
            {
                self.input_image: images,
                self.width: [i.shape[1] for i in images]
            }
        )
        npchars = np.array(list(self.CHARACTERS))
        names = []
        for r in inds:
            names.append(''.join(npchars[r[r != -1]]))
        return names


def ocr_all(images: List[np.ndarray], **kwargs) -> List[str]:
    classifier = Decoder.get_instance()

    images_sized = []
    for im in images:
        _, thresh = cv2.threshold(np.max(im, axis=2), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        _, components = imageops.connected_components(thresh)
        components = [c for c in components[1:] if c.area > 25]
        if not components:
            # TODO
            images_sized.append(np.zeros((20, 300, 3), np.uint8))
            continue
        y, h = np.median([c.y for c in components]), np.median([c.h for c in components])
        y -= h * 0.05
        h *= 1.15
        y, h = int(y), int(h)
        im = im[max(0, y):min(y + h, im.shape[0])]
        s = classifier.IMAGE_HEIGHT / im.shape[0]
        im = cv2.resize(im, (int(im.shape[1] * s), classifier.IMAGE_HEIGHT))[:, :classifier.IMAGE_WIDTH]
        im = cv2.copyMakeBorder(im, 0, 0, 0, classifier.IMAGE_WIDTH - im.shape[1], cv2.BORDER_CONSTANT)
        images_sized.append(im)

    return classifier.decode(images_sized)


def ocr(image: np.ndarray, **kwargs) -> str:
    return ocr_all([image], **kwargs)[0]

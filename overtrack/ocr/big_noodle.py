import os
import string
from typing import List, Tuple

import cv2
import logging
import numpy as np
import tensorflow as tf

from overtrack.util import imageops

logger = logging.getLogger(__name__)


class Classifier:
    HEIGHT = 25
    WIDTH = int(HEIGHT * 0.9 + 0.5)
    CHARACTERS = string.digits[1:] + string.ascii_uppercase
    DROPOUT_RATE = 0.1
    CONV1_SIZE = (HEIGHT - 2, WIDTH - 2)

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
        with tf.variable_scope('BigNoodleClassifier') as v:
            self.input_images = tf.placeholder(tf.float32, shape=(None, self.HEIGHT, self.WIDTH))
            # image_float = tf.cast(self.input_images, tf.float32)
            # perc = tf.contrib.distributions.percentile(image_float, 95, axis=(1, 2))
            # image_scaled = (image_float * 255.) / perc
            # image_scaled_cent = tf.clip_by_value(image_scaled, 0, 255) / 255. - 0.5
            # image_scaled_cent = image_float / 255. - 0.5
            image_reshape = tf.expand_dims(self.input_images, axis=-1)
            image_dropout = tf.layers.dropout(image_reshape, rate=self.DROPOUT_RATE, training=False)
            conv1 = tf.layers.conv2d(
                image_dropout,
                len(self.CHARACTERS),
                self.CONV1_SIZE,
                strides=(1, 1),
                activation=None,
                padding='valid',
                name='conv1'
            )
            logits = tf.reduce_max(
                conv1,
                axis=(1, 2)
            )
            self.probs = tf.nn.softmax(logits)
            self.char = tf.argmax(logits, axis=1)

            var_prefix = v.name + '/'
            vars = v.global_variables()

        p = os.path.join(os.path.dirname(__file__), 'data', 'big_noodle.npz')
        logger.info('Loading BigNoodleClassifier weights from %s', p)
        restore_dict = dict(np.load(p))
        for v in vars:
            # strip off the scope prefix as the saved vars do not include this
            self.sess.run(v.assign(restore_dict[v.name[len(var_prefix):]]))

    def classify(self, images: List[np.ndarray]) -> List[str]:
        if not len(images):
            return []
        norm_images = []
        for im in images:
            p = np.percentile(im, 95)
            im = im.astype(np.float) * (255. / p)
            im = np.clip(im, 0, 255) / 255. - 0.5
            norm_images.append(im)
        return [
            self.CHARACTERS[i] for i in self.sess.run(self.char, {self.input_images: norm_images})
        ]


def to_gray(image: np.ndarray, channel: str=None, debug: bool=False) -> np.ndarray:
    if len(image.shape) == 2:
        if channel:
            raise ValueError(f'Cannot convert gray image to gray using { channel }')
        else:
            # image already gray
            pass
    else:
        if not channel or channel == 'grey':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif channel in 'bgr':
            channel_index = 'bgr'.index(channel)
            image = image[:, :, channel_index]
        elif channel in 'sv':
            channel_index = 'hsv'.index(channel)
            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
            image = image_hsv[:, :, channel_index]
        elif channel == 'max':
            image = np.max(image, axis=2)
        elif channel == 'min':
            image = np.min(image, axis=2)
        else:
            raise ValueError(f'Don\'t know how to convert BGR image to grey using { channel }')

    return image


def segment(gray_image: np.ndarray, segmentation: str = 'otsu_above_mean', min_area: int=10, height: int=None, debug: bool = False) -> List[np.ndarray]:
    segments = []

    # TODO: implement simpler/faster segmentation
    if segmentation.startswith('otsu'):
        if segmentation == 'otsu_above_mean':
            tval = imageops.otsu_thresh(gray_image, int(np.mean(gray_image) * 0.75), 255)
            _, thresh = cv2.threshold(gray_image, tval, 255, cv2.THRESH_BINARY)
        elif segmentation == 'otsu':
            _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        else:
            raise ValueError(f'Don\t know how to segment image using { segmentation }')

        labels, components = imageops.connected_components(thresh)

        # TODO: estimate the size of the characters, and discard things that don't match
        components = [c for c in components[1:] if c.area > min_area]
        if height:
            components = [c for c in components if height * 0.9 < c.h < height * 1.1]

        if not len(components):
            logger.warning('Could not find any characters')
            return []

        components = sorted(components, key=lambda c: c.x)

        average_top = int(np.median([c.y for c in components]))
        average_height = int(np.median([c.h for c in components]))
        # top = Counter([y for (x, y, w, h, a) in stats[1:]]).most_common(1)[0][0]
        # height = Counter([h for (x, y, w, h, a) in stats[1:]]).most_common(1)[0][0]

        border_size = average_height * 0.05
        height_tolerance = average_height * 0.2

        # I is approx 40% as wide as it is high
        # 1 can be 30%
        min_width = average_height * 0.2
        # M is approx 80% as wide as it is high
        max_width = average_height * 0.9

        top = round(max(0., average_top - border_size))
        if not height:
            height = round(min(average_height + border_size, gray_image.shape[0]))

        if debug:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.imshow(gray_image, interpolation='none')
            plt.title('segment image')

            plt.figure()
            plt.imshow(thresh, interpolation='none')
            plt.title('segment thresh')

            plt.figure()
            plt.imshow(labels, interpolation='none')
            plt.title('segment components')

            plt.show()

        for component in components:
            if abs(min(component.h, gray_image.shape[0] - component.y) - height) > height_tolerance:
                logger.warning(f'Found component with height={component.h} but expected height={height}')
                continue

            if not min_width < component.w < max_width:
                logger.warning(f'Found component with width={component.w} - expected range was [{min_width :1.1f}, {max_width :1.1f}]')
                continue

            y1 = top
            y2 = top + height
            x1 = round(max(0., component.x - border_size))
            x2 = round(min(component.x + component.w + border_size, gray_image.shape[1]))

            if y2 > gray_image.shape[0]:
                logger.warning(f'Found component with y={component.y}, using height={height} would take this outside the image')
                continue

            mask = (labels[y1:y2, x1:x2] == component.label).astype(np.uint8) * 255
            mask = cv2.dilate(mask, np.ones((3, 3)))
            character = cv2.bitwise_and(gray_image[y1:y2, x1:x2], mask)

            segments.append(character)
    else:
        raise ValueError(f'Don\t know how to segment image using { segmentation }')

    return segments


def resize_segments(segments: List[np.ndarray], height: int=25) -> List[np.ndarray]:
    width = int(height * 0.9 + 0.5)
    r = []
    for im in segments:
        s = height / im.shape[0]
        im = cv2.resize(im, (int(im.shape[1] * s), height), interpolation=cv2.INTER_LINEAR)[:, :width]
        im = cv2.copyMakeBorder(im, 0, 0, 0, width - im.shape[1], cv2.BORDER_CONSTANT)
        r.append(im)
    return r


def ocr(image: np.ndarray, channel: str=None, segmentation: str='otsu_above_mean', min_area: int=25, height: int=None, debug: bool=False) -> str:
    image = to_gray(image, channel=channel, debug=debug)
    segments = segment(image, height=height, segmentation=segmentation, min_area=min_area, debug=debug)

    segments_sized = resize_segments(segments, height=25)
    classifier = Classifier.get_instance()
    return ''.join(classifier.classify(segments_sized))


def ocr_all(images: List[np.ndarray], **kwargs) -> List[str]:
    return [ocr(image, **kwargs) for image in images]

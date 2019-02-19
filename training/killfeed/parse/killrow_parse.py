import glob
import itertools
import logging
import os
import random
import shutil
import string
import sys
import time
import typing
from typing import List, Tuple, Optional, NamedTuple

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.contrib.layers import dense_to_sparse
from tensorflow.python.framework import tensor_shape
from tensorflow.python.keras import Model, Sequential, backend
from tensorflow.python.keras.callbacks import TensorBoard, ModelCheckpoint, Callback, LambdaCallback
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.regularizers import *
from tensorflow.python.keras.models import load_model
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.utils import Sequence
from tensorflow.python.keras import backend as K

from overtrack import data

logger = logging.getLogger()


TRAINING_DIR = r'C:\scratch\owl-killfeed-2'
NAME = 'kill'

HEIGHT = 46
WIDTH = 500

# use a kernel height of HEIGHT-SLIP_Y and then max along x-axis
# this means the model should be resilient to the row being +-SLIP_Y pixels offset
SLIP_Y = 3
HIDDEN_FEATURES = 256

# TODO: Y_RANDOM_PAD = 2

BATCH_SIZE = 32

class Output(NamedTuple):
    name: str

    values: List[str]

    kernel_width: int
    kernel_maxpool: int = 1


OUTPUTS = [
    Output(
        'text',
        string.ascii_uppercase + string.digits[1:],
        15,
        2
    ),
    Output(
        'hero',
        sorted(list(data.heroes.keys()) + ['ashe.bob', 'dva.mech', 'junkrat.riptire', 'orisa.supercharger', 'torbjorn.turret']),
        50,
        70
    )
]

class Image:
    def __init__(self, path: str):
        self.path = path
        self.data = str(os.path.normpath(self.path)).split(os.path.sep)[-2]

        # hack fixes
        self.data = self.data.replace('.ASHER_IR', '.ASHER')
        self.data = self.data.replace('.AIMOU', '.TAIMOU')

        try:
            left, right = self.data.split('_')

            self.text = ''
            self.hero = []
            if left:
                self.text += left.split('.')[2].replace('0', 'O').split(' ')[0]
                self.hero.append(left.split('.')[1].replace('-', '.'))

            self.text += right.split('.')[2].replace('0', 'O').split(' ')[0]
            self.hero.append(right.split('.')[1].replace('-', '.'))
        except Exception as e:
            raise ValueError(f'Failed to parse "{self.data}": {e}')

    def imread(self) -> np.ndarray:
        im = cv2.imread(self.path)
        assert im.shape == (HEIGHT, WIDTH, 3)
        return im

    def make_expected(self) -> Tuple[List[int]]:
        try:
            r = []
            for output in OUTPUTS:
                l = []
                for e in getattr(self, output.name):
                    l.append(output.values.index(e))
                r.append(l)
            return tuple(r)
        except Exception as e:
            raise ValueError(f'Got exception while processing "{self.data}": {e}')


class ImageLoader(Sequence):
    def __init__(self, images: List[Image], batch_size=25, preprocessor: ImageDataGenerator=None) -> None:
        self.images = list(images)
        self.batch_size = batch_size
        self.preprocessor = preprocessor

    def shuffle(self) -> None:
        print('suffling')
        random.shuffle(self.images)

    def __len__(self) -> int:
        return int(np.floor(len(self.images) / float(self.batch_size)))

    def __getitem__(self, i: int) -> Tuple[np.ndarray, List[np.ndarray]]:
        batch = self.images[i * self.batch_size:(i + 1) * self.batch_size]
        assert len(batch) == self.batch_size, f'Got batch of size {len(batch)} for i={i}, len={len(self)}'

        images = []
        expected = [[] for _ in OUTPUTS]
        for image in batch:
            im = image.imread()
            if self.preprocessor:
                im = self.preprocessor.random_transform(im)
            images.append(im)
            for i, (e, o) in enumerate(zip(image.make_expected(), OUTPUTS)):
                a = np.full((((WIDTH - 2 + 3) - (o.kernel_width - 1)) // o.kernel_maxpool, ), -1)
                a[:len(e)] = e
                expected[i].append(a)

        images = np.array(images)
        expected = [np.array(e) for e in expected]
        # print([e.shape for e in expected])
        # print(expected)

        return images, expected


class MaxAlongDims(Layer):

    def __init__(self, dims: typing.Sequence[int], **kwargs):
        super(MaxAlongDims, self).__init__(**kwargs)
        self.dims = dims

    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape).as_list()
        newdims = []
        for i, dim in enumerate(input_shape):
            if i not in self.dims:
                newdims.append(dim)
        return tensor_shape.TensorShape(newdims)

    def get_config(self):
        config = {
            'dims': self.dims,
        }
        base_config = super(MaxAlongDims, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return backend.sum(inputs, axis=self.dims)

def make_ctc_loss(sequence_length: int, preprocess_collapse_repeated=False, ctc_merge_repeated=False):
    def ctc_loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.int32)
        sparse = dense_to_sparse(y_true, eos_token=-1)
        loss = tf.nn.ctc_loss(
            sparse,
            y_pred,
            [sequence_length for _ in range(BATCH_SIZE)],
            preprocess_collapse_repeated=preprocess_collapse_repeated,
            ctc_merge_repeated=ctc_merge_repeated,
            time_major=False
        )
        return tf.cond(
            tf.is_inf(tf.reduce_sum(loss)),
            lambda: loss * 0,
            lambda: loss
        )
        # with tf.control_dependencies([
        #     tf.print(
        #         '\ny_true\n', y_true,
        #         '\nsparse\n', sparse,
        #         '\nloss\n', loss
        #     )
        # ]):
        #     return loss + 0
    return ctc_loss


def construct_model() -> Model:
    image = Input(shape=(HEIGHT, WIDTH, 3), name='image')

    normed_image = BatchNormalization(input_shape=(None, None, 3))(image)

    conv1 = Conv2D(
        2,
        (3, 3),
        name='conv1',
        activation='relu',
        # padding='same',
        # kernel_regularizer=l2(0.0001),
        kernel_initializer='he_normal'
    )(normed_image)

    conv2 = Conv2D(
        HIDDEN_FEATURES,
        (HEIGHT-SLIP_Y, 4),
        name='conv2',
        activation='relu',
        # padding='same',
        # activity_regularizer=l1(0.00001),
        kernel_initializer='he_normal'
    )(conv1)
    conv2_pooled = MaxAlongDims(
        (1, ),
        name='conv2_pooled'
    )(conv2)
    conv2_permuted = Permute(
        (2, 1),
        name='conv2_permuted'
    )(conv2_pooled)
    conv2_reshape = Lambda(
        lambda e: tf.expand_dims(e, -1),
        name='conv2_reshape'
    )(conv2_permuted)
    # conv2_reshape = Reshape(
    #     (HIDDEN_FEATURES, conv2_permuted.get_shape()[2], 1),
    #     name='conv2_reshape'
    # )(conv2_permuted)

    outputs = {}
    for output_definition in OUTPUTS:
        features = len(output_definition.values) + 1
        output = Conv2D(
            features,
            (HIDDEN_FEATURES, output_definition.kernel_width),
            name=output_definition.name + '_conv'
        )(conv2_reshape)
        if output_definition.kernel_maxpool != 1:
            output = MaxPool2D(
                (1, output_definition.kernel_maxpool),
                name=output_definition.name + '_pooled'
            )(output)
        # output = Reshape(
        #     (output.get_shape()[2], features),
        #     name=output_definition.name
        # )(output)
        output = Lambda(
            lambda e: e[:, 0, :, :],
            name=output_definition.name
        )(output)
        outputs[output_definition.name] = output

    model = Model(
        inputs=image,
        outputs=list(outputs.values())
    )
    model.compile(
        optimizer=Adam(),
        loss={
            name: make_ctc_loss(output.get_shape()[1])
            for name, output in outputs.items()},
        # metrics=[accuracy, accuracy_positive]
        # options=run_options,
        # run_metadata=run_metadata
    )

    model.summary()
    return model


def get_next_logdir(d: str, name='run') -> str:
    os.makedirs(d, exist_ok=True)
    for i in itertools.count():
        p = os.path.join(d, f'{name}_{i}')
        if not os.path.exists(p):
            return p


class VisualiseCallback(Callback):

    def __init__(self, images: List[Image], frequency: float):
        super().__init__()
        self.images = images
        self.frequency = frequency
        self.last_shown = 0

    def on_batch_end(self, batch, logs=None):
        if time.time() - self.last_shown > self.frequency:
            self.last_shown = time.time()
            self.visualise()

    def visualise(self):
        image: Image = random.choice(self.images)
        im = image.imread()
        pred = self.model.predict([[im]], 1)
        im2 = cv2.resize(im, (0, 0), fx=3, fy=3)
        # print(image.data)
        cv2.putText(
            im2,
            image.data,
            (0, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        y = 70
        for o, p in zip(OUTPUTS, pred):
            decoded, neg_sum_logits = keras.backend.get_session().run(tf.nn.ctc_greedy_decoder(np.transpose(p, (1, 0, 2)), [p.shape[1]], False))
            result = np.array(list(o.values), dtype=np.object)[decoded[0].values]
            if len(result) and len(result[0]) == 1:
                result = ''.join(result)
            cv2.putText(
                im2,
                f'{o.name}: {result}',
                (0, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            y += 35
        cv2.imshow('image', im2)
        cv2.waitKey(1)
        # rows = []
        # for _ in range(3):
        #     row = []
        #     for _ in range(3):
        #         image = random.choice(self.images)
        #         im = image.imread()
        #
        #         pred = self.model.predict([[im]], 1)[0]
        #         expc = image.make_expected()
        #
        #         expc_im = (np.hstack([np.expand_dims(expc, 1)] * 50) * 255).astype(np.uint8)
        #         pred_im = (np.hstack([np.expand_dims(pred, 1)] * 50) * 255).astype(np.uint8)
        #
        #         rowim = np.hstack((
        #             cv2.resize(im, (0, 0), fx=1 / DOWNSCALE, fy=1 / DOWNSCALE),
        #             cv2.cvtColor(pred_im, cv2.COLOR_GRAY2BGR),
        #             cv2.cvtColor(expc_im, cv2.COLOR_GRAY2BGR)
        #         ))
        #         row.append(rowim)
        #     rows.append(np.hstack(row))
        # cv2.imshow('samples', cv2.resize(np.vstack(rows), (0, 0), fx=0.5, fy=0.5))
        # cv2.waitKey(1)


def main(use_gpu=True) -> None:
    np.set_printoptions(precision=5, suppress=True)

    from tensorflow.python.client import device_lib
    print(device_lib.list_local_devices())

    config = tf.ConfigProto(device_count={'GPU': 1 if use_gpu else 0, 'CPU': 1}, log_device_placement=False)
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    keras.backend.set_session(sess)

    image_paths = glob.glob(TRAINING_DIR + '/**/**/kills/**/*.png', recursive=True)
    images = [Image(p) for p in image_paths]
    assert len(images), 'Could not load any images'
    print(f'Loaded {len(images)} images')

    # image = random.choice(images)
    # print(image.data)
    # print(image.make_expected())
    # cv2.imshow('image', image.imread())
    # cv2.waitKey(0)

    model: Model = construct_model()
    image_loader = ImageLoader(images, batch_size=BATCH_SIZE)
    model.fit_generator(
        image_loader,
        epochs=50,
        callbacks=[
            LambdaCallback(on_epoch_begin=lambda *_: image_loader.shuffle()),

            TensorBoard(log_dir=get_next_logdir('./logs', name=NAME)),
            ModelCheckpoint(f'./models/{NAME}_checkpoint.h5'),
            VisualiseCallback(images, frequency=10),
        ],
        # max_queue_size=20,
        # workers=4,
        # use_multiprocessing=True
    )
    os.makedirs('./models', exist_ok=True)
    model.save(f'./models/{NAME}.h5')


if __name__ == '__main__':
    main()

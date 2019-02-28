import glob
import itertools
import logging
import os
import random
import string
import time
import typing
from typing import List, NamedTuple, Tuple, Dict

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.contrib.layers import dense_to_sparse
from tensorflow.python.framework import tensor_shape
from tensorflow.python.keras import Model, backend
from tensorflow.python.keras.callbacks import Callback, LambdaCallback, ModelCheckpoint, TensorBoard
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.utils import Sequence

from overwatch import data

logger = logging.getLogger()


TRAINING_DIR = r'C:\scratch\owl-killfeed-2'
NAME = 'kill_extralayer'

HEIGHT = 46
WIDTH = 500

# use a kernel height of HEIGHT-SLIP_Y and then max along x-axis
# this means the model should be resilient to the row being +-SLIP_Y pixels offset
SLIP_Y = 3
HIDDEN_FEATURES = 50

# TODO: Y_RANDOM_PAD = 2

BATCH_SIZE = 16

class Output(NamedTuple):
    name: str

    values: List[str]

    kernel_width: int
    conv_maxpool: int = 1
    kernel_maxpool: int = 1


# TODO: make these all one class
OTHERS = ['dva.mech', 'junkrat.riptire', 'orisa.supercharger', 'torbjorn.turret', 'symmetra.teleporter', 'training.bot']
HEROES = sorted(list(data.heroes.keys()) + ['ashe.bob'] + OTHERS)
OUTPUTS = [
    Output(
        'text',
        string.ascii_uppercase + string.digits[1:],
        15,
        1,
        2
    ),
    Output(
        'hero',
        HEROES,
        50,
        5,
        5
    )
]

class Image:
    def __init__(self, path: str):
        self.path = path
        self.data = str(os.path.normpath(self.path)).split(os.path.sep)[-2]

        # hack fixes
        self.data = self.data.replace('.ASHER_IR', '.ASHER')
        self.data = self.data.replace('.AIMOU', '.TAIMOU')
        self.data = self.data.replace('.training_bot', '.training-bot')

        try:
            left, right = self.data.split('_')

            self.text = ''
            self.hero = []
            if left:
                if 'live-killfeed' in path:
                    n = left.split('.')[1].replace('0', 'O').split(' ')[0]
                    h = left.split('.')[2].replace('-', '.')
                else:
                    n = left.split('.')[2].replace('0', 'O').split(' ')[0]
                    h = left.split('.')[1].replace('-', '.')
                assert h in HEROES, f'{h} not found in HEREOS, but got data {self.data}'
                self.text += n
                self.hero.append(h)

            if 'live-killfeed' in path:
                n = right.split('.')[1].replace('0', 'O').split(' ')[0]
                h = right.split('.')[2].replace('-', '.')
            else:
                n = right.split('.')[2].replace('0', 'O').split(' ')[0]
                h = right.split('.')[1].replace('-', '.')
            assert h in HEROES, f'{h} not found in HEREOS, but got data {self.data}'
            self.text += n
            self.hero.append(h)
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
                inds = []
                for e in getattr(self, output.name):
                    inds.append(output.values.index(e))
                r.append(inds)
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

    def get_config(self) -> Dict[str, any]:
        config = {
            'dims': self.dims,
        }
        base_config = super(MaxAlongDims, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return backend.max(inputs, axis=self.dims)

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

    conv0 = Conv2D(
        8,
        (3, 3),
        name='conv0',
        activation='relu',
    )(normed_image)

    conv1 = Conv2D(
        1,
        (3, 3),
        name='conv1',
        activation='relu',
        # kernel_regularizer=l2(0.0001),
        kernel_initializer='he_normal'
    )(conv0)

    conv2 = Conv2D(
        HIDDEN_FEATURES,
        (conv1.get_shape()[1].value-SLIP_Y, 4),
        name='conv2',
        activation='relu',
        # activity_regularizer=l1(0.00001),
        kernel_initializer='he_normal'
    )(conv1)
    conv2_pooled = MaxAlongDims(
        (1, ),
        name='conv2_pool_height'
    )(conv2)
    conv2_permuted = Permute(
        (2, 1),
        name='conv2_permuted'
    )(conv2_pooled)
    conv2_reshape = Lambda(
        lambda e: tf.expand_dims(e, -1),
        name='conv2_reshape'
    )(conv2_permuted)

    outputs = {}
    for output_definition in OUTPUTS:
        output = conv2_reshape
        if output_definition.conv_maxpool != 1:
            output = MaxPool2D(
                (1, output_definition.conv_maxpool),
                name=output_definition.name + '_convpool'
            )(output)

        features = len(output_definition.values) + 1
        output = Conv2D(
            features,
            (HIDDEN_FEATURES, output_definition.kernel_width),
            name=output_definition.name + '_conv'
        )(output)
        if output_definition.kernel_maxpool != 1:
            output = MaxPool2D(
                (1, output_definition.kernel_maxpool),
                name=output_definition.name + '_pooled'
            )(output)
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
            for name, output in outputs.items()
        },
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
        self.last_batch = 0

    def on_batch_end(self, batch, logs=None):
        if time.time() - self.last_shown > self.frequency and batch - self.last_batch > 50:
            self.last_shown = time.time()
            self.last_batch = batch
            self.visualise()

    def visualise(self):
        cv2.imshow('images', np.vstack([self.make_image(2) for _ in range(3)]))
        cv2.waitKey(1)

    def make_image(self, scale=3):
        image: Image = random.choice(self.images)
        im = image.imread()
        pred = self.model.predict([[im]], 1)
        im2 = cv2.resize(im, (0, 0), fx=scale, fy=scale)
        # print(image.data)
        cv2.putText(
            im2,
            image.data,
            (0, 12 * scale),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.3 * scale,
            (0, 255, 0),
            2
        )
        y = 20 * scale + 10
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
                0.3 * scale,
                (0, 255, 0),
                2
            )
            y += 12 * scale
        return im2


def main(use_gpu=True) -> None:
    np.set_printoptions(precision=5, suppress=True)

    from tensorflow.python.client import device_lib
    print(device_lib.list_local_devices())

    config = tf.ConfigProto(device_count={'GPU': 1 if use_gpu else 0, 'CPU': 1}, log_device_placement=False)
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    keras.backend.set_session(sess)

    print('Loading paths')

    paths1 = glob.glob(TRAINING_DIR + '/**/**/kills/**/*.png', recursive=True)
    paths2 = glob.glob('C:/scratch/live-killfeed' + '/**/kills/**/*.png', recursive=True)
    print(len(paths1), len(paths2))
    while len(paths1) > len(paths2):
        paths2 += random.sample(paths2, 500)

    image_paths = paths1 + paths2
    image_paths = [p for p in image_paths if os.path.normpath(p).split(os.path.sep)[-2][0] != '_']

    images = [Image(p) for p in image_paths]
    assert len(images), 'Could not load any images'
    print(f'Loaded {len(images)} images')

    # image = random.choice(images)
    # print(image.data)
    # print(image.make_expected())
    # cv2.imshow('image', image.imread())
    # cv2.waitKey(0)

    model: Model = construct_model()
    model.load_weights(f'./models/{NAME}_checkpoint.h5')
    image_loader = ImageLoader(images, batch_size=BATCH_SIZE)
    model.fit_generator(
        image_loader,
        epochs=50,
        callbacks=[
            LambdaCallback(on_epoch_begin=lambda *_: image_loader.shuffle()),

            TensorBoard(log_dir=get_next_logdir('./logs', name=NAME)),
            ModelCheckpoint(f'./models/{NAME}_checkpoint.h5'),
            VisualiseCallback(images, frequency=30),
        ],
        max_queue_size=20,
        workers=4,
        use_multiprocessing=True
    )
    os.makedirs('./models', exist_ok=True)
    model.save(f'./models/{NAME}.h5')


if __name__ == '__main__':
    main()

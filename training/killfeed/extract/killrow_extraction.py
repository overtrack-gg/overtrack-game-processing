import glob
import itertools
import logging
import os
import random
import time
import typing
from typing import Dict, List, Tuple

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.framework import tensor_shape
from tensorflow.python.keras import Model, backend
from tensorflow.python.keras.callbacks import Callback, LambdaCallback
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.regularizers import *
from tensorflow.python.keras.utils import Sequence

logger = logging.getLogger()


TRAINING_DIR = r'C:\scratch\owl-killfeed'
NAME = 'killrow'

DOWNSCALE = 2
SQUASH = 4
DETECTION_KERNEL = (26, 8)
EXPECTED_HEIGHT = 2

BATCH_SIZE = 3

class Image:
    def __init__(self, path: str):
        self.path = path
        self._height: int = None
        posistions = str(os.path.basename(self.path)).rsplit('.', 1)[0].split('_', 1)[1]
        if posistions:
            self.positions = [float(p) for p in posistions.split('_')]
        else:
            self.positions = []

    @property
    def height(self) -> int:
        if self._height is None:
            self.imread()
        return self._height

    def imread(self) -> np.ndarray:
        im = cv2.imread(self.path)
        assert im.shape == (1080, 1920, 3)
        self._height = im.shape[0]
        return im

    def make_expected(self) -> np.ndarray:
        r = np.zeros((int(self.height / DOWNSCALE), ), np.float)
        for p in self.positions:
            for i in range(EXPECTED_HEIGHT):
                r[int(p / DOWNSCALE) + i] = 1
        return r


class ImageLoader(Sequence):
    def __init__(self, images: List[Image], batch_size=25, preprocessor: ImageDataGenerator=None) -> None:
        self.images = images
        self.batch_size = batch_size
        self.preprocessor = preprocessor

    def __len__(self) -> int:
        return int(np.ceil(len(self.images) / float(self.batch_size)))

    def shuffle(self) -> None:
        random.shuffle(self.images)

    def __getitem__(self, i: int) -> Tuple[np.ndarray, np.ndarray]:
        batch = self.images[i * self.batch_size:(i + 1) * self.batch_size]

        images = []
        expected = []
        for image in batch:
            im = image.imread()
            if self.preprocessor:
                im = self.preprocessor.random_transform(im)
            images.append(im)
            expected.append(image.make_expected())

        images = np.array(images)
        expected = np.array(expected)

        return images, expected

class RandomBrightnessContrast(Layer):

    def __init__(self, brightness_delta: float, contrast_lower: float, contrast_upper: float, **kwargs):
        super(RandomBrightnessContrast, self).__init__(**kwargs)
        self.brightness_delta = brightness_delta
        self.contrast_lower = contrast_lower
        self.contrast_upper = contrast_upper

    def call(self, inputs, training=None):
        def randomed():
            bright = tf.map_fn(lambda img: tf.image.random_brightness(img, self.brightness_delta), inputs)
            contrast = tf.image.random_contrast(bright, self.contrast_lower, self.contrast_upper)
            return contrast

        return K.in_train_phase(randomed, inputs, training=training)

    def get_config(self) -> Dict[str, any]:
        config = {
            'brightness_delta': self.brightness_delta,
            'contrast_lower': self.contrast_lower,
            'contrast_upper': self.contrast_upper
        }
        base_config: Dict[str, any] = super(RandomBrightnessContrast, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def compute_output_shape(self, input_shape):
        return input_shape


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
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return backend.max(inputs, axis=self.dims)


class SumAlongDims(Layer):

    def __init__(self, dims: typing.Sequence[int], **kwargs):
        super(SumAlongDims, self).__init__(**kwargs)
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
        base_config = super(SumAlongDims, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return backend.sum(inputs, axis=self.dims)


class VisualiseCallback(Callback):

    def __init__(self, images: List[Image], frequency: float):
        super().__init__()
        self.images = images
        self.frequency = frequency
        self.last_shown = 0

    def on_batch_end(self, batch, logs=None):
        if time.time() - self.last_shown > self.frequency:
            self.last_shown = time.time()
            rows = []
            for _ in range(3):
                row = []
                for _ in range(3):
                    image = random.choice(self.images)
                    im = image.imread()

                    pred = self.model.predict([[im]], 1)[0]
                    expc = image.make_expected()

                    expc_im = (np.hstack([np.expand_dims(expc, 1)] * 50) * 255).astype(np.uint8)
                    pred_im = (np.hstack([np.expand_dims(pred, 1)] * 50) * 255).astype(np.uint8)

                    rowim = np.hstack((
                        cv2.resize(im, (0, 0), fx=1 / DOWNSCALE, fy=1 / DOWNSCALE),
                        cv2.cvtColor(pred_im, cv2.COLOR_GRAY2BGR),
                        cv2.cvtColor(expc_im, cv2.COLOR_GRAY2BGR)
                    ))
                    row.append(rowim)
                rows.append(np.hstack(row))
            cv2.imshow('samples', cv2.resize(np.vstack(rows), (0, 0), fx=0.5, fy=0.5))
            cv2.waitKey(1)


def construct_model() -> Model:
    # image = Input(shape=(None, None, 3), name='image')
    image = Input(shape=(1080, 1920, 3), name='image')
    scaled = AveragePooling2D((2, 2))(image)

    # image_fuzz = Dropout(0.02)(image)
    # image_fuzz = GaussianNoise(4)(image_fuzz)
    # image_fuzz = RandomBrightnessContrast(40, 0.6, 1.4, name='random_brightness_contrast')(image_fuzz)
    normed_image = BatchNormalization(input_shape=(None, None, 3))(scaled)

    conv1 = Conv2D(
        2,
        (3, 3),
        name='conv1',
        activation='relu',
        padding='same',
        kernel_regularizer=l2(0.0001),
        kernel_initializer='he_normal'
    )(normed_image)
    conv1 = MaxPool2D(
        (1, 4),
        name='squash'
    )(conv1)

    conv2 = Conv2D(
        8,
        (4, 4),
        name='conv2',
        activation='relu',
        padding='same',
        activity_regularizer=l1(0.00001),
        kernel_initializer='he_normal'
    )(conv1)

    detection = Conv2D(
        1,
        DETECTION_KERNEL,
        name='detection',
        activation=None,
        padding='same'
    )(conv2)
    detection_y = SumAlongDims(
        (2, 3)
    )(detection)
    detection_y = Activation(
        'sigmoid'
    )(detection_y)

    model = Model(
        inputs=image,
        outputs=detection_y
    )
    model.compile(
        optimizer=Adam(),
        loss='binary_crossentropy',
        metrics=[accuracy, accuracy_positive]
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


# noinspection PyTypeChecker
def accuracy(y_true: tf.Tensor, y_pred: tf.Tensor):
    b_true = tf.cast(y_true > 0.5, tf.float32)
    b_pred = tf.cast(y_pred > 0.5, tf.float32)
    correct = tf.cast(tf.equal(b_true, b_pred), tf.float32)
    return tf.reduce_mean(correct, axis=1)


# noinspection PyTypeChecker
def accuracy_positive(y_true: tf.Tensor, y_pred: tf.Tensor):
    b_true = tf.cast(y_true > 0.5, tf.float32)
    b_pred = tf.cast(y_pred > 0.5, tf.float32)
    correct = tf.cast(tf.equal(b_true, b_pred), tf.float32)
    return (tf.reduce_sum(correct * b_true, axis=1) + 1e-4) / (tf.reduce_sum(b_true, axis=1) + 1e-4)


def main(train=True) -> None:
    np.set_printoptions(precision=5, suppress=True)

    from tensorflow.python.client import device_lib
    print(device_lib.list_local_devices())

    config = tf.ConfigProto(device_count={'GPU': 1 if train else 0, 'CPU': 1}, log_device_placement=False)
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    keras.backend.set_session(sess)

    image_paths = glob.glob(TRAINING_DIR + '/**/*/frames/*.png', recursive=True)
    images = [Image(p) for p in image_paths]

    # model: Model = load_model(
    #     f'./models/{NAME}_checkpoint.h5',
    #     custom_objects={
    #         'MaxAlongDims': MaxAlongDims,
    #         "GlorotUniform": tf.keras.initializers.glorot_uniform
    #     }
    # )

    model: Model = construct_model()

    # model.load_weights(f'./models/{NAME}_checkpoint.h5')

    image_loader = ImageLoader(images, batch_size=BATCH_SIZE)
    os.makedirs('./models', exist_ok=True)
    model.fit_generator(
        image_loader,
        epochs=50,
        callbacks=[
            # TensorBoard(log_dir=get_next_logdir('./logs', name=NAME)),
            # ModelCheckpoint(f'./models/{NAME}_checkpoint.h5'),
            VisualiseCallback(images, frequency=30),
            LambdaCallback(on_epoch_begin=lambda *_: image_loader.shuffle())
        ],
        max_queue_size=20,
        workers=4,
        use_multiprocessing=True
    )
    # model.save(f'./models/{NAME}.h5')

def visualise_r(im, r):
    expected_im = (np.hstack([np.expand_dims(r, 1)] * 50) * 255).astype(np.uint8)
    exim = np.hstack((cv2.resize(im, (0, 0), fx=1 / DOWNSCALE, fy=1 / DOWNSCALE), cv2.cvtColor(expected_im, cv2.COLOR_GRAY2BGR)))
    return exim


if __name__ == '__main__':
    main(True)

import glob
import itertools
import logging
import os
import random
import shutil
from typing import List, Optional, Tuple

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras import Model
from tensorflow.python.keras.callbacks import ModelCheckpoint, TensorBoard
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.regularizers import *
from tensorflow.python.keras.utils import Sequence

logger = logging.getLogger()


TRAINING_DIR = r'C:\scratch\objective'
IMAGE_SIZE = (170, 560, 3)
# KOTH_CROP = ((50, 10), (265, 265))
# CHECKPOINT_CROP = ((23, 100), (180, 180))

OUTPUTS = [
    ('game_mode', ['not_overwatch', 'koth', 'checkpoint']),
    ('game_state', ['prepare', 'started', 'overtime']),
    ('koth_ownership', 'xBR'),
    ('koth_map', 'xABC'),
    ('checkpoint_quickplay', 1),
    ('checkpoint_attacking', 1),
    ('checkpoint_payload', 1),
]
IGNORE = 0


def sigmoid(x):
    if np.isscalar(x):
        return 1 / (1 + np.math.exp(-x))
    else:
        return [sigmoid(y) for y in x]


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


class Image:
    def __init__(self, path: str):
        self.path = path
        self.parts = path.split(os.path.sep)[len(os.path.normpath(TRAINING_DIR).split(os.path.sep)):]

    def imread(self) -> np.ndarray:
        im = cv2.imread(self.path)
        return im

    def __str__(self) -> str:
        s = 'Image('
        for name, vals in OUTPUTS:
            s += name
            s += '='
            if (type(vals) is int and vals > 1) or type(vals) in [list, str]:
                s += vals[getattr(self, name)]
            else:
                s += f'{getattr(self, name):1.1f}'
            s += ', '
        return s[:-2] + ')'

    # ------ generic fields ------

    @property
    def game_state(self) -> int:
        if self.is_overwatch and self.round_started:
            if self.overtime:
                return 2
            else:
                return 1
        else:
            return 0

    @property
    def game_mode(self) -> int:
        if self.is_overwatch:
            if self.is_koth:
                return 1
            else:
                return 2
        else:
            return 0

    # ------ utility fields ------

    @property
    def is_overwatch(self) -> int:
        return self.parts[0] == 'is_overwatch'

    @property
    def is_koth(self) -> int:
        if not self.is_overwatch:
            return IGNORE
        else:
            return self.parts[1] == 'koth'

    @property
    def round_started(self) -> int:
        if not self.is_overwatch:
            return IGNORE
        elif self.is_koth:
            # ['is_overwatch', 'koth', 'started', ...]
            # ['is_overwatch', 'koth', 'prepare', ...]
            return self.parts[2] == 'started'
        else:
            # ['is_overwatch', 'checkpoint', 'attack', 'prepare', ...]
            # ['is_overwatch', 'checkpoint', 'attack', 'payload', ...]
            return self.parts[3] != 'prepare'

    @property
    def overtime(self) -> int:
        if not self.is_overwatch:
            return IGNORE
        else:
            return 'overtime' in self.parts

    # ------ KOTH fields ------

    @property
    def koth_ownership(self) -> int:
        if not self.is_overwatch or not self.is_koth or not self.round_started:
            return 0
        else:
            # ['is_overwatch', 'koth', 'started', 'blue', ...]
            return ['uncap', 'blue', 'red'].index(self.parts[3])

    @property
    def koth_map(self) -> int:
        if not self.is_overwatch or not self.is_koth or not self.round_started:
            return 0
        else:
            # ['is_overwatch', 'koth', 'started', 'blue', 'C', ...]
            # ['is_overwatch', 'koth', 'started', 'uncap', 'A', ...]
            # ['is_overwatch', 'koth', 'started', 'uncap', 'lock', ...]
            return ['lock', 'A', 'B', 'C'].index(self.parts[4])

    # ------ checkpoint fields ------

    @property
    def checkpoint_quickplay(self) -> int:
        if not self.is_overwatch or self.is_koth:
            return IGNORE
        else:
            return 'quickplay' in self.parts

    @property
    def checkpoint_attacking(self) -> int:
        if not self.is_overwatch or self.is_koth:
            return IGNORE
        else:
            # ['is_overwatch', 'checkpoint', 'attack', ...]
            # ['is_overwatch', 'checkpoint', 'defend', ...]
            return self.parts[2] == 'attack'

    @property
    def checkpoint_payload(self) -> int:
        if not self.is_overwatch or self.is_koth or not self.round_started:
            # TODO: checking for PL even in prepare state should be possible
            return IGNORE
        else:
            # ['is_overwatch', 'checkpoint', 'defend', 'overtime', ...]
            # ['is_overwatch', 'checkpoint', 'defend', 'objective', ...]
            # ['is_overwatch', 'checkpoint', 'defend', 'payload', ...]
            # ['is_overwatch', 'checkpoint', 'defend', 'prepare', ...]
            return self.parts[3] == 'payload'

            # return ['prepare', 'payload', 'objective'].index(self.parts[3])


class ImageLoader(Sequence):
    def __init__(self, images: List[Image], batch_size=25, preprocessor: ImageDataGenerator=None) -> None:
        self.images = images
        self.batch_size = batch_size
        self.preprocessor = preprocessor

    def __len__(self) -> int:
        return int(np.ceil(len(self.images) / float(self.batch_size)))

    def __getitem__(self, i: int) -> Tuple[np.ndarray, List[np.ndarray]]:
        if i == 0:
            print('shuffling')
            random.shuffle(self.images)

        batch = self.images[i * self.batch_size:(i + 1) * self.batch_size]

        images = []
        for image in batch:
            im = image.imread()
            if self.preprocessor:
                im = self.preprocessor.random_transform(im)
            images.append(im)
        images = np.array(images)

        expected = []
        for i, (name, o) in enumerate(OUTPUTS):
            if type(o) is str:
                o = len(o)
            arr = []
            for image in batch:
                arr.append([getattr(image, name)])
            expected.append(np.array(arr))

        return images, expected


class Prediction:

    def __init__(self, data: List[np.ndarray]):
        for (name, o), val in zip(OUTPUTS, data):
            if o == 1:
                val = val[0, 0]
            else:
                val = softmax(val[0])
            setattr(self, name, val)

    def __str__(self) -> str:
        s = 'Prediction('
        for name, vals in OUTPUTS:
            s += name
            s += '='
            if (type(vals) is int and vals > 1) or type(vals) in [str, list]:
                s += vals[np.argmax(getattr(self, name))]
            else:
                s += f'{getattr(self, name):1.1f}'
            s += ', '
        return s[:-2] + ')'

    # noinspection PyUnresolvedReferences
    def mismatch_reason(self, image: Image) -> Optional[str]:
        if np.argmax(self.game_mode) != image.game_mode:
            return 'game_mode'
        elif np.argmax(self.game_mode) == 0:
            return None

        # if (self.is_koth > 0.5) != image.is_koth:
        #     return 'is_koth'
        # if (self.round_started > 0.5) != image.round_started:
        #     return 'round_started'
        # if (self.overtime > 0.5) != image.overtime:
        #     return 'overtime'

        if image.is_koth:
            if np.argmax(self.koth_ownership) != image.koth_ownership:
                return 'koth_ownership'
            if np.argmax(self.koth_map) != image.koth_map:
                return 'koth_map'
        else:
            if (self.checkpoint_quickplay > 0.5) != image.checkpoint_quickplay:
                return 'checkpoint_quickplay'
            if (self.checkpoint_attacking > 0.5) != image.checkpoint_attacking:
                return 'checkpoint_attacking'
            if not image.overtime and (self.checkpoint_payload > 0.5) != image.checkpoint_payload:
                return 'checkpoint_payload'
        return None

    def matches(self, image: Image) -> bool:
        return self.mismatch_reason(image) is None

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

    def get_config(self):
        config = {
            'brightness_delta': self.brightness_delta,
            'contrast_lower': self.contrast_lower,
            'contrast_upper': self.contrast_upper
        }
        base_config = super(RandomBrightnessContrast, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def compute_output_shape(self, input_shape):
        return input_shape


run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
run_metadata = tf.RunMetadata()


def construct_model() -> Model:
    image = Input(shape=IMAGE_SIZE, name='image')

    # image_fuzz = Dropout(0.02)(image)
    # image_fuzz = GaussianNoise(4)(image_fuzz)
    # image_fuzz = RandomBrightnessContrast(40, 0.6, 1.4, name='random_brightness_contrast')(image_fuzz)
    normed_image = BatchNormalization(input_shape=(None, None, 3))(image)

    # normed_image = Lambda(lambda x: x / 255.0 - 0.5)(image)

    conv1 = Conv2D(2, (4, 4), name='conv1', activation='relu', kernel_regularizer=l2(0.0001), kernel_initializer='he_normal')(normed_image)
    conv1 = MaxPool2D((3, 3), name='conv1_maxpool')(conv1)

    # conv2 = Conv2D(8, (3, 3), name='conv2', activation='relu')(conv1)
    # conv2 = MaxPool2D((2, 2), name='conv2_maxpool')(conv2)

    conv2 = Conv2D(8, (4, 4), name='conv2', activation='relu', activity_regularizer=l1(0.00001), kernel_initializer='he_normal')(conv1)

    conv2_mp = MaxPool2D((2, 2), name='conv2_maxpool')(conv2)
    conv3 = Conv2D(32, (3, 3), name='conv3', activation='relu', activity_regularizer=l1(0.0001), kernel_initializer='he_normal')(conv2_mp)

    position_independant = GlobalMaxPool2D(name='pi_maxpool')(conv3)
    position_independant = Flatten()(position_independant)

    position_dependant = Conv2D(2, (1, 1), name='pd_combine', activation='relu', kernel_regularizer=l2(0.0001), kernel_initializer='he_normal')(conv2)
    position_dependant = MaxPool2D((6, 10), name='pd_maxpool')(position_dependant)
    position_dependant = Flatten()(position_dependant)
    position_dependant = Dropout(0.05)(position_dependant)
    position_dependant = Dense(8, name='pd_dense', activation='relu', kernel_regularizer=l2(0.0001), kernel_initializer='he_normal')(position_dependant)

    shared_model = concatenate([position_independant, position_dependant])
    # shared_model = Dense(32, activation='relu')(shared_model)

    outputs = {
        name: Dense(o if type(o) is int else len(o), name=f'{name}', activation='sigmoid' if o == 1 else 'softmax')(shared_model)
        for name, o in OUTPUTS
    }

    model = Model(
        inputs=image,
        outputs=list(outputs.values())
    )
    model.compile(
        optimizer=Adam(lr=0.01),
        loss={
            name: 'binary_crossentropy' if o == 1 else 'sparse_categorical_crossentropy'
            for name, o in OUTPUTS
        },
        metrics={
            name: 'binary_accuracy' if o == 1 else 'sparse_categorical_accuracy'
            for name, o in OUTPUTS
        },
        loss_weights={
            name: 5 if name == 'koth_map' else 1 for name, o in OUTPUTS
        },
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


def main() -> None:
    name = '8_32_bs128_newclass_prepfix'

    np.set_printoptions(precision=2, suppress=True)

    from tensorflow.python.client import device_lib
    print(device_lib.list_local_devices())

    config = tf.ConfigProto(device_count={'GPU': 1, 'CPU': 1}, log_device_placement=False)
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    keras.backend.set_session(sess)

    image_paths = glob.glob(TRAINING_DIR + '/**/*.png', recursive=True)
    images = [Image(p) for p in image_paths]
    random.shuffle(images)
    # images = images[:10*1000]

    # model: Model = load_model(
    #     './models/8_32_bs128_regulized_relu_altmode.h5',
    #     custom_objects={
    #         'RandomBrightnessContrast': RandomBrightnessContrast
    #     }
    # )

    model = construct_model()
    image_loader = ImageLoader(images, batch_size=128)
    model.fit_generator(
        image_loader,
        epochs=50,
        callbacks=[
            TensorBoard(log_dir=get_next_logdir('./logs', name=name)),
            ModelCheckpoint(f'./models/{name}_checkpoint.h5')
        ],
        max_queue_size=20,
        workers=4,
        use_multiprocessing=True
    )
    os.makedirs('./models', exist_ok=True)
    model.save(f'./models/{name}.h5')

    # from tensorflow.python.client import timeline
    # tl = timeline.Timeline(run_metadata.step_stats)
    # ctf = tl.generate_chrome_trace_format()
    # os.makedirs('output', exist_ok=True)
    # with open('output/timeline.json', 'w') as f:
    #     f.write(ctf)

    # random_brightness_contrast = K.function(
    #     [model.input, K.learning_phase()],
    #     [model.get_layer('random_brightness_contrast').output]
    # )
    random.shuffle(images)
    for i, image in enumerate(images):
        oim = image.imread()
        # im = random_brightness_contrast([[oim], 1])[0][0]
        # im = np.clip(im, 0, 255).astype(np.uint8)
        im = oim

        r = model.predict(
            [[oim]],
            1
        )
        prediction = Prediction(r)
        if prediction.mismatch_reason(image):
            # shutil.move(image.path, os.path.join(TRAINING_DIR, os.path.basename(image.path)))
            # print(i, len(images), int((i / len(images)) * 100))
            # continue

            print('\n')
            print(i, len(images), int((i / len(images) * 100)))
            print(image.path)
            print(' ' * 4, image)
            print(prediction)
            print(prediction.mismatch_reason(image), 'didn\'t match')

            cv2.putText(
                im,
                prediction.mismatch_reason(image),
                (20, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 0, 255),
                2
            )
            cv2.imshow('image', np.hstack([oim, im]))

            if cv2.waitKey(0) == 32:
                shutil.move(image.path, os.path.join(TRAINING_DIR, os.path.basename(image.path)))
        else:
            print('.', end='')


if __name__ == '__main__':
    main()

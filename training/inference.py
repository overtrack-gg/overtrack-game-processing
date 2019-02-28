import glob
import logging
import random
from typing import Dict

import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.engine import Layer
from tensorflow.python.keras.models import Model, load_model

from training.objective import Image, Prediction

TRAINING_DIR = r'C:\scratch\objective'


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

        return K.in_train_phase(randomed, inputs, training=False)

    def get_config(self) -> Dict[str, any]:
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


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = tf.ConfigProto(device_count={'GPU': 0, 'CPU': 1}, log_device_placement=False)
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    keras.backend.set_session(sess)

    # cap = OBSFrameExtractor('Overwatch', debug=True)

    images = [Image(p) for p in glob.glob(TRAINING_DIR + '/**/*.png', recursive=True)]

    model: Model = load_model(
        './models/8_32_bs128_regulized_relu_altmode_checkpoint.h5',
        custom_objects={
            'RandomBrightnessContrast': RandomBrightnessContrast
        }

    )
    print(model.layers)

    inp = model.input
    outputs = [layer.output for layer in model.layers[1:]]
    functors = [K.function([inp, K.learning_phase()], [out]) for out in outputs]

    print(functors)

    outs = {l.name: f for l, f in zip(model.layers[1:], functors)}
    print(outs)

    random_brightness_contrast = K.function(
        [model.input, K.learning_phase()],
        [model.get_layer('random_brightness_contrast').output]
    )
    random.shuffle(images)
    for i, image in enumerate(images):
        oim = image.imread()
        im = random_brightness_contrast([[oim], 1])[0][0]
        im = np.clip(im, 0, 255).astype(np.uint8)

        r = model.predict(
            [[oim]],
            1
        )
        prediction = Prediction(r)
        if prediction.mismatch_reason(image):
            print('\n')
            print(i, len(images), int((i / len(images) * 100)))
            print(image.path)
            print(' ' * 4, image)
            print(prediction)
            print(Prediction(model.predict(
                [[im]],
                1
            )))
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
            cv2.waitKey(0)
        else:
            print('.', end='')


if __name__ == '__main__':
    main()

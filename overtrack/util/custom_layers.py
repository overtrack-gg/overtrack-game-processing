from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import tensorflow as tf
from tensorflow.python.framework import tensor_shape
from tensorflow.python.keras import backend
from tensorflow.python.keras.layers import Layer
from tensorflow.python.ops import sparse_ops
from tensorflow.python.ops.gen_ctc_ops import ctc_greedy_decoder


class MaxAlongDims(Layer):

    def __init__(self, dims: Sequence[int], **kwargs):
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


# class RandomBrightnessContrast(Layer):
#
#     def __init__(self, brightness_delta: float, contrast_lower: float, contrast_upper: float, **kwargs):
#         super(RandomBrightnessContrast, self).__init__(**kwargs)
#         self.brightness_delta = brightness_delta
#         self.contrast_lower = contrast_lower
#         self.contrast_upper = contrast_upper
#
#     def call(self, inputs, training=None):
#         def randomed():
#             bright = tf.map_fn(lambda img: tf.image.random_brightness(img, self.brightness_delta), inputs)
#             contrast = tf.image.random_contrast(bright, self.contrast_lower, self.contrast_upper)
#             return contrast
#
#         return K.in_train_phase(randomed, inputs, training=training)
#
#     def get_config(self) -> Dict[str, any]:
#         config = {
#             'brightness_delta': self.brightness_delta,
#             'contrast_lower': self.contrast_lower,
#             'contrast_upper': self.contrast_upper
#         }
#         base_config: Dict[str, any] = super(RandomBrightnessContrast, self).get_config()
#         # noinspection PyTypeChecker
#         return dict(list(base_config.items()) + list(config.items()))
#
#     def compute_output_shape(self, input_shape):
#         return input_shape


class SumAlongDims(Layer):

    def __init__(self, dims: Sequence[int], **kwargs):
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


class ExpandDims(Layer):

    def __init__(self, axis: int = -1, **kwargs):
        super(ExpandDims, self).__init__(**kwargs)
        self.axis = axis

    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape).as_list()
        newdims = list(input_shape)
        if self.axis == -1:
            newdims.append(1)
        else:
            newdims.insert(self.axis, 1)
        return tensor_shape.TensorShape(newdims)

    def get_config(self) -> Dict[str, any]:
        config = {
            'axis': self.axis,
        }
        base_config = super(ExpandDims, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return backend.expand_dims(inputs, axis=self.axis)


class Squeeze(Layer):

    def __init__(self, axis: int = -1, **kwargs):
        super(Squeeze, self).__init__(**kwargs)
        self.axis = axis

    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape).as_list()
        newdims = list(input_shape)
        newdims.pop(self.axis)
        return tensor_shape.TensorShape(newdims)

    def get_config(self) -> Dict[str, any]:
        config = {
            'axis': self.axis,
        }
        base_config = super(Squeeze, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return backend.squeeze(inputs, axis=self.axis)


class Pad(Layer):

    def __init__(self, paddings: Any, **kwargs):
        super(Pad, self).__init__(**kwargs)
        self.paddings = paddings

    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape).as_list()
        return tensor_shape.TensorShape(input_shape)

    def get_config(self) -> Dict[str, any]:
        config = {
            'paddings': self.paddings,
        }
        base_config = super(Pad, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return tf.pad(inputs, paddings=self.paddings)


class NormaliseByte(Layer):

    def __init__(self, **kwargs):
        super(NormaliseByte, self).__init__(**kwargs)

    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape).as_list()
        return tensor_shape.TensorShape(input_shape)

    def get_config(self) -> Dict[str, any]:
        config = {
        }
        base_config = super(NormaliseByte, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training=None):
        return tf.cast(inputs, tf.float32) / 255. - 0.5


class CTCDecoder(Layer):

    def __init__(self, **kwargs):
        super(CTCDecoder, self).__init__(**kwargs)

    def compute_output_shape(self, input_shape):
        input_shape = tensor_shape.TensorShape(input_shape).as_list()
        newdims = list(input_shape)
        newdims.pop(1)
        print(newdims)
        return tensor_shape.TensorShape(newdims)

    def get_config(self):
        config = {
        }
        base_config = super(CTCDecoder, self).get_config()
        # noinspection PyTypeChecker
        return dict(list(base_config.items()) + list(config.items()))

    # def build(self, input_shape):
    #     # print('>', input_shape)
    #     # assert isinstance(input_shape, list)
    #     super(CTCDecoder, self).build(input_shape)

    def call(self, inputs, training=None):
        (decoded,), log_prob = tf.nn.ctc_greedy_decoder(
            tf.transpose(inputs, (1, 0, 2)),
            tf.tile([inputs.shape[1]], [tf.shape(inputs)[0]]),
            True
        )
        return sparse_ops.sparse_to_dense(decoded.indices, decoded.dense_shape, decoded.values, default_value=-1)
        # decoded_dense = [
        #     sparse_ops.sparse_to_dense(st.indices, st.dense_shape, st.values, default_value=-1)
        #     for st in decoded
        # ]
        # return decoded_dense[0]
        # with tf.control_dependencies([
        #     tf.print('inputs', tf.shape(inputs), '\noutputs', decoded_dense[0], '\ntile', tf.tile([inputs.shape[1]], [tf.shape(inputs)[0]]), '\n')
        # ]):
        #     return decoded_dense[0] * 1

def make_ctc_decoder(inputs):
    (decoded,), log_prob = tf.nn.ctc_greedy_decoder(
        tf.transpose(inputs, (1, 0, 2)),
        tf.tile([inputs.shape[1]], [tf.shape(inputs)[0]]),
        True
    )
    r = sparse_ops.sparse_to_dense(decoded.indices, decoded.dense_shape, decoded.values, default_value=-1)
    return [r, log_prob]

def _decode_ctc(logits: Union[list, np.ndarray], merge_repeated=True, alphabet: Optional[np.ndarray] = None, seq_lens: Optional[List[int]] = None):
    if isinstance(logits, list):
        logits = np.array(logits)
    decoded_ix, decoded_val, decoded_shape, log_probabilities = ctc_greedy_decoder(
        np.transpose(logits, (1, 0, 2)),
        np.full((logits.shape[0],), fill_value=logits.shape[1], dtype=np.int) if not seq_lens else seq_lens,
        merge_repeated=merge_repeated
    )
    return _decoded_to_rows(
        decoded_ix.numpy(),
        decoded_val.numpy(),
        decoded_shape.numpy(),
        alphabet=alphabet,
        aslist=True
    )

def _decoded_to_rows(idx, val, shape, alphabet=None, aslist=False):
    outputs = []
    valitr = iter(val)
    for i in range(shape[0]):
        row_idx = idx[idx[:, 0] == i][:, 1]
        row = np.empty_like(row_idx)
        for a in row_idx:
            row[a] = next(valitr)
        if alphabet is not None:
            row = alphabet[row]
        if aslist:
            row = row.tolist()
        outputs.append(row)
    return outputs


custom_objects = {
    'MaxAlongDims': MaxAlongDims,
    'ExpandDims': ExpandDims,
    'Squeeze': Squeeze,
    'Pad': Pad,
    'NormaliseByte': NormaliseByte
}

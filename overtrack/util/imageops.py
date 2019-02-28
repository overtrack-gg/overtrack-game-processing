import os
import string

import tesserocr
import cv2
import numpy as np
from typing import NamedTuple, List, Tuple, Optional


class ConnectedComponent(NamedTuple):

    label: int
    x: int
    y: int
    w: int
    h: int

    area: int
    centroid: Tuple[float, float]


def connected_components(image: np.ndarray, connectivity=4) -> Tuple[np.ndarray, List[ConnectedComponent]]:
    r, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=connectivity)
    components = []
    for i, (stat, centroid) in enumerate(zip(stats, centroids)):
        # thanks mypy :/
        components.append(ConnectedComponent(
            i,
            int(stat[0]),
            int(stat[1]),
            int(stat[2]),
            int(stat[3]),
            int(stat[4]),
            centroid=(float(centroid[0]), float(centroid[1]))
        ))
    return labels, components


def otsu_thresh(vals: np.ndarray, mn: int, mx: int) -> int:
    # adapted from https://github.com/scikit-image/scikit-image/blob/v0.14.0/skimage/filters/thresholding.py#L230: threshold_otsu

    mn = np.clip(mn, 0, 253)
    mx = np.clip(mx, mn + 2, 255)
    hist, bin_edges = np.histogram(vals, mx - mn, (mn, mx + 1))
    hist = hist.astype(float)
    bin_edges = bin_edges[1:]

    # class probabilities for all possible thresholds
    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]
    # class means for all possible thresholds
    # handle divide-by-zero by outputting 0
    mean1 = np.divide(np.cumsum(hist * bin_edges), weight1, np.zeros_like(weight1), where=weight1 != 0)
    mean2 = np.divide(np.cumsum((hist * bin_edges)[::-1]), weight2[::-1], out=np.zeros_like(weight2[::-1]), where=weight2[::-1] != 0)[::-1]

    # Clip ends to align class 1 and class 2 variables:
    # The last value of `weight1`/`mean1` should pair with zero values in
    # `weight2`/`mean2`, which do not exist.
    variance12 = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2
    variance12[np.isnan(variance12)] = 0

    idx = np.argmax(variance12)
    threshold = bin_edges[:-1][idx]
    return threshold


def fast_gaussian(im: np.ndarray, v: float, scale: float=2):
    ims = cv2.resize(im, (0, 0), fx=1 / scale, fy=1 / scale)
    im2 = cv2.GaussianBlur(ims, (0, 0), v // scale)
    return cv2.resize(im2, (im.shape[1], im.shape[0]), fx=scale, fy=scale)


# def match_templates_masked(image, templates, last=None):
#     if last is not None:
#         pass
#     # mask = cv2.cvtColor()


def otsu_thresh_lb_fraction(image: np.ndarray, fraction: float) -> np.ndarray:
    if len(image.shape) == 3:
        image = np.min(image, axis=2)
    otsu_lb = int(np.mean(image) * fraction)
    tval = otsu_thresh(image, otsu_lb, 255)
    _, thresh = cv2.threshold(image, tval, 255, cv2.THRESH_BINARY)
    return thresh


# eng.traineddata from https://github.com/tesseract-ocr/tessdata/blob/master/eng.traineddata
# noinspection PyArgumentList
tesseract_only = tesserocr.PyTessBaseAPI(
    path=os.path.join(os.path.dirname(__file__), 'data'),
    lang='eng',
    oem=tesserocr.OEM.TESSERACT_ONLY,
    psm=tesserocr.PSM.SINGLE_LINE
)

# noinspection PyArgumentList
tesseract_lstm = tesserocr.PyTessBaseAPI(
    path=os.path.join(os.path.dirname(__file__), 'data'),
    oem=tesserocr.OEM.LSTM_ONLY,
    psm=tesserocr.PSM.SINGLE_LINE
)

# noinspection PyArgumentList
tesseract_futura = tesserocr.PyTessBaseAPI(
    path=os.path.join(os.path.dirname(__file__), 'data'),
    lang='Futura',
    oem=tesserocr.OEM.TESSERACT_ONLY,
    psm=tesserocr.PSM.SINGLE_LINE
)


def tesser_ocr(
        image: np.ndarray,
        whitelist=string.printable,
        invert=False, scale=1,
        blur: float=None,
        debug=False,
        engine=tesseract_only,
        get_confidence=False) -> str:
    engine.SetVariable('tessedit_char_whitelist', whitelist)
    if invert:
        image = 255 - image
    if scale != 1:
        image = cv2.resize(image, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    if blur:
        image = cv2.GaussianBlur(image, (0, 0), blur)

    if debug:
        cv2.imshow('tesser_ocr', image)
        cv2.waitKey(0)

    if len(image.shape) == 2:
        height, width = image.shape
        channels = 1
    else:
        height, width, channels = image.shape
    engine.SetImageBytes(image.tobytes(), width, height, channels, width * channels)
    s = engine.GetUTF8Text()
    if ' ' not in whitelist:
        s = s.replace(' ', '')
    if '\n' not in whitelist:
        s = s.replace('\n', '')

    if get_confidence:
        return s, float(engine.MeanTextConf()) / 100
    else:
        return s


def otsu_mask(image, dilate: Optional[int]=3):
    _, mask = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    if dilate:
        mask = cv2.erode(mask, np.ones((2, 2)))
        mask = cv2.dilate(mask, np.ones((dilate, dilate)))
    return cv2.bitwise_and(image, mask)


def unsharp_mask(image, unsharp: float, weight: float, threshold: int=None):
    unsharp = fast_gaussian(image, unsharp, scale=2)
    im = cv2.addWeighted(image, weight, unsharp, 1 - weight, 0)
    if threshold:
        if len(image.shape) == 3:
            gray = np.min(im, axis=2)
        else:
            gray = im
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        return thresh
    else:
        return im


def tesser_ocr_all(images: List[np.ndarray], **kwargs) -> List[str]:
    return [
        tesser_ocr(image, **kwargs) for image in images
    ]


def imread(path, mode=None):
    if mode is not None:
        im = cv2.imread(path, mode)
    else:
        im = cv2.imread(path)
    if im is None:
        if os.path.exists(path):
            raise ValueError(f'Unable to read {path} as an image')
        else:
            raise FileNotFoundError(path)
    else:
        return im


def findContours(image, mode, method, contours=None, hierarchy=None, offset=None):
    r = cv2.findContours(image, mode, method, contours=contours, hierarchy=hierarchy, offset=offset)
    if len(r) == 3:
        return r[1:]
    else:
        return r


if __name__ == '__main__':
    print(os.environ['PATH'])
    print(tesserocr.tesseract_version())

    ocr = tesserocr.PyTessBaseAPI(oem=tesserocr.OEM.LSTM_ONLY)

    gray = image = cv2.imread('C:\\tmp\\gray.png', 0)
    height, width = image.shape
    channels = 1

    ocr.SetImageBytes(image.tobytes(), width, height, channels, width * channels)
    print(ocr.GetUTF8Text())

    ocr.SetImageBytes((255 - image).tobytes(), width, height, channels, width * channels)
    print(ocr.GetUTF8Text())

    print('--')
    print(tesser_ocr(gray, whitelist=string.ascii_uppercase))
    print(tesser_ocr(gray, invert=True, whitelist=string.ascii_uppercase))

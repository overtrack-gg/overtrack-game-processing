from typing import List, Any, Callable, Optional, Tuple, Union, Sequence

import cv2
import numpy as np

from overtrack.overwatch.ocr import big_noodle
from overtrack.util import imageops


def manual_thresh(gray_image: np.ndarray, scale: float=3.) -> int:
    cv2.namedWindow('thresh')
    cv2.createTrackbar('t', 'thresh', 0, 255, lambda x: None)
    lastt = t = 0
    while True:
        _, thresh = cv2.threshold(gray_image, t, 255, cv2.THRESH_BINARY)
        cv2.imshow('thresh', cv2.resize(
            np.vstack((
                gray_image,
                thresh
            )),
            (0, 0),
            fx=scale,
            fy=scale
        ))
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
        t = cv2.getTrackbarPos('t', 'thresh')
        if t != lastt:
            print(t)
            lastt = t
    cv2.destroyAllWindows()
    return t


def manul_thresh_adaptive(gray_image: np.ndarray, scale: float = 3.) -> Tuple[int, int, int]:
    cv2.namedWindow('thresh')
    cv2.createTrackbar('method', 'thresh', 0, 1, lambda x: None)
    cv2.createTrackbar('block_size', 'thresh', 0, 100, lambda x: None)
    cv2.createTrackbar('c', 'thresh', 100, 200, lambda x: None)
    while True:
        method = [cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.ADAPTIVE_THRESH_MEAN_C][cv2.getTrackbarPos('method', 'thresh')]
        block_size = cv2.getTrackbarPos('block_size', 'thresh') * 2 + 3
        c = cv2.getTrackbarPos('c', 'thresh') - 100
        thresh = cv2.adaptiveThreshold(gray_image, 255, method, cv2.THRESH_BINARY, block_size, c)
        cv2.imshow('thresh', cv2.resize(
            np.vstack((
                gray_image,
                thresh
            )),
            (0, 0),
            fx=scale,
            fy=scale
        ))
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()
    print(['ADAPTIVE_THRESH_GAUSSIAN_C', 'ADAPTIVE_THRESH_MEAN_C'][cv2.getTrackbarPos('method', 'thresh')], block_size, c)
    return method, block_size, c


def manual_thresh_otsu(
        image: np.ndarray,
        template: np.ndarray=None,
        scale: float=3.,
        stack: Callable[[Sequence[np.ndarray]], np.ndarray]=np.vstack,
        grayop: Callable[..., Union[np.ndarray, float]]=np.min) -> None:
    if len(image.shape) == 3:
        gray_image = grayop(image, axis=2)
    else:
        gray_image = image
    cv2.namedWindow('thresh otsu')
    cv2.createTrackbar('thresh', 'thresh otsu', 0, 255, lambda x: None)

    def set_by_mn_mx(*args: Any) -> None:
        mn = cv2.getTrackbarPos('mn', 'thresh otsu')
        mx = cv2.getTrackbarPos('mx', 'thresh otsu')
        tval = imageops.otsu_thresh(
            gray_image,
            mn,
            mx
        )
        cv2.setTrackbarPos('thresh', 'thresh otsu', int(tval))

    cv2.createTrackbar('mn', 'thresh otsu', 0, 255, set_by_mn_mx)
    cv2.createTrackbar('mx', 'thresh otsu', 255, 255, set_by_mn_mx)

    fraction_max = 3

    def set_by_fraction(val: int) -> None:
        fraction = val / 100
        otsu_lb = int(np.mean(image) * fraction)
        cv2.setTrackbarPos('mn', 'thresh otsu', otsu_lb)
        set_by_mn_mx()

    cv2.createTrackbar('fraction', 'thresh otsu', 100, (fraction_max * 100), set_by_fraction)
    set_by_fraction(100)

    old = 0
    while True:
        t = cv2.getTrackbarPos('thresh', 'thresh otsu')

        _, thresh = cv2.threshold(gray_image, t, 255, cv2.THRESH_BINARY)
        if t != old:
            old = t
            if template is not None:
                print(np.min(cv2.matchTemplate(thresh, template, cv2.TM_SQDIFF_NORMED)))
        cv2.imshow('thresh otsu', cv2.resize(
            stack((
                gray_image,
                thresh,
                cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            )),
            (0, 0),
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_NEAREST
        ))
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()


def manual_unsharp_mask(image: np.ndarray, scale: float=2, callback: Optional[Callable[[np.ndarray], None]]=None) -> Tuple[float, float, float]:
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    updated = [True]

    def update(_: int) -> None:
        updated[0] = True

    cv2.namedWindow('unsharp')
    cv2.createTrackbar('size', 'unsharp', 40, 100, update)
    cv2.createTrackbar('weight', 'unsharp', 40, 500, update)
    cv2.createTrackbar('threshold', 'unsharp', 240, 255, update)
    while True:
        size = max(1, cv2.getTrackbarPos('size', 'unsharp') / 10)
        weight = cv2.getTrackbarPos('weight', 'unsharp') / 10
        threshold = cv2.getTrackbarPos('threshold', 'unsharp')

        unsharp = imageops.fast_gaussian(image, size, scale=1)
        im = cv2.addWeighted(image, weight, unsharp, 1 - weight, 0)
        gray = np.min(im, axis=2)
        _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        cv2.imshow('unsharp', cv2.resize(
            np.hstack((
                image,
                cv2.cvtColor(np.min(image, axis=2), cv2.COLOR_GRAY2BGR),
                unsharp,
                im,
                cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
                cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR),
            )),
            (0, 0),
            fx=scale,
            fy=scale
        ))
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

        if updated[0]:
            if callback:
                callback(thresh)

            updated[0] = False

    cv2.destroyAllWindows()
    print(size, weight, threshold)
    return size, weight, threshold


def show_ocr_segmentations(names: List[np.ndarray], **kwargs: Any) -> None:
    cv2.imshow('names', np.vstack(names))
    segmented_names = []
    for im in names:
        segments = big_noodle.segment(big_noodle.to_gray(im, channel='max'), **kwargs)
        segmented_name = np.hstack(cv2.copyMakeBorder(s, 0, 0, 0, 3, cv2.BORDER_CONSTANT, value=128) for s in segments)
        segmented_name = cv2.copyMakeBorder(segmented_name, 0, 5, 0, (names[0].shape[1] + 200) - segmented_name.shape[1], cv2.BORDER_CONSTANT, value=128)
        segmented_names.append(segmented_name)
    cv2.imshow('segments', np.vstack(segmented_names))
    cv2.waitKey(0)


def tesser_ocr(im: np.ndarray, vscale: float = 3, **kwargs) -> None:
    def update(_: int) -> None:
        scale = max(1, cv2.getTrackbarPos('scale', 'ocr'))
        blur = max(1, cv2.getTrackbarPos('blur', 'ocr') / 10)
        invert = cv2.getTrackbarPos('invert', 'ocr')

        text = imageops.tesser_ocr(
            im,
            scale=scale,
            blur=blur,
            invert=bool(invert),

            **kwargs
        )
        print(text)

    cv2.namedWindow('ocr')
    cv2.createTrackbar('scale', 'ocr', 4, 10, update)
    cv2.createTrackbar('blur', 'ocr', 10, 100, update)
    cv2.createTrackbar('invert', 'ocr', 0, 1, update)
    while True:
        cv2.imshow('ocr', cv2.resize(
            im,
            (0, 0),
            fx=vscale,
            fy=vscale
        ))
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()

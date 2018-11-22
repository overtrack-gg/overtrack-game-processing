from typing import List

import cv2
import numpy as np

from overtrack.ocr import big_noodle
from overtrack.util import imageops


def manual_thresh(gray_image: np.ndarray) -> int:
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
            fx=3,
            fy=3
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


def manual_thresh_otsu(image: np.ndarray, template=None, scale=3., stack=np.vstack, grayop=np.min) -> None:
    if len(image.shape) == 3:
        gray_image = grayop(image, axis=2)
    else:
        gray_image = image
    cv2.namedWindow('thresh otsu')
    cv2.createTrackbar('thresh', 'thresh otsu', 0, 255, lambda x: None)

    def set_by_mn_mx(*args):
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

    FRACTION_MAX = 3

    def set_by_fraction(val):
        fraction = val / 100
        otsu_lb = int(np.mean(image) * fraction)
        cv2.setTrackbarPos('mn', 'thresh otsu', otsu_lb)
        set_by_mn_mx()

    cv2.createTrackbar('fraction', 'thresh otsu', 100, (FRACTION_MAX * 100), set_by_fraction)
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


def show_ocr_segmentations(names: List[np.ndarray], **kwargs) -> None:
    cv2.imshow('names', np.vstack(names))
    segmented_names = []
    for im in names:
        segments = big_noodle.segment(big_noodle.to_gray(im, channel='max'), **kwargs)
        segmented_name = np.hstack(cv2.copyMakeBorder(s, 0, 0, 0, 3, cv2.BORDER_CONSTANT, value=128) for s in segments)
        segmented_name = cv2.copyMakeBorder(segmented_name, 0, 5, 0, (names[0].shape[1] + 200) - segmented_name.shape[1], cv2.BORDER_CONSTANT, value=128)
        segmented_names.append(segmented_name)
    cv2.imshow('segments', np.vstack(segmented_names))
    cv2.waitKey(0)

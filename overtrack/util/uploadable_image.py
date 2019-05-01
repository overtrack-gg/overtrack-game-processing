import logging
from collections import deque
from typing import Dict, TYPE_CHECKING, List

from dataclasses import dataclass

if TYPE_CHECKING:
    import numpy as np

MAXLEN = 15

active_images: Dict[str, 'UploadableImage'] = {}
logger = logging.getLogger('Image')


def lazy_upload(key: str, image: 'np.ndarray', timestamp: float, maxlen: int = MAXLEN) -> 'UploadableImage':
    if key not in active_images:
        active_images[key] = UploadableImage(key, maxlen)

    active_images[key].append(image, timestamp)
    return active_images[key]


class UploadableImage:

    def __init__(self, key: str, maxlen: int):
        self.key = key
        self.images = deque(maxlen=maxlen)
        self.url = None
        logger.info(f'Created {self}')

    def append(self, image: 'np.ndarray', timestamp: float) -> None:
        logger.info(f'{self}: Adding image @ {timestamp:.1f}')
        self.images.append((timestamp, image))

    def make_single(self) -> 'np.ndarray':
        # import numpy as np
        # return np.mean([i for t, i in self.images], axis=0).astype(np.uint8)
        return [i for t, i in self.images][len(self.images) // 2]

    @property
    def timestamps(self) -> List[int]:
        return [t for t, i in self.images]

    @property
    def count(self) -> int:
        return len(self.images)

    def __del__(self):
        logger.info(f'Disposing of {self}')

    def __str__(self) -> str:
        if self.url is None:
            ustr = ', uploaded=False'
        else:
            ustr = f', url={self.url}'
        return f'Image(key={self.key}{ustr}, count={len(self.images)})'

    __repr__ = __str__

    def _typeddump(self) -> Dict:
        if self.url is None:
            logger.warning(f'Dumping image {self} before it is uploaded')
            logger.error('Dumping image before it has an upload URL')
        return {
            'key': self.key,
            'url': self.url,
            'timestamps': self.timestamps
        }


@dataclass
class UploadedImage:
    key: str
    url: str
    timestamps: List[float]

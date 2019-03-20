import logging
from typing import List, Tuple, Dict, Optional

import cv2
import zipfile
import numpy as np

logger = logging.getLogger(__name__)


class ExtractionRegions:

    def __init__(self, name: str, image: np.ndarray):
        self.name = name
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                # use alpha channel
                image = image[:, :, 3]
            else:
                # use any non-zero pixel (across all color channels)
                _, image = cv2.threshold(np.max(image, axis=2), 1, 255, cv2.THRESH_BINARY)
        else:
            # use any non-zero pixel
            image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)

        self.regions: List[Tuple[int, int, int, int]] = []

        r, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=4)
        for x, y, w, h, a in stats[1:]:
            if w * h != a:
                logger.warning(f'ExtractionRegions { name } got non-rectangular region {w}*{h}!={a}')
            self.regions.append((x, y, w, h))

        # sort regions by y, x
        self.regions = sorted(self.regions, key=lambda e: (e[1], e[0]))

    def extract(self, image: np.ndarray) -> List[np.ndarray]:
        image_regions = []
        for x, y, w, h in self.regions:
            if y >= image.shape[0]:
                logger.error(f'ExtractionRegions { self.name } unable to extract region at y={y} from image with height={image.shape[0]}')
                image_region = np.zeros((h, y), np.uint8)
            elif x >= image.shape[1]:
                logger.error(f'ExtractionRegions { self.name } unable to extract region at y={y} from image with height={image.shape[0]}')
                image_region = np.zeros((h, y), np.uint8)
            else:
                image_region = image[
                    y:y + h,
                    x:x + w
                ]
            if image_region.shape[:2] != (h, w):
                logger.warning(
                    f'ExtractionRegions { self.name } got region of size { image_region.shape[:2] } from extraction region with h={h}, w={w} - padding image'
                )
                image_region = cv2.copyMakeBorder(image_region, 0, 0, w - image_region.shape[1], h - image_region.shape[0], cv2.BORDER_CONSTANT, value=0)
            image_regions.append(image_region)
        return image_regions

    def extract_one(self, image: np.ndarray) -> np.ndarray:
        return self.extract(image)[0]

    def draw(self, image: np.ndarray) -> None:
        for i, (x, y, w, h) in enumerate(self.regions):
            cv2.rectangle(
                image,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                1
            )
            for t, c in (3, (0, 0, 0)), (1, (0, 255, 0)):
                cv2.putText(
                    image,
                    f'{self.name}[{i}]',
                    (x + 5, y - 7),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    c,
                    t
                )

    def __str__(self) -> str:
        return f'{ self.__class__.__name__ }(name="{ self.name }", { len(self.regions) } regions)'

    __repr__ = __str__


class ExtractionRegionsCollection:

    def __init__(self, path: str):
        self.regions: Dict[str, ExtractionRegions] = {}
        with zipfile.ZipFile(path) as z:
            for f in z.namelist():
                if not f.startswith('L') or not f.endswith('.png'):
                    # not a layer
                    continue
                layer_props = f.rsplit('.', 1)[0].split(',')
                layer_name = layer_props[3].replace('%002E', '.')
                if not layer_name.startswith('region.'):
                    continue
                region_name = layer_name[len('region.'):]
                with z.open(f, 'r') as fobj:
                    logger.debug('Loading region %s from %s', region_name, path)
                    layer = cv2.imdecode(np.frombuffer(fobj.read(), dtype=np.uint8), -1)
                    self.regions[region_name] = ExtractionRegions(region_name, layer)

    def __getitem__(self, key: str) -> ExtractionRegions:
        if key not in self.regions:
            raise KeyError(f'region {key} was not in regions: {self.regions.keys()}')
        return self.regions[key]

    def __str__(self) -> str:
        return f'{ self.__class__.__name__ }(regions={ self.regions } regions)'

    def draw(self, image: Optional[np.ndarray]) -> None:
        if image is None:
            return
        for region in self.regions.values():
            region.draw(image)


if __name__ == '__main__':
    print(ExtractionRegionsCollection('../game/tab/data/regions/16_9.zip'))

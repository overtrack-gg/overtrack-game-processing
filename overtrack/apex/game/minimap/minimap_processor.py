from functools import lru_cache

import requests
import time
import logging
import os
from collections import deque
from typing import Optional, Tuple

import cv2
import numpy as np
from tensorflow.python.keras import Model
from tensorflow.python.keras.saving import load_from_saved_model

from scipy import optimize
from overtrack.apex import ocr
from overtrack.apex.game.minimap.models import Circle, Location, Minimap
from overtrack.frame import Frame
from overtrack.processor import Processor
from overtrack.util import imageops, time_processing
from overtrack.util.custom_layers import custom_objects
from overtrack.util.logging_config import config_logger
from overtrack.util.region_extraction import ExtractionRegionsCollection

logger = logging.getLogger('MinimapProcessor')

def _draw_map_location(
    debug_image: Optional[np.ndarray],
    minimap: Minimap,

    map_image: np.ndarray,
    map_template: np.ndarray,
    filtered: np.ndarray,
    edges: Optional[np.ndarray],
) -> None:

    if debug_image is None:
        return

    lines = [f'location={minimap.location}']

    out = cv2.cvtColor(map_image[:-200, :-200], cv2.COLOR_GRAY2BGR)
    overlay = np.zeros_like(out)
    cv2.circle(
        out,
        minimap.location.coordinates,
        6,
        (0, 255, 255),
        4,
        cv2.LINE_AA
    )

    if edges is not None and minimap.inner_circle:
        for im in out, overlay:
            cv2.circle(
                im,
                (int(minimap.inner_circle.coordinates[0]), int(minimap.inner_circle.coordinates[1])),
                int(minimap.inner_circle.r),
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )
            cv2.circle(
                im,
                (int(minimap.inner_circle.coordinates[0]), int(minimap.inner_circle.coordinates[1])),
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )
        lines.append(f'inner={minimap.inner_circle}')

    if edges is not None and minimap.outer_circle:
        for im in out, overlay:
            cv2.circle(
                im,
                (int(minimap.outer_circle.coordinates[0]), int(minimap.outer_circle.coordinates[1])),
                int(minimap.outer_circle.r),
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )
            cv2.circle(
                im,
                (int(minimap.outer_circle.coordinates[0]), int(minimap.outer_circle.coordinates[1])),
                1,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )
        lines.append(f'outer={minimap.outer_circle}')

    debug_image[500:500 + filtered.shape[0], 300:300 + filtered.shape[1]] = filtered
    if edges is not None:
        debug_image[500:500 + edges.shape[0], 550:550 + edges.shape[1]] = edges.astype(np.uint8) * 255
    debug_image[500:500 + filtered.shape[0], 800:800 + filtered.shape[1]] = cv2.cvtColor(filtered[:, :, 0], cv2.COLOR_GRAY2BGR)
    # debug_image[500:500 + filtered.shape[0], 1050:1050 + filtered.shape[1]] = cv2.cvtColor(map_template[
    #     minimap.location.coordinates[1] - 240 // 2 + 8:
    #     minimap.location.coordinates[1] + 240 // 2 - 8,
    #     minimap.location.coordinates[0] - 240 // 2 + 8:
    #     minimap.location.coordinates[0] + 240 // 2 - 8
    # ], cv2.COLOR_GRAY2BGR)

    if minimap.location.bearing is None:
        # draw synthetic minimap. This should match the actual minimap, if it doesn't then something is wrong in the parsing
        debug_image[400:400 + 240, 50:50 + 240] = out[
            minimap.location.coordinates[1] - 240 // 2:minimap.location.coordinates[1] + 240 // 2,
            minimap.location.coordinates[0] - 240 // 2:minimap.location.coordinates[0] + 240 // 2
        ]
        debug_image[500:500 + filtered.shape[0], 1050:1050 + filtered.shape[1]] = cv2.cvtColor(map_template[
            minimap.location.coordinates[1] - filtered.shape[0] // 2:
            minimap.location.coordinates[1] + filtered.shape[0] // 2,
            minimap.location.coordinates[0] - filtered.shape[1] // 2:
            minimap.location.coordinates[0] + filtered.shape[1] // 2
        ], cv2.COLOR_GRAY2BGR)

        # draw the circle overlay on top of the actual minimap
        if minimap.location.zoom == 1:
            cv2.addWeighted(
                debug_image[
                    50:50 + 240,
                    50:50 + 240
                ],
                1,
                overlay[
                    minimap.location.coordinates[1] - 240 // 2:minimap.location.coordinates[1] + 240 // 2,
                    minimap.location.coordinates[0] - 240 // 2:minimap.location.coordinates[0] + 240 // 2
                ],
                0.25,
                0,
                dst=debug_image[
                    50:50 + 240,
                    50:50 + 240
                ]
            )

        # draw the minimap rectangle on the full map
        cv2.rectangle(
            out,
            (minimap.location.coordinates[0] - int(240 * minimap.location.zoom) // 2, minimap.location.coordinates[1] - int(240 * minimap.location.zoom) // 2),
            (minimap.location.coordinates[0] + int(240 * minimap.location.zoom) // 2, minimap.location.coordinates[1] + int(240 * minimap.location.zoom) // 2),
            (0, 255, 255),
            4
        )
    else:
        # rotate the map so we can draw the synthetic minimap with matching rotation
        height, width, _ = out.shape
        rot = cv2.getRotationMatrix2D(
            minimap.location.coordinates,
            minimap.location.bearing - 360,
            1
        )
        rout = cv2.warpAffine(
            out,
            rot,
            (width, height)
        )
        rout = cv2.resize(rout, (0, 0), fx=1/minimap.location.zoom, fy=1/minimap.location.zoom)
        debug_image[400:400 + 240, 50:50 + 240] = rout[
            int(minimap.location.coordinates[1] / minimap.location.zoom) - 240 // 2:
            int(minimap.location.coordinates[1] / minimap.location.zoom) + 240 // 2,
            int(minimap.location.coordinates[0] / minimap.location.zoom) - 240 // 2:
            int(minimap.location.coordinates[0] / minimap.location.zoom) + 240 // 2
        ]

        # draw the expected template next to the actual filtered output
        trout = cv2.warpAffine(
            map_template,
            rot,
            (width, height)
        )
        trout = cv2.resize(trout, (0, 0), fx=1 / minimap.location.zoom, fy=1 / minimap.location.zoom)
        debug_image[500:500 + filtered.shape[0], 1050:1050 + filtered.shape[1]] = cv2.cvtColor(
            trout[
                int(minimap.location.coordinates[1] / minimap.location.zoom) - 240 // 2 + 8:
                int(minimap.location.coordinates[1] / minimap.location.zoom) + 240 // 2 - 8,
                int(minimap.location.coordinates[0] / minimap.location.zoom) - 240 // 2 + 8:
                int(minimap.location.coordinates[0] / minimap.location.zoom) + 240 // 2 - 8
            ],
            cv2.COLOR_GRAY2BGR
        )

        # rotate then draw the circles on top of the actual minimap
        roverlay = cv2.warpAffine(
            overlay,
            rot,
            (width, height)
        )
        roverlay = cv2.resize(roverlay, (0, 0), fx=1 / minimap.location.zoom, fy=1 / minimap.location.zoom)
        cv2.addWeighted(
            debug_image[
                50:50 + 240,
                50:50 + 240
            ],
            1,
            roverlay[
                int(minimap.location.coordinates[1] / minimap.location.zoom) - 240 // 2:
                int(minimap.location.coordinates[1] / minimap.location.zoom) + 240 // 2,
                int(minimap.location.coordinates[0] / minimap.location.zoom) - 240 // 2:
                int(minimap.location.coordinates[0] / minimap.location.zoom) + 240 // 2
            ],
            0.25,
            0,
            dst=debug_image[
                50:50 + 240,
                50:50 + 240
            ]
        )

        # work out the corners of the minimap, and draw these on the full map
        tl = (minimap.location.coordinates[0] - (240 * minimap.location.zoom) // 2, minimap.location.coordinates[1] - (240 * minimap.location.zoom) // 2)
        tr = (minimap.location.coordinates[0] + (240 * minimap.location.zoom) // 2, minimap.location.coordinates[1] - (240 * minimap.location.zoom) // 2)
        bl = (minimap.location.coordinates[0] - (240 * minimap.location.zoom) // 2, minimap.location.coordinates[1] + (240 * minimap.location.zoom) // 2)
        br = (minimap.location.coordinates[0] + (240 * minimap.location.zoom) // 2, minimap.location.coordinates[1] + (240 * minimap.location.zoom) // 2)
        cv2.polylines(
            out,
            cv2.transform(
                np.array([[tl, tr, br, bl]]),
                rot
            ).astype(np.int32),
            True,
            (0, 255, 255),
            4,
        )

    sout = cv2.resize(out, (0, 0), fx=0.25, fy=0.25)
    debug_image[100:100 + sout.shape[0], 300:300 + sout.shape[1]] = sout

    for i, line in enumerate(lines):
        cv2.putText(
            debug_image,
            line,
            (730, 250 + 50 * i),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 0),
            3
        )
        cv2.putText(
            debug_image,
            line,
            (730, 250 + 50 * i),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            1
        )

template_blur_pre = 1.0
template_canny_t1 = 30
template_canny_t2 = 100
template_blur_post = 2.0


class MinimapProcessor(Processor):
    REGIONS = ExtractionRegionsCollection(os.path.join(os.path.dirname(__file__), '..', 'data', 'regions', '16_9.zip'))
    SPECTATE = imageops.imread(os.path.join(os.path.dirname(__file__), 'data', 'spectate.png'), 0)
    THRESHOLD = 0.3

    @classmethod
    def load_map(cls, path: str):
        cls.MAP = cv2.copyMakeBorder(imageops.imread(path, 0), 0, 240, 0, 240, cv2.BORDER_CONSTANT)
        cls.MAP_TEMPLATE = cv2.GaussianBlur(cls.MAP, (0, 0), 1.1).astype(np.float)
        cls.MAP_TEMPLATE *= 2
        cls.MAP_TEMPLATE = np.clip(cls.MAP_TEMPLATE, 0, 255).astype(np.uint8)

    MAP_VERSION = 0

    def __init__(self):
        self.map_rotated = deque(maxlen=10)
        self.map_rotate_in_config = None  # TODO
        self.model: Model = load_from_saved_model(
            os.path.join(os.path.dirname(__file__), 'data', 'minimap_filter'),
            # "C:/Users/simon/overtrack_2/training/apex_minimap/v3/inprog_models/v12_14_with_mini",
            custom_objects=custom_objects
        )
        # from tensorflow.python.keras.saving import export_saved_model
        # export_saved_model(self.model, os.path.join(os.path.dirname(__file__), 'data', 'minimap_filter'), serving_only=True)

    def eager_load(self):
        self.REGIONS.eager_load()
        self._check_for_rotate_setting()
        self._check_for_map_update()

    def _check_for_rotate_setting(self):
        try:
            from client.util import knownpaths
            games_path = knownpaths.get_path(knownpaths.FOLDERID.SavedGames, knownpaths.UserHandle.current)
            config_path = os.path.join(games_path, 'Respawn', 'Apex', 'profile', 'profile.cfg')
            value = None
            with open(config_path) as f:
                for line in f.readlines():
                    if line.startswith('hud_setting_minimapRotate'):
                        value = line.split()[1].strip().replace('"', '')
            if value:
                pvalue = value.lower() in ['1', 'true']
                logger.info(f'Extracted hud_setting_minimapRotate: "{value}" from {config_path} - setting rotate to {pvalue}')
                self.map_rotate_in_config = pvalue
            else:
                logger.info(f'Could not find hud_setting_minimapRotate in {config_path} - setting rotate to autodetect')
                self.map_rotate_in_config = None

        except:
            logger.exception(f'Failed to read hud_setting_minimapRotate from profile - setting rotate to autodetect')
            self.map_rotate_in_config = None

    def _check_for_map_update(self):
        logger.info('Checking for map updates')
        try:
            r = requests.get('https://overtrack-client-2.s3-us-west-2.amazonaws.com/dynamic/apex-map/current.json')
            logger.info(f'Checking for map update: {r} "{r.content}"')
            if r.status_code == 404:
                logger.info('Map updates not enabled')
                return

            data = r.json()
            if data['version'] <= self.MAP_VERSION:
                logger.info(f'Current version {self.MAP_VERSION} is up to date - update version is {data["version"]}')
                return
            else:
                maps_path = os.path.join(os.path.join(os.path.dirname(__file__), 'data', 'maps'))
                os.makedirs(maps_path, exist_ok=True)

                map_path = os.path.join(maps_path, f'{data["version"]}.png')
                if os.path.exists(map_path):
                    try:
                        self.__class__.load_map(map_path)
                    except:
                        logger.info('Map corrupted')
                        os.remove(map_path)
                    else:
                        logger.info(f'Loaded map {data["version"]} from {map_path}')
                        return

                logger.info(f'Downloading map {data["version"]} from {data["url"]} to {map_path}')
                with requests.get(data['url'], stream=True) as r:
                    r.raise_for_status()
                    with open(map_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                self.__class__.load_map(map_path)

        except:
            logger.exception('Failed to check for map update')

    def update(self):
        self._check_for_rotate_setting()
        self._check_for_map_update()

    @time_processing
    def process(self, frame: Frame):
        spectate_image = frame.image_yuv[40:40+30, 670:670+130, 0]
        _, spectate_image_t = cv2.threshold(spectate_image, 220, 255, cv2.THRESH_BINARY)
        is_spectate = np.max(cv2.matchTemplate(spectate_image_t, self.SPECTATE, cv2.TM_CCORR_NORMED)) > 0.9

        if not is_spectate:
            map_image = frame.image[50:50 + 240, 50:50 + 240]
        else:
            map_image = frame.image[114:114 + 240, 50:50 + 240]

        t0 = time.perf_counter()
        filtered = np.clip(self.model.predict([[map_image]], 1)[0], 0, 255).astype(np.uint8)
        logger.debug(f'predict {(time.perf_counter() - t0) * 1000:.2f}')

        # location, min_loc, min_val = self._get_location(filtered[:, :, 0])
        location = None
        zoom = self._get_zoom(frame)

        t0 = time.perf_counter()
        if self.map_rotate_in_config or (len(self.map_rotated) and (sum(self.map_rotated) / len(self.map_rotated)) > 0.75):
            # 75% of last 10 frames said map was rotated - check rotated first
            logger.debug(f'Checking rotated first')
            bearing = self._get_bearing(frame, frame.debug_image)
            if bearing is not None:
                location = self._get_location(filtered[:, :, 0], bearing, zoom=zoom)
                logger.debug(f'Got rotated location={location}')
            if (location is None or location.match > self.THRESHOLD) and self.map_rotate_in_config is None:
                # try unrotated
                alt_location = self._get_location(filtered[:, :, 0], zoom=zoom)
                logger.debug(f'Got unrotated location={alt_location}')
                if location is None or alt_location.match < location.match:
                    location = alt_location
        else:
            logger.debug(f'Checking unrotated first')
            location = self._get_location(filtered[:, :, 0], zoom=zoom)
            logger.debug(f'Got unrotated location={location}')
            if location.match > self.THRESHOLD and self.map_rotate_in_config is None:
                bearing = self._get_bearing(frame, frame.debug_image)
                if bearing is not None:
                    alt_location = self._get_location(filtered[:, :, 0], bearing, zoom=zoom)
                    logger.debug(f'Got rotated location={alt_location}')
                    if alt_location.match < location.match:
                        location = alt_location
        logger.debug(f'match {(time.perf_counter() - t0) * 1000:.2f}')

        logger.debug(f'Got location: {location}')
        if location and location.match < self.THRESHOLD:
            self.map_rotated.append(location.bearing is not None)

            # from overtrack.util.debugops import sliders
            # filtered[:, :, 0] = 0
            # sliders(
            #     filtered,
            #     blur=lambda im, b_0_100: cv2.GaussianBlur(im, (0, 0), b_0_100 / 10) if b_0_100 else im,
            #     mul=lambda im, m_10_100: np.clip(im.astype(np.float) * (m_10_100 / 10), 0, 255).astype(np.uint8),
            #     filter_edge=lambda im, t_0_255, p_1_70, e_1_30, k_1_30: self.filter_edge(im, t_0_255, p_1_70, e_1_30, k_1_30)
            # )

            t0 = time.perf_counter()
            blur = cv2.GaussianBlur(filtered, (0, 0), 4)

            blur[:, :, 0] = 0
            edges = self.filter_edge(blur, 50, 20, 20, 10)
            edges[:5, :] = 0
            edges[-5:, :] = 0
            edges[:, :5] = 0
            edges[:, -5:] = 0
            logger.debug(f'filter edges {(time.perf_counter() - t0) * 1000:.2f}')

            t0 = time.perf_counter()
            frame.minimap = Minimap(
                location,
                self._get_circle(edges[:, :, 1], location),
                self._get_circle(edges[:, :, 2], location),
                spectate=is_spectate,
                version=1,
            )
            logger.debug(f'get circles {(time.perf_counter() - t0) * 1000:.2f}')

            try:
                _draw_map_location(
                    frame.debug_image,
                    frame.minimap,

                    self.MAP,
                    self.MAP_TEMPLATE,
                    filtered,
                    edges
                )
            except:
                logger.exception('Failed to draw debug map location')

            return True
        elif location:
            try:
                _draw_map_location(
                    frame.debug_image,
                    Minimap(
                        location,
                        None,
                        None,
                    ),

                    self.MAP,
                    self.MAP_TEMPLATE,
                    filtered,
                    None
                )
            except Exception as e:
                print(e)
        return False

    def _get_zoom(self, frame):
        zoom = 1
        if 'game_time' in frame:
            if frame.game_time > 1100:
                # round 5 closing / ring 6
                zoom = 0.375
            elif frame.game_time > 980:
                # round 4 closing / ring 5
                zoom = 0.75
        return zoom

    def _get_bearing(self, frame: Frame, debug_image: Optional[np.ndarray]) -> Optional[int]:
        bearing_image = self.REGIONS['bearing'].extract_one(frame.image_yuv[:, :, 0])
        _, bearing_thresh = cv2.threshold(bearing_image, 190, 255, cv2.THRESH_BINARY)

        if debug_image is not None:
            debug_image[
                90:90 + bearing_image.shape[0],
                1020:1020 + bearing_image.shape[1],
            ] = cv2.cvtColor(bearing_image, cv2.COLOR_GRAY2BGR)
            debug_image[
                90:90 + bearing_image.shape[0],
                1100:1100 + bearing_image.shape[1],
            ] = cv2.cvtColor(bearing_thresh, cv2.COLOR_GRAY2BGR)

        bearing = imageops.tesser_ocr(
            bearing_thresh,
            expected_type=int,
            engine=ocr.tesseract_ttlakes_digits,
            warn_on_fail=False
        )
        if bearing is None or not 0 <= bearing <= 360:
            logger.debug(f'Got invalid bearing: {bearing}')
            return None
        if bearing is not None:
            logger.debug(f'Got bearing={bearing}')
            return bearing
        else:
            return None

    def _get_location(self, region: np.ndarray, bearing: Optional[int] = None, zoom: Optional[float] = None) -> Location:
        rot = None
        if bearing is None:
            map_template = self.MAP_TEMPLATE
        else:
            height, width = self.MAP_TEMPLATE.shape
            rot = cv2.getRotationMatrix2D(
                (self.MAP_TEMPLATE.shape[1] // 2, self.MAP_TEMPLATE.shape[0] // 2),
                bearing - 360,
                1
            )
            map_template = cv2.warpAffine(
                self.MAP_TEMPLATE,
                rot,
                (width, height)
            )

        if zoom and zoom != 1:
            region = cv2.resize(
                region,
                (0, 0),
                fx=zoom,
                fy=zoom
            )

        match = cv2.matchTemplate(
            map_template,
            region,
            cv2.TM_SQDIFF_NORMED
        )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)

        # import matplotlib.pyplot as plt
        # plt.figure()
        # plt.imshow(region, interpolation='none')
        # plt.figure()
        # plt.imshow(map_template, interpolation='none')
        # plt.figure()
        # plt.imshow(match, interpolation='none')
        # plt.show()

        coords = min_loc[0] + int(240 * zoom) // 2 - 8, min_loc[1] + int(240 * zoom) // 2 - 8
        if rot is not None:
            inv = cv2.invertAffineTransform(rot)
            coords = tuple(cv2.transform(np.array([[coords]]), inv)[0][0])

        return Location(
            coords,
            min_val,
            bearing=bearing,
            zoom=zoom
        )

    def filter_edge(self, im: np.ndarray, thresh: int, edge_type_box_size: int, edge_type_widening: int, edge_extraction_size: int) -> np.ndarray:
        thresh = im > thresh

        x_edge_prominent = cv2.boxFilter(im, 0, (2, edge_type_box_size), normalize=True)
        y_edge_prominent = cv2.boxFilter(im, 0, (edge_type_box_size, 2), normalize=True)
        greater = (x_edge_prominent > y_edge_prominent).astype(np.uint8)
        greater = cv2.dilate(greater, np.ones((1, edge_type_widening)))
        greater = cv2.erode(greater, np.ones((edge_type_widening, 1)))

        w_edge = thresh & (cv2.dilate(im, np.ones((1, edge_extraction_size))) == im)
        h_edge = thresh & (cv2.dilate(im, np.ones((edge_extraction_size, 1))) == im)

        # cv2.imshow('x_edge_prominent', x_edge_prominent)
        # cv2.imshow('y_edge_prominent', y_edge_prominent)
        # cv2.imshow('greater', greater * 255)
        # cv2.imshow('w_edge', w_edge.astype(np.uint8) * 255)
        # cv2.imshow('h_edge', h_edge.astype(np.uint8) * 255)

        edge = (w_edge * greater) + (h_edge * (1 - greater))
        return edge

    def _get_circle(self, filt: np.ndarray, location: Location) -> Optional[Circle]:
        y_i, x_i = np.nonzero(filt)
        if len(y_i) > 10:
            def calc_R(x, y, xc, yc):
                """
                calculate the distance of each 2D points from the center (xc, yc)
                """
                return np.sqrt((x - xc) ** 2 + (y - yc) ** 2)
            def f(c, x, y):
                """
                calculate the algebraic distance between the data points
                and the mean circle centered at c=(xc, yc)
                """
                Ri = calc_R(x, y, *c)
                error = Ri - Ri.mean()
                return error

            x_m = np.mean(x_i)
            y_m = np.mean(y_i)
            center_estimate = x_m, y_m
            result = optimize.least_squares(
                f,
                center_estimate,
                args=(x_i, y_i),
                # loss='soft_l1',
            )
            center = result.x
            x, y = center
            r_i = calc_R(x_i, y_i, x, y)
            r = r_i.mean()
            residu = np.sum((r_i - r) ** 2)

            minimap_center_relative = (x - (240 // 2 - 8)), y - (240 // 2 - 8)
            if location.bearing is not None:
                rot = cv2.getRotationMatrix2D(
                    (0, 0),
                    360 - location.bearing,
                    1
                )
                minimap_center_relative = tuple(cv2.transform(np.array([[minimap_center_relative]]), rot)[0][0])

            return Circle(
                (location.coordinates[0] + minimap_center_relative[0] * location.zoom, location.coordinates[1] + minimap_center_relative[1] * location.zoom),
                r * location.zoom,
                residu,
                len(y_i),
                )

        return None


def main() -> None:
    import glob
    import random

    config_logger('map_processor', logging.DEBUG, write_to_file=False)

    # find_best_match()
    # exit(0)

    pipeline = MinimapProcessor()
    paths = glob.glob('d:/overtrack/frames_rot/*.json')[1630:]

    # random.shuffle(paths)

    # paths = ['D:/overtrack/frames_rot/1569668416.76_image.png']
    # paths = [
    #    r'd:/overtrack/frames_rot\1569669144.44_frame.json'
    #     r'd:/overtrack/frames_rot\1569670312.41_image.png'
    # ]

    for p in paths:
        print(p)
        imp = p.replace('frame.json', 'image.png')
        try:
            frame = Frame.create(
                cv2.resize(cv2.imread(imp), (1920, 1080)),
                float(os.path.basename(p).split('_')[0]),
                True,
                file=imp
            )
        except:
            logging.exception('')
            continue
        frame.game_time = frame.timestamp - 1569665630

        pipeline.process(frame)
        print(frame)
        cv2.imshow('debug', frame.debug_image)

        cv2.waitKey(0)


MinimapProcessor.load_map(os.path.join(os.path.dirname(__file__), 'data', '2.png'))
MinimapProcessor.MAP_VERSION = 2


if __name__ == '__main__':
    # main()
    from overtrack import util

    p = MinimapProcessor()

    # p.map_rotate_in_config = True
    # p._check_for_rotate_setting = lambda: None
    # p._get_zoom = lambda frame: 0.375
    # util.test_processor(
    #     "D:/overtrack/worlds_edge/video_frames/SEASON 3 IS HERE LETS GOOO - SPONSORED STREAM #AD-v488890432/20178.34.image.png",
    #     p,
    #     'minimap',
    #     game='apex',
    #     test_all=False
    # )

    # p.MAP = cv2.copyMakeBorder(imageops.imread("C:/Users/simon/overtrack_2/apex_map/target.png", 0), 0, 240, 0, 240, cv2.BORDER_CONSTANT)
    # p.MAP_TEMPLATE = cv2.GaussianBlur(
    #     cv2.Canny(
    #         cv2.GaussianBlur(
    #             p.MAP,
    #             (0, 0),
    #             template_blur_pre
    #         ),
    #         template_canny_t1,
    #         template_canny_t2
    #     ),
    #     (0, 0),
    #     template_blur_post
    # ).astype(np.float)
    # p.MAP_TEMPLATE /= 100
    # p.MAP_TEMPLATE *= 255
    # p.MAP_TEMPLATE = np.clip(p.MAP_TEMPLATE, 0, 255).astype(np.uint8)
    util.test_processor('minimap_s3', p, 'minimap', game='apex')

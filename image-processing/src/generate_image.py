from supervision.detection.utils import polygon_to_mask
import cv2
import numpy as np
import random
from shapely.geometry import Point, Polygon


import MagicScissorsApp


def copy_paste(
    source_image: np.ndarray,
    source_polygon: np.ndarray,
    target_image: np.ndarray,
    scale: float = 1.0,
    x: int = 0,
    y: int = 0,
) -> np.ndarray:
    """
    Copy and paste a region from a source image into a target image.
    Attributes:
        source_image (np.ndarray): The image to be copied.
        source_polygon (np.ndarray): The polygon area to be copied.
        target_image (np.ndarray): The image to be pasted into.
        scale: scale factor to apply to the source image
        x: x offset to paste into the target image at
        y: y offset to paste into the target image at
    Returns:
        np.ndarray: The target image with the source image pasted into it.
    """

    # generate mask image based on polygon
    source_height, source_width = source_image.shape[0:2]
    mask = polygon_to_mask(source_polygon, (source_width, source_height))

    #if the source is going to be bigger than the target, then we need to scale it down so it will fit
    if source_width > target_image.shape[1] or source_height > target_image.shape[0]:
        scale = min(target_image.shape[1] / source_width, target_image.shape[0] / source_height)
        # print("scaling source image down to fit", scale)

    # scale the source and mask
    scaled_source = cv2.resize(source_image, None, fx=scale, fy=scale)
    scaled_mask = cv2.resize(mask, None, fx=scale, fy=scale)
    scaled_height, scaled_width = scaled_source.shape[0:2]

    _mask = np.expand_dims(scaled_mask, axis=2)

    _patch_bg = target_image[y : y + scaled_height, x : x + scaled_width, :]

    # print("patch shapes:", _mask.shape, scaled_source.shape, _patch_bg.shape)

    # generate a patch from the source image  / with background from target image where we are pasting
    patch = np.where(_mask, scaled_source, _patch_bg)

    # paste the patch area into the output image
    target_image[y : y + scaled_height, x : x + scaled_width, :] = patch

    return target_image


def random_point_in_background(bg, max_x, max_y):
    polygon = Polygon(bg.polygon)
    minx, miny, maxx, maxy = polygon.bounds
    # print("polygon bounds", minx, miny, maxx, maxy)

    maxx = min(maxx, max_x)
    maxy = min(maxy, max_y)

    # print("target max x, y", max_x, max_y)
    # print("picked max x, y", maxx, maxy)
    attempt = 0
    # print("get random point in background", maxx, maxy)
    while True:
        pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if polygon.contains(pnt):
            # print("found random point", pnt, pnt.x, pnt.y)
            return [pnt.x, pnt.y]
        else:
            attempt += 1
        if attempt > 100:
            # print("failed to find random point in background", minx, miny, maxx, maxy, max_x, max_y)
            return [None, None]

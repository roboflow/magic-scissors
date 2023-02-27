from supervision.detection.utils import generate_2d_mask
import cv2
import numpy as np

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
    source_width, source_height = source_image.shape[0:2]
    mask = generate_2d_mask(source_polygon, (source_width, source_height))

    # scale the source and mask
    scaled_source = cv2.resize(source_image, None, fx=scale, fy=scale)
    scaled_mask = cv2.resize(mask, None, fx=scale, fy=scale)
    scaled_width, scaled_height = scaled_source.shape[0:2]

    # generate a patch from the source image  / with background from target image where we are pasting
    patch = np.where(
        np.expand_dims(scaled_mask, axis=2),
        scaled_source,
        target_image[y : y + scaled_height, x : x + scaled_width, :],
    )

    # paste the patch area into the output image
    target_image[y : y + scaled_height, x : x + scaled_width, :] = patch

    return target_image


def generate_image(bg, objects):

    print("generate image with background", bg.filename)

    background_image = cv2.imread(bg.filename)

    for obj in objects:
        obj_image = cv2.imread(obj.filename)
        obj_annotation = obj.get_annotation_data()

        polygon = obj_annotation["polygon"]
        print("pasting object", obj.filename)
        result = copy_paste(obj_image, polygon, background_image)
        cv2.imshow("output", result)
        cv2.waitKey(0)

    return MagicScissorsApp.GeneratedImage(bg, objects)


if __name__ == "__main__":

    bg_src = "/Users/hansent/Desktop/ms_temp/backgrounds/train/images/cart1_png.rf.522660df56f449c4b3fa55909808ac6c.jpg"
    bg_label = "/Users/hansent/Desktop/ms_temp/backgrounds/train/images/cart1_png.rf.522660df56f449c4b3fa55909808ac6c.txt"

    bg = MagicScissorsApp.Background(bg_src)

    objects = [
        MagicScissorsApp.ObjectOfInterest(
            "/Users/hansent/Desktop/ms_temp/objects_of_interest/train/images/IMG_1191_rotated90_jpg.rf.3a2caf871efdbfaa37d3eb98334caa65.jpg"
        ),
        MagicScissorsApp.ObjectOfInterest(
            "/Users/hansent/Desktop/ms_temp/objects_of_interest/train/images/IMG_1754_rotated90_jpg.rf.6c029f2d09b9e0b4cc38393d2ab943c4.jpg"
        ),
    ]

    generate_image(bg, objects)
    cv2.destroyAllWindows()

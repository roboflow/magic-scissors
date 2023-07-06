import datetime
import json
import os
import random
import traceback

import cv2
import numpy as np
import roboflow
import tqdm
import glob
from shapely.geometry import MultiPolygon, Polygon

from . import generate_image


class ObjectOfInterest:
    def __init__(self, filename, polygon, classname, split):
        self.filename = filename
        self.polygon = polygon
        self.classname = classname
        self.split = split


class Background:
    def __init__(self, filename, polygon, classname, split):
        self.filename = filename
        self.polygon = polygon
        self.classname = classname
        self.split = split


class GeneratedImage:
    def __init__(
        self,
        identifier,
        background,
        object_of_interests,
        scale_min,
        scale_max,
        annotate_occlusion=False,
    ):
        self.identifier = identifier
        self.background = background
        self.object_of_interests = object_of_interests

        self.annotate_occlusion = annotate_occlusion

        self.image_data = None
        self.annotations = []

        background_image = cv2.imread(self.background.filename)

        for obj in self.object_of_interests:
            obj_image = cv2.imread(obj.filename)

            polygon = obj.polygon

            scale = random.uniform(scale_min, scale_max)

            while True:
                max_y = background_image.shape[0] - (obj_image.shape[0] * scale)
                max_x = background_image.shape[1] - (obj_image.shape[1] * scale)

                x, y = generate_image.random_point_in_background(
                    self.background, max_x, max_y
                )

                if max_y < 0 or max_x < 0 or x == None or y == None:
                    scale = scale / 2
                else:
                    break

            if len(polygon) == 0:
                continue

            self.image_data = generate_image.copy_paste(
                obj_image, polygon, background_image, scale, int(x), int(y)
            )

            new_polygon = []
            for p in obj.polygon:
                new_x = (p[0] * scale) + int(x)
                new_y = (p[1] * scale) + int(y)
                new_polygon.append([new_x, new_y])

            self.annotations.append(
                {"polygon": new_polygon, "classname": obj.classname}
            )

    def to_coco_json(self):
        categories = []
        category_counter = 0
        category_by_name = {}
        for a in self.annotations:
            c = {
                "id": category_counter,
                "name": a["classname"],
                "supercategory": "none",
            }
            category_counter += 1

            category_by_name[a["classname"]] = c
            categories.append(c)

        annotations = []
        annotation_counter = 0
        # annotation and index
        for i, a in enumerate(self.annotations):
            polygon = Polygon(a["polygon"])

            # if we're not allowing occlusion to be part of the annotation
            # we need to iterate over all the other annotations on top of
            # this one (after it in the list of annotations) and subtract
            # their area from the current annotation
            if not self.annotate_occlusion:
                for j in range(i + 1, len(self.annotations)):
                    other_polygon = Polygon(self.annotations[j]["polygon"])
                    polygon = polygon.difference(other_polygon)

            minx, miny, maxx, maxy = polygon.bounds

            if isinstance(polygon, Polygon):
                flattened_polygons = [
                    item for sublist in polygon.exterior.coords for item in sublist
                ]
            elif isinstance(polygon, MultiPolygon):
                flattened_polygons = []
                for p in polygon.geoms:
                    flattened_polygons.extend(
                        [item for sublist in p.exterior.coords for item in sublist]
                    )
            else:
                raise ValueError("Unsupported geometry type")

            a = {
                "id": annotation_counter,
                "image_id": 0,
                "category_id": category_by_name[a["classname"]]["id"],
                "bbox": [minx, miny, maxx, maxy],
                "area": 0,
                "segmentation": flattened_polygons,
                "iscrowd": 0,
            }
            annotation_counter += 1
            annotations.append(a)

        return {
            "categories": categories,
            "images": [
                {
                    "id": 0,
                    "license": 1,
                    "file_name": self.identifier + ".jpg",
                    "height": self.image_data.shape[0],
                    "width": self.image_data.shape[1],
                }
            ],
            "annotations": annotations,
        }


class MagicScissors:
    """
    Generate synthetic data using background data and objects of interest.

    Attributes:
        working_dir (str): The directory to store the downloaded data and generated images.
        dataset_size (int): The number of images to generate.
        min_objects_per_image (int): The minimum number of objects to paste into each image.
        max_objects_per_image (int): The maximum number of objects to paste into each image.
        min_size_variance (int): The minimum amount of variance to apply to the size of the objects of interest.
        max_size_variance (int): The maximum amount of variance to apply to the size of the objects of interest.
        annotate_occlusion (bool): Whether or not to annotate occlusion in the generated images.
        upload_to_roboflow (bool): Whether or not to upload the generated images to Roboflow.
        roboflow_api_key (str): The Roboflow API key to use when uploading to Roboflow.
        roboflow_workspace (str): The Roboflow workspace to use when uploading to Roboflow.
        roboflow_project (str): The Roboflow project to use when uploading to Roboflow.
    """

    def __init__(
        self,
        working_dir,
        dataset_size=0,
        min_objects_per_image=0,
        max_objects_per_image=0,
        min_size_variance=0,
        max_size_variance=0,
        annotate_occlusion=0,
        upload_to_roboflow=False,
        roboflow_api_key="",
        roboflow_workspace="",
        roboflow_project="",
    ):
        # these will get populated with the objects of interest and backgrounds
        # after we download the respective versions holding the image and annotation data
        # for them
        self.objects_of_interest = []
        self.backgrounds = []
        self.generated_images = []

        if upload_to_roboflow and (
            not roboflow_api_key or not roboflow_workspace or not roboflow_project
        ):
            raise ValueError(
                "You must provide a Roboflow API key, workspace, and project to upload to Roboflow"
            )

        self.dataset_size = dataset_size
        self.min_objects_per_image = min_objects_per_image
        self.max_objects_per_image = max_objects_per_image
        self.min_size_variance = min_size_variance
        self.max_size_variance = max_size_variance
        self.annotate_occlusion = annotate_occlusion
        self.upload_to_roboflow = upload_to_roboflow
        self.roboflow_api_key = roboflow_api_key
        self.roboflow_workspace = roboflow_workspace
        self.roboflow_project = roboflow_project

        self.working_dir = working_dir

        if self.upload_to_roboflow:
            self._rf = roboflow.Roboflow(api_key=roboflow_api_key)

    def download_objects_of_interest_from_roboflow(self, url: str):
        """
        Download objects of interest for image generation from Roboflow.

        Attributes:
            url (str): The Roboflow URL to download the objects of interest from.
        """
        location = self.working_dir + "/objects_of_interest"

        # download dataset
        if not os.path.exists(location):
            v = roboflow.download_dataset(url, model_format="coco", location=location)

        # add all the images as objects of interest
        train_objects = self.load_objects_of_interest_from_coco("train", False)
        test_objects = self.load_objects_of_interest_from_coco("test", False)
        valid_objects = self.load_objects_of_interest_from_coco("valid", False)

        self.objects_of_interest.extend(train_objects)
        self.objects_of_interest.extend(test_objects)
        self.objects_of_interest.extend(valid_objects)

    def download_backgrounds_from_roboflow(self, url: str):
        """
        Download backgrounds for image generation from Roboflow.

        Attributes:
            url (str): The Roboflow URL to download the backgrounds from.
        """
        location = self.working_dir + "/backgrounds"

        # download dataset
        if not os.path.exists(location):
            v = roboflow.download_dataset(url, model_format="coco", location=location)

        # add test images as objects of interest
        self.backgrounds = self.load_backgrounds_from_coco("train", False)

    def load_backgrounds_from_coco(self, split, manual=True):
        """
        Load background data from a COCO JSON file.

        Attributes:
            split (str): The split to load the background data from.
            manual (bool): Whether or not to manually set the backgrounds attribute in self. Don't set this value to True unless extending the MagicScissors object.

        Returns:
            list: A list of Background objects.
        """
        folder = self.working_dir + "/backgrounds/" + split
        try:
            json_file = open(folder + "/_annotations.coco.json")
            annotation_data = json.load(json_file)
        except:
            return []

        images = annotation_data["images"]
        annotations = annotation_data["annotations"]
        categories = annotation_data["categories"]

        backgrounds = []

        for img in images:
            image_id = img["id"]
            filename = folder + "/" + img["file_name"]
            annotation = next(
                (a for a in annotations if a["image_id"] == image_id), None
            )
            if not annotation:
                continue

            classname = categories[annotation["category_id"]]["name"]
            segmentation = annotation["segmentation"]
            if len(segmentation) == 0:
                # convert bbox to polygon ([x,y,w,h] -> [[x,y,x+w,y,x+w,y+h,x,y+h]])
                bbox = annotation["bbox"]
                segmentation = [
                    [
                        bbox[0],
                        bbox[1],
                        bbox[0] + bbox[2],
                        bbox[1],
                        bbox[0] + bbox[2],
                        bbox[1] + bbox[3],
                        bbox[0],
                        bbox[1] + bbox[3],
                    ]
                ]

            polygon = np.array(segmentation).astype(np.int32).reshape(-1, 2)

            obj = Background(filename, polygon, classname, split)
            backgrounds.append(obj)

        if manual:
            self.backgrounds = backgrounds

        return backgrounds

    def load_objects_of_interest_from_coco(self, split, manual=True):
        """
        Load object data from a COCO JSON file.

        Attributes:
            split (str): The split to load the object data from.
            manual (bool): Whether or not to manually set the objects_of_interest attribute in self. Don't set this value to True unless extending the MagicScissors object.

        Returns:
            list: A list of ObjectOfInterest objects.
        """
        folder = self.working_dir + "/objects_of_interest/" + split
        try:
            json_file = open(folder + "/_annotations.coco.json")
            annotation_data = json.load(json_file)
        except:
            return []

        images = annotation_data["images"]
        annotations = annotation_data["annotations"]
        categories = annotation_data["categories"]

        objects = []

        for img in images:
            image_id = img["id"]
            filename = folder + "/" + img["file_name"]
            annotation = next(
                (a for a in annotations if a["image_id"] == image_id), None
            )
            if not annotation:
                continue

            classname = categories[annotation["category_id"]]["name"]
            segmentation = annotation["segmentation"]
            if len(segmentation) == 0:
                # convert bbox to polygon ([x,y,w,h] -> [[x,y,x+w,y,x+w,y+h,x,y+h]])
                bbox = annotation["bbox"]
                segmentation = [
                    [
                        bbox[0],
                        bbox[1],
                        bbox[0] + bbox[2],
                        bbox[1],
                        bbox[0] + bbox[2],
                        bbox[1] + bbox[3],
                        bbox[0],
                        bbox[1] + bbox[3],
                    ]
                ]
            polygon = np.array(segmentation).astype(np.int32).reshape(-1, 2)

            obj = ObjectOfInterest(filename, polygon, classname, split)
            objects.append(obj)

        if manual:
            self.objects_of_interest = objects

        return objects

    def generate_dataset(self):
        folder = self.working_dir + "/output"

        if not os.path.exists(folder):
            os.mkdir(folder)

        if self.upload_to_roboflow:
            destination_project = self._rf.workspace(self.roboflow_workspace).project(self.roboflow_project)

        batch_name = "magic_scissors_" + datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M"
        )

        if os.path.exists(folder + "/" + batch_name):
            files = glob.glob(folder + "/" + batch_name + "/*")
            for f in files:
                os.remove(f)

            os.rmdir(folder + "/" + batch_name)

        os.mkdir(folder + "/" + batch_name)

        images_generated = 0
        i = 0

        with tqdm.tqdm(total=self.dataset_size * 2) as pbar:
            while (images_generated < self.dataset_size) and (
                i < self.dataset_size * 2
            ):
                i = i + 1
                pbar.update(1)
                num_objects = random.randint(
                    self.min_objects_per_image, self.max_objects_per_image
                )

                background = random.choice(self.backgrounds)
                objects = random.choices(self.objects_of_interest, k=num_objects)

                generated_image = GeneratedImage(
                    str(i),
                    background,
                    objects,
                    self.min_size_variance,
                    self.max_size_variance,
                    self.annotate_occlusion,
                )

                base_name = folder + "/" + batch_name + "/" + str(i) + ".jpeg"

                if generated_image.image_data is None:
                    continue

                cv2.imwrite(
                    base_name + ".jpg",
                    generated_image.image_data,
                )

                with open(base_name + ".json", "w") as f:
                    json.dump(generated_image.to_coco_json(), f)

                kwargs = {
                    "image_path": base_name + ".jpg",
                    "annotation_path": base_name + ".json",
                    "batch_name": batch_name,
                    "tag_names": [batch_name],
                }

                if self.upload_to_roboflow:
                    print("uploading file", base_name)
                    try:
                        destination_project.upload(**kwargs)
                        images_generated = images_generated + 1
                    except:
                        print(
                            "failed to upload file, continuing to the next though: ",
                            base_name,
                            str(traceback.format_exc()),
                        )
                        if os.path.exists(base_name + ".json"):
                            with open(base_name + ".json", "r") as f:
                                print(f.read())
        if i > self.dataset_size * 2:
            print(
                "Failed to generate enough images, only generated ",
                images_generated,
                " images",
            )
        return batch_name

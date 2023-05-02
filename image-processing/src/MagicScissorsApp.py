import glob
import random
import roboflow
from roboflow import Roboflow
import numpy as np
import json
import generate_image
import cv2
import os
from shapely.geometry import Point, Polygon, MultiPolygon
import datetime
from pathlib import Path
import traceback

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
        self, identifier, background, object_of_interests, scale_min, scale_max, annotate_occlusion=False
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
            print("pasting object", obj.filename)
            scale = random.uniform(scale_min, scale_max)

            max_y = background_image.shape[0] - (obj_image.shape[0] * scale)
            max_x = background_image.shape[1] - (obj_image.shape[1] * scale)

            x, y = generate_image.random_point_in_background(
                self.background, max_x, max_y
            )
            # print("copy paste:", polygon, scale, x, y)
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
        #annotation and index
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
                flattened_polygons = [item for sublist in polygon.exterior.coords for item in sublist]
            elif isinstance(polygon, MultiPolygon):
                flattened_polygons = []
                for p in polygon.geoms:
                    flattened_polygons.extend([item for sublist in p.exterior.coords for item in sublist])
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


class MagicScissorsApp:
    def __init__(self, request_parameters, working_dir):

        # these will get populated with the objects of interest and backgrounds
        # after we download the respective versions holding the image and annotation data
        # for them
        self.objects_of_interest = []
        self.backgrounds = []
        self.generated_images = []

        try:
            self.api_key = request_parameters["apiKey"]

            # version references/url to grab items from
            self.objects_of_interest_url = request_parameters["objectsOfInterest"]

            # version references/url to grab background images from
            self.backgrounds_version_url = request_parameters["backgrounds"]

            # dataset url for dataset to add images to
            self.destination_dataset_url = request_parameters["destination"]

            # generation settings
            request_settings = request_parameters["settings"]
            self.dataset_size = request_settings["datasetSize"]
            self.min_objects_per_image = request_settings["objectsPerImage"]["min"]
            self.max_objects_per_image = request_settings["objectsPerImage"]["max"]
            self.min_size_variance = request_settings["sizeVariance"]["min"]
            self.max_size_variance = request_settings["sizeVariance"]["max"]
            self.annotate_occlusion = request_settings.get("annotateOcclusion", False)
        except Exception as e:
            print("Error parsing request parameters", e)
            raise Exception(
                "failed to initialize MagicScissorsApp from request parameters"
            )

        self.working_dir = working_dir

        self._rf = Roboflow(api_key=self.api_key)

        print("MAGIC SCISSORS app initialized:")
        print("  working directory:", self.working_dir)
        print("  settings:")
        print("    api_key", self.api_key)
        print("    objects_of_interest_url:", self.objects_of_interest_url)
        print("    backgrounds_version_url:", self.backgrounds_version_url)
        print("    destination_dataset_url:", self.destination_dataset_url)
        print("    dataset_size:", self.dataset_size)
        print("    min_objects_per_image:", self.min_objects_per_image)
        print("    max_objects_per_image:", self.max_objects_per_image)
        print("    min_size_variance:", self.min_size_variance)
        print("    max_size_variance:", self.max_size_variance)

    def download_objects_of_interest(self):
        workspace, project, version = self.objects_of_interest_url.split("/")
        location = self.working_dir + "/objects_of_interest"

        # download dataset
        v = self._rf.workspace(workspace).project(project).version(int(version))
        v.download("coco", location=location)

        # add all the images as objects of interest
        train_objects = self.load_objects_of_interest_from_coco("train")
        test_objects = self.load_objects_of_interest_from_coco("test")
        valid_objects = self.load_objects_of_interest_from_coco("valid")

        self.objects_of_interest.extend(train_objects)
        self.objects_of_interest.extend(test_objects)
        self.objects_of_interest.extend(valid_objects)

    def download_backgrounds(self):
        workspace, project, version = self.backgrounds_version_url.split("/")
        location = self.working_dir + "/backgrounds"

        # rf = Roboflow(api_key=self.api_key)
        v = self._rf.workspace(workspace).project(project).version(int(version))
        v.download("coco", location=location)

        # add test images as objects of interest
        self.backgrounds = self.load_backgrounds_from_coco("train")

    def load_backgrounds_from_coco(self, split):
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
                # print("no annotation for image:", image_id, filename)
                continue

            classname = categories[annotation["category_id"]]["name"]
            segmentation = annotation["segmentation"]
            if(len(segmentation) == 0):
                # convert bbox to polygon ([x,y,w,h] -> [[x,y,x+w,y,x+w,y+h,x,y+h]])
                bbox = annotation["bbox"]
                segmentation = [[
                    bbox[0],
                    bbox[1],
                    bbox[0] + bbox[2],
                    bbox[1],
                    bbox[0] + bbox[2],
                    bbox[1] + bbox[3],
                    bbox[0],
                    bbox[1] + bbox[3],
                ]]


            polygon = np.array(segmentation).astype(np.int32).reshape(-1, 2)

            obj = Background(filename, polygon, classname, split)
            # print("adding object of interest", filename, polygon, classname)
            backgrounds.append(obj)

        return backgrounds

    def load_objects_of_interest_from_coco(self, split):
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
                # print("no annotation for image:", image_id, filename)
                continue

            classname = categories[annotation["category_id"]]["name"]
            segmentation = annotation["segmentation"]
            polygon = np.array(segmentation).astype(np.int32).reshape(-1, 2)

            obj = ObjectOfInterest(filename, polygon, classname, split)
            # print("adding object of interest", filename, polygon, classname)
            objects.append(obj)

        return objects

    def generate_dataset(self):
        print("generating dataset")

        folder = self.working_dir + "/output"

        if not os.path.exists(folder):
            os.mkdir(folder)

        workspace, project = self.destination_dataset_url.split("/")
        destination_project = self._rf.workspace(workspace).project(project)

        batch_name = "magic_scissors_" + datetime.datetime.now().strftime(
            "%Y-%m-%d_%H-%M"
        )

        # for i in range(0, 1):
        print("generating", self.dataset_size, "images")
        images_generated = 0
        i = 0
        while (images_generated < self.dataset_size) and (i < self.dataset_size * 2):
            i = i+1
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
                self.annotate_occlusion
            )

            print("write output file:", generated_image.identifier)

            base_name = folder + "/" + generated_image.identifier

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

            print("uploading file", base_name)
            try:
                destination_project.upload(**kwargs)
                images_generated = images_generated+1
            except:
                print("failed to upload file, continuing to the next though: ", base_name, str(traceback.format_exc()))
                if os.path.exists(base_name + ".json"):
                    print("Printing annotation file contents:")
                    with open(base_name + ".json", "r") as f:
                        print(f.read())
        if i > self.dataset_size * 2:
            print("Failed to generate enough images, only generated ", images_generated, " images")
        return batch_name


if __name__ == "__main__":
    request_data = {
        "apiKey": roboflow.load_roboflow_api_key(),
        # "objectsOfInterest": "magic-scissors/grocery-items-hrmxb/8",
        # "backgrounds": "magic-scissors/shopping-carts/3",
        # "destination": "magic-scissors/synthetic-images",
        "objectsOfInterest": "cv-roasts/source-images/2",
        "backgrounds": "cv-roasts/backgrounds-yoqbe/2",
        "destination": "cv-roasts/coffee-cups-roboflow-livestream",
        "settings": {
            "datasetSize": 10,
            "objectsPerImage": {"min": 1, "max": 1},
            "sizeVariance": {"min": 0.4, "max": 0.5},
            # "annotateOcclusion": False
        }
    }

    working_dir = f"{Path.home()}/Desktop/ms_temp"

    magic_scissors = MagicScissorsApp(request_data, working_dir)
    magic_scissors.download_objects_of_interest()
    magic_scissors.download_backgrounds()
    tag_name = magic_scissors.generate_dataset()
    # tag_name = magic_scissors.upload_dataset_to_destination()
    print("done, tagged as:", tag_name)

import glob
import random
from roboflow import Roboflow
import numpy as np
import json
import generate_image


class ObjectOfInterest:
    def __init__(self, filename, polygon, classname, split):
        self.filename = filename
        self.fpolygon = polygon
        self.classname = classname
        self.split = split


class Background:
    def __init__(self, filename, polygon, classname, split):
        self.filename = filename
        self.polygon = polygon
        self.classname = classname
        self.split = split


class GeneratedImage:
    def __init__(self, background, object_of_interests):
        self.background = background
        self.object_of_interests = object_of_interests


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
        except Exception as e:
            print("Error parsing request parameters", e)
            raise Exception(
                "failed to initialize MagicScissorsApp from request parameters"
            )

        self.working_dir = working_dir

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

        rf = Roboflow(api_key=self.api_key)
        v = rf.workspace(workspace).project(project).version(int(version))

        # TODO: want to download coco here, but the call fails because it cant find a yamp file
        v.download("coco", location=location)

        # add all the images as objects of interest
        train_objects = self.load_objects_of_interest_from_coco("train")
        test_objects = self.load_objects_of_interest_from_coco("test")
        valid_objects = self.load_objects_of_interest_from_coco("valid")

        self.objects_of_interest.extend(train_objects)
        self.objects_of_interest.extend(test_objects)
        self.objects_of_interest.extend(valid_objects)

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

    def download_backgrounds(self):
        workspace, project, version = self.backgrounds_version_url.split("/")

        location = self.working_dir + "/backgrounds"

        rf = Roboflow(api_key=self.api_key)
        v = rf.workspace(workspace).project(project).version(int(version))

        # TODO: want to download coco here, but the call fails because it cant find a yamp file
        v.download("coco", location=location)

        # add all the images as objects of interest
        # TODO: depending on dataset format and wehter to tonclude all splits, need to do multiple paths / glob patterns
        train_backgrounds = self.load_backgrounds_from_coco("train")
        test_backgrounds = self.load_backgrounds_from_coco("test")
        valid_backgrounds = self.load_backgrounds_from_coco("valid")

        self.backgrounds.extend(train_backgrounds)
        self.backgrounds.extend(test_backgrounds)
        self.backgrounds.extend(valid_backgrounds)

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
            polygon = np.array(segmentation).astype(np.int32).reshape(-1, 2)

            obj = Background(filename, polygon, classname, split)
            # print("adding object of interest", filename, polygon, classname)
            backgrounds.append(obj)

        return backgrounds

    def generate_dataset(self):
        print("generating dataset")

        for i in range(0, self.dataset_size):
            num_objects = random.randint(
                self.min_objects_per_image, self.max_objects_per_image
            )

            background = random.choice(self.backgrounds)
            objects = random.choices(self.objects_of_interest, k=num_objects)

            generated_image = generate_image.generate_image(background, objects)
            self.generated_images.append(generated_image)

    def upload_dataset_to_destination(self):
        print("uploading dataset to destination")
        for generated_image in self.generated_images:
            print("  upload image...")


if __name__ == "__main__":

    import os

    request_data = {
        "apiKey": os.environ["API_KEY"],
        "objectsOfInterest": "magic-scissors/grocery-items-hrmxb/1",
        "backgrounds": "magic-scissors/shopping-carts/1",
        "destination": "magic-scissors/synthetic-data",
        "settings": {
            "datasetSize": 250,
            "objectsPerImage": {"min": 1, "max": 5},
            "sizeVariance": {"min": 0.9, "max": 1.1},
        },
    }

    working_dir = "/Users/hansent/Desktop/ms_temp"

    magic_scissors = MagicScissorsApp(request_data, working_dir)
    magic_scissors.download_objects_of_interest()
    magic_scissors.download_backgrounds()
    # magic_scissors.generate_dataset()
    # magic_scissors.upload_dataset_to_destination()

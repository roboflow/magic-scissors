import tempfile
from roboflow import Roboflow


class MagicScissorsApp:

    def __init__(self, request_parameters, working_dir):
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
                "failed to initialize MagicScissorsApp from request parameters")

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
        v.download("yolov5pytorch", location=location)

    def download_backgrounds(self):
        workspace, project, version = self.backgrounds_version_url.split("/")

        location = self.working_dir + "/backgrounds"

        rf = Roboflow(api_key=self.api_key)
        v = rf.workspace(workspace).project(project).version(int(version))
        v.download("yolov5pytorch", location=location)


if __name__ == "__main__":

    request_data = {
        "apiKey": "xRLqUXrImvWxPeqD5WFg",
        "objectsOfInterest": "magic-scissors/grocery-items-hrmxb/1",
        "backgrounds": "magic-scissors/shopping-carts/1",
        "destination": "magic-scissors/synthetic-data",
        "settings": {
            "datasetSize": 250,
            "objectsPerImage": {
                "min": 1,
                "max": 5
            },
            "sizeVariance": {
                "min": 0.9,
                "max": 1.1
            }
        }
    }

    working_dir = "/Users/hansent/Desktop/ms_temp"

    magic_scissors = MagicScissorsApp(request_data, working_dir)
    magic_scissors.download_objects_of_interest()
    magic_scissors.download_backgrounds()
    # magic_scissors.generate_dataset()
    # magic_scissors.upload_dataset_to_destination()

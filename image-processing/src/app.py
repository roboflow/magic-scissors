from flask import Flask, request, jsonify
import roboflow
import os

app = Flask(__name__)


@app.route("/python/go", methods=["POST"])
def go():

    print("\n\n=====================")
    print("MAGIC SCISSORS starting request")
    # get request parameters
    api_key = request.json["apiKey"]

    # version references/url to grab items from
    objects_of_interest_url = request.json["objectsOfInterest"]

    # version references/url to grab background images from
    backgrounds_version_url = request.json["backgrounds"]

    # dataset url for dataset to add images to
    destination_dataset_url = request.json["destination"]

    # settings for generating images
    request_settings = request.json["settings"]
    dataset_size = request_settings["datasetSize"]
    min_objects_per_image = request_settings["objectsPerImage"]["min"]
    max_objects_per_image = request_settings["objectsPerImage"]["max"]
    min_size_variance = request_settings["sizeVariance"]["min"]
    max_size_variance = request_settings["sizeVariance"]["max"]

    print("using api_key", api_key)

    print("download objects of interest:", objects_of_interest_url)

    print("download backgrounds:", backgrounds_version_url)

    print("generate images")
    print("  destination_dataset_url:", destination_dataset_url)
    print("  dataset_size:", dataset_size)
    print("  min_objects_per_image:", min_objects_per_image)
    print("  max_objects_per_image:", max_objects_per_image)
    print("  min_size_variance:", min_size_variance)
    print("  max_size_variance:", max_size_variance)

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

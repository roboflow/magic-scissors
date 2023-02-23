from flask import Flask, request, jsonify
import tempfile
import os

from MagicScissorsApp import MagicScissorsApp

app = Flask(__name__)


@app.route("/python/go", methods=["POST"])
def go():

    print("=====================")
    print("MAGIC SCISSORS REQUEST STARTED")
    print("=====================")

    with tempfile.TemporaryDirectory() as tempdir:
        magic_scissors = MagicScissorsApp(request.json, tempdir)
        magic_scissors.download_objects_of_interest()
        magic_scissors.download_backgrounds()
        # magic_scissors.generate_dataset()
        # magic_scissors.upload_dataset_to_destination()

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

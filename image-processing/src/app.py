print("INIT MAGIC SCISSORS SERVICE")

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

    try:
        with tempfile.TemporaryDirectory() as tempdir:
            magic_scissors = MagicScissorsApp(request.json, tempdir)
            magic_scissors.download_objects_of_interest()
            magic_scissors.download_backgrounds()
            tag_name = magic_scissors.generate_dataset()
            # tag_name = magic_scissors.upload_dataset_to_destination()
        print("finished.  sending response")
        return jsonify({"success": True, "tag_name": tag_name})

    except Exception as e:
        print("caught an error.  sending error response")
        print("ERROR:", e)
        return jsonify({"success": False}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

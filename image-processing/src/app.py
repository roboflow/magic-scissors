from flask import Flask
import os

app = Flask(__name__)

@app.route("/python/go")
def go():
    return "Hello from Python!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
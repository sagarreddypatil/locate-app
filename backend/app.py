from flask import Flask, request

app = Flask(__name__)


@app.route("/input", methods=["POST"])
def process_input():
    blob = request.get_data()
    blob.save("wow.mp3")


@app.route("/")
def index():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
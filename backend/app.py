import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from random import randint

import speech_recognition as sr
from pydub import AudioSegment

from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)
CORS(app)


recognizer = sr.Recognizer()
sr.AudioFile("wow")


model = AutoModelForQuestionAnswering.from_pretrained(
    "distilbert-base-uncased-distilled-squad"
)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad")
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)


def extract_item_loc(sentence: str):
    item = qa_pipeline(question="What is the item?", context=sentence)["answer"]
    location = qa_pipeline(question=f"Where is {item}?", context=sentence)["answer"]

    return item.lower(), location.lower()


@app.route("/input", methods=["POST"])
def process_input():
    uid = randint(0, 99999)

    blob = request.get_data()
    with open(f"{uid}.mp3", "wb") as file:
        file.write(blob)

    mp3tc = AudioSegment.from_mp3(f"{uid}.mp3")
    mp3tc.export(f"{uid}.wav", format="wav")

    with sr.AudioFile(f"{uid}.wav") as source:
        audio = recognizer.record(source)
        input_trascription = recognizer.recognize_google(audio).lower()

    item, location = extract_item_loc(input_trascription)

    response = {}

    if input_trascription.split()[0].strip().lower() == "where":
        response = {
            "type": "retrieval",
            "transcription": input_trascription,
            "item": item,
        }
    else:
        response = {
            "type": "addition",
            "transcription": input_trascription,
            "item": item,
            "location": location,
        }

    os.remove(f"{uid}.wav")
    os.remove(f"{uid}.mp3")

    print(response)
    return jsonify(response)


@app.route("/")
def index():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
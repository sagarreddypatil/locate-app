import os

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from random import randint

import speech_recognition as sr
from pydub import AudioSegment

from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

from gtts import gTTS

from io import BytesIO

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)
CORS(app)


recognizer = sr.Recognizer()
sr.AudioFile("wow")


model = AutoModelForQuestionAnswering.from_pretrained(
    "distilbert-base-cased-distilled-squad"
)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
item_stopwords = ["my", "the", "a"]


def normalize_item(item: str):
    return " ".join(
        [word for word in item.split() if word.lower() not in item_stopwords]
    )


def extract_item_loc(sentence: str):
    item = qa_pipeline(question="What is the item?", context=sentence)["answer"]
    location = qa_pipeline(question=f"Where is {item}?", context=sentence)["answer"]

    return item.lower(), location.lower()


def do_tts(text: str, filename: str):
    voice = gTTS(text)
    voice.save(filename)


def text_is_question(text: str):
    query = text.lower()
    if (
        query.startswith("what")
        or query.startswith("where")
        or query.startswith("which")
        or query.startswith("why")
        or query.startswith("how")
    ):
        return True
    return False


@app.route("/input", methods=["POST"])
def process_input():
    uid = f"tmp-{randint(0, 999999)}"

    blob = request.get_data()
    with open(f"{uid}.mp3", "wb") as file:
        file.write(blob)

    mp3tc = AudioSegment.from_mp3(f"{uid}.mp3")
    mp3tc.export(f"{uid}.wav", format="wav")

    with sr.AudioFile(f"{uid}.wav") as source:
        audio = recognizer.record(source)
        input_trascription = recognizer.recognize_google(audio)

    item, location = extract_item_loc(input_trascription)
    item = normalize_item(item)

    response = {}

    if input_trascription.split()[0].strip().lower().startswith(
        "where"
    ) or text_is_question(location):
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


@app.route("/tts", methods=["POST"])
def tts():
    uid = f"tmp-send-{randint(0, 999999)}"

    content = request.json
    if content is None:
        return "Dude what the hell"

    text = content["text"]
    print(f"TTS Request: {text}")
    do_tts(text, f"{uid}.mp3")

    with open(f"{uid}.mp3", "rb") as file:
        mp3_file = file.read()

    os.remove(f"{uid}.mp3")

    return send_file(BytesIO(mp3_file), mimetype="audio/mpeg")


@app.route("/")
def index():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
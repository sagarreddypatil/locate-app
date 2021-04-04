import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from random import randint

import speech_recognition as sr
from pydub import AudioSegment

from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

import torch
import soundfile as sf
from univoc import Vocoder
from tacotron import load_cmudict, text_to_id, Tacotron

from cStringIO import StringIO

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
item_stopwords = ["my", "the", "a"]


def normalize_item(item: str):
    return " ".join(
        [word for word in item.split() if word.lower() not in item_stopwords]
    )


def extract_item_loc(sentence: str):
    item = qa_pipeline(question="What is the item?", context=sentence)["answer"]
    location = qa_pipeline(question=f"Where is {item}?", context=sentence)["answer"]

    return item.lower(), location.lower()


vocoder = Vocoder.from_pretrained(
    "https://github.com/bshall/UniversalVocoding/releases/download/v0.2/univoc-ljspeech-7mtpaq.pt"
).cuda()
tacotron = Tacotron.from_pretrained(
    "https://github.com/bshall/Tacotron/releases/download/v0.1/tacotron-ljspeech-yspjx3.pt"
).cuda()
cmudict = load_cmudict()


def do_tts(text: str):
    x = torch.LongTensor(text_to_id(text, cmudict)).unsqueeze(0).cuda()
    with torch.no_grad():
        mel, _ = tacotron.generate(x)
        wav, sr = vocoder.generate(mel.transpose(1, 2))

    return wav, sr


@app.route("/input", methods=["POST"])
def process_input():
    uid = f"tmp-{randint(0, 99999)}"

    blob = request.get_data()
    with open(f"{uid}.mp3", "wb") as file:
        file.write(blob)

    mp3tc = AudioSegment.from_mp3(f"{uid}.mp3")
    mp3tc.export(f"{uid}.wav", format="wav")

    with sr.AudioFile(f"{uid}.wav") as source:
        audio = recognizer.record(source)
        input_trascription = recognizer.recognize_google(audio).lower()

    item, location = extract_item_loc(input_trascription)
    item = normalize_item(item)

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


@app.route("/tts")
def tts():
    content = request.json["text"]
    wav, sr = do_tts(content)


@app.route("/")
def index():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
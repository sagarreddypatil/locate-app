import torch
import soundfile as sf
from univoc import Vocoder
from tacotron import load_cmudict, text_to_id, Tacotron

# download pretrained weights for the vocoder (and optionally move to GPU)
vocoder = Vocoder.from_pretrained(
    "https://github.com/bshall/UniversalVocoding/releases/download/v0.2/univoc-ljspeech-7mtpaq.pt"
).cuda()

# download pretrained weights for tacotron (and optionally move to GPU)
tacotron = Tacotron.from_pretrained(
    "https://github.com/bshall/Tacotron/releases/download/v0.1/tacotron-ljspeech-yspjx3.pt"
).cuda()

# load cmudict and add pronunciation of PyTorch
cmudict = load_cmudict()

text = "I am going to murder you in your sleep."

# convert text to phone ids
x = torch.LongTensor(text_to_id(text, cmudict)).unsqueeze(0).cuda()

# synthesize audio
with torch.no_grad():
    mel, _ = tacotron.generate(x)
    wav, sr = vocoder.generate(mel.transpose(1, 2))

# save output
sf.write("out.wav", wav, sr)

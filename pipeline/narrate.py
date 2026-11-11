#!/usr/bin/env python3
"""Record an episode's narration with the Kokoro open-source voice model and write the timeline that times the picture.
usage: narrate.py EPISODE.json     -> out/<id>/narr/voice.wav + timeline.json
Setup (per machine): pip install kokoro-onnx soundfile scipy ; download kokoro-v1.0.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 into ./tts/
Speakers: "N" is the narrator; any other code must be a key of the episode's "voices" map, e.g.
  "voices": {"D": "am_puck", "S": "bm_lewis", "G": "am_fenrir -3"}   (a trailing number is a pitch shift in semitones)"""
import sys, os, json, numpy as np, soundfile as sf
from scipy.signal import resample_poly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ep = json.load(open(sys.argv[1], encoding='utf-8')); out = os.path.join(ROOT, 'out', ep['id'], 'narr'); os.makedirs(out, exist_ok=True)
from kokoro_onnx import Kokoro
k = Kokoro(os.path.join(ROOT, 'tts', 'kokoro-v1.0.onnx'), os.path.join(ROOT, 'tts', 'voices-v1.0.bin'))
VOICES = {'N': 'bm_george'}; VOICES.update(ep.get('voices', {})); SPEED = {'N': 0.88}; SR = 48000
def say(sp, text):
    spec = VOICES[sp].split(); voice = spec[0]; semis = float(spec[1]) if len(spec) > 1 else 0.0
    tts = text.replace('LORD', 'Lord').replace('’', "'").replace('“', '"').replace('”', '"').replace('—', ': ')
    speed = SPEED.get(sp, 0.95) * (2 ** (-semis / 12.0) if semis else 1.0)      # pre-compensate the slowdown from pitching down
    s, sr = k.create(tts, voice=voice, speed=speed, lang='en-gb' if voice.startswith('b') else 'en-us'); s = np.asarray(s, np.float64)
    idx = np.where(np.abs(s) > 0.012 * np.max(np.abs(s)))[0]; s = s[max(idx[0] - int(0.02 * sr), 0):min(idx[-1] + int(0.10 * sr), len(s))]
    s = resample_poly(s, SR, sr)
    if semis: s = resample_poly(s, int(round(1000 * 2 ** (-semis / 12.0))), 1000)
    s *= 0.085 / np.sqrt(np.mean(s ** 2)); n = int(0.008 * SR); s[:n] *= np.linspace(0, 1, n); s[-n:] *= np.linspace(1, 0, n)
    return s
t = 1.0; track = []; beats = []
for b in ep['beats']:
    b0 = t; segs = []
    for j, sg in enumerate(b['segs']):
        s = say(sg['sp'], sg['text']); segs.append(dict(sp=sg['sp'], text=sg['text'], start=round(t, 2), end=round(t + len(s) / SR, 2)))
        track.append((t, s)); t += len(s) / SR + (0.30 if j < len(b['segs']) - 1 else 0)
    beats.append(dict(id=b['id'], start=round(b0, 2), end=round(t, 2), segs=segs)); t += b.get('pause', 0.85)
total = t + 1.5; mix = np.zeros(int(total * SR))
for st, s in track: mix[int(st * SR):int(st * SR) + len(s)] += s
sf.write(out + '/voice.wav', mix * (0.85 / np.max(np.abs(mix))), SR, subtype='PCM_16')
json.dump(dict(total=round(total, 2), beats=beats), open(out + '/timeline.json', 'w'), indent=1, ensure_ascii=False)
for b in beats: print(b['id'], b['start'], '->', b['end'])
print('total', round(total, 1))

#!/usr/bin/env python3
"""Score and final mix for an episode: synthesized underscore ducked under the narration.
usage: mix.py EPISODE.json   (reads out/<id>/narr/voice.wav + timeline.json, writes out/<id>/narr/mix.wav)
Cue times come from the episode's "cues": {"tension": [t0, t1], "swell": [t0, t1], "strike": t, "resolve": t}."""
import sys, os, json
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ep = json.load(open(sys.argv[1], encoding='utf-8')); media = os.path.join(ROOT, 'out', ep['id'], 'narr')
tl = json.load(open(media + '/timeline.json')); DUR = ep['shots'][-1]['t1']; cues = ep.get('cues', {})
SR = 48000; N = int(SR * DUR); t = np.arange(N) / SR; TAU = 2 * np.pi; rng = np.random.default_rng(11)
def ss(x, a, b):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def tone(f, harm=(1.0,), det=0.0, ph=0.0):
    return sum(a * np.sin(TAU * f * k * (1 + det) * t + ph * k) for k, a in enumerate(harm, 1))
def band(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def st(fn): return np.stack([fn(0), fn(1)], axis=1)
def reverb(x, decay, length=3.2, seed=1):
    r = np.random.default_rng(seed); n = int(SR * length); ti = np.arange(n) / SR; out = np.zeros_like(x)
    for c in range(2):
        ir = band(r.normal(0, 1, n) * np.exp(-ti / decay), 150, 6000); ir /= np.sqrt(np.sum(ir ** 2)); out[:, c] = fftconvolve(x[:, c], ir)[:len(x)]
    return out
resolve = cues.get('resolve', DUR * 0.85); tens = cues.get('tension', [DUR * 0.55, resolve]); strike = cues.get('strike', resolve - 2.5); swell = cues.get('swell', [resolve - 20, resolve - 15])
L = np.zeros((N, 2)); h = (1.0, 0.5, 0.33, 0.2, 0.12)
drone = ss(t, 0, 3) * (1 - ss(t, DUR - 4, DUR))
for f, a in ((73.42, 0.9), (110.0, 0.55), (146.83, 0.6)):
    L += a * 0.05 * st(lambda c: tone(f, h, 0.0012 if c else -0.0012, c * 0.7)) * drone[:, None]
minor = ss(t, 2, 8) * (1 - ss(t, resolve - 1.0, resolve + 0.5))                      # D minor colour until the resolve
L += 0.030 * st(lambda c: tone(174.61, (1, 0.4, 0.2), 0.001 if c else -0.001)) * minor[:, None]
tension = ss(t, tens[0], tens[0] + 6) * (1 - ss(t, strike - 0.2, strike))             # low pulse through the confrontation
beat = 0.92; ph = np.mod(t - tens[0], beat)
thump = np.sin(TAU * 52 * ph) * np.exp(-ph / 0.16) * (0.5 + 0.5 * ss(t, tens[0], strike))
L += 0.16 * (thump * tension)[:, None]
L += 0.022 * st(lambda c: tone(155.56, (1, 0.5, 0.25), 0.002 if c else -0.002)) * (tension * (0.5 + 0.5 * np.sin(TAU * 0.11 * t)))[:, None]   # uneasy minor second
sw = ss(t, swell[0], swell[1]) * (1 - ss(t, swell[1], swell[1] + 2.5))                 # rising pad under the declaration
for f in (220.0, 293.66, 440.0):
    L += 0.022 * st(lambda c: tone(f, (1, 0.5, 0.3, 0.15), 0.0015 if c else -0.0015)) * sw[:, None]
tb = np.clip(t - strike, 0, None); hit = (t >= strike) * np.exp(-tb / 1.2)
L += 0.30 * (np.sin(TAU * (38 * tb - 4 * tb ** 2 * (tb < 1))) * hit * ss(t, strike, strike + 0.02))[:, None]
for f, a in ((587.33, 1.0), (880.0, 0.6), (1174.66, 0.4)):
    L += 0.022 * a * st(lambda c: np.sin(TAU * f * (1 + (0.0007 if c else -0.0007)) * t)) * ((t >= strike) * np.exp(-tb / 2.4))[:, None]
maj = (ss(t, resolve, resolve + 5) ** 1.3) * (1 - ss(t, DUR - 5, DUR - 0.5))           # D major after the fall
hh = tuple(1 / k ** 1.35 for k in range(1, 7))
for f, a in zip((146.83, 220.0, 293.66, 369.99, 440.0, 587.33, 739.99), (0.9, 0.8, 1.0, 0.9, 0.8, 0.6, 0.4)):
    for det in (-0.0016, 0.0, 0.0016):
        L += 0.010 * a * st(lambda c: tone(f, hh, det + (0.0004 if c else -0.0004), det * 900 + c)) * maj[:, None]
music = L * 0.72 + reverb(L, 1.0) * 0.5; music *= (ss(t, 0, 0.6) * (1 - ss(t, DUR - 1, DUR)))[:, None]; music /= np.max(np.abs(music))
sr, v = wavfile.read(media + '/voice.wav'); v = v.astype(np.float64) / (32768.0 if v.dtype == np.int16 else 1.0)
if v.ndim > 1: v = v[:, 0]
assert sr == SR, sr
voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]; voice *= 0.085 / (np.sqrt(np.mean(voice[np.abs(voice) > 1e-4] ** 2)) + 1e-9)
active = np.zeros(N)
for b in tl['beats']:
    for s in b['segs']: active[max(int((s['start'] - 0.25) * SR), 0):min(int((s['end'] + 0.35) * SR), N)] = 1
win = np.hanning(int(0.35 * SR)); duck = fftconvolve(active, win / win.sum(), mode='same')
vs = np.stack([voice, voice], axis=1); vmix = vs + reverb(vs, 0.5, 2.0, 2) * 0.15
mix = music * (0.36 * (1 - 0.55 * duck))[:, None] + vmix * 2.3
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.15) / np.tanh(1.15) * 0.89
wavfile.write(media + '/mix.wav', SR, (mix * 32767).astype(np.int16))
db = lambda x: round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12), 1)
print('mix written | voice dB', db((vmix * 2.3)[active > 0.5]), '| music under voice dB', db((music * (0.36 * (1 - 0.55 * duck))[:, None])[active > 0.5]))

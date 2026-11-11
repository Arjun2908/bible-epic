#!/usr/bin/env python3
"""Assemble an episode: clips and stills cut to the narration, verse captions, score, end card.
usage: assemble.py EPISODE.json OUT.mp4   (needs out/<id>/stills, out/<id>/clips, out/<id>/narr/{voice.wav,timeline.json})"""
import sys, os, json, re, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsb

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, 'assets', 'fonts')
BOOKS = {'GEN': 'Genesis', '1SA': '1 Samuel'}

def ss(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def font(name, size, weight):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f
F_VERSE = font('CormorantGaramond[wght].ttf', 60, 600); F_REF = font('Cinzel[wght].ttf', 25, 500)
F_TITLE = font('Cinzel[wght].ttf', 92, 500); F_SUB = font('CormorantGaramond[wght].ttf', 44, 500); F_NOTE = font('CormorantGaramond-Italic[wght].ttf', 34, 500)
IVORY, GOLD = (246, 238, 218), (238, 214, 162)

def line_img(text, fnt, color, tracking=0):
    d = ImageDraw.Draw(Image.new('L', (8, 8)))
    tw = int(sum(d.textlength(c, font=fnt) for c in text) + tracking * (len(text) - 1)) + 4 if tracking else int(d.textlength(text, font=fnt)) + 4
    asc, desc = fnt.getmetrics(); pad = 48
    im = Image.new('L', (tw + 2 * pad, asc + desc + 2 * pad), 0); d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for c in text: d.text((x, pad), c, font=fnt, fill=255); x += d.textlength(c, font=fnt) + tracking
    else: d.text((pad, pad), text, font=fnt, fill=255)
    a = np.asarray(im, np.float32) / 255
    sh = np.clip(np.asarray(im.filter(ImageFilter.GaussianBlur(18)), np.float32) / 255 * 3.4, 0, 1)
    return dict(a=a, sh=sh, color=np.array(color[::-1], np.float32), w=tw, pad=pad)

def wrap(text, fnt, maxw):
    d = ImageDraw.Draw(Image.new('L', (8, 8))); lines, cur = [], ''
    for w in text.split(' '):
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    if len(lines) > 1:      # rebalance: narrow the width until the line count would grow
        best = lines
        for mw in range(int(maxw), 500, -40):
            l2, cur = [], ''
            for w in text.split(' '):
                t = (cur + ' ' + w).strip()
                if d.textlength(t, font=fnt) <= mw or not cur: cur = t
                else: l2.append(cur); cur = w
            l2.append(cur)
            if len(l2) > len(lines): break
            best = l2
        lines = best
    return lines

def blit(f, ln, cx, top, alpha):
    x0 = int(cx - ln['w'] / 2) - ln['pad']; y0 = int(top) - ln['pad']; h, w = ln['a'].shape
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya: return
    pa = ln['a'][ya - y0:yb - y0, xa - x0:xb - x0, None] * alpha; ps = ln['sh'][ya - y0:yb - y0, xa - x0:xb - x0, None] * alpha * 0.82
    reg = f[ya:yb, xa:xb]; reg *= (1 - ps); reg += (ln['color'] - reg) * pa

def captions(ep, tl):
    """One caption per spoken segment, with ellipses where an excerpt starts or ends mid-sentence."""
    caps = []
    for b, t in zip(ep['beats'], tl['beats']):
        r = b['ref']; src = bsb.norm(bsb.verses(r['book'], r['ch'], r['v'][0], r['v'][1])); pos = 0
        ref = f"{BOOKS.get(r['book'], r['book'])} {r['ch']}:{r['v'][0]}" + (f"-{r['v'][1]}" if r['v'][1] != r['v'][0] else '')
        for s, ts in zip(b['segs'], t['segs']):
            n = bsb.norm(s['text']); i = src.find(n, pos); j = i + len(n); pos = j
            before = src[:i].rstrip(); text = s['text']
            if i > 0 and before[-1:] not in '.!?"' and before[-1:] != '': text = '…' + text
            if text.rstrip()[-1:] not in '.!?”"': text = text + '…'
            lines = [line_img(l, F_VERSE, IVORY) for l in wrap(text, F_VERSE, 1500)]
            caps.append(dict(t0=ts['start'] - 0.25, t1=ts['end'] + 0.45, lines=lines, ref=line_img(ref.upper(), F_REF, GOLD, 7)))
    for a, b in zip(caps, caps[1:]): a['t1'] = min(a['t1'], b['t0'] + 0.15)
    return caps

def draw_caps(f, caps, t):
    for c in caps:
        if c['t0'] - 0.1 <= t <= c['t1'] + 0.1:
            a = float(ss(t, c['t0'], c['t0'] + 0.3) * (1 - ss(t, c['t1'] - 0.3, c['t1'])))
            if a <= 0: continue
            top = int(0.885 * H) - 72 * len(c['lines'])
            for i, ln in enumerate(c['lines']): blit(f, ln, W / 2, top + 72 * i, a)
            blit(f, c['ref'], W / 2, int(0.905 * H), a)

# ---------------------------------------------------------------- picture
def load_still(path):
    im = cv2.imread(path); s = 2560 / im.shape[1]
    return cv2.resize(im, (2560, int(round(im.shape[0] * s))), interpolation=cv2.INTER_AREA)

def rect_frame(im, cx, cy, zoom):
    """Crop a 16:9 window (centre in 0-1 units, zoom >= 1) and scale it to the frame."""
    ih, iw = im.shape[:2]; w = iw / zoom; h = w * H / W
    if h > ih: h = ih; w = h * W / H
    x0 = np.clip(cx * iw - w / 2, 0, iw - w); y0 = np.clip(cy * ih - h / 2, 0, ih - h)
    M = np.float32([[W / w, 0, -x0 * W / w], [0, H / h, -y0 * H / h]])
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def move_for(motion, use):
    """(cx0, cy0, z0) -> (cx1, cy1, z1) from the shot's motion words; `use` varies repeat uses of the same art."""
    m = motion.lower(); a = [0.5, 0.5, 1.03]; b = [0.5, 0.5, 1.13]
    if 'pull back' in m: a, b = [0.5, 0.5, 1.22], [0.5, 0.5, 1.03]
    if 'tilt up' in m: a, b = [0.5, 0.66, 1.22], [0.5, 0.36, 1.22]
    if 'tilt down' in m: a, b = [0.5, 0.36, 1.2], [0.5, 0.62, 1.2]
    if 'pan' in m: a, b = [0.34, 0.5, 1.3], [0.66, 0.5, 1.3]
    if 'crop' in m:
        cx = [0.36, 0.64, 0.5][use % 3]; a[0] = b[0] = cx; a[2] += 0.28; b[2] += 0.28
        if 'pan' in m: a[0], b[0] = 0.32, 0.68
    if 'fast' in m: b[2] = a[2] + 0.22
    if 'eyes' in m: a, b = [0.5, 0.36, 1.15], [0.5, 0.34, 1.45]
    return a, b

class Clip:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path); self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 24
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)); self.i = -1; self.cur = None
    def frame(self, idx):
        idx = min(idx, self.n - 1)
        while self.i < idx:
            ok, fr = self.cap.read()
            if not ok: break
            self.i += 1; self.cur = fr
        fr = self.cur
        if fr.shape[1] != W or fr.shape[0] != H:
            s = max(W / fr.shape[1], H / fr.shape[0]); fr = cv2.resize(fr, (int(math.ceil(fr.shape[1] * s)), int(math.ceil(fr.shape[0] * s))), interpolation=cv2.INTER_CUBIC)
            y0 = (fr.shape[0] - H) // 2; x0 = (fr.shape[1] - W) // 2; fr = fr[y0:y0 + H, x0:x0 + W]
        return fr

def main():
    ep = json.load(open(sys.argv[1], encoding='utf-8')); outfile = sys.argv[2]
    media = os.path.join(ROOT, 'out', ep['id']); tl = json.load(open(media + '/narr/timeline.json'))
    caps = captions(ep, tl); sel = ep.get('selects', {}); shots = ep['shots']; total = shots[-1]['t1']
    clip_of = {c['from']: f"{media}/clips/{c['id']}.mp4" for c in ep.get('clips', [])}
    tmp = outfile.replace('.mp4', '.silent.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    uses, stills, prev, report, clips, used = {}, {}, None, [], {}, {}
    endcard = [(line_img(ep.get('card_title', ep['title']).upper(), F_TITLE, IVORY, 14), 0.36), (line_img(f"{ep['passage']}  ·  Berean Standard Bible", F_SUB, GOLD), 0.50)] + \
              [(line_img(l, F_NOTE, IVORY), 0.66 + 0.043 * i) for i, l in enumerate(ep.get('card_notes', []))]
    for sh in shots:
        n0, n1 = int(round(sh['t0'] * FPS)), int(round(sh['t1'] * FPS)); art = sh['art']; use = uses.get(art, 0); uses[art] = use + 1
        clip = None
        if art != 'END':
            if art not in stills: stills[art] = load_still(f"{media}/stills/{art}_t{sel.get(art, 1)}.jpg")
            p = clip_of.get(art)
            if art not in clips and p and os.path.exists(p) and os.path.getsize(p) > 10000: clips[art] = Clip(p); used[art] = 0.0
        a, b = move_for(sh['motion'], use); dur = (n1 - n0) / FPS
        if art in clips:      # keep playing the clip across repeat uses while enough of it is left
            left = clips[art].n / clips[art].fps - used[art]
            if left >= 0.72 * dur: clip = clips[art]; off = used[art]; speed = min(1.0, max(left / dur, 0.72)); used[art] += dur * speed
        report.append(f"{sh['t0']:6.1f}-{sh['t1']:6.1f} {art:4s} {'clip' if clip else 'still'}")
        for n in range(n0, n1):
            t = n / FPS; k = (n - n0) / max(n1 - n0 - 1, 1)
            if art == 'END':
                base = stills.get('A1'); fr = rect_frame(base, 0.5, 0.5, 1.2 + 0.05 * k).astype(np.float32) * 0.16 if base is not None else np.zeros((H, W, 3), np.float32)
                for ln, y in endcard: blit(fr, ln, W / 2, y * H, float(ss(t, sh['t0'] + 0.5, sh['t0'] + 1.5)))
                fr *= float(1 - ss(t, total - 0.9, total))
            else:
                if clip:
                    fr = clip.frame(int((off + (t - sh['t0']) * speed) * clip.fps)).astype(np.float32)
                else:
                    e = k * k * (3 - 2 * k) * 0.35 + k * 0.65
                    fr = rect_frame(stills[art], a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e, a[2] + (b[2] - a[2]) * e).astype(np.float32)
                    if 'shake' in sh['motion']: fr = np.roll(fr, (int(5 * math.sin(t * 31)), int(7 * math.sin(t * 23))), axis=(0, 1))
                if 'flash' in sh['motion'] and n - n0 < 7: fr += (255 - fr) * (1 - (n - n0) / 7) * 0.85
                if prev is not None and n - n0 < 5: fr = prev + (fr - prev) * ((n - n0 + 1) / 6)
                fr *= float(ss(t, 0, 1.0))
                draw_caps(fr, caps, t)
            out = np.clip(fr, 0, 255).astype(np.uint8); enc.stdin.write(out.tobytes())
        prev = out.astype(np.float32)
        print(report[-1], flush=True)
    enc.stdin.close(); enc.wait()
    audio = media + '/narr/mix.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', '-shortest', outfile], check=True)
    os.remove(tmp); print('wrote', outfile)

if __name__ == '__main__':
    main()

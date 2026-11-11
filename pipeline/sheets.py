#!/usr/bin/env python3
"""Small contact sheets of every take, committed to review/<episode>/ so takes can be judged without the full files.
usage: sheets.py EPISODE.json"""
import sys, os, json, glob
from PIL import Image, ImageDraw
ep = json.load(open(sys.argv[1], encoding='utf-8'))
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1]))))
src = os.path.join(root, 'out', ep['id'], 'stills'); dst = os.path.join(root, 'review', ep['id']); os.makedirs(dst, exist_ok=True)
TW, TH, PER = 480, 270, 4
rows = []
for s in ep['stills']:
    fs = sorted(glob.glob(f"{src}/{s['id']}_t*.jpg"))
    if not fs: continue
    row = Image.new('RGB', (TW * 3, TH + 26), (24, 22, 20)); d = ImageDraw.Draw(row)
    for i, f in enumerate(fs[:3]):
        im = Image.open(f).convert('RGB'); im.thumbnail((TW, TH)); row.paste(im, (i * TW + (TW - im.width) // 2, 26 + (TH - im.height) // 2))
        d.text((i * TW + 6, 6), f"{s['id']}  take {i + 1}   {Image.open(f).size[0]}x{Image.open(f).size[1]}", fill=(240, 225, 190))
    rows.append(row)
for f in glob.glob(dst + '/sheet_*.jpg'): os.remove(f)
for p in range(0, len(rows), PER):
    page = Image.new('RGB', (TW * 3, (TH + 26) * len(rows[p:p + PER])))
    for i, r in enumerate(rows[p:p + PER]): page.paste(r, (0, i * (TH + 26)))
    page.save(f'{dst}/sheet_{p // PER + 1:02d}.jpg', 'JPEG', quality=82)
m = os.path.join(root, 'out', ep['id'], 'manifest.json')
if os.path.exists(m): open(dst + '/manifest.json', 'w').write(open(m).read())
print(f'{len(rows)} stills on {-(-len(rows) // PER)} sheets -> {dst}')

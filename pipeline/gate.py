#!/usr/bin/env python3
"""Accuracy gate. Fails unless every spoken segment of an episode is a verbatim excerpt of its cited BSB verse(s),
with the segments of a beat appearing in order.  usage: gate.py episodes/<id>/episode.json"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsb

def main(path):
    ep = json.load(open(path, encoding='utf-8'))
    bad = words = segs = 0
    for b in ep['beats']:
        r = b['ref']
        src = bsb.norm(bsb.verses(r['book'], r['ch'], r['v'][0], r['v'][1])); pos = 0
        for s in b['segs']:
            t = bsb.norm(s['text']); i = src.find(t, pos)
            segs += 1; words += len(t.split())
            if i < 0:
                bad += 1; print(f"MISMATCH {b['id']} {r['book']} {r['ch']}:{r['v']}: {s['text']!r}")
            else:
                pos = i + len(t)
    # shot plan sanity: contiguous, every art id exists, pacing rule (no shot over 10 s)
    arts = {s['id'] for s in ep.get('stills', [])} | {c['id'] for c in ep.get('clips', [])} | {'END'}
    shots = ep.get('shots', [])
    for a, b in zip(shots, shots[1:]):
        if abs(a['t1'] - b['t0']) > 1e-6: bad += 1; print('GAP between shots', a, b)
    for s in shots:
        if s['art'] not in arts: bad += 1; print('UNKNOWN ART', s)
        if s['t1'] - s['t0'] > 10.0: bad += 1; print('SHOT OVER 10 s', s)
    print(f"gate: {'PASS' if not bad else 'FAIL'} | {segs} segments, {words} words, {len(shots)} shots")
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

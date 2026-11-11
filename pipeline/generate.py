#!/usr/bin/env python3
"""Generate the art for one episode.
  generate.py EPISODE.json --mode stills|clips|probe [--only A1,B1] [--takes N] [--dry-run] [--workers 6]
Outputs: out/<episode>/stills/<ID>_t<k>.jpg, out/<episode>/clips/<ID>.mp4, out/<episode>/manifest.json
Resumable: files that already exist are skipped."""
import sys, os, json, argparse, time, io, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def full_prompt(ep, still):
    p = still['prompt']
    for k, c in ep['characters'].items(): p = p.replace('{' + k + '}', c['desc'])
    for k, v in ep.get('blocks', {}).items(): p = p.replace('{' + k + '}', v)
    lead = ''
    if still.get('refs'):
        who = ' and '.join(ep['characters'][r]['name'] for r in still['refs'])
        lead = (f'Use the attached character reference sheet{"s" if len(still["refs"]) > 1 else ""} only for the appearance of {who}: same face, hair, build and costume. '
                'Paint a completely new scene, not a reference sheet: ')
        if p.startswith('Character reference sheet'):      # a new life-stage sheet derived from an earlier sheet (new costume, same person)
            lead = f'Use the attached portrait only for the face, hair, skin and build of {who}: this is the same person. Paint a new '
            p = p[0].lower() + p[1:]
    return lead + p + ' ' + ep['style']

def save_jpg(data, path):
    Image.open(io.BytesIO(data)).convert('RGB').save(path, 'JPEG', quality=93)

def placeholder(text, path):
    im = Image.new('RGB', (1280, 720), (70, 60, 50)); ImageDraw.Draw(im).text((30, 30), text[:900], fill=(240, 230, 210)); im.save(path, 'JPEG')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('episode'); ap.add_argument('--mode', default='stills'); ap.add_argument('--only', default='')
    ap.add_argument('--takes', type=int, default=0); ap.add_argument('--redo', default='false'); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    ep = json.load(open(a.episode, encoding='utf-8'))
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(a.episode))))
    out = os.path.join(root, 'out', ep['id']); os.makedirs(out + '/stills', exist_ok=True); os.makedirs(out + '/clips', exist_ok=True)
    mpath = out + '/manifest.json'
    man = json.load(open(mpath)) if os.path.exists(mpath) else {'episode': ep['id'], 'stills': {}, 'clips': {}, 'log': []}
    only = {x.strip() for x in a.only.split(',') if x.strip()}
    if not a.dry_run: import xai
    if a.redo.lower() == 'true' and only:
        import glob
        for i in only:
            for f in glob.glob(f'{out}/stills/{i}_t*.jpg') + glob.glob(f'{out}/clips/{i}.mp4'): os.remove(f); print('  removed', os.path.basename(f))
    jobs = []

    if a.mode in ('stills', 'probe'):
        stills = [s for s in ep['stills'] if not only or s['id'] in only]
        if a.mode == 'probe': stills = [s for s in ep['stills'] if s['id'] in (only or {ep['stills'][0]['id']})]
        for s in stills:
            takes = a.takes or s.get('takes', ep.get('takes', 3))
            todo = [k for k in range(1, takes + 1) if not os.path.exists(f"{out}/stills/{s['id']}_t{k}.jpg")]
            if not todo: continue
            def job(s=s, todo=todo):
                prompt = full_prompt(ep, s); refs = [os.path.join(root, ep['characters'][r]['ref']) for r in s.get('refs', [])]
                if a.dry_run:
                    for k in todo: placeholder(f"{s['id']} take {k}\n{prompt}", f"{out}/stills/{s['id']}_t{k}.jpg")
                else:
                    imgs = []
                    while len(imgs) < len(todo):            # the API may return fewer than asked
                        imgs += xai.image(prompt, n=len(todo) - len(imgs), refs=refs)
                    for k, d in zip(todo, imgs): save_jpg(d, f"{out}/stills/{s['id']}_t{k}.jpg")
                return ('stills', s['id'], {'takes': takes, 'refs': s.get('refs', []), 'prompt': prompt})
            jobs.append(job)
    elif a.mode == 'clips':
        sel = ep.get('selects', {})
        for c in ep['clips']:
            if (only and c['id'] not in only) or os.path.exists(f"{out}/clips/{c['id']}.mp4"): continue
            def job(c=c):
                src = f"{out}/stills/{c['from']}_t{sel.get(c['from'], 1)}.jpg"
                if a.dry_run: open(f"{out}/clips/{c['id']}.mp4", 'wb').write(b'')
                else: open(f"{out}/clips/{c['id']}.mp4", 'wb').write(xai.video(c['prompt'], src, duration=c.get('duration', 6)))
                return ('clips', c['id'], {'from': c['from'], 'take': sel.get(c['from'], 1), 'duration': c.get('duration', 6)})
            jobs.append(job)

    print(f"{ep['id']}: mode={a.mode}, {len(jobs)} jobs", flush=True)
    fails = 0; t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(j) for j in jobs]):
            try:
                kind, i, info = f.result(); man[kind][i] = info; print('  ok', kind, i, flush=True)
            except Exception as e:
                fails += 1; man['log'].append(str(e)[:500]); print('  FAILED', str(e)[:500], flush=True); traceback.print_exc()
            json.dump(man, open(mpath, 'w'), indent=1)
    json.dump(man, open(mpath, 'w'), indent=1)
    print(f'done in {time.time() - t0:.0f}s, {fails} failed', flush=True)
    sys.exit(1 if fails and fails == len(jobs) else 0)

if __name__ == '__main__':
    main()

"""Minimal xAI Imagine API client (images, image edits with references, image-to-video).
The key comes from the XAI_API_KEY environment variable and is never logged.
Optional request fields whose exact names are not confirmed by the docs are dropped one by one if the API rejects them."""
import os, time, base64, json, io, requests
from PIL import Image

BASE = 'https://api.x.ai/v1'
IMAGE_MODEL = os.environ.get('XAI_IMAGE_MODEL', 'grok-imagine-image-2.0')
VIDEO_MODEL = os.environ.get('XAI_VIDEO_MODEL', 'grok-imagine-video-1.5')
COST = {'ticks': 0}   # xAI reports cost per response in ticks; 1e10 ticks = 1 USD
_dropped = set()   # optional fields the API has rejected in this run

def _headers():
    return {'Authorization': 'Bearer ' + os.environ['XAI_API_KEY'], 'Content-Type': 'application/json'}

def _post(path, body, optional=()):
    body = {k: v for k, v in body.items() if k not in _dropped}
    opt = [k for k in optional if k in body]
    for attempt in range(8):
        r = requests.post(BASE + path, headers=_headers(), json=body, timeout=300)
        if r.status_code == 200:
            j = r.json(); COST['ticks'] += (j.get('usage') or {}).get('cost_in_usd_ticks', 0) or 0
            return j
        msg = r.text[:600]
        if r.status_code in (429, 500, 502, 503, 504):
            wait = min(90, 4 * 2 ** attempt); print(f'  {path} {r.status_code}, retry in {wait}s: {msg[:160]}', flush=True); time.sleep(wait); continue
        if 'moderat' in msg.lower():      # a moderation refusal is about the picture, not the request: never drop request fields for it
            raise RuntimeError(f'{path} {r.status_code}: {msg}')
        if r.status_code in (400, 422) and opt:
            k = next((f for f in opt if f in msg), opt[-1])   # drop the field the error names, else the last optional one
            print(f'  {path} {r.status_code}: dropping optional field "{k}": {msg[:200]}', flush=True)
            _dropped.add(k); opt.remove(k); body.pop(k, None); continue
        raise RuntimeError(f'{path} {r.status_code}: {msg}')
    raise RuntimeError(f'{path}: gave up after retries')

def data_uri(path, max_side=1536):
    im = Image.open(path).convert('RGB'); im.thumbnail((max_side, max_side))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=90)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

def board(paths, height=1024):
    """Several reference sheets side by side as one image (fallback when multi-image input is refused)."""
    ims = [Image.open(p).convert('RGB') for p in paths]
    ims = [im.resize((int(im.width * height / im.height), height)) for im in ims]
    out = Image.new('RGB', (sum(i.width for i in ims), height))
    x = 0
    for im in ims: out.paste(im, (x, 0)); x += im.width
    buf = io.BytesIO(); out.save(buf, 'JPEG', quality=90)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

def _images_from(resp):
    out = []
    for d in resp.get('data', []):
        if d.get('b64_json'): out.append(base64.b64decode(d['b64_json']))
        elif d.get('url'): out.append(requests.get(d['url'], timeout=300).content)
    if not out: raise RuntimeError('no images in response: ' + json.dumps(resp)[:400])
    return out

def image(prompt, n=1, refs=(), aspect_ratio='16:9', resolution='2k', multi='images'):
    """Returns a list of image bytes. refs: paths of reference images (character sheets)."""
    body = {'model': IMAGE_MODEL, 'prompt': prompt, 'n': n, 'aspect_ratio': aspect_ratio, 'resolution': resolution, 'response_format': 'b64_json'}
    optional = ('resolution', 'response_format', 'aspect_ratio', 'n')
    if not refs:
        return _images_from(_post('/images/generations', body, optional))
    if len(refs) == 1 or multi == 'board':
        body['image'] = {'url': data_uri(refs[0]) if len(refs) == 1 else board(refs), 'type': 'image_url'}
        return _images_from(_post('/images/edits', body, optional))
    body['images'] = [{'url': data_uri(p), 'type': 'image_url'} for p in refs]
    try:
        return _images_from(_post('/images/edits', body, optional))
    except RuntimeError as e:
        print('  multi-image edit refused, falling back to one reference board:', str(e)[:200], flush=True)
        return image(prompt, n, refs, aspect_ratio, resolution, multi='board')

def video(prompt, image_path, duration=6, aspect_ratio='16:9', resolution='1080p', poll=6, timeout=1800):
    """Image-to-video. Returns mp4 bytes."""
    body = {'model': VIDEO_MODEL, 'prompt': prompt, 'image': {'url': data_uri(image_path, 1920)}, 'duration': duration,
            'aspect_ratio': aspect_ratio, 'resolution': resolution}
    rid = _post('/videos/generations', body, ('resolution', 'aspect_ratio'))['request_id']
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = requests.get(f'{BASE}/videos/{rid}', headers=_headers(), timeout=120)
        j = r.json() if r.status_code == 200 else {}
        st = j.get('status')
        if st == 'done' or (j.get('video') or {}).get('url'):
            COST['ticks'] += (j.get('usage') or {}).get('cost_in_usd_ticks', 0) or 0
            return requests.get(j['video']['url'], timeout=600).content
        if st in ('failed', 'expired'): raise RuntimeError(f'video {rid} {st}: {json.dumps(j)[:300]}')
        time.sleep(poll)
    raise RuntimeError(f'video {rid} timed out')

#!/usr/bin/env python3
"""Work queue for parallel scheduled runs. One small file per unit in state/ so runs do not collide on a shared ledger.
  next_unit.py              -> shows the unit this run should work on (a stale unfinished one first, else the next unclaimed)
  next_unit.py --claim      -> also writes/refreshes state/<id>.json; commit and push it at once to hold the claim
  next_unit.py --summary    -> progress and estimated spend
State file: {"id", "status": claimed|written|stills|selected|clips|banked|blocked, "claimed_at", "updated_at", "images", "clip_seconds", "cost_usd" (copy from review/<id>/manifest.json), "next_step", "notes"}
A unit not updated for STALE_HOURS and not banked may be resumed by any run. Update the file (and push) after every step."""
import sys, os, json, glob, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STALE_HOURS = 2.0; BUDGET_USD = 20000; PRICE_IMAGE = 0.08; PRICE_CLIP_SECOND = 0.15    # deliberately pessimistic prices
DEADLINE = dt.date(2026, 11, 30); GOSPELS_NO_LATER_THAN = dt.date(2026, 11, 24)
now = dt.datetime.now(dt.timezone.utc)
units = json.load(open(os.path.join(ROOT, 'story-spine.json')))['units']
state = {}
for f in glob.glob(os.path.join(ROOT, 'state', '*.json')):
    s = json.load(open(f)); state[s['id']] = s
images = sum(s.get('images', 0) for s in state.values()); secs = sum(s.get('clip_seconds', 0) for s in state.values())
est = sum(s['cost_usd'] if s.get('cost_usd') else s.get('images', 0) * PRICE_IMAGE + s.get('clip_seconds', 0) * PRICE_CLIP_SECOND for s in state.values())   # real cost where recorded
banked = sum(1 for s in state.values() if s['status'] == 'banked')
if '--summary' in sys.argv:
    by = {}
    for s in state.values(): by[s['status']] = by.get(s['status'], 0) + 1
    print(f'{banked}/{len(units)} banked | {by} | {images} images, {secs:.0f} clip seconds | pessimistic estimate ${est:,.0f} of ${BUDGET_USD:,} cap'); sys.exit(0)
if now.date() > DEADLINE: print('DEADLINE PASSED: do not trigger generation. Assemble banked units instead.'); sys.exit(3)
if est >= BUDGET_USD: print(f'BUDGET STOP: pessimistic estimate ${est:,.0f} reached the ${BUDGET_USD:,} cap. Do not trigger generation.'); sys.exit(4)
def age(s): return (now - dt.datetime.fromisoformat(s['updated_at'])).total_seconds() / 3600
order = units
if now.date() >= GOSPELS_NO_LATER_THAN:      # do not let the Gospels miss the credit deadline
    order = [u for u in units if u['season'] == 8] + [u for u in units if u['season'] != 8]
pick = next((u for u in order if u['id'] in state and state[u['id']]['status'] not in ('banked', 'blocked') and age(state[u['id']]) > STALE_HOURS), None)
resume = pick is not None
if pick is None: pick = next((u for u in order if u['id'] not in state), None)
if pick is None: print('NOTHING TO CLAIM: every unit is banked or in progress.'); sys.exit(5)
print(('RESUME ' if resume else 'NEW ') + json.dumps(pick, ensure_ascii=False))
if resume: print('previous state: ' + json.dumps(state[pick['id']], ensure_ascii=False))
if '--claim' in sys.argv:
    s = state.get(pick['id'], dict(id=pick['id'], status='claimed', claimed_at=now.isoformat(timespec='seconds'), images=0, clip_seconds=0, next_step='write episode file', notes=''))
    s['updated_at'] = now.isoformat(timespec='seconds')
    json.dump(s, open(os.path.join(ROOT, 'state', pick['id'] + '.json'), 'w'), indent=1); print('claimed', pick['id'])

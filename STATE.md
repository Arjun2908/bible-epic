# State

Updated: 11 Nov 2026

## Done
- Test 1: Genesis 1:1-5, procedural, narrated (made in Claude's workspace, not in this repo).
- Pilot 2 (David and Goliath, 1 Samuel 17): script written, gated and voiced; character sheets for David, Goliath and Saul approved and committed in `refs/`; episode file ready.
- Pipeline skeleton: gate, xAI client, generator, contact sheets, workflow. Tested offline with a dry run only.

## Blocked on Arjun
- `XAI_API_KEY` repository secret.

## Next, in order
1. `gh workflow run generate.yml -f episode=p02-david-goliath -f mode=probe -f only=B1,E1` to learn the API's real behaviour (field names, reference handling, output size). Fix `pipeline/xai.py` from the logs.
2. Full stills for pilot 2, review sheets, selects, clips.
3. Build the assembly step on pilot 2 (narration, captions, music, render in Actions). Ship the pilot film.
4. Write `story-spine.json`: all 66 books as seasons, episodes and 8-minute sequences.
5. Bank the art before 30 Nov: for each sequence in spine order, write the episode file, gate, generate stills and clips. Gospels last.
6. After the deadline: assemble episodes in order.

## Decision log
- 11 Nov 2026: Arjun waived per-step approval. Defaults in `PIPELINE.md`.
- Goliath's height follows the BSB main text (six cubits and a span); the footnoted shorter reading is noted in the pilot's accuracy notes.
- Pilot 2 ends at 1 Samuel 17:50; verse 51 is not shown in the pilot.

## Spend
- Nothing yet.

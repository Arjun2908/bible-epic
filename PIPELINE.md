# Pipeline

## Roles
- **Claude** (in claude.ai sessions, including scheduled ones): writes episode files, triggers workflows with `gh workflow run`, reviews contact sheets, picks takes, assembles episodes. Claude's workspace cannot reach api.x.ai, only GitHub, so all generation happens in GitHub Actions.
- **GitHub Actions**: runs the accuracy gate, calls the xAI API, stores media in releases, commits review sheets.
- **Arjun**: owns the repo and the `XAI_API_KEY` secret. He has waived per-step approval (11 Nov 2026): decisions are made by Claude, logged in `STATE.md`, and can be overruled later.

## Episode loop (proven on pilot 2)
1. **Write** `episodes/<id>/episode.json`. Copy the structure of `episodes/p02-david-goliath/episode.json`: `beats` (speaker code + verbatim BSB excerpt + verse reference), `voices`, `characters` (name, description, reference sheet), `blocks` (reusable prompt text), `stills` (prompt with `{TOKENS}`, `refs`), `clips` (one per still: `V-<still id>`, motion prompt, 6 or 8 s), `shots`, `cues`, `card_title`, `card_notes`.
2. **Gate**: `python pipeline/bsb.py build && python pipeline/gate.py episodes/<id>/episode.json`. Never push an episode that fails.
3. **Narrate** (sets the timing): `python pipeline/narrate.py episodes/<id>/episode.json`, then lay the `shots` against `out/<id>/narr/timeline.json` so each shot sits under the words it shows. Keep `voice.wav` and `timeline.json`: commit them under `episodes/<id>/narr/` (small) so assembly can run later.
4. **New characters**: add a still with no refs whose prompt starts "Character reference sheet of ...: full-body front view and a head-and-shoulders portrait side by side, plain warm-grey background", generate it, pick a take, save it as `refs/REF-<NAME>.jpg` (download the release asset), commit. Never put a second person in a reference sheet: they leak into scenes.
5. **Stills**: `gh workflow run generate.yml --ref main -f episode=<id> -f mode=stills`. About 3 minutes per 60 images.
6. **Review** `review/<id>/sheet_*.jpg` after `git pull --rebase`. Record the chosen take per still in `selects`. For stills with no usable take, fix the prompt and run again with `-f only=A1,B3 -f redo=true`.
7. **Clips**: `-f mode=clips` animates every selected still (about 3 minutes per 20 clips, 1920x1088, 24 fps).
8. **Assemble** (needs no xAI credits, can wait until after the credit deadline): download `media.zip` and every `clips-*.zip` and unzip them into `out/<id>/`, then `python pipeline/mix.py <episode>` and `python pipeline/assemble.py <episode> out.mp4`. Re-encode for delivery with `-crf 24 -maxrate 5M`.
9. **Update `STATE.md`** (what was done, spend, next unit) and push.

## Working through GitHub from a Claude session
- Attach the repo first: add_repo for `Arjun2908/bible-epic` with push access, then clone.
- GraphQL is blocked. Always pass `--ref main` to `gh workflow run`; poll with `gh api repos/Arjun2908/bible-epic/actions/runs/<id>`; read logs with `gh api repos/.../actions/jobs/<job id>/logs`.
- `gh release download` does not work. Use `gh api repos/.../releases/tags/<id>` for the asset id, then `gh api -H "Accept: application/octet-stream" repos/.../releases/assets/<asset id> > media.zip`.
- After `git push`, wait about 20 seconds before `gh workflow run`: a run dispatched at once can check out the commit before your push (a run of s01e01c missed a character sheet that way). Trigger one run per episode at a time and wait for it: a second queued run replaces any run already waiting, and a run dispatched from an older commit fails at "Commit review sheets" (its media is still stored).
- Run `-f mode=clips` without `only` only when every still has an entry in `selects`: an unselected still is animated from take 1.
- The workspace cannot reach api.x.ai. Never ask for or handle the API key.

## Running workflows safely
- One workflow run per episode at a time. GitHub keeps only one waiting run per episode and cancels older waiting ones, so trigger a run, wait for it to complete, then trigger the next.
- A run can end red although generation worked (the step that failed tells you). The media is in the release as soon as "Store full-size media" succeeds; if only "Commit review sheets" failed, re-run with a tiny `only=` to rebuild and commit the sheets.
- "Generated image rejected by content moderation" is about the picture, not the request, and it is still charged. Do not retry the same prompt more than once: reword it (cover and frame unclothed figures with foliage, light, distance or tight framing; no words like naked or nude; no gore).
- Each run prints its real cost and stores the running total in `review/<id>/manifest.json` as `cost_usd`. Copy that number into `state/<id>.json` as `cost_usd` when you update the state.

## Review checklist (lessons so far)
- Check posture and direction against the verse (pilot: three takes showed Goliath on his back; the text says facedown). Say it twice in the prompt and name what must be hidden or visible.
- Count countable things the text numbers (five stones: two of three takes had six or seven).
- Minor characters need their own description block or the model invents a new costume each time.
- Reject Roman-looking kit, medieval armour, ruins or buildings the scene should not have, extra weapons in hands that the text leaves empty.
- Look at one frame near the end of each clip, not only the start: costumes drift during motion.
- Clips carry generated audio; the assembler ignores it. Do not use it without Arjun hearing it.

## Rules every episode must follow
**Accuracy**
- Canon: Protestant 66 books. Translation: Berean Standard Bible, public domain.
- Every spoken or on-screen word is a verbatim BSB excerpt, enforced by the gate. Partial verses are shown with an ellipsis. Skipped verses are listed in the episode's notes.
- The local BSB copy is a 2025 snapshot with known slips (for example a typo at 1 Samuel 17:23). Read every used verse once for obvious typos.
- Visual details are tagged in the episode notes as T (from the text), I (inferred from text, history or archaeology) or D (dramatized). Nothing may contradict the text. Visuals follow the text's own order of events (no sun before day four).
- God the Father is never shown with a face: light, voice, cloud, fire.
- Disputed questions (Exodus dating, Job's placement, Gospel order, Revelation readings): show what the text says, do not resolve the debate, log the choice in `STATE.md`.

**Pacing**
- Shots run 4-8 seconds; nothing unchanged beyond 10 (the gate enforces 10).
- Every shot names an action. People doing things, not settings.
- Rotate framing: wide, medium, close, insert, map.
- Narration and dialogue carry the story continuously. Open on a hook, end on a turn.

**Look**
- Painterly oil style block shared by every prompt (see the pilot episode's `style`).
- Recurring characters always use their committed reference sheet and the same description text.
- Reject: anachronisms, text or watermarks in frame, gore, nudity, anything the passage contradicts.

**Defaults chosen without sign-off (Arjun may overrule)**
- Content: violence is shown without gore; sexual content is implied, never shown; Eden uses foliage, light and framing.
- Voices: one narrator plus distinct character voices.
- Jesus (decided by Arjun, 11 Nov 2026): show him, face included, using the most historically accurate assumption. The Gospels give no physical description, so this is tagged I (inferred) in every episode's notes. Description block to use everywhere: "Jesus, a first-century Galilean Jewish man of about thirty, average height and lean from manual work, olive-brown skin, dark brown eyes, black hair cut fairly short and a short trimmed beard, an ordinary unremarkable face, wearing a knee-length undyed wool tunic, a plain cream mantle with tassels at its corners, a leather belt and simple sandals; no halo, no long flowing hair, no white or blue robes". The first worker to reach the Gospels makes `refs/REF-JESUS.jpg` from this block (no other person in the sheet) and every later episode reuses that one sheet. Infant and boy stages get their own sheets. After the resurrection he looks the same, with the wounds the text mentions (John 20:27). The transfiguration and Revelation 1 follow the text's own description.

## Storage
- Full-size media: assets on the release named after the episode. `media.zip` holds the stills and the manifest; the clips are in `clips-00.zip`, `clips-01.zip`, ... (30 clips each), because a release asset may not exceed 2 GB and one unit's 80 clips alone come to about 1.7 GB (roughly 3.4 MB per clip second). Unzip all of them into `out/<id>/`. Releases stored before 11 Nov 12:15 UTC may still have clips inside `media.zip`; the next workflow run on that episode moves them.
- Review sheets and manifests: committed under `review/`.

## Budget and deadline
- xAI credits: about $25,000, expiring 30 Nov 2026. Art that needs credits is generated first; assembly needs none and can follow.
- Plan: 3 takes per still and one 6-8 s clip for every still. Track counts in `STATE.md`; Arjun can read exact spend in the xAI console.

## Scheduled runs (several run in parallel, every hour)
Each run does ONE unit: one sequence from `story-spine.json` (about 8 minutes of film, 60-90 stills).
1. Attach and clone the repo. Read this file and `STATE.md`. If `STATE.md` starts with BLOCKED and the cause still holds, stop.
2. `python pipeline/bsb.py build`, then `python pipeline/next_unit.py --claim`. Immediately `git add state && git commit && git push`. If the push is rejected, `git pull --rebase`; if your state file now conflicts or someone else holds that unit, discard yours and claim again. If the tool prints DEADLINE PASSED or BUDGET STOP, do not generate anything: assemble a banked unit instead (episode loop step 8), or stop if none.
3. Episode id = unit id (for example `s01e02a`). Read the unit's passages in full from the BSB database before writing. Follow the unit's `notes` and `also`.
4. While banking art (until the deadline), do the episode loop steps 1, 2, 4, 5, 6 and 7 only. Leave `shots` empty and skip narration: timing is done at assembly. Write enough stills that every beat has at least one new picture and no picture would need to hold longer than 8 seconds of narration (roughly one still per 12-15 spoken words), and one clip per still.
5. After every step, update `state/<id>.json` (`status`, `updated_at`, `next_step`, `images`, `clip_seconds`, `notes`) and push, so another run can resume if this one dies.
6. Finish with `status: banked`. Add anything future runs must know to `STATE.md` (new character sheets, decisions, lessons) in a short commit of its own; pull --rebase before pushing.
7. Do not start a second unit in the same run.

Recurring characters: before designing a character, look in `refs/` and reuse the committed sheet and its description text from the episode that introduced it (search `episodes/*/episode.json` for the character key). Characters age: add a new sheet per life stage (`REF-DAVID-KING.jpg`) derived by attaching the earlier sheet as a reference.

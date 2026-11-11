# Pipeline

## Roles
- **Claude** (in claude.ai sessions, including scheduled ones): writes episode files, triggers workflows with `gh workflow run`, reviews contact sheets, picks takes, assembles episodes. Claude's workspace cannot reach api.x.ai, only GitHub, so all generation happens in GitHub Actions.
- **GitHub Actions**: runs the accuracy gate, calls the xAI API, stores media in releases, commits review sheets.
- **Arjun**: owns the repo and the `XAI_API_KEY` secret. He has waived per-step approval (11 Nov 2026): decisions are made by Claude, logged in `STATE.md`, and can be overruled later.

## Episode loop
1. **Write** `episodes/<id>/episode.json`: beats (speaker + verbatim BSB excerpt + verse reference), characters (description + reference sheet), stills (prompt + which sheets to attach), clips, shots (time, art, action, motion).
2. **Gate** locally: `python pipeline/bsb.py build && python pipeline/gate.py episodes/<id>/episode.json`. Never push an episode that fails.
3. **New characters**: generate a reference sheet first (a still with no refs, portrait + full body), review it, commit it to `refs/`.
4. **Generate stills**: `gh workflow run generate.yml -f episode=<id> -f mode=stills`. Watch with `gh run watch`, read failures with `gh run view --log-failed`.
5. **Review** `review/<id>/sheet_*.jpg`. Reject takes that break the text (see rules). Record the chosen take per still in `selects` in the episode file. Re-run with `-f only=A1,B3` for stills with no usable take.
6. **Generate clips**: `-f mode=clips` animates the selected stills.
7. **Assemble** (to be built on the pilot): narration with Kokoro, picture timed to the narration, captions with verse references, music, end card. Runs in Actions; the finished mp4 goes to the episode's release.
8. **Update `STATE.md`** and push.

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
- Jesus: until Arjun decides, his face is not shown directly (from behind, backlit, at a distance, hands). Gospels are generated last so this can still change.

## Storage
- Full-size stills and clips: `media.zip` asset on the release named after the episode (2 GB per asset; split long episodes into sequences of about 8 minutes, one episode id each, for example `s01e01a`).
- Review sheets and manifests: committed under `review/`.

## Budget and deadline
- xAI credits: about $25,000, expiring 30 Nov 2026. Art that needs credits is generated first; assembly needs none and can follow.
- Rough plan: 3 takes per still, one clip per shot where motion helps. Track spend in `STATE.md` from the manifests.

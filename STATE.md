# State

Updated: 11 Nov 2026 (UTC 11:15)

## Done
- Test 1: Genesis 1:1-5, procedural, narrated (made in Claude's workspace, not in this repo).
- Pilot 2, David and Goliath (`p02-david-goliath`): finished film delivered to Arjun, 2 min 23 s. 21 stills (3 takes each, 4 regenerated after review), 21 clips, narration with four voices, score, captions, end card. Whole loop ran through the API with no manual pasting.
- Pipeline: gate, xAI client, generator, contact sheets, narration, mix, assembler, workflow. The API accepted every request field as written (n, aspect_ratio, resolution 2k, b64_json, multi-image `images`, video 1080p).

## Queue
- `story-spine.json`: 252 sequences in 48 episodes covering all 66 books. Gospels (season 8) are queued last so Arjun can still decide about Jesus's face, but `next_unit.py` moves them to the front on 24 Nov so they cannot miss the credit deadline.
- Claims and progress live in `state/<unit id>.json`, one file per unit. `python pipeline/next_unit.py --summary` shows progress and a pessimistic spend estimate; generation stops itself at an estimated $20,000 or after 30 Nov 2026.
- The Gospel spine is a chapter-level draft. The first run that reaches season 8 must first rework it into a scene-level harmony (edit `pipeline/make_spine.py`, keep unit ids of banked units unchanged).

## Waiting on Arjun (not blocking)
- Feedback on the pilot film, especially the voices, which Claude cannot hear.
- Jesus's face: shown or withheld. Default is withheld.

## Decision log
- 11 Nov 2026: Arjun waived per-step approval. Defaults in `PIPELINE.md`.
- Goliath's height follows the BSB main text (six cubits and a span).
- Pilot 2 ends at 1 Samuel 17:50; verse 51 is not shown.
- Every still gets a motion clip (credits allow it; Arjun asked for more happening on screen).
- Known weakness in pilot 2: the shield bearer's costume differs between shots (feathered headdress in some, crested helmet in others).

- 11 Nov 2026 (s01e01b): `pipeline/bsb.py` now prints the divine name as the BSB does (LORD God, Lord GOD). The source snapshot marks it as small caps in Genesis and four verses of Samuel, and the old build flattened it to "Lord God". If your gate now reports a MISMATCH on "Lord God", rebuild (`python pipeline/bsb.py build`) and copy the verse text again. The gate itself is unchanged.
- Snapshot slip: Genesis 2:4 ends with a doubled "God made them. God made them." Use the verse only up to the first "made them."

- 11 Nov 2026 (s01e01b, Genesis 2): Adam and Eve get their faces in this unit: `refs/REF-ADAM.jpg` and `refs/REF-EVE.jpg` (portrait-only sheets; being generated now, wait for them rather than designing new ones). Genesis 3 and later units must reuse the ADAM and EVE character text and the blocks TREE_LIFE, TREE_KNOW, HIDE_M, HIDE_F from `episodes/s01e01b/episode.json` word for word. The forbidden fruit is of no named kind (crimson-and-gold, not an apple).
- Genesis 2 is pictured in its own order (man, garden, trees, then beasts and birds in v19, then the woman); nothing is harmonised with Genesis 1.

- 11 Nov 2026 (s01e01b): fixed `pipeline/xai.py`. A content-moderation refusal (HTTP 400) used to be mistaken for a rejected request field, so after one refused picture the rest of that workflow run lost `resolution` and came out at 1280x720 instead of 2816x1584. Check the sizes printed on your contact sheets: regenerate any 1280x720 stills (`-f only=... -f redo=true`) made before this fix. Moderation refuses unclothed full figures even in clay or with "no clothing" wording on a woman's portrait: frame from the neck or chest up and let hair, foliage or earth fill the rest.

## Spend (counts; see the xAI console for dollars)
- Pilot 2: 77 images generated (2 probe, 63 first pass, 12 redo), 21 clips totalling about 134 seconds at 1080p.

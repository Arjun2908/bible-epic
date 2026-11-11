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

- 11 Nov 2026 (s01e01b, Genesis 2): Adam and Eve get their faces in this unit: `refs/REF-ADAM.jpg` and `refs/REF-EVE.jpg` (portrait-only sheets, committed 11:46 UTC 11 Nov). Genesis 3 and later units must reuse the ADAM and EVE character text and the blocks TREE_LIFE, TREE_KNOW, HIDE_M, HIDE_F from `episodes/s01e01b/episode.json` word for word. The forbidden fruit is of no named kind (crimson-and-gold, not an apple).
- Genesis 2 is pictured in its own order (man, garden, trees, then beasts and birds in v19, then the woman); nothing is harmonised with Genesis 1.

- 11 Nov 2026 (s01e01b): fixed `pipeline/xai.py`. A content-moderation refusal (HTTP 400) used to be mistaken for a rejected request field, so after one refused picture the rest of that workflow run lost `resolution` and came out at 1280x720 instead of 2816x1584. Check the sizes printed on your contact sheets: regenerate any 1280x720 stills (`-f only=... -f redo=true`) made before this fix. Moderation refuses unclothed full figures even in clay or with "no clothing" wording on a woman's portrait: frame from the neck or chest up and let hair, foliage or earth fill the rest.

- 11 Nov 2026 (s01e01c, Genesis 3): Adam and Eve after the fall. Garments of skin (Genesis 3:21 onward, so Genesis 4 and later): `refs/REF-ADAM-SKIN.jpg`, `refs/REF-EVE-SKIN.jpg`, character keys ADAM_SKIN and EVE_SKIN in `episodes/s01e01c/episode.json` (copy the description text word for word). Fig-leaf stage (3:7-20 only): `refs/REF-ADAM-FIG.jpg`, `refs/REF-EVE-FIG.jpg`. All four are derived from the s01e01b portraits, so the faces match.
- `pipeline/generate.py`: a still whose prompt starts "Character reference sheet" and has `refs` is treated as a new life-stage sheet of the same person (the attached sheet is used for face, hair and build only). Use this for aged or re-costumed versions of a recurring character.

- 11 Nov 2026 (s01e01c, Genesis 3) banked: 80 stills, 80 clips. Lessons:
  - Storage changed for every unit: the workflow now writes `media.zip` (stills, manifest) and `clips-NN.zip` (30 clips each). One unit's stills plus 80 clips came within 1% of the 2 GB asset limit, and `gh release upload --clobber` deletes the old asset before uploading, so an oversized upload would have lost the whole unit's media. Details in `PIPELINE.md` (Storage).
  - Do not cancel a clips run unless you must: clips being written at that moment are left as 0-byte files that later runs skip. After any cancelled or failed run, check every clip with ffprobe and regenerate bad ones with `-f redo=true`.
  - Unnamed fruit: describe it positively (block FRUIT in s01e01c: "a small smooth round fruit the size of a plum, its skin marbled in swirls of deep crimson and gold and its flesh amber-gold"). Writing "not an apple, not a pomegranate" made the model paint apples and pomegranates.
  - Moderation: a woman before Genesis 3:7 passes only when framed from the collarbone up with hair and leaves filling the frame (no "bare", no "no clothing" wording); Eve's fig-leaf covering had to be a collarbone-to-knee leaf dress.
  - Clips: a push-in on a small object repaints it (the bitten fruit became a pomegranate): hold the camera instead. "Light on his brow" becomes a glowing mark, "glint in her eyes ... grows brighter" becomes glowing eyes, "light thickens" becomes fire and smoke, a distant unclothed figure that "comes nearer" arrives wearing a dress. Say what must not happen in the clip prompt.

- 11 Nov 2026 (s01e01b): fixed `pipeline/generate.py`: a clip that failed or timed out left an empty .mp4, and later runs skipped it as done. Empty clips are now removed and retried. If your unit was generated before this fix, look for 0-byte files in `clips/`.
- Size warning: one unit of 79 stills x 3 takes (about 420 MB) plus 79 clips (about 19 MB each) makes a `media.zip` of about 1.95 GB, just under the 2 GB release-asset limit. Keep a unit at or below about 80 clips, and do not pile up redo takes; a bigger zip would fail to upload after `--clobber` has already removed the old one.
- Clip runs take about 35 minutes per 70 clips when several workers generate at once (not 3 minutes per 20).

## Spend (counts; see the xAI console for dollars)
- Pilot 2: 77 images generated (2 probe, 63 first pass, 12 redo), 21 clips totalling about 134 seconds at 1080p.

- 11 Nov 2026 (s01e02a, Genesis 4-5): this unit designs Noah. `refs/REF-NOAH.jpg` is being generated now (weathered man of about fifty, grey-streaked hair and beard, brown wool tunic, darker mantle, sandals): Genesis 6-9 units must wait for it and reuse the NOAH description text from `episodes/s01e02a/episode.json` word for word rather than designing a new Noah. Shem, Ham and Japheth are only small boys here (5:32) and have no sheets: the first unit that needs them as men designs them. Other sheets from this unit: REF-CAIN, REF-ABEL, REF-LAMECH-CAIN, REF-SETH, REF-ENOCH (Seth's line).
- Genesis 4-5 choices: no weapon and no blow shown in 4:8; the mark on Cain is never pictured (Cain is seen only from behind after 4:15); the offerings lie on field stones without fire and favor is shown as light; Enoch's taking is footprints that end. Details in the episode notes.
- Lesson: the shared block `TWO` says "one man and one woman". For two men use a block of your own (s01e02a has `TWOMEN`).

- 11 Nov 2026 (s01e02b, Genesis 6): this unit designs Noah's family and the ark. Sheets (committed 12:16 UTC): `refs/REF-SHEM.jpg`, `refs/REF-HAM.jpg`, `refs/REF-JAPHETH.jpg`, `refs/REF-NOAH-WIFE.jpg` (character keys SHEM, HAM, JAPHETH, NOAH_WIFE in `episodes/s01e02b/episode.json`). Genesis 7-9 units: copy the description text word for word, together with the blocks ARK (the finished ark: a long straight-sided chest ten times as long as high, black with pitch, one door in the long side, a gap under the eaves, no prow, mast or windows), WIFE_S, WIFE_H, WIFE_J (the sons' wives, description only). Noah keeps `refs/REF-NOAH.jpg` unchanged through the flood. The three sons look the same age (birth order is disputed) and share their parents' skin tone; they differ in build, hair and tunic colour (Shem cream, Ham rust-brown, Japheth dark grey).
- Genesis 6 choices: the sons of God are mantled men seen only from behind (no wings, no halos), the Nephilim are silhouettes with nothing to give scale, and "120 years" is pictured only as mortality, so none of the three disputes is resolved. No rain falls and no animals come to the ark in this unit (Genesis 7 tells that). Building pictures run under the commands of 6:14-16. Details in the episode notes.
- s01e01c (Genesis 3): about 291 images (279 kept from 6 runs plus refused ones) and about 580 clip seconds (509 s kept, 10 clips redone, a few lost to a cancelled run).

- 11 Nov 2026 (s01e02b banked, Genesis 6): 195 images, 58 clips (400 s). Lessons: (1) the model paints the ark as a round-hulled ship with a prow whenever it is only named ("the ark", "the side of the ark"), even in the background. Every still that shows any part of it needs the ARK block or the words "a perfectly flat, straight vertical wall of black pitch-coated planks, like the wall of an enormous barn, not curved anywhere"; for a distant ark say "a very long, low, straight-sided rectangular black vessel like a great chest, with squared ends, no prow, no curved hull". (2) Reference sheets: add "The plain warm-grey painted background fills the whole picture from edge to edge: no landscape, no sky, no other people anywhere", or two of three takes get a landscape with small figures. (3) In motion prompts do not write "his eyes shine" near divine light: the eyes glow orange by the last frame. Say the eyes stay natural. (4) A light "walking beside" someone came out once as a glowing human shape (rejected): check every take of WALKLIGHT. (5) Group scenes: count heads on an enlarged take; "exactly eight" gave nine once and a child once.

- 11 Nov 2026 (s01e02c, Genesis 7): no new character sheets. New blocks in `episodes/s01e02c/episode.json` for Genesis 8-9 to copy word for word: ARKFLOAT (the ark afloat, door shut), INSIDE (the lamplit stall deck, no windows), FLATWALL (the ark's side seen close), RAIN, NOLAND, NODEAD. No bodies are shown anywhere; no fish in underwater views. The chapter's two tellings of the entry (7:7-9, 7:13-16) are pictured in the text's order, first under cloud, then in the first rain.
- Lessons from s01e02c: (1) Seen close, "the wall of the ark" is painted as a curved ship's hull every time. Say "a towering, perfectly flat, straight vertical wall of horizontal timber planks coated black with pitch, like the side of an enormous barn" (block FLATWALL) and do not rely on the word ark. (2) People asked to "walk up the ramp into the door" are painted walking out toward the viewer. Say "in side view, climbing from left to right toward the doorway at the top of the ramp on the right", or "seen from behind, going up and away from us". (3) A group of eight comes out right only when every person is listed in order with their own description ("From left to right they are: ...", alternating man, woman); "three sons and their wives" gives seven people or five men. (4) NOPEOPLE is often ignored in disaster scenes (onlookers appear); check each take. (5) Workflow fix 511ac72: stills-only runs between 12:11 and 12:21 UTC failed at "Store full-size media" (empty clip list) and their images were NOT uploaded although the sheets were committed. If your sheets show stills that the clips step cannot find, regenerate them.

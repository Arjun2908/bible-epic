# State

Updated: 11 Nov 2026 (UTC 10:45)

## Done
- Test 1: Genesis 1:1-5, procedural, narrated (made in Claude's workspace, not in this repo).
- Pilot 2, David and Goliath (`p02-david-goliath`): finished film delivered to Arjun, 2 min 23 s. 21 stills (3 takes each, 4 regenerated after review), 21 clips, narration with four voices, score, captions, end card. Whole loop ran through the API with no manual pasting.
- Pipeline: gate, xAI client, generator, contact sheets, narration, mix, assembler, workflow. The API accepted every request field as written (n, aspect_ratio, resolution 2k, b64_json, multi-image `images`, video 1080p).

## In flight
- Nothing.

## Queue
1. Write `story-spine.json`: all 66 books in story order as seasons, episodes and sequences of about 8 minutes, each with its passage range, and replace this queue with the sequence ids in order. Gospels (season 8) go last in the queue. Draft season plan is in the claude.ai project doc `production-process.md`: Beginnings (Gen 1-11), Patriarchs (Gen 12-50, Job), Exodus and Wilderness, Conquest and Judges, United Kingdom, Divided Kingdom and Prophets, Exile and Return, Gospels, Acts and Letters, Revelation; about 48 episodes of about 40 minutes.
2. Then one sequence per run, in queue order.

## Waiting on Arjun (not blocking)
- Feedback on the pilot film, especially the voices, which Claude cannot hear.
- Jesus's face: shown or withheld. Default is withheld.

## Decision log
- 11 Nov 2026: Arjun waived per-step approval. Defaults in `PIPELINE.md`.
- Goliath's height follows the BSB main text (six cubits and a span).
- Pilot 2 ends at 1 Samuel 17:50; verse 51 is not shown.
- Every still gets a motion clip (credits allow it; Arjun asked for more happening on screen).
- Known weakness in pilot 2: the shield bearer's costume differs between shots (feathered headdress in some, crested helmet in others).

## Spend (counts; see the xAI console for dollars)
- Pilot 2: 77 images generated (2 probe, 63 first pass, 12 redo), 21 clips totalling about 134 seconds at 1080p.

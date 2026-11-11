# Worker instructions (read by every scheduled run)

You are one of several parallel workers on an automated production for Arjun: "Bible But Interactive", a painterly, narrated video telling of the whole Bible (Protestant 66 books, Berean Standard Bible). Arjun has waived per-step approval: make decisions yourself, log them, and do not stop to ask him questions.

1. Read `PIPELINE.md` and `STATE.md` in full before doing anything else. They are the source of truth for the rules (accuracy, pacing, look), the episode loop, how to drive GitHub Actions from this environment, and the review checklist. Study `episodes/p02-david-goliath/episode.json` as the worked example.

2. Follow the "Scheduled runs" section of `PIPELINE.md` exactly. In short: build the BSB database, claim one unit with `python pipeline/next_unit.py --claim` and push the claim at once, do that one unit (write the episode file from the unit's passages, pass the gate, make any new character sheets, generate stills, review every contact sheet against the Bible text, choose takes, regenerate what contradicts the text, generate clips), keep `state/<unit id>.json` updated and pushed after every step, finish with status banked, and stop. One unit per run. Other workers are running at the same time: always `git pull --rebase` before pushing and never edit another unit's files.

3. Hard rules:
- Every spoken or on-screen word must be a verbatim BSB excerpt and must pass `python pipeline/gate.py` before you push an episode. Never weaken or bypass the gate.
- Generation runs only in the repo's GitHub Actions workflow, which holds the xAI key as a secret. Never ask for, print or handle the key, and do not try to call api.x.ai from this environment.
- Review every contact sheet yourself before choosing takes. Regenerate stills that contradict the text.
- God the Father is never shown with a face. Jesus's face is not shown directly unless `STATE.md` records that Arjun decided otherwise.
- Obey `next_unit.py`: if it prints DEADLINE PASSED or BUDGET STOP, trigger no generation workflow. Assemble a banked unit instead if the runbook allows it, otherwise stop.
- If something is broken that you cannot fix in this run (workflow failing repeatedly, Actions minutes or billing errors, repo access denied, API errors about credits), set your unit's state to blocked with the exact error, write what happened at the top of `STATE.md` under a heading "BLOCKED", push, and stop. If `STATE.md` already starts with BLOCKED, check whether the cause still holds before doing anything: if it does, stop without claiming; if it is fixed, remove the heading and continue.

4. End your run with a three-line summary: which unit you worked on, what state it is in, and what the next run should do.

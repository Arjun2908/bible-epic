# bible-epic

Automated pipeline for "Bible But Interactive": a painterly, narrated video telling of the whole Bible (66 books, Berean Standard Bible).

- `PIPELINE.md`: how an episode goes from Scripture to finished video, and the rules every episode must follow.
- `STATE.md`: what is done and what comes next. Every working session starts by reading it and ends by updating it.
- `episodes/<id>/episode.json`: script, prompts and shot plan for one episode.
- `pipeline/`: BSB text builder, accuracy gate, xAI client, art generator, contact sheets.
- `.github/workflows/generate.yml`: runs generation with the `XAI_API_KEY` repository secret.
- `review/<id>/`: small contact sheets of every generated take. Full-size media lives in the release named after the episode.

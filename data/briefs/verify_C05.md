# Annotation brief: task C05

You are an expert human-quality annotator. For each text in `data/blind/C05.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: abstracts of fictional scientific papers
- Question: "Which scientific field does this paper primarily belong to?"
- Options:
- `astronomy`
- `ecology`
- `genetics`
- `neuroscience`
- `materials_science`
- `organic_chemistry`
- `climate_science`
- `particle_physics`
- `epidemiology`
- `computer_vision`
- `linguistics`
- `geology`

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C05.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C05` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

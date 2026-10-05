# Annotation brief: task C04

You are an expert human-quality annotator. For each text in `data/blind/C04.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: recipe descriptions from a cooking blog or recipe card
- Question: "Which cuisine does this recipe belong to?"
- Options:
- `italian`
- `mexican`
- `japanese`
- `indian`
- `french`
- `thai`
- `korean`
- `moroccan`

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C04.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C04` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

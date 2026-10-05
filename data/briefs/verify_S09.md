# Annotation brief: task S09

You are an expert human-quality annotator. For each text in `data/blind/S09.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: descriptions of planned or ongoing outdoor activities
- Question: "How risky is the described outdoor activity for the people involved?"
- Options:
- `0`: Negligible risk: routine activity in safe conditions
- `1`: Low risk: minor hazards that are well managed
- `2`: Elevated risk: notable hazards or missing precautions that could cause injury
- `3`: Severe risk: conditions or behavior likely to cause serious injury or death

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 3;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S09.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S09` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

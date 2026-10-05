# Annotation brief: task N09

You are an expert human-quality annotator. For each text in `data/blind/N09.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: notes taken during team meetings
- Question: "Do these meeting notes assign a specific task to a specific person?"
- Options:
- `true`: A named person (or clearly identified individual) is responsible for a concrete action
- `false`: No owner for any action (only discussion, decisions, or 'someone should...')

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is true or false (JSON boolean);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/N09.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify N09` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

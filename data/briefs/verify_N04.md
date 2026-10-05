# Annotation brief: task N04

You are an expert human-quality annotator. For each text in `data/blind/N04.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: claims written by an assistant, checked against a source document
- Question: "Is the claim fully supported by the source?"
- Options:
- `true`: Everything in the claim is stated in or directly entailed by the source
- `false`: The claim contradicts the source, adds details not in it, or overgeneralizes

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is true or false (JSON boolean);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/N04.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify N04` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

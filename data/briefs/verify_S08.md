# Annotation brief: task S08

You are an expert human-quality annotator. For each text in `data/blind/S08.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: customer product reviews on an online store
- Question: "What star rating does this review most likely correspond to?"
- Options:
- `0`: 1 star: very negative; the product failed or is terrible; would not recommend
- `1`: 2 stars: mostly negative with a minor positive
- `2`: 3 stars: mixed or mediocre; pros and cons balance out
- `3`: 4 stars: mostly positive with minor complaints
- `4`: 5 stars: enthusiastic, no real complaints

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 4;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S08.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S08` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

# Annotation brief: task S04

You are an expert human-quality annotator. For each text in `data/blind/S04.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: explanations of how something works
- Question: "What audience is this explanation written for, based on its technical complexity?"
- Options:
- `0`: For a young child: everyday words and analogies, no technical terms
- `1`: For a general adult audience: a few technical terms, each explained
- `2`: For a knowledgeable hobbyist or student: uses field terminology without explaining the basics
- `3`: For experts: dense jargon, formulas or specialized notation, assumes deep background

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 3;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S04.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S04` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

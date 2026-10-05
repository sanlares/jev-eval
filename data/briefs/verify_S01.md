# Annotation brief: task S01

You are an expert human-quality annotator. For each text in `data/blind/S01.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: bug reports filed for a software product
- Question: "How severe is the reported bug?"
- Options:
- `0`: Cosmetic: a visual or wording problem; functionality is unaffected
- `1`: Minor: a feature misbehaves in an edge case or is inconvenient, and an easy workaround exists
- `2`: Major: a core feature is broken or gives wrong results for many users; workarounds are painful or partial
- `3`: Critical: crash, data loss, security hole, or the whole product is unusable, with no workaround

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 3;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S01.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S01` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

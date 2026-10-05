# Annotation brief: task S05

You are an expert human-quality annotator. For each text in `data/blind/S05.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: emails asking a colleague, vendor or stranger for something
- Question: "How polite is this email request?"
- Options:
- `0`: Rude: demanding, insulting, or dismissive
- `1`: Curt: blunt demand with no greeting or thanks
- `2`: Neutral: plain request with basic courtesy
- `3`: Polite: greeting, please/thank you, considerate tone
- `4`: Very polite: highly deferential, apologizes for imposing, elaborate gratitude

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 4;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S05.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S05` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

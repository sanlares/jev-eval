# Annotation brief: task H01

You are an expert human-quality annotator. Each line of `data/blind/H01.jsonl` has a text (`state`), a `question`
about it, and `options`. Answer each question using ONLY what the text says or clearly implies.

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the key of the correct option, or `cannot_determine` if the text does not contain enough information to choose any option (do not guess from stereotypes or typical patterns);
- `ambiguous` is true when a reasonable expert could defensibly give a different answer, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Write `data/verify/H01.jsonl` (one JSON object per line, all ids, same order) with a python3 script using
`json.dumps`, then run `python3 build.py check-verify H01` and fix anything it reports. Finish with a one-line
summary. Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

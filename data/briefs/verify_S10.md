# Annotation brief: task S10

You are an expert human-quality annotator. For each text in `data/blind/S10.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: posts written in hobby forums
- Question: "How experienced in the hobby is the person who wrote this post?"
- Options:
- `0`: Complete beginner: brand new, does not know basic terminology
- `1`: Novice: knows a few basic terms but struggles with fundamentals
- `2`: Advanced beginner: understands the basics and is learning to apply them
- `3`: Intermediate: comfortable with core techniques, working on refinement
- `4`: Advanced amateur: deep technical knowledge, specialized equipment, consistent results
- `5`: Semi-professional: occasionally paid for the work, discusses workflow and clients
- `6`: Seasoned expert: many years of experience, teaches others, industry-level nuance

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 6;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S10.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S10` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

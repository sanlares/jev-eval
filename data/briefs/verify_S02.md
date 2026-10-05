# Annotation brief: task S02

You are an expert human-quality annotator. For each text in `data/blind/S02.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: messages from customers to a company's support chat
- Question: "How frustrated is the customer?"
- Options:
- `0`: Calm and neutral: no sign of annoyance
- `1`: Mildly inconvenienced: slight annoyance but patient and friendly
- `2`: Clearly frustrated: complains about the problem and expresses dissatisfaction
- `3`: Very frustrated: mentions repeated failures, strong complaints, patience running out
- `4`: Furious: hostile, threatens to leave or escalate, may use all caps or insults

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 4;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S02.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S02` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

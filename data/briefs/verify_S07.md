# Annotation brief: task S07

You are an expert human-quality annotator. For each text in `data/blind/S07.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: question-answer pairs from a help forum or chatbot log
- Question: "How well does the answer address the question that was asked? (Judge relevance and completeness, not factual accuracy.)"
- Options:
- `0`: Does not address the question at all: off-topic or a refusal
- `1`: Touches the topic but does not answer what was asked
- `2`: Partially answers: addresses the question but misses an important part
- `3`: Fully answers the question directly and completely

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 3;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S07.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S07` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

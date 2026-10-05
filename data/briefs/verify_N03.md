# Annotation brief: task N03

You are an expert human-quality annotator. For each text in `data/blind/N03.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: retrieved passages in a question-answering system
- Question: "Does the passage contain the information needed to answer the question?"
- Options:
- `true`: The answer can be found in or directly inferred from the passage
- `false`: The passage does not provide the answer, even if it is on a related topic

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is true or false (JSON boolean);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/N03.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify N03` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

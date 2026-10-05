# Annotation brief: task N01

You are an expert human-quality annotator. For each text in `data/blind/N01.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: messages from customers to an online store
- Question: "Is the customer asking for a refund (their money back)?"
- Options:
- `true`: Explicitly or implicitly asks to get their money returned
- `false`: Asks for something else (replacement, repair, exchange, store credit, information), or mentions refunds without requesting one

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is true or false (JSON boolean);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/N01.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify N01` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

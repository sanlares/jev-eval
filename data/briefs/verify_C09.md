# Annotation brief: task C09

You are an expert human-quality annotator. For each text in `data/blind/C09.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: comments posted in online hobby forums
- Question: "How should this forum comment be moderated?"
- Options:
- `acceptable`: Normal on-topic contribution, including strong but civil disagreement
- `harassment`: Insults, demeans or personally attacks another user
- `spam`: Advertising, affiliate links, or unsolicited promotion
- `misinformation`: States clearly false factual claims, e.g. health or science myths, as true
- `off_topic`: Civil but unrelated to the thread's subject

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C09.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C09` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

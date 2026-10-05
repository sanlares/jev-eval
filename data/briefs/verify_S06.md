# Annotation brief: task S06

You are an expert human-quality annotator. For each text in `data/blind/S06.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: messages sent to a company's internal IT helpdesk
- Question: "How urgent is this helpdesk request?"
- Options:
- `0`: Can wait: a question or minor request with no deadline and little impact
- `1`: Soon: affects someone's work or has a deadline within days
- `2`: Immediate: work is stopped for many people, a security incident, or a deadline within hours

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 2;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S06.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S06` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

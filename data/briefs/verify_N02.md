# Annotation brief: task N02

You are an expert human-quality annotator. For each text in `data/blind/N02.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: free-text fields from forms, emails and support tickets
- Question: "Does the text contain personal data that identifies or contacts a specific private individual?"
- Options:
- `true`: Contains at least one of: a personal phone number, personal email address, home street address, government ID number, bank or card number, or a full name together with a date of birth
- `false`: No such data; first names alone, public figures, company phone numbers, or generic addresses like support@company.com do not count

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is true or false (JSON boolean);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/N02.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify N02` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

# Annotation brief: task N08

You are an expert human-quality annotator. For each text in `data/blind/N08.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: messages users type into a customer-service chatbot
- Question: "Is the user asking to talk to a human agent?"
- Options:
- `true`: Requests a person, live agent, representative or phone call with staff
- `false`: Anything else, including complaints about the bot without asking for a person

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is true or false (JSON boolean);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/N08.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify N08` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

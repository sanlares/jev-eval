# Annotation brief: task C02

You are an expert human-quality annotator. For each text in `data/blind/C02.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: short personal messages and social-media posts
- Question: "Which emotion does the writer primarily express?"
- Options:
- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C02.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C02` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

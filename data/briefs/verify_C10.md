# Annotation brief: task C10

You are an expert human-quality annotator. For each text in `data/blind/C10.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: hotel reviews from a travel site
- Question: "Which aspect of the hotel is this review mainly about?"
- Options:
- `cleanliness`: Dirt, hygiene, housekeeping, smells
- `staff_service`: Reception, staff attitude, helpfulness, check-in experience
- `location`: Neighborhood, distance to attractions, transport, surroundings
- `room_comfort`: Bed, room size, furniture, temperature, view
- `food`: Breakfast, restaurant, bar, room service
- `other`: Anything else (e.g. pool, parking, wifi, gym)

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C10.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C10` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

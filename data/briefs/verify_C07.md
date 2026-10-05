# Annotation brief: task C07

You are an expert human-quality annotator. For each text in `data/blind/C07.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: patient-portal messages describing symptoms
- Question: "Which specialty department should this patient message be routed to?"
- Options:
- `cardiology`: Heart and blood vessels: chest pressure, palpitations, blood pressure
- `dermatology`: Skin, hair and nails: rashes, moles, itching, acne
- `gastroenterology`: Digestive system: stomach pain, reflux, bowel problems, liver
- `neurology`: Brain and nerves: headaches, numbness, seizures, memory, dizziness
- `orthopedics`: Bones, joints and muscles: fractures, sprains, back or knee pain
- `ophthalmology`: Eyes and vision: blurred vision, eye pain, floaters, red eye

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C07.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C07` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

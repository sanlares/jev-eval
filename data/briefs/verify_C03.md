# Annotation brief: task C03

You are an expert human-quality annotator. For each text in `data/blind/C03.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: fictional news articles (headline plus first paragraph); no business, markets or economy stories
- Question: "What is the main topic of this news article?"
- Options:
- `politics`: Government, elections, legislation, diplomacy, political parties
- `sports`: Athletes, teams, matches, tournaments, transfers
- `science`: Research discoveries, space, physics, biology, archaeology
- `health`: Medicine, diseases, public health, hospitals, nutrition
- `technology`: Gadgets, software, the internet, AI, cybersecurity, tech products
- `entertainment`: Movies, music, TV, celebrities, games, books, arts
- `crime_justice`: Crimes, police investigations, trials, court rulings
- `weather_environment`: Weather events, natural disasters, climate, pollution, wildlife conservation

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C03.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C03` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

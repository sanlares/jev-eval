# Generation brief: task S08

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: customer product reviews on an online store
- Question that will be asked about each text: "What star rating does this review most likely correspond to?"
- Label values (as they appear in the plan) and their meaning:
- `0` → 1 star: very negative; the product failed or is terrible; would not recommend
- `1` → 2 stars: mostly negative with a minor positive
- `2` → 3 stars: mixed or mediocre; pros and cons balance out
- `3` → 4 stars: mostly positive with minor complaints
- `4` → 5 stars: enthusiastic, no real complaints
- Task-specific notes: mixed_signals: e.g. lists several small gripes but clearly loves it (4-5), or praises packaging but product broke (1-2).

## Plan
`data/plan/S08.jsonl` has 55 rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
`subtopic` (the situation to write about; invent everything else) and `writer` (persona/style; may be null).

Difficulty:
- **easy**: The label is obvious: explicit, typical cues that any reader would recognise.
- **medium**: The label must be inferred from context. Avoid the most obvious keywords and never use the label name itself.
- **hard**: Hard case of the row's hard_type (see 'Hard types' below). The label must STILL be unambiguous to a careful expert reader.

Hard types used in this task:
- **long_irrelevant**: Long text where most content is irrelevant chatter; the signal that determines the label is only one or two sentences somewhere in the middle.
- **mixed_signals**: Contains both positive and negative elements, but the overall stance is still clearly the labeled one.
- **sarcasm**: The literal words say one thing but the intended meaning (which determines the label) is the opposite; a human gets it immediately.

Length:
- **long**: ~180-350 words.
- **medium**: 3-6 sentences (~50-120 words).
- **short**: 1-2 sentences (at most ~40 words).

## Hard rules
1. The assigned label must be clearly the best answer for a careful expert, including hard items. Hard means
   "requires care", never "ambiguous". If a hard_type would make the item ambiguous, adjust it until it isn't.
2. In medium and hard items never use the label name or copy the label description. Never add meta-commentary
   about the label (e.g. "this is a billing issue").
3. Everything is fictional: invent names, companies, places, numbers. No real people, brands or tickers.
4. English only. Make every item distinct: vary names, openings, structure and details; do not reuse templates.
5. The `state` of each item is a plain string.

## Output
Write `data/raw/S08.jsonl` with one JSON object per line, `{"id": ..., "state": ...}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw S08` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.

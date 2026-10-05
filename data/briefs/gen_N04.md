# Generation brief: task N04

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: claims written by an assistant, checked against a source document
- Question that will be asked about each text: "Is the claim fully supported by the source?"
- Label values (as they appear in the plan) and their meaning:
- `true` → Everything in the claim is stated in or directly entailed by the source
- `false` → The claim contradicts the source, adds details not in it, or overgeneralizes
- Task-specific notes: numbers: claim changes a figure (40% vs 14%) (false) or restates it in a different form (true). near_miss: 'some' vs 'all', 'may' vs 'will' (false). negation: claim negates something the source says did not happen (true) or flips a negation (false).

## Plan
`data/plan/N04.jsonl` has 56 rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
`subtopic` (the situation to write about; invent everything else) and `writer` (persona/style; may be null).

Difficulty:
- **easy**: The label is obvious: explicit, typical cues that any reader would recognise.
- **medium**: The label must be inferred from context. Avoid the most obvious keywords and never use the label name itself.
- **hard**: Hard case of the row's hard_type (see 'Hard types' below). The label must STILL be unambiguous to a careful expert reader.

Hard types used in this task:
- **near_miss**: Almost qualifies for the opposite label but differs in one crucial detail.
- **negation**: Use negation or an explicit denial to flip a surface cue (the text mentions X, but says it is not the case / not wanted).
- **numbers**: The correct label depends on reading a number, quantity or measurement correctly.

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
5. The `state` of each item is a JSON object with exactly these keys:
  - `source`: a short fictional source document
  - `claim`: one sentence claim about it

## Output
Write `data/raw/N04.jsonl` with one JSON object per line, `{"id": ..., "state": ...}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw N04` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.

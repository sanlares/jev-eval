# Generation brief: task S02

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: messages from customers to a company's support chat
- Question that will be asked about each text: "How frustrated is the customer?"
- Label values (as they appear in the plan) and their meaning:
- `0` → Calm and neutral: no sign of annoyance
- `1` → Mildly inconvenienced: slight annoyance but patient and friendly
- `2` → Clearly frustrated: complains about the problem and expresses dissatisfaction
- `3` → Very frustrated: mentions repeated failures, strong complaints, patience running out
- `4` → Furious: hostile, threatens to leave or escalate, may use all caps or insults
- Task-specific notes: Distractor: a serious problem described calmly (low frustration) or a trivial problem with high frustration. Sarcasm: polite words, clearly very frustrated.

## Plan
`data/plan/S02.jsonl` has 55 rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
`subtopic` (the situation to write about; invent everything else) and `writer` (persona/style; may be null).

Difficulty:
- **easy**: The label is obvious: explicit, typical cues that any reader would recognise.
- **medium**: The label must be inferred from context. Avoid the most obvious keywords and never use the label name itself.
- **hard**: Hard case of the row's hard_type (see 'Hard types' below). The label must STILL be unambiguous to a careful expert reader.

Hard types used in this task:
- **distractor**: Prominently mention a cue that belongs to a different label, but make the correct label clearly the main point.
- **implicit**: No explicit keywords at all; the label is only inferable from indirect, concrete details.
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
Write `data/raw/S02.jsonl` with one JSON object per line, `{"id": ..., "state": ...}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw S02` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.

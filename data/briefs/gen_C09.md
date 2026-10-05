# Generation brief: task C09

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: comments posted in online hobby forums
- Question that will be asked about each text: "How should this forum comment be moderated?"
- Label values (as they appear in the plan) and their meaning:
- `"acceptable"` → Normal on-topic contribution, including strong but civil disagreement
- `"harassment"` → Insults, demeans or personally attacks another user
- `"spam"` → Advertising, affiliate links, or unsolicited promotion
- `"misinformation"` → States clearly false factual claims, e.g. health or science myths, as true
- `"off_topic"` → Civil but unrelated to the thread's subject
- Task-specific notes: Keep harassment mild (mocking, belittling; no slurs, no threats). Distractor: heated but civil disagreement -> acceptable, or genuinely helpful-sounding advice that is actually a disguised product plug -> spam. Sarcasm: passive-aggressive personal attack -> harassment.

## Plan
`data/plan/C09.jsonl` has 55 rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
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
5. The `state` of each item is a JSON object with exactly these keys:
  - `forum`: forum name/topic
  - `thread_title`: title of the thread
  - `comment`: the comment to moderate

## Output
Write `data/raw/C09.jsonl` with one JSON object per line, `{"id": ..., "state": ...}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw C09` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.

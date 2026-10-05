# Generation brief: task S07

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: question-answer pairs from a help forum or chatbot log
- Question that will be asked about each text: "How well does the answer address the question that was asked? (Judge relevance and completeness, not factual accuracy.)"
- Label values (as they appear in the plan) and their meaning:
- `0` → Does not address the question at all: off-topic or a refusal
- `1` → Touches the topic but does not answer what was asked
- `2` → Partially answers: addresses the question but misses an important part
- `3` → Fully answers the question directly and completely
- Task-specific notes: Distractor: a long, fluent answer about a closely related topic that never answers the actual question (level 1). near_miss: a multi-part question with one part left unanswered (level 2).

## Plan
`data/plan/S07.jsonl` has 58 rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
`subtopic` (the situation to write about; invent everything else) and `writer` (persona/style; may be null).

Difficulty:
- **easy**: The label is obvious: explicit, typical cues that any reader would recognise.
- **medium**: The label must be inferred from context. Avoid the most obvious keywords and never use the label name itself.
- **hard**: Hard case of the row's hard_type (see 'Hard types' below). The label must STILL be unambiguous to a careful expert reader.

Hard types used in this task:
- **distractor**: Prominently mention a cue that belongs to a different label, but make the correct label clearly the main point.
- **long_irrelevant**: Long text where most content is irrelevant chatter; the signal that determines the label is only one or two sentences somewhere in the middle.
- **near_miss**: Almost qualifies for the opposite label but differs in one crucial detail.

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
  - `question`: the user's question
  - `answer`: the response to evaluate

## Output
Write `data/raw/S07.jsonl` with one JSON object per line, `{"id": ..., "state": ...}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw S07` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.

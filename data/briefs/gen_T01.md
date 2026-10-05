# Generation brief: task T01

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: tweets about publicly traded companies, using FICTIONAL company names and $TICKERS
- Question that will be asked about each text: "How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?"
- Label values (as they appear in the plan) and their meaning:
- `0` → Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` → Mildly bearish: leans negative; suggests some decline or underperformance
- `2` → Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` → Mildly bullish: leans positive; suggests some gains
- `4` → Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)
- Task-specific notes: Use cashtags, emojis and trading slang naturally. The level reflects the direction the tweet points to (author's view and/or the news it reports). Level 2 (neutral) is routine or in-line news, balanced takes, or genuinely undecided authors. sarcasm: 'another record quarter, sure 🙄 $XYZ' (bearish). mixed_signals: 'beat on revenue but guidance slashed' with a clear overall lean. jargon_only: 'loading $ABC puts, see you at 12' (bearish), '🚀🚀 $ABC diamond hands' (bullish).

## Plan
`data/plan/T01.jsonl` has 165 rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
`subtopic` (the situation to write about; invent everything else) and `writer` (persona/style; may be null).

Difficulty:
- **easy**: The label is obvious: explicit, typical cues that any reader would recognise.
- **medium**: The label must be inferred from context. Avoid the most obvious keywords and never use the label name itself.
- **hard**: Hard case of the row's hard_type (see 'Hard types' below). The label must STILL be unambiguous to a careful expert reader.

Hard types used in this task:
- **jargon_only**: The stance is conveyed only through domain slang, jargon or emojis, with no plain-English sentiment words.
- **mixed_signals**: Contains both positive and negative elements, but the overall stance is still clearly the labeled one.
- **sarcasm**: The literal words say one thing but the intended meaning (which determines the label) is the opposite; a human gets it immediately.

Length:
- **medium**: a 2-3 tweet thread (use 1/, 2/, 3/)
- **short**: a single tweet (max 280 characters)

## Hard rules
1. The assigned label must be clearly the best answer for a careful expert, including hard items. Hard means
   "requires care", never "ambiguous". If a hard_type would make the item ambiguous, adjust it until it isn't.
2. In medium and hard items never use the label name or copy the label description. Never add meta-commentary
   about the label (e.g. "this is a billing issue").
3. Everything is fictional: invent names, companies, places, numbers. No real people, brands or tickers.
4. English only. Make every item distinct: vary names, openings, structure and details; do not reuse templates.
5. The `state` of each item is a plain string.

## Output
Write `data/raw/T01.jsonl` with one JSON object per line, `{"id": ..., "state": ...}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw T01` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.

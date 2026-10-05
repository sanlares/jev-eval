# Annotation brief: task T01

You are an expert human-quality annotator. For each text in `data/blind/T01.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: tweets about publicly traded companies, using FICTIONAL company names and $TICKERS
- Question: "How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?"
- Options:
- `0`: Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1`: Mildly bearish: leans negative; suggests some decline or underperformance
- `2`: Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3`: Mildly bullish: leans positive; suggests some gains
- `4`: Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 4;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/T01.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify T01` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

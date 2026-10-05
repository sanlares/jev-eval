# Annotation brief: task S03

You are an expert human-quality annotator. For each text in `data/blind/S03.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: messages and short texts from many settings (emails, notes, chats, letters)
- Question: "How formal is the language of this text?"
- Options:
- `0`: Very informal: slang, abbreviations, emojis, no capitalization, chat-style
- `1`: Casual: relaxed everyday language with contractions and a friendly tone
- `2`: Neutral: standard, clear language suitable for most contexts
- `3`: Formal: professional register, complete sentences, polite conventions, few contractions
- `4`: Very formal: ceremonial or legalistic language, elaborate courtesy, rigid structure

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the integer level index, 0 to 4;
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/S03.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify S03` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

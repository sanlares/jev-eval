# Annotation brief: task C08

You are an expert human-quality annotator. For each text in `data/blind/C08.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: programming questions posted on a Q&A site (may include code snippets)
- Question: "Which language or technology is this question primarily about?"
- Options:
- `python`
- `javascript`
- `sql`
- `rust`
- `java`
- `css`
- `bash`
- `git`
- `docker`
- `r`: The R language
- `go`: The Go language
- `cpp`: C++

For every item output `{"id": ..., "label": ..., "ambiguous": ..., "note": ...}` where
- `label` is the option key exactly as written (string);
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/C08.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify C08` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).

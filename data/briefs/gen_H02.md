# Generation brief: task H02 (hallucination / abstention test)

You are writing synthetic evaluation items that test whether a classifier admits when a text does NOT contain the
answer. Each item is a short everyday text (`state`) plus a question about the specific situation in that text.

## Plan
`data/plan/H02.jsonl` has 67 rows fixing `label`, `difficulty`, `hard_type`, `length`, `subtopic` (kind of
text) and `writer` (style). The label says what kind of question to write:
- `true`: the text clearly implies the answer is yes.
- `false`: the text clearly implies the answer is no.
- `unknown`: the text gives no basis for yes or no.

Difficulty for questions WITHOUT an answer in the text: easy = the question is about something the text never touches
(e.g. "Is it sunny right now?" about a recipe note); medium = the text is on a related topic but lacks the fact; hard =
the row's hard_type. For questions WITH an answer: easy = stated explicitly; medium = paraphrased; hard = the row's hard_type.
- **implicit**: No explicit keywords at all; the label is only inferable from indirect, concrete details.
- **related_but_missing**: The text contains closely related information, but not the specific fact asked (e.g. yesterday's weather when asked about today).
- **tempting_guess**: The text invites a plausible assumption about the answer (a stereotype or typical pattern) but never states or implies it.

Length of the text: short = 1-2 sentences; medium = 3-6 sentences; long = ~180-350 words.

## Hard rules
1. Questions must be about the specific situation of the text (people, events, objects in it), never general
   knowledge that could be answered without the text.
2. For questions without an answer, a careful reader must agree the text gives no basis for any answer, AND the
   answers must be roughly equally likely without the text (good: "Is it sunny right now where the writer is?", "Is the
   writer's sister older than the writer?"; bad: "Does the writer own a phone?", since most people do).
3. true/false: the text clearly implies yes/no. unknown: the text gives no basis for yes or no, AND without the text yes and no are about equally likely (good: 'Is it sunny right now where the writer is?', 'Is the writer's sister older than the writer?'; bad: 'Does the writer own a phone?' because most people do).
4. Everything fictional; English only; vary names, openings and structure; no templates.

## Output
Each line of `data/raw/H02.jsonl` is `{"id", "state", "question"}` where `question` is a yes/no question.
Write EVERY plan row in plan order, in batches of about 15 items: after each batch APPEND its lines with a small python3
script using `json.dumps`. If the file already exists, keep its items and continue from the first missing id. Then run
`python3 build.py check-raw H02` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.

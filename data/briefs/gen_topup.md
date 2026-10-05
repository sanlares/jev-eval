# Top-up generation brief

Some items were removed after quality review, so a few extra rows were appended to these plans.
For each task below: read `data/briefs/gen_TASK.md` for the task context and rules, then write ONLY the new ids
listed here, APPENDING them to `data/raw/TASK.jsonl` (keep existing lines untouched), then run
`python3 build.py check-raw TASK` until it prints OK. Follow the extra guidance for each label closely:
these rows exist precisely because earlier items sat on the border between two labels.

## C02
- label `"surprise"` -> ids C02_056 .. C02_057 (2 rows). Astonishment at something unexpected WITHOUT a dominant positive or negative feeling (not delight, not fear, not annoyance).

## C03
- label `"science"` -> ids C03_058 .. C03_059 (2 rows). A research/discovery story that is clearly science (not a technology product, not climate/weather/environment).

## C08
- label `"python"` -> ids C08_062 .. C08_063 (2 rows). Include unmistakable Python cues (def/import syntax, pip, pandas/numpy, IndentationError, etc.), no other language mentioned.

## S02
- label `1` -> ids S02_055 .. S02_062 (8 rows). Level 1: the customer explicitly shows SLIGHT annoyance (e.g. 'a bit annoying', 'slightly frustrating', a small sigh) but stays patient and friendly. Do NOT write a fully calm message.
- label `2` -> ids S02_063 .. S02_064 (2 rows). Level 2: explicit complaint and dissatisfaction, but no repeated-failure pattern, no ultimatum, no hostility.

## S03
- label `2` -> ids S03_055 .. S03_060 (6 rows). Level 2 (neutral): plain standard language for any context: complete sentences, no slang, no emojis, few or no contractions, no chatty asides, no elaborate courtesy formulas.
- label `4` -> ids S03_061 .. S03_062 (2 rows). Level 4 (very formal): ceremonial or legalistic phrasing ('hereby', 'pursuant to', 'it is with the utmost regret', formal notices or invitations).

## S09
- label `1` -> ids S09_058 .. S09_060 (3 rows). Level 1 (low): the activity has one or two named minor hazards that are explicitly managed; not trivially safe (not a supervised bunny hill), not dangerous.
- label `2` -> ids S09_061 .. S09_062 (2 rows). Level 2 (elevated): a notable hazard or missing precaution that could cause injury, but not life-threatening.

## H02
- label `"unknown"` -> ids H02_067 .. H02_081 (15 rows). The text gives NO basis for yes or no, AND without the text yes and no are about 50/50. Good: 'Is it sunny right now where the writer is?', 'Is the writer's sister older than the writer?', 'Did the meeting start before 10am?' (no time info), 'Is the writer's apartment on an even-numbered floor?'. BAD, never use: handedness, owning common items, specific colors, 'did X mention topic Y' (usually no), 'does a product work on a common surface' (usually yes), anything the text hints at.

## S05
- label `2` -> ids S05_055 .. S05_063 (9 rows). Level 2 (neutral): a plain request with minimal courtesy: at most one 'please' or 'could you'. NO greeting, NO thanks, NO apology, NO warmth or considerate asides, and nothing blunt or rude either.

## S07
- label `0` -> ids S07_058 .. S07_064 (7 rows). Level 0: the answer does NOT address the question at all: either a refusal/deflection ('I can't help with that', 'ask someone else') or an answer about a clearly DIFFERENT subject (e.g. question about cooking, answer about a car). Never write an answer on a neighbouring topic of the same domain (that is level 1).
- label `2` -> ids S07_065 .. S07_068 (4 rows). Level 2: the question has two explicit parts; the answer fully and directly answers one part and says nothing about the other.

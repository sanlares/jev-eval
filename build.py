"""Dataset pipeline (stdlib only, so agents can run it with plain python3).

  python3 build.py briefs               # write generation + annotation briefs
  python3 build.py check-raw TASK [--part K/N]  # validate a generator's output (or slice K of N)
  python3 build.py join-parts TASK      # concatenate data/raw/TASK.part*.jsonl and validate
  python3 build.py blind [TASK...]      # write label-free copies for blind verification
  python3 build.py check-verify TASK    # validate an annotator's output
  python3 build.py merge                # agreement stats + disagreement queue + audit sample
  python3 build.py final [--check]      # apply decisions, dedupe, balanced trim, write data/final (+ CSVs)
  python3 build.py human-check          # compare YOUR answers in data/final/revision_humana.csv with the ground truth
"""
import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from specs import (ABSTAIN_KEY, ABSTAIN_TEXT, DIFFICULTY_GUIDE, FINAL_N, HARD_TYPE_GUIDE, LENGTH_GUIDE, TASKS,
                   jev_questions, labels, tweet_targets)

ROOT = Path(__file__).parent
D = ROOT / "data"
AUDIT_SHARE = 0.05
DEDUPE_JACCARD = 0.6


def load_env():
    """Read KEY=VALUE lines from jev_eval/.env (without overriding real env vars). JET_KEY is accepted as the TypeSafe key."""
    import os
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip().removeprefix("export ").strip(), v.strip().strip("'\""))
    if not os.environ.get("TYPESAFE_API_KEY") and os.environ.get("JET_KEY"):
        os.environ["TYPESAFE_API_KEY"] = os.environ["JET_KEY"]


async def call_with_retries(make_call, is_retryable, max_attempts=6):
    """Run `await make_call()` with our own retry loop (SDK retries are turned off so they can't hide in the timing).
    Returns (result, latency in seconds of the successful attempt only, number of attempts)."""
    import asyncio
    import time
    for attempt in range(1, max_attempts + 1):
        t0 = time.perf_counter()
        try:
            result = await make_call()
            return result, time.perf_counter() - t0, attempt
        except Exception as e:  # noqa: BLE001 - re-raised below unless the caller says it is retryable
            if attempt == max_attempts or not is_retryable(e):
                raise
            await asyncio.sleep(min(30.0, 0.5 * 2 ** (attempt - 1)) + random.random() * 0.25)


def read_jsonl(p):
    p = Path(p)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def write_jsonl(p, rows):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def state_text(state):
    return state if isinstance(state, str) else "\n".join(f"{k}: {v}" for k, v in state.items())


def label_meanings(task):
    t = TASKS[task]
    if t["primitive"] == "choice":
        return {k: (v or k.replace("_", " ")) for k, v in t["criteria"].items()}
    if t["primitive"] == "score":
        return dict(enumerate(t["criteria"]))
    if t["primitive"] == "noul":
        return {True: t["criteria"]["true"], False: t["criteria"]["false"]}
    return dict(enumerate(t["level_guide"]))


def annotation_question(task):
    """What the blind annotator answers: identical to Jev's question (tweets: the 5-level score)."""
    q = jev_questions(task)
    return q["sentiment"] if TASKS[task]["primitive"] == "tweets" else q["answer"]


def label_format(task):
    p = TASKS[task]["primitive"]
    n = len(labels(task))
    return {"choice": "the option key exactly as written (string)",
            "score": f"the integer level index, 0 to {n - 1}",
            "noul": "true or false (JSON boolean)",
            "tweets": "the integer level index, 0 to 4"}[p]


def is_halluc(task):
    return TASKS[task]["primitive"] == "hallucination"


def intended_label(task, plan_row, raw_row):
    """Ground-truth label before adjudication. H01: the generator's correct option, or the abstain option."""
    if is_halluc(task) and TASKS[task]["qtype"] == "choice":
        return raw_row.get("answer") if plan_row["label"] == "answerable" else ABSTAIN_KEY
    return plan_row["label"]


# ------------------------------------------------------------------ briefs

def gen_brief_halluc(task):
    t = TASKS[task]
    plan = read_jsonl(D / "plan" / f"{task}.jsonl")
    choice = t["qtype"] == "choice"
    slots = ("- `answerable`: exactly ONE of your options is clearly correct according to the text.\n"
             "- `unanswerable`: the text gives NO basis to choose any option; every option stays plausible."
             if choice else
             "- `true`: the text clearly implies the answer is yes.\n- `false`: the text clearly implies the answer is no.\n"
             "- `unknown`: the text gives no basis for yes or no.")
    fields = ('`{"id", "state", "question", "options", "answer"}` where `options` is an object with 3 or 4 plausible '
              'answers (short snake_case keys -> one-line description) and `answer` is the correct key for answerable '
              'rows or null for unanswerable rows. NEVER include a "can\'t tell / not enough info" option: the system '
              f'adds `{ABSTAIN_KEY}` automatically.'
              if choice else '`{"id", "state", "question"}` where `question` is a yes/no question.')
    hard = "\n".join(f"- **{h}**: {HARD_TYPE_GUIDE[h]}" for h in sorted({r["hard_type"] for r in plan if r["hard_type"]}))
    return f"""# Generation brief: task {task} (hallucination / abstention test)

You are writing synthetic evaluation items that test whether a classifier admits when a text does NOT contain the
answer. Each item is a short everyday text (`state`) plus a question about the specific situation in that text.

## Plan
`data/plan/{task}.jsonl` has {len(plan)} rows fixing `label`, `difficulty`, `hard_type`, `length`, `subtopic` (kind of
text) and `writer` (style). The label says what kind of question to write:
{slots}

Difficulty for questions WITHOUT an answer in the text: easy = the question is about something the text never touches
(e.g. "Is it sunny right now?" about a recipe note); medium = the text is on a related topic but lacks the fact; hard =
the row's hard_type. For questions WITH an answer: easy = stated explicitly; medium = paraphrased; hard = the row's hard_type.
{hard}

Length of the text: short = 1-2 sentences; medium = 3-6 sentences; long = ~180-350 words.

## Hard rules
1. Questions must be about the specific situation of the text (people, events, objects in it), never general
   knowledge that could be answered without the text.
2. For questions without an answer, a careful reader must agree the text gives no basis for any answer, AND the
   answers must be roughly equally likely without the text (good: "Is it sunny right now where the writer is?", "Is the
   writer's sister older than the writer?"; bad: "Does the writer own a phone?", since most people do).
3. {t['gen_notes']}
4. Everything fictional; English only; vary names, openings and structure; no templates.

## Output
Each line of `data/raw/{task}.jsonl` is {fields}
Write EVERY plan row in plan order, in batches of about 15 items: after each batch APPEND its lines with a small python3
script using `json.dumps`. If the file already exists, keep its items and continue from the first missing id. Then run
`python3 build.py check-raw {task}` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.
"""


def verify_brief_halluc(task):
    choice = TASKS[task]["qtype"] == "choice"
    how = (f"`label` is the key of the correct option, or `{ABSTAIN_KEY}` if the text does not contain enough "
           "information to choose any option (do not guess from stereotypes or typical patterns)"
           if choice else
           '`label` is true if the text clearly implies yes, false if it clearly implies no, or the string "unknown" '
           "if the text gives no basis to answer (do not guess from stereotypes or typical patterns)")
    return f"""# Annotation brief: task {task}

You are an expert human-quality annotator. Each line of `data/blind/{task}.jsonl` has a text (`state`), a `question`
about it{", and `options`" if choice else ""}. Answer each question using ONLY what the text says or clearly implies.

For every item output `{{"id": ..., "label": ..., "ambiguous": ..., "note": ...}}` where
- {how};
- `ambiguous` is true when a reasonable expert could defensibly give a different answer, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Write `data/verify/{task}.jsonl` (one JSON object per line, all ids, same order) with a python3 script using
`json.dumps`, then run `python3 build.py check-verify {task}` and fix anything it reports. Finish with a one-line
summary. Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).
"""


def gen_brief(task):
    if is_halluc(task):
        return gen_brief_halluc(task)
    t = TASKS[task]
    plan = read_jsonl(D / "plan" / f"{task}.jsonl")
    meanings = "\n".join(f"- `{json.dumps(k)}` → {v}" for k, v in label_meanings(task).items())
    used_hard = sorted({r["hard_type"] for r in plan if r["hard_type"]})
    hard = "\n".join(f"- **{h}**: {HARD_TYPE_GUIDE[h]}" for h in used_hard)
    lengths = t.get("length_guide", LENGTH_GUIDE)
    length = "\n".join(f"- **{k}**: {lengths[k]}" for k in sorted({r["length"] for r in plan}))
    if "state_format" in t:
        fmt = ("a JSON object with exactly these keys:\n" +
               "\n".join(f"  - `{k}`: {v}" for k, v in t["state_format"].items()))
    else:
        fmt = "a plain string."
    q = annotation_question(task)
    return f"""# Generation brief: task {task}

You are writing synthetic **evaluation items** for a text classifier. Every item has a PRE-ASSIGNED
ground-truth label. Your job is to write the text so that a careful expert would assign exactly that label.

## The task
- Domain: {t['domain']}
- Question that will be asked about each text: "{q['instructions']}"
- Label values (as they appear in the plan) and their meaning:
{meanings}
- Task-specific notes: {t['gen_notes']}

## Plan
`data/plan/{task}.jsonl` has {len(plan)} rows. Each row fixes: `label`, `difficulty`, `hard_type`, `length`,
`subtopic` (the situation to write about; invent everything else) and `writer` (persona/style; may be null).

Difficulty:
- **easy**: {DIFFICULTY_GUIDE['easy']}
- **medium**: {DIFFICULTY_GUIDE['medium']}
- **hard**: {DIFFICULTY_GUIDE['hard']}

Hard types used in this task:
{hard}

Length:
{length}

## Hard rules
1. The assigned label must be clearly the best answer for a careful expert, including hard items. Hard means
   "requires care", never "ambiguous". If a hard_type would make the item ambiguous, adjust it until it isn't.
2. In medium and hard items never use the label name or copy the label description. Never add meta-commentary
   about the label (e.g. "this is a billing issue").
3. Everything is fictional: invent names, companies, places, numbers. No real people, brands or tickers.
4. English only. Make every item distinct: vary names, openings, structure and details; do not reuse templates.
5. The `state` of each item is {fmt}

## Output
Write `data/raw/{task}.jsonl` with one JSON object per line, `{{"id": ..., "state": ...}}`, for EVERY plan row, in
plan order. Work in batches of about 15 items: after each batch, APPEND its lines to the file with a small python3
script using `json.dumps` (avoids escaping errors), so progress is saved. If the file already exists when you start,
keep the items in it and continue from the first plan id that is missing. When all rows are written, run
`python3 build.py check-raw {task}` and fix anything it reports. Finish with a one-line summary.
Apart from your plan file and your output file, do not read or write anything in `data/`.
"""


def verify_brief(task):
    if is_halluc(task):
        return verify_brief_halluc(task)
    t = TASKS[task]
    q = annotation_question(task)
    crit = q["criteria"]
    if isinstance(crit, list):
        opts = "\n".join(f"- `{i}`: {c}" for i, c in enumerate(crit))
    else:
        opts = "\n".join(f"- `{k}`" + (f": {v}" if v else "") for k, v in crit.items())
    return f"""# Annotation brief: task {task}

You are an expert human-quality annotator. For each text in `data/blind/{task}.jsonl` (fields `id`, `state`),
answer the question below exactly as a careful expert would, judging only the text itself.

- Context: {t['domain']}
- Question: "{q['instructions']}"
- Options:
{opts}

For every item output `{{"id": ..., "label": ..., "ambiguous": ..., "note": ...}}` where
- `label` is {label_format(task)};
- `ambiguous` is true when a reasonable expert could defensibly choose a different option, else false;
- `note` is one short sentence explaining the choice when ambiguous (else an empty string).

Label every item independently; do not try to balance labels. Write `data/verify/{task}.jsonl` (one JSON object
per line, all ids, same order) with a python3 script using `json.dumps`, then run
`python3 build.py check-verify {task}` and fix anything it reports. Finish with a one-line summary.
Do not open any other file in `data/` (in particular never open data/plan, data/raw or other briefs).
"""


def cmd_briefs():
    for task in TASKS:
        (D / "briefs").mkdir(parents=True, exist_ok=True)
        (D / "briefs" / f"gen_{task}.md").write_text(gen_brief(task))
        (D / "briefs" / f"verify_{task}.md").write_text(verify_brief(task))
    print(f"wrote {2 * len(TASKS)} briefs to data/briefs/")


# ------------------------------------------------------------------ checks

def cmd_check_raw(task, part=None):
    """part='K/N' validates data/raw/<task>.partK.jsonl against the K-th of N contiguous slices of the plan."""
    plan = read_jsonl(D / "plan" / f"{task}.jsonl")
    path = D / "raw" / f"{task}.jsonl"
    if part:
        k, n = map(int, part.split("/"))
        size = -(-len(plan) // n)
        plan, path = plan[(k - 1) * size:k * size], D / "raw" / f"{task}.part{k}.jsonl"
    try:
        raw = read_jsonl(path)
    except json.JSONDecodeError as e:
        sys.exit(f"FAIL: invalid JSON line: {e}")
    errs = []
    ids = [r.get("id") for r in raw]
    missing = [r["id"] for r in plan if r["id"] not in set(ids)]
    if missing:
        errs.append(f"missing ids: {missing}")
    extra = set(ids) - {r["id"] for r in plan}
    if extra:
        errs.append(f"unknown ids: {sorted(extra)}")
    dup = [i for i, c in Counter(ids).items() if c > 1]
    if dup:
        errs.append(f"duplicate ids: {dup}")
    keys = TASKS[task].get("state_format")
    for r in raw:
        s = r.get("state")
        if keys:
            if not isinstance(s, dict) or set(s) != set(keys) or not all(str(v).strip() for v in s.values()):
                errs.append(f"{r.get('id')}: state must be an object with non-empty keys {sorted(keys)}")
        elif not isinstance(s, str) or len(s.strip()) < 3:
            errs.append(f"{r.get('id')}: state must be a non-empty string")
    if is_halluc(task):
        slot = {r["id"]: r["label"] for r in plan}
        for r in raw:
            if not isinstance(r.get("question"), str) or len(r["question"].strip()) < 5:
                errs.append(f"{r.get('id')}: missing question")
            if TASKS[task]["qtype"] == "choice":
                opts = r.get("options")
                if not isinstance(opts, dict) or not 3 <= len(opts) <= 4 or ABSTAIN_KEY in opts:
                    errs.append(f"{r.get('id')}: options must be an object with 3-4 keys (without {ABSTAIN_KEY})")
                elif slot.get(r.get("id")) == "answerable" and r.get("answer") not in opts:
                    errs.append(f"{r.get('id')}: answerable row needs answer = one of the option keys")
                elif slot.get(r.get("id")) == "unanswerable" and r.get("answer") is not None:
                    errs.append(f"{r.get('id')}: unanswerable row needs answer = null")
    texts = [state_text(r["state"]).strip().lower() for r in raw if r.get("state")]
    exact_dups = [t[:60] for t, c in Counter(texts).items() if c > 1]
    if exact_dups:
        errs.append(f"identical texts: {exact_dups}")
    if errs:
        sys.exit("FAIL\n" + "\n".join(errs[:30]))
    print(f"OK {task}: {len(raw)} items")


def cmd_join_parts(task):
    parts = sorted((D / "raw").glob(f"{task}.part*.jsonl"))
    write_jsonl(D / "raw" / f"{task}.jsonl", [r for p in parts for r in read_jsonl(p)])
    cmd_check_raw(task)


def cmd_check_verify(task):
    blind = read_jsonl(D / "blind" / f"{task}.jsonl")
    try:
        ver = read_jsonl(D / "verify" / f"{task}.jsonl")
    except json.JSONDecodeError as e:
        sys.exit(f"FAIL: invalid JSON line: {e}")
    allowed = labels(task)
    if is_halluc(task):
        allowed = [True, False, "unknown"]
    per_item = {r["id"]: list(r["options"]) for r in blind if "options" in r}
    errs = []
    got = {r.get("id") for r in ver}
    missing = [r["id"] for r in blind if r["id"] not in got]
    if missing:
        errs.append(f"missing ids: {missing}")
    for r in ver:
        lab = r.get("label")
        ok_set = per_item.get(r.get("id"), allowed)
        ok = any(lab == a and type(lab) is type(a) for a in ok_set)
        if not ok:
            errs.append(f"{r.get('id')}: label {lab!r} not in {ok_set}")
        if not isinstance(r.get("ambiguous"), bool):
            errs.append(f"{r.get('id')}: ambiguous must be true/false")
    if errs:
        sys.exit("FAIL\n" + "\n".join(errs[:30]))
    print(f"OK {task}: {len(ver)} annotations")


def cmd_blind(tasks):
    for task in tasks or TASKS:
        raw = read_jsonl(D / "raw" / f"{task}.jsonl")
        if raw:
            rows = []
            for r in raw:
                b = {"id": r["id"], "state": r["state"]}
                if is_halluc(task):
                    b["question"] = r["question"]
                    if "options" in r:
                        b["options"] = {**r["options"], ABSTAIN_KEY: ABSTAIN_TEXT}
                rows.append(b)
            write_jsonl(D / "blind" / f"{task}.jsonl", rows)
            print(f"blind {task}: {len(raw)}")


# ------------------------------------------------------------------ merge / adjudication queue

def cohen_kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def needs_review(task, intended, verified, ambiguous):
    if ambiguous:
        return True
    if TASKS[task]["primitive"] in ("score", "tweets"):
        tol = 1 if len(labels(task)) >= 7 else 0  # 7-level scale: adjacent-level disagreement tolerated
        return abs(intended - verified) > tol
    return intended != verified


def cmd_merge():
    queue, audit, stats = [], [], []
    for task in TASKS:
        plan = {r["id"]: r for r in read_jsonl(D / "plan" / f"{task}.jsonl")}
        raw = {r["id"]: r for r in read_jsonl(D / "raw" / f"{task}.jsonl")}
        ver = {r["id"]: r for r in read_jsonl(D / "verify" / f"{task}.jsonl")}
        ids = [i for i in plan if i in raw and i in ver]
        if not ids:
            continue
        a = [intended_label(task, plan[i], raw[i]) for i in ids]
        b = [ver[i]["label"] for i in ids]
        agreed = []
        for i, intended in zip(ids, a):
            p, v = plan[i], ver[i]
            row = {"id": i, "task_id": task, "intended": intended, "verifier": v["label"],
                   "ambiguous": v["ambiguous"], "note": v.get("note", ""), "difficulty": p["difficulty"],
                   "hard_type": p["hard_type"], "state": raw[i]["state"]}
            if is_halluc(task):
                row["question"], row["options"] = raw[i]["question"], raw[i].get("options")
            (queue if needs_review(task, intended, v["label"], v["ambiguous"]) else agreed).append(row)
        audit += random.Random(f"audit-{task}").sample(agreed, max(1, round(AUDIT_SHARE * len(agreed))))
        exact = sum(x == y for x, y in zip(a, b)) / len(ids)
        stats.append(dict(task=task, n=len(ids), exact_agree=round(exact, 3), kappa=round(cohen_kappa(a, b), 3),
                          flagged=sum(q["task_id"] == task for q in queue)))
    write_jsonl(D / "review" / "queue.jsonl", queue)
    write_jsonl(D / "review" / "audit.jsonl", audit)
    json.dump(stats, open(D / "review" / "agreement.json", "w"), indent=1)
    for s in stats:
        print(s)
    print(f"flagged for adjudication: {len(queue)} | audit sample: {len(audit)}")


# ------------------------------------------------------------------ final

def shingles(text, k=5):
    t = re.sub(r"\s+", " ", text.lower())
    return {t[i:i + k] for i in range(max(1, len(t) - k + 1))}


def label_in_text(task, label, text):
    if TASKS[task]["primitive"] != "choice":
        return None
    return label.replace("_", " ") in text.lower()


def cmd_final(check_only=False):
    decisions = {d["id"]: d for d in read_jsonl(D / "review" / "decisions.jsonl")}
    rng = random.Random(42)
    out, report = defaultdict(list), []
    for task in TASKS:
        t = TASKS[task]
        plan = read_jsonl(D / "plan" / f"{task}.jsonl")
        raw = {r["id"]: r for r in read_jsonl(D / "raw" / f"{task}.jsonl")}
        ver = {r["id"]: r for r in read_jsonl(D / "verify" / f"{task}.jsonl")}
        items, dropped, relabeled = [], Counter(), 0
        for p in plan:
            if p["id"] not in raw:
                dropped["not_generated"] += 1
                continue
            if p["id"] not in ver:  # every final item must have passed blind verification
                dropped["unverified"] += 1
                continue
            label, dec = intended_label(task, p, raw[p["id"]]), decisions.get(p["id"])
            if dec is None and p["id"] in ver and needs_review(task, label, ver[p["id"]]["label"], ver[p["id"]]["ambiguous"]):
                dropped["unadjudicated"] += 1
                continue
            if dec and dec["action"] == "drop":
                dropped["adjudicated_drop"] += 1
                continue
            if dec and dec["action"] == "relabel":
                label, relabeled = dec["label"], relabeled + 1
            it = {**p, "label": label, "plan_label": p["label"], "state": raw[p["id"]]["state"],
                  "review": dec["source"] if dec else None}
            if is_halluc(task):
                it["question"] = raw[p["id"]]["question"]
                if "options" in raw[p["id"]]:
                    it["options"] = raw[p["id"]]["options"]
            items.append(it)
        # near-duplicate removal (keeps the first occurrence)
        kept, sh = [], []
        for it in items:
            s = shingles(state_text(it["state"]))
            if any(len(s & o) / len(s | o) > DEDUPE_JACCARD for o in sh):
                dropped["near_duplicate"] += 1
                continue
            kept.append(it)
            sh.append(s)
        # balanced trim to the per-label targets fixed by the plan (final counts)
        from make_plan import target_counts
        targets = target_counts(task, random.Random(f"42-{task}"))
        by_label = defaultdict(list)  # hallucination tasks are balanced by plan slot (answerable/unanswerable)
        for it in kept:
            by_label[json.dumps(it["plan_label"] if is_halluc(task) else it["label"])].append(it)
        final = []
        for lab, n in targets.items():
            pool = by_label.get(json.dumps(lab), [])
            rng.shuffle(pool)
            final += pool[:n]
            if len(pool) < n:
                dropped[f"short_label_{lab}"] += n - len(pool)
        final.sort(key=lambda r: r["id"])
        for it in final:
            it["label_in_text"] = label_in_text(task, it["label"], state_text(it["state"]))
            if t["primitive"] == "tweets":
                it["targets"] = tweet_targets(it["label"])
            if t["primitive"] == "choice":
                it["n_options"] = len(t["criteria"])
            if t["primitive"] in ("score", "tweets"):
                it["n_levels"] = len(labels(task))
            it.pop("subtopic", None), it.pop("writer", None)
        out[t["primitive"]] += final
        report.append(dict(task=task, generated=len(raw), final=len(final), target=FINAL_N[t["primitive"]],
                           relabeled=relabeled, **dropped))
    problems = [r for r in report if r["final"] != r["target"]]
    for r in report:
        print(r)
    if check_only:
        sys.exit(f"CHECK FAILED: {len(problems)} tasks off target" if problems else "CHECK OK")
    for prim, rows in out.items():
        write_jsonl(D / "final" / f"{prim}.jsonl", rows)
        write_csv(D / "final" / f"{prim}.csv", [csv_row(r) for r in rows])
    write_csv(D / "final" / "dataset_completo.csv", [csv_row(r) for rows in out.values() for r in rows])
    write_csv(D / "final" / "revision_humana.csv", human_sample(out))
    json.dump({k: jev_questions(k) for k in TASKS}, open(D / "final" / "questions.json", "w"), indent=1)
    json.dump(report, open(D / "final" / "build_report.json", "w"), indent=1)
    write_card(out, report, decisions)
    print({k: len(v) for k, v in out.items()}, "| off-target tasks:", [r["task"] for r in problems])


def write_card(out, report, decisions):
    """data/final/DATASET.md: how the ground truth was built, with the numbers."""
    agree = {a["task"]: a for a in json.load(open(D / "review" / "agreement.json"))}
    audit = [d for d in decisions.values() if d["source"] == "audit"]
    audit_err = sum(d["action"] != "keep" for d in audit)
    queue = [d for d in decisions.values() if d["source"] == "queue"]
    lines = ["# Dataset card (generated by `build.py final`)", "",
             f"Final items: **{sum(len(v) for v in out.values())}** "
             f"({', '.join(f'{k}: {len(v)}' for k, v in out.items())}).", "",
             "Every item went through: plan with the label fixed in advance -> text written by an agent -> "
             "blind labelling by another agent -> adjudication (Claude Opus, human-supervised) of every disagreement "
             "or case flagged as ambiguous -> random audit of 5% of the agreed cases.", "",
             f"- Cases reviewed in adjudication: {len(queue)} "
             f"(kept {sum(d['action'] == 'keep' for d in queue)}, relabelled {sum(d['action'] == 'relabel' for d in queue)}, "
             f"dropped {sum(d['action'] == 'drop' for d in queue)}).",
             f"- Random audit: {len(audit)} items reviewed, {audit_err} with errors. "
             f"95% upper bound on the label error of non-adjudicated items: ~{100 * (3 if audit_err == 0 else audit_err + 2) / max(1, len(audit)):.1f}%.", "",
             "| task | generated | final | exact agreement (blind annotator) | kappa | relabelled | dropped |",
             "|---|---|---|---|---|---|---|"]
    for r in report:
        a = agree.get(r["task"], {})
        drops = sum(v for k, v in r.items() if k in ("adjudicated_drop", "near_duplicate"))
        lines.append(f"| {r['task']} | {r['generated']} | {r['final']} | {a.get('exact_agree', '-')} | {a.get('kappa', '-')} | "
                     f"{r.get('relabeled', 0)} | {drops} |")
    lines += ["", "Notes: agreement is measured against the planned label BEFORE adjudication. On ordinal scales, "
              "disagreements are usually one level apart. Items marked `topup: true` were added to refill levels "
              "that fell short after drops (medium difficulty).", ""]
    (D / "final" / "DATASET.md").write_text("\n".join(lines))


# ------------------------------------------------------------------ CSV export + human review

def cell(v):
    return v if isinstance(v, (str, int, float)) or v is None else json.dumps(v, ensure_ascii=False)


def write_csv(path, rows):
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: cell(r.get(k)) for k in cols})


def question_for_human(it):
    """The single question a person answers for an item, with its options, as plain text."""
    qs = jev_questions(it["task_id"], it)
    q = qs.get("sentiment") or qs["answer"]
    crit = q.get("criteria")
    if isinstance(crit, list):
        opts = " | ".join(f"{i} = {c}" for i, c in enumerate(crit))
    elif crit is None or set(crit) == {"true", "false"}:
        opts = "true | false" + (" | unknown" if TASKS[it["task_id"]]["primitive"] == "hallucination" else "")
    else:
        opts = " | ".join(crit)
    return q["instructions"], opts


def csv_row(it):
    pregunta, opciones = question_for_human(it)
    row = {"id": it["id"], "task_id": it["task_id"], "primitive": it["primitive"], "pregunta": pregunta,
           "opciones": opciones, "texto": state_text(it["state"]), "label": it["label"]}
    row.update({k: v for k, v in it.items() if k not in row and k not in ("state", "question", "options")})
    return row


def human_sample(out, per_task=3):
    """Blind sample for the user to label by hand (the answer key is NOT in this file)."""
    rng = random.Random(2026)
    rows = []
    for prim in out:
        by_task = defaultdict(list)
        for it in out[prim]:
            by_task[it["task_id"]].append(it)
        for task in sorted(by_task):
            for it in rng.sample(by_task[task], min(per_task, len(by_task[task]))):
                pregunta, opciones = question_for_human(it)
                rows.append({"id": it["id"], "tarea": task, "pregunta": pregunta, "opciones": opciones,
                             "texto": state_text(it["state"]), "tu_respuesta": ""})
    rng.shuffle(rows)
    return [{"nro": i + 1, **r} for i, r in enumerate(rows)]


def normalize(ans):
    a = str(ans).strip().lower()
    if a in ("true", "si", "sí", "yes", "verdadero"):
        return "true"
    if a in ("false", "no", "falso"):
        return "false"
    if a in ("unknown", "no se", "no sé", "ns"):
        return "unknown"
    return a


def cmd_human_check():
    gold = {}
    for p in FINAL_N:
        for it in read_jsonl(D / "final" / f"{p}.jsonl"):
            gold[it["id"]] = it["label"]
    rows = list(csv.DictReader(open(D / "final" / "revision_humana.csv", encoding="utf-8")))
    done = [r for r in rows if r["tu_respuesta"].strip()]
    if not done:
        sys.exit("Todavia no hay respuestas en la columna tu_respuesta.")
    agree, per_task, diffs = 0, defaultdict(lambda: [0, 0]), []
    for r in done:
        ok = normalize(r["tu_respuesta"]) == normalize(gold[r["id"]])
        agree += ok
        per_task[r["tarea"]][0] += ok
        per_task[r["tarea"]][1] += 1
        if not ok:
            diffs.append((r["nro"], r["id"], r["tu_respuesta"], gold[r["id"]]))
    print(f"Respondiste {len(done)} de {len(rows)}. Coincidencia con la ground truth: {agree}/{len(done)} = {agree / len(done):.0%}")
    scale = [r for r in done if isinstance(gold[r["id"]], int) and not isinstance(gold[r["id"]], bool)]
    if scale:
        exact = sum(normalize(r["tu_respuesta"]) == normalize(gold[r["id"]]) for r in scale)
        near = sum(r["tu_respuesta"].strip().isdigit() and abs(int(r["tu_respuesta"]) - gold[r["id"]]) <= 1 for r in scale)
        print(f"Escalas: exacto {exact}/{len(scale)}, dentro de +-1 nivel {near}/{len(scale)} "
              f"| Categorias y si/no: {agree - exact}/{len(done) - len(scale)}")
    print("Por tarea:", ", ".join(f"{t} {a}/{n}" for t, (a, n) in sorted(per_task.items())))
    if diffs:
        print("\nDesacuerdos (nro, id, tu respuesta, ground truth):")
        for d in diffs:
            print("  ", *d)


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"briefs": lambda: cmd_briefs(),
     "check-raw": lambda: cmd_check_raw(args[0], args[2] if len(args) > 2 and args[1] == "--part" else None),
     "join-parts": lambda: cmd_join_parts(args[0]),
     "check-verify": lambda: cmd_check_verify(args[0]),
     "blind": lambda: cmd_blind(args),
     "merge": lambda: cmd_merge(),
     "final": lambda: cmd_final("--check" in args),
     "human-check": lambda: cmd_human_check()}[cmd]()

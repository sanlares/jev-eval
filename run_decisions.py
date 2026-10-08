"""Run OpenAI's Decisions API (model gpt-6-luna) on the final dataset. Same protocol as run_jev.py.

Decisions is the same idea as Jev: send evidence + typed questions, get typed answers with probabilities.
Each Jev question is translated 1:1, carrying the same information:
  choice (criteria dict)        -> type "choice", choices=[{value, description}]
  score  (list of level texts)  -> type "score",  levels=[{label, description}]  ("Label: description" is split)
  noul   (criteria true/false)  -> type "predicate" (it has no criteria field, so the true/false criteria are
                                   appended to the instructions)
  JSON-object states            -> serialized to text (the input field only accepts text or user messages)
All questions of an item go in one request (3 for tweets), as with Jev; Decisions evaluates them independently.

Answers are stored raw AND normalized to Jev's shape, so analyze.py treats both models the same way:
  {"answers": {qid: {"type": "choice"|"score"|"noul"|"refusal", ...}}, "usage": {...}, "model": ...}

  .venv/bin/python run_decisions.py --dry-run        # validate payloads, estimate tokens/cost, no API calls
  .venv/bin/python run_decisions.py --smoke          # quick check: 1 item per task -> results/smoke/
  .venv/bin/python run_decisions.py --repeat 100     # full run + re-ask 100 random items (determinism check)

Needs OPENAI_API_KEY (jev_eval/.env is read automatically).
"""
import argparse
import asyncio
import json
import random
from collections import defaultdict
from pathlib import Path

from build import D, call_with_retries, load_env, read_jsonl
from specs import FINAL_N, jev_questions

MODEL = "gpt-6-luna"
OUT = Path(__file__).parent / "results" / "decisions" / "responses.jsonl"
SMOKE_OUT = Path(__file__).parent / "results" / "smoke" / "decisions_responses.jsonl"
PRICE_PER_INPUT_TOKEN = 0.10 / 1e6  # USD; Decisions has no output-token charge


def load_items():
    return [it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")]


def to_input(state):
    return state if isinstance(state, str) else json.dumps(state, ensure_ascii=False, indent=1)


def split_level(text):
    """'Cosmetic: a visual problem' -> {'label': 'Cosmetic', 'description': 'a visual problem'}."""
    label, sep, desc = text.partition(":")
    return {"label": label.strip(), "description": desc.strip()} if sep and desc.strip() else {"label": text.strip()}


def to_decision_questions(item):
    """Translate the exact Jev questions of an item into Decisions questions (same information)."""
    out = []
    for qid, q in jev_questions(item["task_id"], item).items():
        crit = q.get("criteria")
        if q["type"] == "choice":
            choices = [{"value": k, **({"description": v} if v else {})} for k, v in crit.items()]
            out.append({"type": "choice", "name": qid, "instructions": q["instructions"], "choices": choices})
        elif q["type"] == "score":
            out.append({"type": "score", "name": qid, "instructions": q["instructions"],
                        "levels": [split_level(c) for c in crit]})
        else:
            instr = q["instructions"]
            if crit:
                instr += f"\nAnswer yes if: {crit['true']}\nAnswer no if: {crit['false']}"
            out.append({"type": "predicate", "name": qid, "instructions": instr})
    return out


def normalize(decision):
    """Decisions response -> Jev-shaped answers keyed by question name (what analyze.py expects)."""
    answers = {}
    for a in decision["answers"]:
        name = a.get("name")
        if a["type"] == "predicate":
            answers[name] = {"type": "noul", "noul": a["probability"]}
        elif a["type"] == "choice":
            answers[name] = {"type": "choice", "choice": a["choice"], "confidence": a["confidence"],
                             "probabilities": {p["value"]: p["probability"] for p in a["probabilities"]}}
        elif a["type"] == "score":
            answers[name] = {"type": "score", "score": a["score"], "confidence": a["confidence"],
                             "probabilities": {str(p["value"]): p["probability"] for p in a["probabilities"]}}
        else:
            answers[name] = {"type": "refusal"}
    usage = decision.get("usage") or {}
    return {"model": decision.get("model"), "answers": answers,
            "usage": {"input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens")}}


def is_retryable(e):
    import openai
    if isinstance(e, (openai.RateLimitError, openai.InternalServerError, openai.APIConnectionError)):
        return True
    return isinstance(e, openai.APIStatusError) and e.status_code >= 500


async def ask(client, sem, item, rep, fout):
    """One request per item (all of its questions together). Latency = successful attempt only."""
    async with sem:
        resp, latency, attempts = await call_with_retries(
            lambda: client.decisions.create(model=MODEL, input=to_input(item["state"]),
                                            questions=to_decision_questions(item)),
            is_retryable)
    raw = resp.model_dump(mode="json")
    rec = {"id": item["id"], "rep": rep, "latency_s": round(latency, 3), "attempts": attempts,
           "response": normalize(raw), "raw": raw}
    fout.write(json.dumps(rec) + "\n")
    fout.flush()


async def run(items, out, concurrency, reps):
    import openai
    done = {(r["id"], r["rep"]) for r in read_jsonl(out)}
    jobs = [(it, rep) for it, rep in zip(items, reps) if (it["id"], rep) not in done]
    print(f"{len(jobs)} requests to send")
    out.parent.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(concurrency)
    async with openai.AsyncOpenAI(max_retries=0) as client:
        with open(out, "a") as fout:
            res = await asyncio.gather(*(ask(client, sem, it, rep, fout) for it, rep in jobs), return_exceptions=True)
    errors = [(jobs[i][0]["id"], repr(r)) for i, r in enumerate(res) if isinstance(r, Exception)]
    return errors


async def main(args):
    from run_jev import summarize
    items = load_items()
    if args.smoke:  # 1 random item per task, separate file so the real run is not affected
        by_task = defaultdict(list)
        for it in items:
            by_task[it["task_id"]].append(it)
        rng = random.Random(7)
        items = [rng.choice(v) for _, v in sorted(by_task.items())]
        SMOKE_OUT.parent.mkdir(parents=True, exist_ok=True)
        SMOKE_OUT.write_text("")
        errors = await run(items, SMOKE_OUT, args.concurrency, [0] * len(items))
        recs = {r["id"]: r for r in read_jsonl(SMOKE_OUT)}
        lines = [l for it in items if it["id"] in recs for l in summarize(recs[it["id"]]["response"]["answers"], it, "luna")]
        print("\n".join(lines))
        lat = sorted(r["latency_s"] for r in recs.values())
        toks = sum(r["response"]["usage"]["input_tokens"] or 0 for r in recs.values())
        refusals = sum(a["type"] == "refusal" for r in recs.values() for a in r["response"]["answers"].values())
        print(f"\nmodel={next(iter(recs.values()))['response']['model'] if recs else '-'} | requests ok={len(recs)}/{len(items)}"
              f" | errors={len(errors)} | refusals={refusals} | correct={sum(l.startswith('ok') for l in lines)}/{len(lines)}"
              f" | latency median={lat[len(lat) // 2] if lat else 0:.2f}s | input tokens={toks} (~${toks * PRICE_PER_INPUT_TOKEN:.5f})")
    else:
        reps = [0] * len(items)
        if args.repeat:
            extra = random.Random(123).sample(items, args.repeat)
            items, reps = items + extra, reps + [1] * len(extra)
        errors = await run(items, OUT, args.concurrency, reps)
        print(f"done. errors: {len(errors)}")
    for e in errors[:10]:
        print("ERROR", *e)
    if errors:
        print("re-run the same command to retry failed items")


def dry_run():
    from openai.types import decision_create_params  # noqa: F401  (fails early if the SDK is too old)
    items = load_items()
    names_ok = True
    for it in items:
        qs = to_decision_questions(it)
        names_ok &= len({q["name"] for q in qs}) == len(qs)
        for q in qs:
            assert q["instructions"].strip(), it["id"]
            if q["type"] == "choice":
                assert len(q["choices"]) >= 2 and len({c["value"] for c in q["choices"]}) == len(q["choices"]), it["id"]
            if q["type"] == "score":
                assert len(q["levels"]) >= 2 and all(l["label"] for l in q["levels"]), it["id"]
    chars = sum(len(to_input(it["state"])) + len(json.dumps(to_decision_questions(it))) for it in items)
    toks = chars / 4
    print(f"{len(items)} items across {len({it['task_id'] for it in items})} tasks; payloads valid; unique names: {names_ok}")
    print(f"~{toks / 1e3:.0f}K input tokens -> ~${toks * PRICE_PER_INPUT_TOKEN:.4f} (+ repeat pass)")
    for tid in ("C01", "S01", "N01", "T01"):
        ex = next(it for it in items if it["task_id"] == tid)
        print(f"--- example {tid}:", json.dumps({"model": MODEL, "input": to_input(ex["state"])[:120] + "...",
                                                "questions": to_decision_questions(ex)}, indent=1)[:1500])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="quick test: 1 item per task, separate output file")
    ap.add_argument("--repeat", type=int, default=0, help="re-ask N random items to check determinism")
    ap.add_argument("--concurrency", type=int, default=16)
    a = ap.parse_args()
    load_env()
    dry_run() if a.dry_run else asyncio.run(main(a))

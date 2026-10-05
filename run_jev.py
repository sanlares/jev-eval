"""Run Jev on the final dataset. Resumable: already-answered ids are skipped.

  .venv/bin/python run_jev.py --dry-run        # validate payloads, estimate tokens/cost, no API calls
  .venv/bin/python run_jev.py                  # main pass  -> results/jev/responses.jsonl
  .venv/bin/python run_jev.py --repeat 100     # also re-ask 100 random items (determinism check)
  .venv/bin/python run_jev.py --smoke          # quick check: 1 item per task -> results/smoke/ (separate file)

Needs TYPESAFE_API_KEY (or JET_KEY in jev_eval/.env). The model is pinned (specs.JEV_MODEL) for reproducibility.
"""
import argparse
import asyncio
import json
import random
import time
from pathlib import Path

from build import D, load_env, read_jsonl
from specs import FINAL_N, JEV_MODEL, jev_questions

OUT = Path(__file__).parent / "results" / "jev" / "responses.jsonl"
SMOKE_OUT = Path(__file__).parent / "results" / "smoke" / "jev_responses.jsonl"
PRICE_PER_TOKEN = 0.042 / 1e6


def load_items():
    return [it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")]


def sdk_questions(item):
    from typesafe_sdk import Choice, Noul, Score
    out = {}
    for qid, q in jev_questions(item["task_id"], item).items():
        if q["type"] == "choice":
            out[qid] = Choice(instructions=q["instructions"], criteria=q["criteria"])
        elif q["type"] == "score":
            out[qid] = Score(instructions=q["instructions"], criteria=q["criteria"])
        else:
            out[qid] = Noul(instructions=q["instructions"], criteria=q.get("criteria"))
    return out


def validate(item):
    task = item["task_id"]
    for qid, q in jev_questions(task, item).items():
        if q["type"] == "choice":
            assert 2 <= len(q["criteria"]) <= 255, f"{task}/{qid}: 2-255 options"
        if q["type"] == "score":
            assert 2 <= len(q["criteria"]) <= 10, f"{task}/{qid}: 2-10 levels"
        if q["type"] == "noul" and q.get("criteria") is not None:
            assert set(q["criteria"]) == {"true", "false"}, f"{task}/{qid}: noul criteria keys"


async def ask(client, sem, item, rep, fout):
    async with sem:
        t0 = time.perf_counter()
        resp = await client.system_one(state=item["state"], questions=sdk_questions(item))
        rec = {"id": item["id"], "rep": rep, "latency_s": round(time.perf_counter() - t0, 3),
               "response": resp.model_dump(mode="json")}
        fout.write(json.dumps(rec) + "\n")
        fout.flush()


def summarize(answers, item):
    """One short human-readable line per question: Jev's answer vs the ground truth."""
    out = []
    for qid, a in answers.items():
        gold = item["targets"][qid] if "targets" in item else item["label"]
        if a["type"] == "choice":
            pred, extra = a["choice"], f"p={max(a['probabilities'].values()):.2f}"
        elif a["type"] == "score":
            probs = {int(k): v for k, v in a["probabilities"].items()}
            pred, extra = max(probs, key=probs.get), f"E[score]={a['score']:.2f}"
        else:
            pred, extra = a["noul"] >= 0.5, f"P(yes)={a['noul']:.2f}"
        ok = "ok " if gold == "unknown" or pred == gold else "MAL"
        if gold == "unknown":
            ok = "ok " if 0.3 <= a["noul"] <= 0.7 else "MAL"
        out.append(f"{ok} {item['id']:8s} {qid:12s} gold={json.dumps(gold):18s} jev={json.dumps(pred):18s} {extra}")
    return out


async def smoke(args):
    """1 random item per task, written to a separate file so the real run is not affected."""
    from collections import defaultdict
    from typesafe_sdk import AsyncTypeSafeClient
    by_task = defaultdict(list)
    for it in load_items():
        by_task[it["task_id"]].append(it)
    rng = random.Random(7)
    items = [rng.choice(v) for _, v in sorted(by_task.items())]
    SMOKE_OUT.parent.mkdir(parents=True, exist_ok=True)
    SMOKE_OUT.write_text("")
    sem = asyncio.Semaphore(args.concurrency)
    async with AsyncTypeSafeClient(model=JEV_MODEL) as client:
        with open(SMOKE_OUT, "a") as fout:
            res = await asyncio.gather(*(ask(client, sem, it, 0, fout) for it in items), return_exceptions=True)
    errors = [(items[i]["id"], repr(r)) for i, r in enumerate(res) if isinstance(r, Exception)]
    recs = {r["id"]: r for r in read_jsonl(SMOKE_OUT)}
    lines = [l for it in items if it["id"] in recs for l in summarize(recs[it["id"]]["response"]["answers"], it)]
    print("\n".join(lines))
    lat = [r["latency_s"] for r in recs.values()]
    toks = sum((r["response"].get("usage") or {}).get("input_tokens") or 0 for r in recs.values())
    model = next(iter(recs.values()))["response"].get("model") if recs else "-"
    print(f"\nmodel={model} | requests ok={len(recs)}/{len(items)} | errors={len(errors)} | "
          f"correct={sum(l.startswith('ok') for l in lines)}/{len(lines)} | latency median={sorted(lat)[len(lat)//2] if lat else 0:.2f}s "
          f"| input tokens={toks} (~${toks * PRICE_PER_TOKEN:.5f})")
    for e in errors[:5]:
        print("ERROR", *e)


async def main(args):
    from typesafe_sdk import AsyncTypeSafeClient
    items = load_items()
    done = {(r["id"], r["rep"]) for r in read_jsonl(OUT)}
    jobs = [(it, 0) for it in items if (it["id"], 0) not in done]
    if args.repeat:
        for it in random.Random(123).sample(items, args.repeat):
            if (it["id"], 1) not in done:
                jobs.append((it, 1))
    print(f"{len(items)} items, {len(jobs)} requests to send")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(args.concurrency)
    async with AsyncTypeSafeClient(model=JEV_MODEL) as client:
        with open(OUT, "a") as fout:
            results = await asyncio.gather(*(ask(client, sem, it, rep, fout) for it, rep in jobs),
                                           return_exceptions=True)
    errors = [(jobs[i][0]["id"], repr(r)) for i, r in enumerate(results) if isinstance(r, Exception)]
    print(f"done. errors: {len(errors)}")
    for e in errors[:10]:
        print("  ", e)
    if errors:
        print("re-run the same command to retry failed items")


def dry_run():
    items = load_items()
    tasks = sorted({it["task_id"] for it in items})
    for it in items:
        validate(it)
        sdk_questions(it)  # SDK-side validation
    chars = sum(len(json.dumps(it["state"])) + len(json.dumps(jev_questions(it["task_id"], it))) for it in items)
    toks = chars / 4
    print(f"{len(items)} items across {len(tasks)} tasks; payloads valid")
    print(f"~{toks / 1e3:.0f}K input tokens -> ~${toks * PRICE_PER_TOKEN:.4f} (+ repeat pass)")
    ex = items[0]
    print("example payload:", json.dumps({"state": ex["state"], "model": JEV_MODEL,
                                          "questions": jev_questions(ex["task_id"], ex)}, indent=1)[:1200])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--repeat", type=int, default=0, help="re-ask N random items to check determinism")
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--smoke", action="store_true", help="quick test: 1 item per task, separate output file")
    a = ap.parse_args()
    load_env()
    if a.dry_run:
        dry_run()
    else:
        asyncio.run(smoke(a) if a.smoke else main(a))

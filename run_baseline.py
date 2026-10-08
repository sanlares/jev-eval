"""Baseline: Claude Haiku 4.5 answers the same questions (same instructions + criteria) as Jev.

Output format is enforced with structured outputs (`output_config.format` + JSON Schema with an `enum` of the valid
options): the API constrains generation so the reply is always JSON matching the schema. We still parse and validate
every reply and store anything unexpected (refusal, max_tokens, bad JSON) with valid=false.

One call per (item, question), so the three tweet questions never see each other's answers (Jev also evaluates the
questions of a request in isolation). For each call we record the latency of the successful attempt, the number of
attempts (our own retry loop; SDK retries are disabled), and input/output tokens.

  .venv/bin/python run_baseline.py --dry-run   # print one rendered prompt + schema per question type, no API calls
  .venv/bin/python run_baseline.py --smoke     # quick check: 1 item per task -> results/smoke/ (~$0.03)
  .venv/bin/python run_baseline.py             # -> results/haiku/responses.jsonl (resumable, ~$2)

Needs ANTHROPIC_API_KEY (jev_eval/.env is read automatically).
"""
import argparse
import asyncio
import json
import random
from collections import defaultdict
from pathlib import Path

from build import D, call_with_retries, load_env, read_jsonl
from specs import FINAL_N, jev_questions

MODEL = "claude-haiku-4-5"
OUT = Path(__file__).parent / "results" / "haiku" / "responses.jsonl"
SMOKE_OUT = Path(__file__).parent / "results" / "smoke" / "haiku_responses.jsonl"
SYSTEM = "You are a careful classifier. Read the input and answer the question with the single best option."
PRICE_IN, PRICE_OUT = 1.00 / 1e6, 5.00 / 1e6  # USD per token, Claude Haiku 4.5


def render(q, state):
    """Prompt text, JSON schema for the answer, and the list of valid labels."""
    crit = q.get("criteria")
    if q["type"] == "choice":
        opts = "\n".join(f"- {k}" + (f": {v}" if v else "") for k, v in crit.items())
        enum, prop = list(crit), {"type": "string", "enum": list(crit)}
    elif q["type"] == "score":
        opts = "\n".join(f"- {i}: {c}" for i, c in enumerate(crit))
        enum, prop = list(range(len(crit))), {"type": "integer", "enum": list(range(len(crit)))}
    else:
        opts = f"- true: {crit['true']}\n- false: {crit['false']}" if crit else "- true\n- false"
        enum, prop = [True, False], {"type": "boolean"}
    body = state if isinstance(state, str) else json.dumps(state, ensure_ascii=False, indent=1)
    prompt = f"Question: {q['instructions']}\n\nOptions:\n{opts}\n\nInput:\n<input>\n{body}\n</input>"
    schema = {"type": "object", "properties": {"label": prop}, "required": ["label"], "additionalProperties": False}
    return prompt, schema, enum


def is_retryable(e):
    import anthropic
    if isinstance(e, (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError)):
        return True
    return isinstance(e, anthropic.APIStatusError) and e.status_code >= 500


async def ask(client, sem, item, qid, q, fout):
    prompt, schema, enum = render(q, item["state"])
    async with sem:
        msg, latency, attempts = await call_with_retries(
            lambda: client.messages.create(
                model=MODEL, max_tokens=256, system=SYSTEM,
                # SDK 1.x dropped the `temperature` kwarg; Haiku 4.5 still honours it, and determinism matters here
                extra_body={"temperature": 0},
                messages=[{"role": "user", "content": prompt}],
                output_config={"format": {"type": "json_schema", "schema": schema}},
            ),
            is_retryable,
        )
    text = next((b.text for b in msg.content if b.type == "text"), "")
    try:
        label = json.loads(text)["label"]
    except (json.JSONDecodeError, KeyError, TypeError):
        label = None
    valid = msg.stop_reason == "end_turn" and any(label == e and type(label) is type(e) for e in enum)
    rec = {"id": item["id"], "qid": qid, "label": label, "valid": valid, "stop_reason": msg.stop_reason,
           "latency_s": round(latency, 3), "attempts": attempts,
           "input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens}
    if not valid:
        rec["raw_text"] = text[:500]
    fout.write(json.dumps(rec) + "\n")
    fout.flush()


def load_items(smoke):
    items = [it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")]
    # H02 "unknown" items are skipped: a single true/false answer cannot express "don't know"
    items = [it for it in items if it["label"] != "unknown"]
    if smoke:  # 1 random item per task
        by_task = defaultdict(list)
        for it in items:
            by_task[it["task_id"]].append(it)
        rng = random.Random(7)
        items = [rng.choice(v) for _, v in sorted(by_task.items())]
    return items


async def main(args):
    import anthropic
    items = load_items(args.smoke)
    out = SMOKE_OUT if args.smoke else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.smoke:
        out.write_text("")
    done = {(r["id"], r["qid"]) for r in read_jsonl(out) if r["valid"]}
    jobs = [(it, qid, q) for it in items for qid, q in jev_questions(it["task_id"], it).items()
            if (it["id"], qid) not in done]
    print(f"{len(jobs)} calls to send")
    sem = asyncio.Semaphore(args.concurrency)
    async with anthropic.AsyncAnthropic(max_retries=0) as client:
        with open(out, "a") as fout:
            res = await asyncio.gather(*(ask(client, sem, *j, fout) for j in jobs), return_exceptions=True)
    errors = [(jobs[i][0]["id"], repr(r)) for i, r in enumerate(res) if isinstance(r, Exception)]
    recs = read_jsonl(out)
    lat = sorted(r["latency_s"] for r in recs)
    tok_in, tok_out = sum(r["input_tokens"] for r in recs), sum(r["output_tokens"] for r in recs)
    print(f"done. calls ok={len(jobs) - len(errors)}/{len(jobs)} | invalid answers={sum(not r['valid'] for r in recs)} "
          f"| latency median={lat[len(lat) // 2] if lat else 0:.2f}s p90={lat[int(len(lat) * .9)] if lat else 0:.2f}s "
          f"| tokens in={tok_in} out={tok_out} | cost=${tok_in * PRICE_IN + tok_out * PRICE_OUT:.4f}")
    for e in errors[:10]:
        print("ERROR", *e)
    if errors:
        print("re-run the same command to retry failed calls")
    if args.smoke:
        gold = {it["id"]: it for it in items}
        ok = 0
        for r in recs:
            it = gold[r["id"]]
            g = it["targets"][r["qid"]] if "targets" in it else it["label"]
            ok += r["label"] == g
            print(f"{'ok ' if r['label'] == g else 'MAL'} {r['id']:8s} {r['qid']:12s} gold={json.dumps(g):20s} "
                  f"haiku={json.dumps(r['label']):20s} {r['latency_s']:.2f}s")
        print(f"correct={ok}/{len(recs)}")


def dry_run():
    seen = set()
    for p in FINAL_N:
        for it in read_jsonl(D / "final" / f"{p}.jsonl"):
            for qid, q in jev_questions(it["task_id"], it).items():
                key = (q["type"], q.get("criteria") is None)
                if key in seen:
                    continue
                seen.add(key)
                prompt, schema, _ = render(q, it["state"])
                print(f"===== {it['task_id']} / {qid} ({q['type']})\n{prompt}\nSCHEMA: {json.dumps(schema)}\n")
    n = sum(len(jev_questions(it["task_id"], it)) for it in load_items(False))
    print(f"{n} calls in a full run")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="quick test: 1 item per task, separate output file")
    ap.add_argument("--concurrency", type=int, default=8)
    a = ap.parse_args()
    load_env()
    dry_run() if a.dry_run else asyncio.run(main(a))

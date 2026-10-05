"""Baseline: Claude Haiku 4.5 answers the same questions (same instructions + criteria) as Jev.

One call per (item, question); forced tool call with an enum so the answer is always a valid option.
Haiku returns no probabilities, so only hard labels are compared (accuracy, not calibration).

  .venv/bin/python run_baseline.py --dry-run   # print one rendered prompt per question type, no API calls
  .venv/bin/python run_baseline.py             # -> results/haiku/responses.jsonl (resumable)

Needs ANTHROPIC_API_KEY (or an `ant auth login` profile).
"""
import argparse
import asyncio
import json
from pathlib import Path

from build import D, load_env, read_jsonl
from specs import FINAL_N, jev_questions

MODEL = "claude-haiku-4-5"
OUT = Path(__file__).parent / "results" / "haiku" / "responses.jsonl"
SYSTEM = ("You are a careful classifier. Read the input, then answer the question by calling the `answer` tool "
          "with the single best option.")


def render(q, state):
    crit = q["criteria"]
    if q["type"] == "choice":
        opts = "\n".join(f"- {k}" + (f": {v}" if v else "") for k, v in crit.items())
        enum, schema_type = list(crit), "string"
    elif q["type"] == "score":
        opts = "\n".join(f"- {i}: {c}" for i, c in enumerate(crit))
        enum, schema_type = list(range(len(crit))), "integer"
    else:
        opts = f"- true: {crit['true']}\n- false: {crit['false']}" if crit else "- true\n- false"
        enum, schema_type = [True, False], "boolean"
    body = state if isinstance(state, str) else json.dumps(state, ensure_ascii=False, indent=1)
    prompt = f"Question: {q['instructions']}\n\nOptions:\n{opts}\n\nInput:\n<input>\n{body}\n</input>"
    prop = {"type": schema_type} if schema_type == "boolean" else {"type": schema_type, "enum": enum}
    tool = {"name": "answer", "description": "Submit the chosen option.",
            "input_schema": {"type": "object", "properties": {"label": prop}, "required": ["label"],
                             "additionalProperties": False}}
    return prompt, tool, enum


async def ask(client, sem, item, qid, q, fout):
    prompt, tool, enum = render(q, item["state"])
    async with sem:
        msg = await client.messages.create(
            model=MODEL, max_tokens=256, temperature=0, system=SYSTEM,
            tools=[tool], tool_choice={"type": "tool", "name": "answer"},
            messages=[{"role": "user", "content": prompt}],
        )
    call = next((b for b in msg.content if b.type == "tool_use"), None)
    label = call.input.get("label") if call else None
    rec = {"id": item["id"], "qid": qid, "label": label, "valid": label in enum,
           "stop_reason": msg.stop_reason, "input_tokens": msg.usage.input_tokens}
    fout.write(json.dumps(rec) + "\n")
    fout.flush()


async def main(args):
    import anthropic
    items = [it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")]
    # H02 "unknown" items are skipped: a forced true/false answer cannot express "don't know"
    items = [it for it in items if it["label"] != "unknown"]
    done = {(r["id"], r["qid"]) for r in read_jsonl(OUT) if r["valid"]}
    jobs = [(it, qid, q) for it in items for qid, q in jev_questions(it["task_id"], it).items()
            if (it["id"], qid) not in done]
    print(f"{len(jobs)} calls to send")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(args.concurrency)
    async with anthropic.AsyncAnthropic(max_retries=6) as client:
        with open(OUT, "a") as fout:
            res = await asyncio.gather(*(ask(client, sem, *j, fout) for j in jobs), return_exceptions=True)
    errors = [(jobs[i][0]["id"], repr(r)) for i, r in enumerate(res) if isinstance(r, Exception)]
    print(f"done. errors: {len(errors)}", *errors[:10], sep="\n  ")


def dry_run():
    seen = set()
    for p in FINAL_N:
        for it in read_jsonl(D / "final" / f"{p}.jsonl")[:1]:
            for qid, q in jev_questions(it["task_id"], it).items():
                if q["type"] in seen:
                    continue
                seen.add(q["type"])
                prompt, tool, _ = render(q, it["state"])
                print(f"===== {it['task_id']} / {qid} ({q['type']})\n{prompt}\nTOOL: {json.dumps(tool)}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--concurrency", type=int, default=8)
    a = ap.parse_args()
    load_env()
    dry_run() if a.dry_run else asyncio.run(main(a))

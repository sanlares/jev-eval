"""Label-first item plan: fixes label, difficulty, hard_type, length, subtopic and writer
for every item BEFORE any text is generated. Deterministic (seed 42).

Output: data/plan/<task>.jsonl
"""
import json
import math
import random
from collections import Counter
from pathlib import Path

from specs import DEFAULT_LENGTH_WEIGHTS, FINAL_N, TASKS, WRITERS, labels

SEED = 42
OVERAGE = 0.10  # extra items per label to absorb drops at adjudication
DIFF_PATTERN = ["easy", "medium", "hard", "medium", "easy", "hard", "medium", "easy", "hard", "medium"]  # 30/40/30
OUT = Path(__file__).parent / "data" / "plan"


def split_even(n, keys, rng):
    base, rem = divmod(n, len(keys))
    bonus = set(rng.sample(keys, rem))
    return {k: base + (k in bonus) for k in keys}


def target_counts(task, rng):
    t = TASKS[task]
    n = FINAL_N[t["primitive"]]
    labs = labels(task)
    if "label_shares" in t:
        return {l: round(n * t["label_shares"][l]) for l in labs}
    other = t.get("other_label")
    if not other:
        return split_even(n, labs, rng)
    n_other = round(n * t["other_share"])
    counts = split_even(n - n_other, [l for l in labs if l != other], rng)
    counts[other] = n_other
    return counts


def plan_task(task):
    rng = random.Random(f"{SEED}-{task}")
    t = TASKS[task]
    targets = target_counts(task, rng)
    if "hard_types_by_label" in t:  # hallucination tasks: hard types depend on the label
        hard_cycles = {l: rng.sample(v, len(v)) for l, v in t["hard_types_by_label"].items()}
    else:  # original behaviour (keeps the random stream, hence the plans, unchanged)
        cycle = t["hard_types"][:]
        rng.shuffle(cycle)
        hard_cycles = {l: cycle for l in targets}
    n_hard_by_label = {l: 0 for l in targets} if "hard_types_by_label" in t else None
    n_hard = 0
    subtopics = t["subtopics"][:]
    rng.shuffle(subtopics)
    weights = t.get("length_weights", DEFAULT_LENGTH_WEIGHTS)
    writers = t.get("writers", WRITERS)

    rows = []
    for lab, n_target in targets.items():
        n_gen = n_target + math.ceil(OVERAGE * n_target)
        offset = rng.randrange(len(DIFF_PATTERN))
        for j in range(n_gen):
            diff = DIFF_PATTERN[(offset + j) % len(DIFF_PATTERN)]
            hard_type = None
            if diff == "hard":
                cyc = hard_cycles[lab]
                k = n_hard_by_label[lab] if n_hard_by_label is not None else n_hard
                hard_type = cyc[k % len(cyc)]
                if n_hard_by_label is not None:
                    n_hard_by_label[lab] += 1
                n_hard += 1
            if hard_type == "long_irrelevant":
                length = "long"
            else:
                length = rng.choices(list(weights), weights=list(weights.values()))[0]
            rows.append(dict(
                task_id=task,
                primitive=t["primitive"],
                label=lab,
                difficulty=diff,
                hard_type=hard_type,
                length=length,
                subtopic=subtopics[len(rows) % len(subtopics)],
                writer=rng.choice(writers) if writers else None,
            ))
    rng.shuffle(rows)
    for i, r in enumerate(rows):
        r["id"] = f"{task}_{i:03d}"
    return rows, targets


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for task in TASKS:
        rows, targets = plan_task(task)
        path = OUT / f"{task}.jsonl"
        if path.exists():  # plans are frozen once written (texts were generated from them)
            print(f"{task}: plan exists, left untouched")
            continue
        with open(path, "w") as f:
            for r in rows:
                f.write(json.dumps({"id": r.pop("id"), **r}) + "\n")
        total += len(rows)
        diff = Counter(r["difficulty"] for r in rows)
        print(f"{task}: gen={len(rows):3d} final_target={sum(targets.values()):3d} "
              f"labels={len(targets):2d} diff={dict(diff)}")
    json.dump({k: {**v} for k, v in TASKS.items()}, open(OUT.parent / "specs.json", "w"), indent=1, default=str)
    print(f"total planned items: {total}")


if __name__ == "__main__":
    main()

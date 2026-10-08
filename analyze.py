"""Pre-registered analysis: Jev and OpenAI Decisions vs ground truth (accuracy + calibration) and vs each other and
Claude Haiku 4.5 (paired accuracy), plus hallucination, consistency, determinism, latency and cost.

  .venv/bin/python analyze.py                      # real results -> results/report.md, figures, item_level.csv
  .venv/bin/python analyze.py --simulate oracle    # smoke test with fake predictors
                                  (oracle | random | overconfident | calibrated) -> results/sim_<mode>/

Models are listed in MODELS. "prob" models return probabilities (Jev, Decisions; both stored in the same normalized
shape by their runners); "label" models return one label per question (Haiku). Missing result files are skipped.

Primary metrics (fixed before the full runs): accuracy per family (choice / noul@0.5 / scales within +-1 level),
paired accuracy differences between models, and Noul Brier + calibration test. Exact level on scales is secondary:
the human review showed that two careful people disagree by one level on about half of the scale items.
A refusal or an invalid answer counts as wrong. CIs: 95% two-stage cluster bootstrap (tasks, then items), B=2000.
"""
import argparse
import itertools
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest, spearmanr
from sklearn.metrics import cohen_kappa_score, f1_score, roc_auc_score

from build import D, read_jsonl
from specs import ABSTAIN_KEY, FINAL_N, TASKS, jev_questions, tweet_targets

RES = Path(__file__).parent / "results"
B = 2000
N_BINS = 10
FAMILIES = ["choice", "score", "noul", "tweets_score", "tweets_choice", "tweets_noul"]
FAMILY_LABELS = {"choice": "Choice", "score": "Scale (±1)", "noul": "Yes/no", "tweets_score": "Tweets: scale (±1)",
                 "tweets_choice": "Tweets: 3-way", "tweets_noul": "Tweets: rise?"}
MODELS = {  # key (column prefix) -> display name, kind, results folder, USD per input / output token
    "jev": dict(name="Jev", kind="prob", folder="jev", model_id="jev-1.13.0", price_in=0.042 / 1e6, price_out=0.0),
    "luna": dict(name="Decisions", kind="prob", folder="decisions", model_id="gpt-6-luna (OpenAI Decisions)",
                 price_in=0.10 / 1e6, price_out=0.0),
    "haiku": dict(name="Haiku", kind="label", folder="haiku", model_id="claude-haiku-4-5",
                  price_in=1.00 / 1e6, price_out=5.00 / 1e6),
}
COLORS = {"jev": "#3b6fb6", "luna": "#e07b39", "haiku": "#5a9e5a"}
NO_ANSWER = "__no_answer__"  # refusal / invalid answer: counts as wrong


# ---------------------------------------------------------------- metrics on arrays

def ece(conf, correct, n_bins=N_BINS):
    """Expected calibration error with equal-mass bins."""
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    if len(conf) == 0:
        return np.nan
    order = np.argsort(conf, kind="stable")
    bins = np.array_split(order, min(n_bins, len(conf)))
    return sum(len(b) / len(conf) * abs(conf[b].mean() - correct[b].mean()) for b in bins)


def reliability(conf, correct, n_bins=N_BINS):
    order = np.argsort(conf, kind="stable")
    bins = np.array_split(order, n_bins)
    return [(conf[b].mean(), correct[b].mean(), len(b)) for b in bins if len(b)]


def wilson_ci(k, n):
    """95% Wilson interval for a proportion k/n -> (p, lo, hi) as fractions."""
    z, p = 1.96, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return p, max(0.0, c - h), min(1.0, c + h)


def wilson(k, n):
    """Same as wilson_ci, formatted as percentages."""
    if n == 0:
        return "-"
    p, lo, hi = wilson_ci(k, n)
    return f"{100 * p:.0f}% [{100 * lo:.0f}-{100 * hi:.0f}]"


# ---------------------------------------------------------------- data assembly

def question_rows(item):
    """One row per (item, question) with the gold answer."""
    for qid, q in jev_questions(item["task_id"], item).items():
        fam = {"tweets": f"tweets_{q['type']}", "hallucination": f"halluc_{q['type']}"}.get(item["primitive"], q["type"])
        gold = item["targets"][qid] if item["primitive"] == "tweets" else item["label"]
        n = len(q.get("criteria") or [True, False])
        yield dict(id=item["id"], task_id=item["task_id"], qid=qid, family=fam, qtype=q["type"], gold=gold,
                   n_cat=n, difficulty=item["difficulty"], hard_type=item.get("hard_type") or "-",
                   length=item["length"], options=list(q["criteria"]) if q["type"] == "choice" else None)


def parse_prob(row, ans, m):
    """Normalized answer of a probability model -> prefixed columns."""
    t = row["qtype"]
    if ans["type"] == "refusal":
        return {f"{m}_pred": NO_ANSWER, f"{m}_refusal": True}
    if t == "choice":
        probs = {k: float(v) for k, v in ans["probabilities"].items()}
        p = np.array([probs.get(o, 0.0) for o in row["options"]])
        return {f"{m}_pred": ans["choice"], f"{m}_conf": float(ans["confidence"]), f"{m}_ptop": float(p.max()),
                f"{m}_pgold": probs.get(row["gold"], 0.0), f"{m}_probs": p.tolist()}
    if t == "score":
        probs = {int(k): float(v) for k, v in ans["probabilities"].items()}
        p = np.array([probs.get(i, 0.0) for i in range(row["n_cat"])])
        return {f"{m}_pred": int(p.argmax()), f"{m}_conf": float(ans["confidence"]), f"{m}_ptop": float(p.max()),
                f"{m}_pgold": float(p[row["gold"]]), f"{m}_probs": p.tolist(), f"{m}_expected": float(ans["score"])}
    pr = float(ans["noul"])
    pgold = np.nan if row["gold"] == "unknown" else (pr if row["gold"] else 1 - pr)
    return {f"{m}_pred": pr >= 0.5, f"{m}_p": pr, f"{m}_ptop": max(pr, 1 - pr), f"{m}_conf": abs(2 * pr - 1),
            f"{m}_pgold": pgold}


def assemble(items, results):
    """results: {model_key: list of runner records}. Only rep 0 is scored (rep 1 = determinism re-run)."""
    prob = {m: {r["id"]: r["response"] for r in recs if r.get("rep", 0) == 0}
            for m, recs in results.items() if MODELS[m]["kind"] == "prob"}
    lab = {m: {(r["id"], r["qid"]): (r["label"] if r.get("valid", True) else NO_ANSWER) for r in recs}
           for m, recs in results.items() if MODELS[m]["kind"] == "label"}
    rows = []
    for it in items:
        for row in question_rows(it):
            for m, by_id in prob.items():
                ans = (by_id.get(it["id"]) or {}).get("answers", {}).get(row["qid"])
                if ans:
                    row.update(parse_prob(row, ans, m))
            for m, by_q in lab.items():
                row[f"{m}_pred"] = by_q.get((it["id"], row["qid"]))
            rows.append(row)
    df = pd.DataFrame(rows)
    for m in results:
        col = f"{m}_pred"
        if col not in df:
            df[col] = None
        # "unknown" gold (H02) has no right/wrong answer: scored separately in halluc_summary
        df[f"{m}_ok"] = [np.nan if p is None or (isinstance(p, float) and np.isnan(p)) or g == "unknown"
                         else (p != NO_ANSWER and p == g) for p, g in zip(df[col], df["gold"])]
        # scales: "within +-1 level" is the primary metric for these families
        df[f"{m}_ok1"] = [(p != NO_ANSWER and abs(int(p) - int(g)) <= 1) if t == "score" and pd.notna(o) else o
                          for p, g, o, t in zip(df[col], df["gold"], df[f"{m}_ok"], df["qtype"])]
    return df


def present(df, kind=None):
    """Model keys with at least one scored answer (optionally only one kind)."""
    return [m for m in MODELS if f"{m}_ok" in df and df[f"{m}_ok"].notna().any()
            and (kind is None or MODELS[m]["kind"] == kind)]


# ---------------------------------------------------------------- family metrics (exploratory, point estimates)

def family_metrics(d, m):
    j = d.dropna(subset=[f"{m}_ok"])
    out = {"family": d["family"].iloc[0], "model": MODELS[m]["name"], "n": len(j)}
    if j.empty:
        return out
    qtype = d["qtype"].iloc[0]
    out["acc_exact"] = j[f"{m}_ok"].astype(float).mean()
    answered = j[j[f"{m}_pred"] != NO_ANSWER]
    out["no_answer"] = int(len(j) - len(answered))
    if qtype == "choice" and len(answered):
        out["macro_f1"] = np.mean([f1_score(g["gold"].astype(str), g[f"{m}_pred"].astype(str), average="macro")
                                   for _, g in j.groupby("task_id")])
    if qtype == "score" and len(answered):
        out["within1"] = j[f"{m}_ok1"].astype(float).mean()
        out["qwk"] = np.mean([cohen_kappa_score(g["gold"].astype(int), g[f"{m}_pred"].astype(int), weights="quadratic",
                                                labels=list(range(g["n_cat"].iloc[0])))
                              for _, g in answered.groupby("task_id")])
    if MODELS[m]["kind"] != "prob" or answered.empty:
        return out
    if qtype in ("choice", "score"):
        out["ece_top"] = ece(answered[f"{m}_ptop"], answered[f"{m}_ok"])
        onehot = [np.eye(n)[o.index(g) if qtype == "choice" else g]
                  for n, o, g in zip(answered["n_cat"], answered["options"], answered["gold"])]
        out["brier"] = np.mean([((np.array(p) - y) ** 2).sum() for p, y in zip(answered[f"{m}_probs"], onehot)])
    if qtype == "score":
        out["mae_norm"] = (abs(answered[f"{m}_expected"] - answered["gold"]) / (answered["n_cat"] - 1)).mean()
        rps = [((np.cumsum(p) - (np.arange(n) >= g)) ** 2)[:-1].sum() / (n - 1)
               for p, g, n in zip(answered[f"{m}_probs"], answered["gold"], answered["n_cat"])]
        out["rps"] = np.mean(rps)
    if qtype == "noul":
        y, p = answered["gold"].astype(float).values, answered[f"{m}_p"].values
        out["auroc"] = roc_auc_score(y, p) if len(set(y)) == 2 else np.nan
        out["brier"] = np.mean((p - y) ** 2)
        pc = np.clip(p, 1e-6, 1 - 1e-6)
        out["logloss"] = -np.mean(y * np.log(pc) + (1 - y) * np.log(1 - pc))
        out["ece"] = ece(p, y)
    return out


# ---------------------------------------------------------------- cluster bootstrap for primary metrics

def cluster_bootstrap(d, stats, rng):
    """stats: name -> f(sub_df) ; returns {name: (point, lo, hi)} with two-stage resampling."""
    groups = [g.index.values for _, g in d.groupby("task_id")]
    point = {k: f(d) for k, f in stats.items()}
    draws = {k: [] for k in stats}
    for _ in range(B):
        idx = np.concatenate([rng.choice(g, len(g)) for g in (groups[i] for i in rng.integers(len(groups), size=len(groups)))])
        sub = d.loc[idx]
        for k, f in stats.items():
            draws[k].append(f(sub))
    return {k: (point[k], *np.nanpercentile(draws[k], [2.5, 97.5])) for k in stats}


def calibration_test(d, m, rng):
    """ECE plus a consistency-resampling test (Brocker & Smith 2007): outcomes are redrawn as if the model were
    perfectly calibrated (y* ~ Bernoulli(p)); the null ECE distribution absorbs the finite-sample noise floor.
    Noul: p = P(yes) vs gold. Choice/score: p = top-label probability vs correctness. Refusals are excluded."""
    a = d[(d[f"{m}_pred"] != NO_ANSWER) & d[f"{m}_ok"].notna()]
    if a.empty:
        return np.nan, "-"
    if a["qtype"].iloc[0] == "noul":
        p, y = a[f"{m}_p"].values.astype(float), a["gold"].astype(float).values
    else:
        p, y = a[f"{m}_ptop"].values.astype(float), a[f"{m}_ok"].astype(float).values
    obs = ece(p, y)
    null = np.array([ece(p, (rng.random(len(p)) < p).astype(float)) for _ in range(B)])
    pval = (null >= obs).mean()
    return pval, f"{obs:.3f} (null95 {np.percentile(null, 95):.3f}, p={pval:.3f})"


def fmt(t):
    pt, lo, hi = t
    return f"{pt:.3f} [{lo:.3f}, {hi:.3f}]"


def primary(df, rng):
    """Returns (per-model table, pairwise comparison table), both long format."""
    models, prob_models = present(df), present(df, "prob")
    per_model, pairs = [], []
    for fam in FAMILIES:
        d = df[(df["family"] == fam) & (df["gold"] != "unknown")].reset_index(drop=True)
        if d.empty or not any(d[f"{m}_ok"].notna().any() for m in models):
            continue
        scale = d["qtype"].iloc[0] == "score"
        ok = "ok1" if scale else "ok"
        stats = {}
        for m in models:
            stats[f"{m}:acc"] = lambda s, m=m: s[f"{m}_{ok}"].astype(float).mean()
            if scale:
                stats[f"{m}:exact"] = lambda s, m=m: s[f"{m}_ok"].astype(float).mean()
            if m in prob_models and d["qtype"].iloc[0] == "noul":
                stats[f"{m}:brier"] = lambda s, m=m: np.nanmean((s[f"{m}_p"].astype(float) - s["gold"].astype(float)) ** 2)
        pair_list = [(a, b) for a, b in itertools.combinations(models, 2)]
        for a, b in pair_list:
            stats[f"{a}-{b}"] = lambda s, a=a, b=b: (s[f"{a}_{ok}"].astype(float) - s[f"{b}_{ok}"].astype(float)).mean()
        res = cluster_bootstrap(d, stats, rng)
        for m in models:
            row = {"family": fam, "model": MODELS[m]["name"], "metric": "within +-1 level" if scale else "exact",
                   "n": int(d[f"{m}_ok"].notna().sum()), "accuracy": fmt(res[f"{m}:acc"]), "_key": m,
                   "_acc": res[f"{m}:acc"][0], "_acc_lo": res[f"{m}:acc"][1], "_acc_hi": res[f"{m}:acc"][2]}
            if scale:
                row["exact level"] = fmt(res[f"{m}:exact"])
            if m in prob_models:
                row["_cal_p"], row["calibration ECE"] = calibration_test(d, m, rng)
                if f"{m}:brier" in res:
                    row["brier"] = fmt(res[f"{m}:brier"])
            per_model.append(row)
        for a, b in pair_list:
            both = d[d[f"{a}_{ok}"].notna() & d[f"{b}_{ok}"].notna()]
            x, y = both[f"{a}_{ok}"].astype(bool), both[f"{b}_{ok}"].astype(bool)
            only_a, only_b = int((x & ~y).sum()), int((~x & y).sum())
            pt, lo, hi = res[f"{a}-{b}"]
            pairs.append({"family": fam, "comparison": f"{MODELS[a]['name']} - {MODELS[b]['name']}", "n paired": len(both),
                          "difference": fmt(res[f"{a}-{b}"]),
                          "mcnemar": (f"{MODELS[a]['name']}-only={only_a}, {MODELS[b]['name']}-only={only_b}, "
                                      f"p={binomtest(only_a, only_a + only_b).pvalue:.4f}") if only_a + only_b else "no discordant pairs",
                          "_lo": lo, "_hi": hi, "_a": MODELS[a]["name"], "_b": MODELS[b]["name"]})
    return pd.DataFrame(per_model), pd.DataFrame(pairs)


def plain_summary(per_model, pairs):
    """Plain-language tables: accuracy per model, who beats whom, calibration."""
    if per_model.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    order = [c["name"] for c in MODELS.values()]

    def by_family(t):
        t = t.reindex([f for f in FAMILIES if f in t.index])
        t.index = [FAMILY_LABELS[f] for f in t.index]
        return t.rename_axis("question type").reset_index()
    acc = per_model.pivot_table(index="family", columns="model", values="accuracy", aggfunc="first")
    acc = acc[[c for c in order if c in acc.columns]]
    acc.insert(0, "counts as correct", per_model.groupby("family")["metric"].first().map(
        lambda x: "within ±1 level" if x != "exact" else "exact answer"))
    acc = by_family(acc)
    verdicts = pd.DataFrame()
    if not pairs.empty:
        def verdict(r):
            diff = float(r["difference"].split(" ")[0]) * 100
            if r["_lo"] > 0:
                return f"{r['_a']} better ({diff:+.1f} pp)"
            if r["_hi"] < 0:
                return f"{r['_b']} better ({diff:+.1f} pp)"
            return f"no significant difference ({diff:+.1f} pp)"
        v = pairs.assign(verdict=pairs.apply(verdict, axis=1))
        verdicts = v.pivot_table(index="family", columns="comparison", values="verdict", aggfunc="first")
        verdicts = by_family(verdicts[list(dict.fromkeys(c for c in pairs["comparison"] if c in verdicts.columns))])
    cal = per_model[per_model["_cal_p"].notna()] if "_cal_p" in per_model else pd.DataFrame()
    if len(cal):
        cal = cal.assign(c=cal.apply(lambda r: ("no (p<0.05), " if r["_cal_p"] < 0.05 else "yes, ")
                                     + "ECE " + r["calibration ECE"].split(" ")[0], axis=1))
        cal = cal.pivot_table(index="family", columns="model", values="c", aggfunc="first")
        cal = by_family(cal[[c for c in order if c in cal.columns]])
    return acc, verdicts, cal


# ---------------------------------------------------------------- breakdowns, consistency, determinism

def breakdown(df, by):
    models = present(df)
    d = df[df["gold"] != "unknown"]
    g = d.groupby(["family", by])
    t = g.size().to_frame("n")
    for m in models:
        t[MODELS[m]["name"]] = g[f"{m}_ok"].mean()
    return t.round(3).reset_index()


def tweet_consistency(df):
    out = {}
    for m in present(df, "prob"):
        t = df[df["family"].str.startswith("tweets") & df[f"{m}_ok"].notna() & (df[f"{m}_pred"] != NO_ANSWER)]
        if t.empty:
            continue
        w = t.pivot_table(index="id", columns="qid", values=f"{m}_pred", aggfunc="first").dropna()
        e = t[t["qid"] == "sentiment"].set_index("id")[f"{m}_expected"].reindex(w.index)
        p = t[t["qid"] == "expects_rise"].set_index("id")[f"{m}_p"].reindex(w.index)
        collapsed = w["sentiment"].astype(int).map(lambda l: tweet_targets(l)["direction"])
        out[MODELS[m]["name"]] = {
            "spearman(score_expected, P(rise))": round(spearmanr(e, p).statistic, 3),
            "agree(choice, collapsed score)": round((w["direction"] == collapsed).mean(), 3),
            "agree(noul@0.5, choice==bullish)": round((w["expects_rise"].astype(bool) == (w["direction"] == "bullish")).mean(), 3),
        }
    return out


def determinism(results):
    out = {}
    for m, recs in results.items():
        if MODELS[m]["kind"] != "prob":
            continue
        by = {}
        for r in recs:
            by.setdefault(r["id"], {})[r.get("rep", 0)] = r["response"]["answers"]
        pairs = [(v[0], v[1]) for v in by.values() if 0 in v and 1 in v]
        if not pairs:
            continue
        same, maxdiff, nq = 0, 0.0, 0
        for a, b in pairs:
            for qid in a:
                x, y = a[qid], b.get(qid, {"type": "missing"})
                nq += 1
                if x["type"] != y["type"] or x["type"] == "refusal":
                    same += x["type"] == y["type"]
                    continue
                if x["type"] == "noul":
                    maxdiff = max(maxdiff, abs(x["noul"] - y["noul"]))
                    same += (x["noul"] >= .5) == (y["noul"] >= .5)
                else:  # same chosen option / same most likely level (not the float expected score)
                    px, py = x["probabilities"], y["probabilities"]
                    maxdiff = max(maxdiff, max(abs(px[k] - py.get(k, 0)) for k in px))
                    same += max(px, key=px.get) == max(py, key=py.get)
        out[MODELS[m]["name"]] = {"repeated_items": len(pairs), "same_answer_rate": round(same / nq, 4),
                                  "max_prob_abs_diff": round(maxdiff, 4)}
    return out


# ---------------------------------------------------------------- hallucination, human reference, speed & cost

def halluc_summary(df):
    """Long table: one row per measurement, one column per model."""
    models = present(df)
    names = {m: MODELS[m]["name"] for m in models}
    rows = []
    c = df[df.family == "halluc_choice"]
    if len(c):
        un, an = c[c.gold == ABSTAIN_KEY], c[c.gold != ABSTAIN_KEY]
        for what, f in [
            ("H01: picks 'cannot determine' when the text does NOT contain the answer (higher is better)",
             lambda col: ((un[col] == ABSTAIN_KEY).sum(), un[col].notna().sum())),
            ("H01: picks 'cannot determine' when the text DOES contain the answer (lower is better)",
             lambda col: ((an[col] == ABSTAIN_KEY).sum(), an[col].notna().sum())),
            ("H01: picks the right option when the text contains the answer (higher is better)",
             lambda col: ((an[col] == an.gold).sum(), an[col].notna().sum()))]:
            rows.append({"measurement": what, **{names[m]: wilson(*f(f"{m}_pred")) for m in models}})
    n = df[df.family == "halluc_noul"]
    if len(n):
        un, an = n[n.gold == "unknown"], n[n.gold != "unknown"]
        probs = {m: (un[f"{m}_p"].dropna() if f"{m}_p" in un else pd.Series(dtype=float)) for m in models}
        na = {m: (len(probs[m]) == 0) for m in models}
        rows += [
            {"measurement": "H02 no information: mean P(yes) (ideal 0.50)",
             **{names[m]: "n/a" if na[m] else f"{probs[m].mean():.2f}" for m in models}},
            {"measurement": "H02 no information: says 'I can't tell', 0.3 <= P <= 0.7 (higher is better)",
             **{names[m]: "n/a" if na[m] else wilson(((probs[m] >= .3) & (probs[m] <= .7)).sum(), len(probs[m])) for m in models}},
            {"measurement": "H02 no information: confident answer, P < 0.2 or P > 0.8 (lower is better)",
             **{names[m]: "n/a" if na[m] else wilson(((probs[m] < .2) | (probs[m] > .8)).sum(), len(probs[m])) for m in models}},
            {"measurement": "H02 answerable controls: correct (higher is better)",
             **{names[m]: wilson(an[f"{m}_ok"].dropna().astype(bool).sum(), an[f"{m}_ok"].notna().sum()) for m in models}},
        ]
    return pd.DataFrame(rows)


def abstention_rates(df):
    """For the summary chart: {model_key: {"H01": (p, lo, hi), "H02": (p, lo, hi)}} on the no-answer questions."""
    out = {}
    c = df[(df.family == "halluc_choice") & (df.gold == ABSTAIN_KEY)]
    n = df[(df.family == "halluc_noul") & (df.gold == "unknown")]
    for m in present(df):
        r = {}
        k = c[f"{m}_pred"].notna().sum()
        if k:
            r["H01"] = wilson_ci((c[f"{m}_pred"] == ABSTAIN_KEY).sum(), k)
        p = n[f"{m}_p"].dropna() if f"{m}_p" in n else pd.Series(dtype=float)
        if len(p):
            r["H02"] = wilson_ci(((p >= .3) & (p <= .7)).sum(), len(p))
        out[m] = r
    return out


def human_reference():
    """Agreement of the human reviewer with the ground truth (data/final/revision_humana.csv), if filled in."""
    import csv
    from build import normalize
    path = D / "final" / "revision_humana.csv"
    if not path.exists():
        return pd.DataFrame()
    gold = {it["id"]: it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")}
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["tu_respuesta"].strip()]
    out = {"categories and yes/no": [0, 0, None], "ordinal scales": [0, 0, 0]}
    for r in rows:
        g = gold[r["id"]]["label"]
        scale = isinstance(g, int) and not isinstance(g, bool)
        k = "ordinal scales" if scale else "categories and yes/no"
        out[k][1] += 1
        out[k][0] += normalize(r["tu_respuesta"]) == normalize(g)
        if scale and r["tu_respuesta"].strip().lstrip("-").isdigit():
            out[k][2] += abs(int(r["tu_respuesta"]) - g) <= 1
    return pd.DataFrame([{"type": k, "items reviewed": n, "exact agreement": wilson(a, n),
                          "within ±1 level": wilson(w, n) if w is not None else "-"}
                         for k, (a, n, w) in out.items() if n])


def speed_and_cost(results):
    """Latency of the successful attempt (retries excluded) and token cost, per model.
    Jev and Decisions answer all questions of an item in one request; Haiku makes one request per question."""
    rows = []
    for m, recs in results.items():
        cfg = MODELS[m]
        recs = [r for r in recs if r.get("rep", 0) == 0 and "latency_s" in r]
        if not recs:
            continue
        lat = np.array([r["latency_s"] for r in recs]) * 1000
        if cfg["kind"] == "prob":
            nq = sum(len(r["response"]["answers"]) for r in recs)
            usage = [(r["response"].get("usage") or {}) for r in recs]
            tin = sum(u.get("input_tokens") or 0 for u in usage)
            tout = sum(u.get("output_tokens") or 0 for u in usage)
        else:
            nq = len(recs)
            tin, tout = sum(r["input_tokens"] for r in recs), sum(r["output_tokens"] for r in recs)
        cost = tin * cfg["price_in"] + tout * cfg["price_out"]
        logged = any("attempts" in r for r in recs)
        rows.append({"model": cfg["name"], "requests": len(recs), "questions": nq,
                     "median latency (ms)": round(float(np.median(lat))), "p90 (ms)": round(float(np.percentile(lat, 90))),
                     "p99 (ms)": round(float(np.percentile(lat, 99))),
                     "requests retried": int(sum(r.get("attempts", 1) > 1 for r in recs)) if logged else "not logged",
                     "total cost (USD)": round(cost, 4), "cost per 1,000 questions (USD)": round(1000 * cost / nq, 4),
                     "_key": m})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- figures

def figures(df, out):
    prob_models = present(df, "prob")
    fams = [f for f in ["choice", "score", "noul", "tweets_noul"] if f in set(df["family"])]
    if not prob_models or not fams:
        return
    fig, axes = plt.subplots(len(prob_models), len(fams), figsize=(4.2 * len(fams), 3.8 * len(prob_models)), squeeze=False)
    for r, m in enumerate(prob_models):
        for ax, fam in zip(axes[r], fams):
            d = df[(df.family == fam) & df[f"{m}_ok"].notna() & (df[f"{m}_pred"] != NO_ANSWER)]
            if d.empty:
                ax.axis("off")
                continue
            if d["qtype"].iloc[0] == "noul":
                conf, hit, label = d[f"{m}_p"].values, d["gold"].astype(float).values, "P(yes)"
            else:
                conf, hit, label = d[f"{m}_ptop"].values, d[f"{m}_ok"].astype(float).values, "top-label probability"
            pts = reliability(conf, hit)
            ax.plot([0, 1], [0, 1], ls="--", c="grey", lw=1)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", c="#3b6fb6")
            ax.set(title=f"{MODELS[m]['name']} - {fam} (ECE={ece(conf, hit):.3f})", xlabel=label,
                   ylabel="observed frequency", xlim=(0, 1), ylim=(0, 1))
    fig.tight_layout()
    fig.savefig(out / "reliability.png", dpi=130)
    plt.close(fig)

    fig, axes = plt.subplots(1, len(prob_models), figsize=(5.5 * len(prob_models), 4), squeeze=False)
    for ax, m in zip(axes[0], prob_models):
        for fam in [f for f in FAMILIES if f in set(df.family) and not f.endswith("noul")]:
            d = df[(df.family == fam) & df[f"{m}_ok"].notna()].copy()
            if d.empty:
                continue
            d["_c"] = d[f"{m}_conf"].fillna(-1)  # refusals last
            d = d.sort_values("_c", ascending=False)
            cov = np.arange(1, len(d) + 1) / len(d)
            ax.plot(cov, d[f"{m}_ok"].astype(float).cumsum().values / np.arange(1, len(d) + 1), label=fam)
        ax.set(xlabel="coverage (answered, most confident first)", ylabel="accuracy on answered",
               title=f"{MODELS[m]['name']} risk-coverage")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "risk_coverage.png", dpi=130)
    plt.close(fig)


def bars(ax, groups, values, models, fmt_label):
    """Grouped bars: values[m][g] = (point, lo, hi) or None (drawn as 'n/a')."""
    w, x = 0.8 / len(models), np.arange(len(groups))
    for i, m in enumerate(models):
        xs = x + (i - (len(models) - 1) / 2) * w
        for xi, g in zip(xs, groups):
            v = values[m].get(g)
            if v is None:
                ax.text(xi, 0, "n/a", ha="center", va="bottom", fontsize=7, color="grey")
                continue
            pt, lo, hi = v
            yerr = None if lo is None else [[max(0, pt - lo)], [max(0, hi - pt)]]
            ax.bar(xi, pt, w, color=COLORS[m], yerr=yerr, capsize=2, ecolor="#555", error_kw={"lw": 0.8},
                   label=MODELS[m]["name"] if g == groups[0] else None)
            ax.text(xi, (hi if lo is not None else pt), fmt_label(pt), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x, groups)
    ax.margins(x=0.06)
    ax.spines[["top", "right"]].set_visible(False)


def summary_figure(df, per_model, speed, out):
    """One-glance bar chart: errors per question type, abstention, latency, cost."""
    models = present(df)
    if per_model.empty or not models:
        return
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), gridspec_kw={"width_ratios": [1.6, 1]})
    fams = [f for f in FAMILIES if f in set(per_model.family)]
    pm = per_model.set_index(["_key", "family"])
    lab = {f: FAMILY_LABELS[f].replace(": ", ":\n") for f in fams}
    err = {m: {lab[f]: (100 * (1 - pm.loc[(m, f), "_acc"]), 100 * (1 - pm.loc[(m, f), "_acc_hi"]),
                                  100 * (1 - pm.loc[(m, f), "_acc_lo"])) for f in fams if (m, f) in pm.index}
           for m in models}
    ax = axes[0, 0]
    bars(ax, [lab[f] for f in fams], err, models, lambda v: f"{v:.1f}")
    ax.set(ylabel="error rate (%)", title="Error rate by question type (lower is better; whiskers = 95% CI)")
    ax.legend(frameon=False)

    ab = abstention_rates(df)
    groups = ["H01: multiple choice\n(picks 'cannot determine')", "H02: yes/no\n(0.3 ≤ P(yes) ≤ 0.7)"]
    vals = {m: {g: (lambda t: (100 * t[0], 100 * t[1], 100 * t[2]))(ab[m][k]) if k in ab.get(m, {}) else None
                for g, k in zip(groups, ["H01", "H02"])} for m in models}
    ax = axes[0, 1]
    bars(ax, groups, vals, models, lambda v: f"{v:.0f}%")
    ax.set(ylabel="% of no-information questions", ylim=(0, 105),
           title="Says 'I can't tell' when the text has no answer\n(higher is better; whiskers = 95% CI)")

    sp = speed.set_index("_key") if len(speed) else pd.DataFrame()
    sp_models = [m for m in models if m in sp.index]
    for ax, col, fmt_label, title, note in [
            (axes[1, 0], "median latency (ms)", lambda v: f"{v:,.0f} ms", "Median latency per request (lower is better)",
             "Jev and Decisions: one request per text (all its questions); Haiku: one request per question"),
            (axes[1, 1], "cost per 1,000 questions (USD)", lambda v: f"${v:.3f}", "Cost per 1,000 questions, USD (lower is better)",
             "list prices x tokens measured in this run")]:
        vals = [float(sp.loc[m, col]) for m in sp_models]
        ax.bar([MODELS[m]["name"] for m in sp_models], vals, 0.6, color=[COLORS[m] for m in sp_models])
        for i, v in enumerate(vals):
            ax.text(i, v, fmt_label(v), ha="center", va="bottom", fontsize=9)
        ax.set_title(title)
        ax.set_xlabel(note, fontsize=8, color="#555")
        ax.margins(y=0.12)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Jev vs OpenAI Decisions vs Claude Haiku 4.5 on {df['id'].nunique():,} synthetic items "
                 f"({len(df):,} questions)", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out / "summary.png", dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------- report

def md(t):
    return t.to_markdown(index=False) if len(t) else "_no data_"


def public(t):
    return t[[c for c in t.columns if not str(c).startswith("_")]] if len(t) else t


def report(df, items, results, out, title):
    rng = np.random.default_rng(0)
    per_model, pairs = primary(df, rng)
    acc, verdicts, cal = plain_summary(per_model, pairs)
    fam = pd.DataFrame([family_metrics(df[df.family == f], m) for f in FAMILIES if f in set(df.family)
                        for m in present(df)]).round(3)
    included = ", ".join(f"{MODELS[m]['name']} (`{MODELS[m]['model_id']}`)" for m in results if results[m])
    speed = speed_and_cost(results)
    not_logged = [r["model"] for _, r in speed.iterrows() if r["requests retried"] == "not logged"] if len(speed) else []
    lines = [f"# {title}", "",
             f"Models: {included} | items: {len(items)} | questions: {len(df)}", "",
             "![summary](summary.png)", "",
             "## Plain-language summary", "",
             "Accuracy = share of correct answers, with its 95% confidence interval in brackets (cluster bootstrap over "
             "tasks). On scales, landing within ±1 level of the correct level counts as correct; the exact level is in "
             "the detailed metrics below. A refusal or an invalid answer counts as wrong.", "",
             "### Accuracy per model", md(acc), "",
             "### Which model is better? (paired differences: both models answered the same items)", md(verdicts), "",
             "### Are the probabilities calibrated? (only models that return probabilities)",
             "'yes' = no miscalibration detected beyond sampling noise; 'no (p<0.05)' = the model is systematically "
             "over- or under-confident.", "", md(cal), "",
             "### Human reference (blind review of a random sample)", md(human_reference()), "",
             "### Speed and cost",
             "Latency = the successful attempt only (back-offs after rate limits are excluded). Jev and Decisions answer "
             "all questions about an item in one request (3 for tweets); Haiku makes one request per question. Runs are "
             "concurrent and depend on the network: compare medians, not single values."
             + (f" {', '.join(not_logged)}: this run predates the retry-free timer, so a request's latency may include "
                "automatic SDK retries (the median is robust to this; p99 may not be)." if not_logged else ""), "",
             md(public(speed)), "",
             "### Hallucination: does the model admit when the text doesn't contain the answer?",
             "Haiku returns no probabilities, hence 'n/a' for the H02 no-information rows.", "", md(halluc_summary(df)), "",
             "## Primary metrics per model (95% cluster-bootstrap CI; clusters = tasks)", md(public(per_model)), "",
             "## Pairwise comparisons (difference = first minus second model)", md(public(pairs)), "",
             "## All metrics per family and model (point estimates)", md(fam), "",
             "## By difficulty", md(breakdown(df, "difficulty")), "",
             "## By hard type", md(breakdown(df, "hard_type")), "",
             "## By length", md(breakdown(df, "length")), "",
             "## By number of options / levels", md(breakdown(df, "n_cat")), "",
             "## Per task (diagnostic only: n=50, ±11pp)", md(breakdown(df, "task_id")), "",
             "## Tweets: cross-format consistency", "```", json.dumps(tweet_consistency(df), indent=1), "```", "",
             "## Determinism (repeat pass)", "```", json.dumps(determinism(results), indent=1), "```", "",
             "![reliability](reliability.png)", "", "![risk-coverage](risk_coverage.png)", ""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text("\n".join(lines))
    df.drop(columns=["options"] + [c for c in df.columns if c.endswith("_probs")], errors="ignore").to_csv(
        out / "item_level.csv", index=False)
    figures(df, out)
    summary_figure(df, per_model, speed, out)
    print("\n".join(lines[:16]))
    print(f"\n-> {out / 'report.md'}")
    return per_model, pairs


# ---------------------------------------------------------------- simulation (smoke tests)

def simulate(mode, rng):
    """Fake answers on the final items: Jev with `mode`, Decisions always calibrated, Haiku right 80% of the time."""
    items = [it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")]
    for task in ([] if items else TASKS):  # before data/final exists, fall back to the plan
        for r in read_jsonl(D / "plan" / f"{task}.jsonl")[:FINAL_N[TASKS[task]["primitive"]]]:
            if r["primitive"] == "tweets":
                r["targets"] = tweet_targets(r["label"])
            if r["primitive"] == "hallucination":
                r["question"] = "simulated question?"
                if TASKS[task]["qtype"] == "choice":
                    r["options"] = {"opt_a": "A", "opt_b": "B", "opt_c": "C"}
                    r["label"] = "opt_a" if r["label"] == "answerable" else ABSTAIN_KEY
            items.append(r)

    def fake(it, mode):
        answers = {}
        for qid, q in jev_questions(it["task_id"], it).items():
            gold = it["targets"][qid] if it["primitive"] == "tweets" else it["label"]
            opts = list(q["criteria"]) if q["type"] == "choice" else (list(range(len(q["criteria"]))) if q["type"] == "score" else [True, False])
            if gold == "unknown":  # H02: nothing to be right about; simulate a model that says 0.5 or guesses
                answers[qid] = {"type": "noul", "noul": 0.5 if mode in ("oracle", "calibrated") else float(rng.choice([0.05, 0.95]))}
                continue
            k = len(opts)
            if mode == "oracle":
                pred, ptop = gold, 1.0
            elif mode == "random":
                pred, ptop = opts[rng.integers(k)], 1.0 / k
            elif mode == "overconfident":  # right 70% of the time, always claims 0.95
                pred = gold if rng.random() < 0.7 else opts[(opts.index(gold) + 1 + rng.integers(k - 1)) % k]
                ptop = 0.95
            else:  # calibrated: claims q, right with probability q
                qv = rng.uniform(max(0.5, 1.0 / k), 1.0)
                pred = gold if rng.random() < qv else opts[(opts.index(gold) + 1 + rng.integers(k - 1)) % k]
                ptop = qv
            probs = {o: (ptop if o == pred else (1 - ptop) / (k - 1)) for o in opts}
            if mode == "random":
                probs = {o: 1.0 / k for o in opts}
            if q["type"] == "choice":
                answers[qid] = {"type": "choice", "choice": pred, "confidence": ptop, "probabilities": probs}
            elif q["type"] == "score":
                answers[qid] = {"type": "score", "score": sum(i * p for i, p in probs.items()), "confidence": ptop,
                                "probabilities": {str(i): p for i, p in probs.items()}}
            else:
                answers[qid] = {"type": "noul", "noul": probs[True]}
        return answers

    results = {"jev": [], "luna": [], "haiku": []}
    for it in items:
        results["jev"].append({"id": it["id"], "rep": 0, "response": {"answers": fake(it, mode)}})
        results["luna"].append({"id": it["id"], "rep": 0, "response": {"answers": fake(it, "calibrated")}})
        for qid, q in jev_questions(it["task_id"], it).items():
            gold = it["targets"][qid] if it["primitive"] == "tweets" else it["label"]
            if gold == "unknown":
                continue
            opts = list(q["criteria"]) if q["type"] == "choice" else (list(range(len(q["criteria"]))) if q["type"] == "score" else [True, False])
            h = gold if rng.random() < 0.8 else opts[(opts.index(gold) + 1) % len(opts)]
            results["haiku"].append({"id": it["id"], "qid": qid, "label": h, "valid": True})
    return items, results


def main():
    warnings.filterwarnings("ignore", category=RuntimeWarning)  # empty slices / degenerate per-task metrics
    warnings.filterwarnings("ignore", message=".*(ill-defined|single label|Only one class).*")
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulate", choices=["oracle", "random", "overconfident", "calibrated"])
    a = ap.parse_args()
    if a.simulate:
        items, results = simulate(a.simulate, np.random.default_rng(1))
        out, title = RES / f"sim_{a.simulate}", f"SIMULATION ({a.simulate}) - not real results"
    else:
        items = [it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")]
        results = {m: read_jsonl(RES / cfg["folder"] / "responses.jsonl") for m, cfg in MODELS.items()}
        results = {m: r for m, r in results.items() if r}
        out, title = RES, "Benchmark report: Jev vs OpenAI Decisions vs Claude Haiku 4.5"
    df = assemble(items, results)
    report(df, items, results, out, title)


if __name__ == "__main__":
    main()

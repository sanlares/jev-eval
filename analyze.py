"""Pre-registered analysis: Jev vs ground truth (accuracy + calibration) and vs Haiku 4.5 (accuracy).

  .venv/bin/python analyze.py                      # real results -> results/report.md, figures, item_level.csv
  .venv/bin/python analyze.py --simulate oracle    # smoke tests on the plan with fake predictors
                                  (oracle | random | overconfident | calibrated) -> results/sim_<mode>/

Primary metrics (fixed before the full Jev run): accuracy per family (choice / noul@0.5 / scales within +-1 level),
paired Jev-Haiku accuracy difference, and Noul Brier + ECE. Exact level on scales is secondary: the human review showed
that two careful people disagree by one level on about half of the scale items. Everything else is exploratory.
CIs: 95% two-stage cluster bootstrap (tasks, then items within task), B=2000.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest, spearmanr
from sklearn.metrics import cohen_kappa_score, f1_score, roc_auc_score

from build import D, read_jsonl
from specs import ABSTAIN_KEY, FINAL_N, JEV_MODEL, TASKS, jev_questions, labels, tweet_targets

RES = Path(__file__).parent / "results"
B = 2000
N_BINS = 10
FAMILIES = ["choice", "score", "noul", "tweets_score", "tweets_choice", "tweets_noul"]


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


def parse_jev(row, ans):
    t = row["qtype"]
    if t == "choice":
        probs = {k: float(v) for k, v in ans["probabilities"].items()}
        p = np.array([probs.get(o, 0.0) for o in row["options"]])
        pred = ans["choice"]
        return dict(jev_pred=pred, jev_conf=float(ans["confidence"]), jev_ptop=float(p.max()),
                    jev_pgold=probs.get(row["gold"], 0.0), jev_probs=p.tolist())
    if t == "score":
        probs = {int(k): float(v) for k, v in ans["probabilities"].items()}
        p = np.array([probs.get(i, 0.0) for i in range(row["n_cat"])])
        return dict(jev_pred=int(p.argmax()), jev_conf=float(ans["confidence"]), jev_ptop=float(p.max()),
                    jev_pgold=float(p[row["gold"]]), jev_probs=p.tolist(), jev_expected=float(ans["score"]))
    pr = float(ans["noul"])
    pgold = np.nan if row["gold"] == "unknown" else (pr if row["gold"] else 1 - pr)
    return dict(jev_pred=pr >= 0.5, jev_p=pr, jev_ptop=max(pr, 1 - pr), jev_conf=abs(2 * pr - 1), jev_pgold=pgold)


def assemble(items, jev_resps, haiku_resps):
    jev0 = {r["id"]: r["response"] for r in jev_resps if r["rep"] == 0}
    hk = {(r["id"], r["qid"]): r["label"] for r in haiku_resps if r.get("valid", True)}
    rows = []
    for it in items:
        for row in question_rows(it):
            ans = (jev0.get(it["id"]) or {}).get("answers", {}).get(row["qid"])
            if ans:
                row.update(parse_jev(row, ans))
            row["haiku_pred"] = hk.get((it["id"], row["qid"]))
            rows.append(row)
    df = pd.DataFrame(rows)
    # "unknown" gold (H02) has no right/wrong answer: it is scored separately in halluc_summary
    df["jev_ok"] = [(p == g) if isinstance(p, (str, bool, np.bool_, int, np.integer)) and g != "unknown" else np.nan
                    for p, g in zip(df.get("jev_pred", pd.Series([None] * len(df))), df["gold"])]
    df["haiku_ok"] = [(p == g) if p is not None and g != "unknown" else np.nan
                      for p, g in zip(df["haiku_pred"], df["gold"])]
    # scales (score questions): also "within +-1 level", the primary metric for these families
    for who in ("jev", "haiku"):
        preds = df.get(f"{who}_pred", pd.Series([None] * len(df)))
        df[f"{who}_ok1"] = [abs(int(p) - int(g)) <= 1 if t == "score" and pd.notna(o) else o
                            for p, g, o, t in zip(preds, df["gold"], df[f"{who}_ok"], df["qtype"])]
    return df


# ---------------------------------------------------------------- family metrics (exploratory, point estimates)

def family_metrics(d):
    fam = d["family"].iloc[0]
    j = d.dropna(subset=["jev_ok"])
    m = {"n": len(d), "jev_acc": j["jev_ok"].mean()}
    if d["haiku_ok"].notna().any():
        m["haiku_acc"] = d["haiku_ok"].dropna().mean()
    if j.empty:
        return m
    qtype = d["qtype"].iloc[0]
    if qtype in ("choice", "score"):
        m["jev_ece_top"] = ece(j["jev_ptop"], j["jev_ok"])
        onehot = [np.eye(n)[o.index(g) if qtype == "choice" else g]
                  for n, o, g in zip(j["n_cat"], j["options"], j["gold"])]
        m["jev_brier"] = np.mean([((np.array(p) - y) ** 2).sum() for p, y in zip(j["jev_probs"], onehot)])
    if qtype == "choice":
        m["jev_macro_f1"] = np.mean([f1_score(g["gold"].astype(str), g["jev_pred"].astype(str), average="macro")
                                     for _, g in j.groupby("task_id")])
        if "haiku_acc" in m:
            m["haiku_macro_f1"] = np.mean([f1_score(g["gold"].astype(str), g["haiku_pred"].astype(str), average="macro")
                                           for _, g in d.dropna(subset=["haiku_ok"]).groupby("task_id")])
    if qtype == "score":
        m["jev_within1"] = (abs(j["jev_pred"].astype(int) - j["gold"].astype(int)) <= 1).mean()
        m["jev_mae_norm"] = (abs(j["jev_expected"] - j["gold"]) / (j["n_cat"] - 1)).mean()
        m["jev_qwk"] = np.mean([cohen_kappa_score(g["gold"].astype(int), g["jev_pred"].astype(int), weights="quadratic",
                                                  labels=list(range(g["n_cat"].iloc[0])))
                                for _, g in j.groupby("task_id")])
        rps = []
        for p, g, n in zip(j["jev_probs"], j["gold"], j["n_cat"]):
            rps.append(((np.cumsum(p) - (np.arange(n) >= g)) ** 2)[:-1].sum() / (n - 1))
        m["jev_rps"] = np.mean(rps)
        h = d.dropna(subset=["haiku_ok"])
        if len(h):
            m["haiku_within1"] = (abs(h["haiku_pred"].astype(int) - h["gold"].astype(int)) <= 1).mean()
            m["haiku_qwk"] = np.mean([cohen_kappa_score(g["gold"].astype(int), g["haiku_pred"].astype(int),
                                                        weights="quadratic", labels=list(range(g["n_cat"].iloc[0])))
                                      for _, g in h.groupby("task_id")])
    if qtype == "noul":
        y, p = j["gold"].astype(float).values, j["jev_p"].values
        m["jev_auroc"] = roc_auc_score(y, p) if len(set(y)) == 2 else np.nan
        m["jev_brier"] = np.mean((p - y) ** 2)
        pc = np.clip(p, 1e-6, 1 - 1e-6)
        m["jev_logloss"] = -np.mean(y * np.log(pc) + (1 - y) * np.log(1 - pc))
        m["jev_ece"] = ece(p, y)
    return m


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


def calibration_test(d, rng):
    """ECE plus a consistency-resampling test (Brocker & Smith 2007): outcomes are redrawn as if Jev were
    perfectly calibrated (y* ~ Bernoulli(p)); the null ECE distribution absorbs the finite-sample noise floor.
    Noul: p = P(yes) vs gold. Choice/score: p = top-label probability vs correctness."""
    if d["qtype"].iloc[0] == "noul":
        p, y = d["jev_p"].values.astype(float), d["gold"].astype(float).values
    else:
        p, y = d["jev_ptop"].values.astype(float), d["jev_ok"].astype(float).values
    obs = ece(p, y)
    null = np.array([ece(p, (rng.random(len(p)) < p).astype(float)) for _ in range(B)])
    return f"{obs:.3f} ({np.percentile(null, 95):.3f}, p={(null >= obs).mean():.3f})"


def primary(df, rng):
    out = []
    for fam in FAMILIES:
        d = df[(df["family"] == fam) & df["jev_ok"].notna()].reset_index(drop=True)
        if d.empty:
            continue
        scale = d["qtype"].iloc[0] == "score"
        j, h = ("jev_ok1", "haiku_ok1") if scale else ("jev_ok", "haiku_ok")  # primary metric columns
        stats = {"jev_acc": lambda s: s[j].astype(float).mean()}
        if scale:
            stats["jev_exact"] = lambda s: s["jev_ok"].astype(float).mean()
        paired = d[h].notna().all()
        if paired:
            stats["haiku_acc"] = lambda s: s[h].astype(float).mean()
            stats["diff_jev_minus_haiku"] = lambda s: (s[j].astype(float) - s[h].astype(float)).mean()
        if d["qtype"].iloc[0] == "noul":
            stats["jev_brier"] = lambda s: np.mean((s["jev_p"] - s["gold"].astype(float)) ** 2)
        res = cluster_bootstrap(d, stats, rng)
        row = {"family": fam, "metric": "within +-1 level" if scale else "exact", "n_items": len(d),
               "n_tasks": d["task_id"].nunique()}
        for k, (pt, lo, hi) in res.items():
            row[k] = f"{pt:.3f} [{lo:.3f}, {hi:.3f}]"
        if paired:
            b = int((d[j].astype(bool) & ~d[h].astype(bool)).sum())
            c = int((~d[j].astype(bool) & d[h].astype(bool)).sum())
            row["mcnemar"] = f"jev-only={b}, haiku-only={c}, p={binomtest(b, b + c).pvalue:.4f}" if b + c else "no discordant pairs"
        row["jev_ece (null95, p)"] = calibration_test(d, rng)
        out.append(row)
    return pd.DataFrame(out).fillna("")


# ---------------------------------------------------------------- breakdowns, consistency, determinism

def breakdown(df, by):
    d = df[df["jev_ok"].notna()]
    g = d.groupby(["family", by])
    t = g.agg(n=("jev_ok", "size"), jev_acc=("jev_ok", "mean"))
    if d["haiku_ok"].notna().any():
        t["haiku_acc"] = g["haiku_ok"].mean()
    return t.round(3).reset_index()


def tweet_consistency(df):
    t = df[df["family"].str.startswith("tweets") & df["jev_ok"].notna()]
    if t.empty:
        return {}
    w = t.pivot_table(index="id", columns="qid", values=["jev_pred"], aggfunc="first")["jev_pred"]
    e = t[t["qid"] == "sentiment"].set_index("id")["jev_expected"]
    p = t[t["qid"] == "expects_rise"].set_index("id")["jev_p"]
    collapsed = w["sentiment"].astype(int).map(lambda l: tweet_targets(l)["direction"])
    return {
        "spearman(score_expected, P(rise))": round(spearmanr(e, p.reindex(e.index)).statistic, 3),
        "agree(choice, collapsed score)": round((w["direction"] == collapsed).mean(), 3),
        "agree(noul@0.5, choice==bullish)": round((w["expects_rise"].astype(bool) == (w["direction"] == "bullish")).mean(), 3),
    }


def determinism(items, jev_resps):
    by = {}
    for r in jev_resps:
        by.setdefault(r["id"], {})[r["rep"]] = r["response"]["answers"]
    pairs = [(v[0], v[1]) for v in by.values() if 0 in v and 1 in v]
    if not pairs:
        return {}
    same, maxdiff = 0, 0.0
    for a, b in pairs:
        for qid in a:
            x, y = a[qid], b[qid]
            if x["type"] == "noul":
                maxdiff = max(maxdiff, abs(x["noul"] - y["noul"]))
                same += (x["noul"] >= .5) == (y["noul"] >= .5)
            else:
                maxdiff = max(maxdiff, max(abs(x["probabilities"][k] - y["probabilities"][k]) for k in x["probabilities"]))
                same += x.get("choice", x.get("score")) == y.get("choice", y.get("score"))
    nq = sum(len(a) for a, _ in pairs)
    return {"repeated_items": len(pairs), "same_answer_rate": round(same / nq, 4), "max_prob_abs_diff": round(maxdiff, 4)}


# ---------------------------------------------------------------- hallucination + plain-language summary

def wilson(k, n):
    """95% Wilson interval for a proportion k/n (as percentages)."""
    if n == 0:
        return "-"
    z, p = 1.96, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return f"{100 * p:.0f}% [{max(0, 100 * (c - h)):.0f}-{min(100, 100 * (c + h)):.0f}]"


def halluc_summary(df):
    """Long table: one row per measurement, one column per model."""
    rows = []
    c = df[df.family == "halluc_choice"]
    if len(c) and "jev_pred" in c:
        un, an = c[c.gold == ABSTAIN_KEY], c[c.gold != ABSTAIN_KEY]

        def col(pred_col, f):
            return wilson(*f(pred_col)) if not c[pred_col].isna().all() else "-"
        for what, f in [
            ("H01: elige 'no se puede determinar' cuando el texto NO tiene la respuesta (mas es mejor)",
             lambda pc: ((un[pc] == ABSTAIN_KEY).sum(), len(un))),
            ("H01: elige 'no se puede determinar' cuando el texto SI tiene la respuesta (menos es mejor)",
             lambda pc: ((an[pc] == ABSTAIN_KEY).sum(), len(an))),
            ("H01: acierta la opcion cuando el texto tiene la respuesta (mas es mejor)",
             lambda pc: ((an[pc] == an.gold).sum(), len(an)))]:
            rows.append({"medicion": what, "Jev": col("jev_pred", f), "Haiku": col("haiku_pred", f)})
    n = df[df.family == "halluc_noul"]
    if len(n) and "jev_p" in n:
        p = n[n.gold == "unknown"]["jev_p"].dropna()
        an = n[n.gold != "unknown"]
        rows += [
            {"medicion": "H02 sin informacion: P(si) promedio (ideal 0.50)", "Jev": f"{p.mean():.2f}" if len(p) else "-", "Haiku": "n/a"},
            {"medicion": "H02 sin informacion: dice 'no se', 0.3 <= P <= 0.7 (mas es mejor)",
             "Jev": wilson(((p >= .3) & (p <= .7)).sum(), len(p)), "Haiku": "n/a"},
            {"medicion": "H02 sin informacion: alucina con confianza, P < 0.2 o P > 0.8 (menos es mejor)",
             "Jev": wilson(((p < .2) | (p > .8)).sum(), len(p)), "Haiku": "n/a"},
            {"medicion": "H02 controles con respuesta: acierta (mas es mejor)",
             "Jev": wilson(an["jev_ok"].dropna().astype(bool).sum(), an["jev_ok"].notna().sum()),
             "Haiku": wilson(an["haiku_ok"].dropna().astype(bool).sum(), an["haiku_ok"].notna().sum())},
        ]
    return pd.DataFrame(rows)


def human_reference():
    """Agreement of the human reviewer with the ground truth (data/final/revision_humana.csv), if filled in."""
    import csv
    from build import normalize
    path = D / "final" / "revision_humana.csv"
    if not path.exists():
        return pd.DataFrame()
    gold = {it["id"]: it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")}
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["tu_respuesta"].strip()]
    out = {"categorias y si/no": [0, 0, None], "escalas": [0, 0, 0]}
    for r in rows:
        g = gold[r["id"]]["label"]
        scale = isinstance(g, int) and not isinstance(g, bool)
        k = "escalas" if scale else "categorias y si/no"
        out[k][1] += 1
        out[k][0] += normalize(r["tu_respuesta"]) == normalize(g)
        if scale and r["tu_respuesta"].strip().lstrip("-").isdigit():
            out[k][2] += abs(int(r["tu_respuesta"]) - g) <= 1
    return pd.DataFrame([{"tipo": k, "items revisados": n, "coincidencia exacta": wilson(a, n),
                          "dentro de +-1 nivel": wilson(w, n) if w is not None else "-"}
                         for k, (a, n, w) in out.items() if n])


def plain_summary(prim):
    """One line per family, in plain Spanish."""
    out = []
    for _, r in prim.iterrows():
        line = {"que se mide": r["family"], "metrica": "acierta +-1 nivel" if r["metric"] != "exact" else "exacta",
                "accuracy Jev [IC 95%]": r["jev_acc"]}
        if r.get("haiku_acc"):
            lo, hi = map(float, r["diff_jev_minus_haiku"].split("[")[1].rstrip("]").split(","))
            line["accuracy Haiku [IC 95%]"] = r["haiku_acc"]
            line["¿Jev distinto de Haiku?"] = ("si, Jev mejor" if lo > 0 else "si, Jev peor" if hi < 0 else "no se puede afirmar")
        pval = float(r["jev_ece (null95, p)"].split("p=")[1].rstrip(")"))
        line["¿probabilidades de Jev calibradas?"] = "no (p<0.05)" if pval < 0.05 else "no se detecta descalibracion"
        out.append(line)
    return pd.DataFrame(out)


# ---------------------------------------------------------------- figures

def figures(df, out):
    fams = [f for f in ["choice", "score", "noul", "tweets_noul"] if f in set(df["family"]) and df[df.family == f]["jev_ok"].notna().any()]
    if not fams:
        return
    fig, axes = plt.subplots(1, len(fams), figsize=(4.2 * len(fams), 4), squeeze=False)
    for ax, fam in zip(axes[0], fams):
        d = df[(df.family == fam) & df["jev_ok"].notna()]
        if d["qtype"].iloc[0] == "noul":
            conf, hit, label = d["jev_p"].values, d["gold"].astype(float).values, "P(yes)"
        else:
            conf, hit, label = d["jev_ptop"].values, d["jev_ok"].astype(float).values, "top-label probability"
        pts = reliability(conf, hit)
        ax.plot([0, 1], [0, 1], ls="--", c="grey", lw=1)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", c="#3b6fb6")
        ax.set(title=f"{fam} (ECE={ece(conf, hit):.3f})", xlabel=label, ylabel="observed frequency", xlim=(0, 1), ylim=(0, 1))
    fig.tight_layout()
    fig.savefig(out / "reliability.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.5, 4))
    for fam in [f for f in FAMILIES if f in set(df.family) and not f.endswith("noul")]:
        d = df[(df.family == fam) & df["jev_ok"].notna()].sort_values("jev_conf", ascending=False)
        if d.empty:
            continue
        cov = np.arange(1, len(d) + 1) / len(d)
        ax.plot(cov, d["jev_ok"].astype(float).cumsum().values / np.arange(1, len(d) + 1), label=fam)
    ax.set(xlabel="coverage (answered, most confident first)", ylabel="accuracy on answered", title="Jev risk-coverage")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "risk_coverage.png", dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------- report

def md(t):
    return t.to_markdown(index=False) if len(t) else "_no data_"


def report(df, items, jev_resps, out, title):
    rng = np.random.default_rng(0)
    prim = primary(df, rng)
    fam = pd.DataFrame([{"family": f, **family_metrics(df[df.family == f])} for f in FAMILIES if f in set(df.family)]).round(3)
    per_task = breakdown(df, "task_id")
    lines = [f"# {title}", "",
             f"Model: `{JEV_MODEL}` | baseline: `claude-haiku-4-5` | items: {len(items)} | questions: {len(df)}", "",
             "## Resumen simple", "",
             "Accuracy = % de respuestas correctas. IC 95% = rango donde esta el valor real con 95% de confianza. "
             "Si el IC de la diferencia Jev-Haiku no incluye 0, la diferencia es estadisticamente significativa.", "",
             md(plain_summary(prim)), "",
             "En las escalas la metrica principal es 'acierta dentro de +-1 nivel' (el nivel exacto queda como "
             "metrica secundaria, columna jev_exact): dos personas cuidadosas difieren en un nivel en ~la mitad de "
             "estos items.", "",
             "### Referencia humana (revision a ciegas de una muestra)", md(human_reference()), "",
             "### Alucinacion: ¿Jev admite cuando el texto no tiene la respuesta?",
             "(Haiku no da probabilidades, por eso 'n/a' en H02 sin informacion.)", md(halluc_summary(df)), "",
             "## Primary metrics (95% cluster-bootstrap CI; clusters = tasks)", md(prim), "",
             "_ECE column: observed ECE (95th percentile of ECE under perfect calibration, p-value). "
             "A small p means miscalibration beyond the finite-sample noise floor._", "",
             "## All metrics per family (point estimates)", md(fam), "",
             "## By difficulty", md(breakdown(df, "difficulty")), "",
             "## By hard type", md(breakdown(df, "hard_type")), "",
             "## By length", md(breakdown(df, "length")), "",
             "## By number of options / levels", md(breakdown(df, "n_cat")), "",
             "## Per task (diagnostic only: n=50, ±11pp)", md(per_task), "",
             "## Tweets: cross-format consistency (Jev)", "```", json.dumps(tweet_consistency(df), indent=1), "```", "",
             "## Determinism (repeat pass)", "```", json.dumps(determinism(items, jev_resps), indent=1), "```", "",
             "![reliability](reliability.png)", "", "![risk-coverage](risk_coverage.png)", ""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text("\n".join(lines))
    df.drop(columns=["options", "jev_probs"], errors="ignore").to_csv(out / "item_level.csv", index=False)
    figures(df, out)
    print("\n".join(lines[:12]))
    print(f"\n-> {out / 'report.md'}")
    return prim, fam


# ---------------------------------------------------------------- simulation (smoke tests)

def simulate(mode, rng):
    """Fake Jev/Haiku responses on the planned items (labels known, text irrelevant)."""
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
    jev, hk = [], []
    for it in items:
        answers = {}
        for qid, q in jev_questions(it["task_id"], it).items():
            gold = it["targets"][qid] if it["primitive"] == "tweets" else it["label"]
            opts = list(q["criteria"]) if q["type"] == "choice" else (list(range(len(q["criteria"]))) if q["type"] == "score" else [True, False])
            if gold == "unknown":  # H02: nothing to be right about; simulate a model that says 0.5 or guesses
                p = 0.5 if mode in ("oracle", "calibrated") else float(rng.choice([0.05, 0.95]))
                answers[qid] = {"type": "noul", "noul": p}
                continue
            k = len(opts)
            if mode == "oracle":
                pred, ptop = gold, 1.0
            elif mode == "random":
                pred, ptop = opts[rng.integers(k)], 1.0 / k
            elif mode == "overconfident":  # right 70% of the time, always claims 0.95
                pred = gold if rng.random() < 0.7 else opts[(opts.index(gold) + 1 + rng.integers(k - 1)) % k] if k > 1 else gold
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
            h = gold if rng.random() < 0.8 else opts[(opts.index(gold) + 1) % k]
            hk.append({"id": it["id"], "qid": qid, "label": h, "valid": True})
        jev.append({"id": it["id"], "rep": 0, "response": {"answers": answers}})
    return items, jev, hk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulate", choices=["oracle", "random", "overconfident", "calibrated"])
    a = ap.parse_args()
    if a.simulate:
        items, jev, hk = simulate(a.simulate, np.random.default_rng(1))
        out, title = RES / f"sim_{a.simulate}", f"SIMULATION ({a.simulate}) - not real results"
    else:
        items = [it for p in FINAL_N for it in read_jsonl(D / "final" / f"{p}.jsonl")]
        jev, hk = read_jsonl(RES / "jev" / "responses.jsonl"), read_jsonl(RES / "haiku" / "responses.jsonl")
        out, title = RES, "Jev benchmark report"
    df = assemble(items, jev, hk)
    report(df, items, jev, out, title)


if __name__ == "__main__":
    main()

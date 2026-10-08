"""Builds results/cases.md: every question where at least one model fails, written out in full, with a verdict.

  .venv/bin/python make_cases.py      # needs the three result files in results/ (see analyze.py)

The notes below are a human-supervised reading of each failing item after the full runs. They do not change any
score: they only say whether an error is clear, a near-tie, or caused by a debatable label.
"""
import json
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

import analyze as A
from specs import jev_questions

warnings.filterwarnings("ignore")
OUT = Path(__file__).parent / "results" / "cases.md"

TASK_NAMES = {"C01": "Support-ticket routing", "C02": "Emotion of a message", "C03": "News topic",
              "C04": "Cuisine of a recipe", "C05": "Scientific field of an abstract", "C06": "Smart-home command",
              "C07": "Medical specialty", "C08": "Programming language", "C09": "Content moderation",
              "C10": "Hotel-review aspect", "S01": "Bug severity", "S02": "Customer frustration", "S03": "Formality",
              "S04": "Technical level", "S05": "Politeness of an email", "S06": "Helpdesk urgency",
              "S07": "Does the answer answer the question?", "S08": "Star rating of a review",
              "S09": "Risk of an activity", "S10": "Hobby expertise", "N01": "Asks for a refund?",
              "N02": "Contains personal data?", "N03": "Does the passage answer the question?",
              "N04": "Does the source support the claim?", "N05": "Same product?", "N06": "Phishing?",
              "N07": "Delivery problem?", "N08": "Asks for a human?", "N09": "Assigns an action item?",
              "N10": "Has the event already happened?", "T01": "Stock tweets",
              "H01": "Hallucination (multiple choice)", "H02": "Hallucination (yes/no)"}
HARD_NAMES = {"long_irrelevant": "long irrelevant context", "near_miss": "near miss", "mixed_signals": "mixed signals",
              "jargon_only": "jargon only", "tempting_guess": "tempting guess",
              "related_but_missing": "related info, missing fact"}
NAMES = {"jev": "Jev", "luna": "Decisions", "haiku": "Haiku"}

# ---- reading of every failing item: (verdict, explanation). verdict: clear | borderline | label
NOTES = {
    "C02_048": ("label", "The dog left a 'beautiful present' on the pillow and the writer thanks it sarcastically. The label says disgust; all three models say anger. With that much sarcasm, anger is as defensible as disgust."),
    "C04_048": ("label", "It is hotteok (a Korean street dessert), but the text has no exclusively Korean cue: fried dough with brown sugar, cinnamon and nuts fits Mexican or Moroccan cooking just as well. The label is right but cannot be deduced from the text."),
    "H01_006": ("label", "Chili recipe with jarred jalapeños, cumin and smoked paprika. The label is `cannot_determine` because the text never says how spicy it is; all three models infer `medium_heat`. It was a 'tempting guess' item, and here the inference is reasonable."),
    "N05_015": ("clear", "The same product listed in kg/cm vs pounds/inches. But 2.3 kg = 5.1 lb (not 6.3) and 108 cm = 42.5 in (not 47.5): the numbers don't match, so it is not the same variant. All three say 'yes' with 92-98% confidence: none of them checks unit conversions."),
    "N05_047": ("clear", "3.8 kg = 8.4 lb, not 6.2 lb (the text itself says one felt lighter). The cord does match (6 m ≈ 19 ft). All three say 'same product' at 92-95%: numbers again."),
    "C02_016": ("clear", "For the first time in three years the specialist sends the writer home with nothing to fix and no follow-up. That is relief and joy. Jev and Decisions say surprise, with low confidence (55-61%)."),
    "C02_046": ("label", "A referee wrongly disallows a goal in a final, the formal complaint gets a useless auto-reply, and the kid cries the whole ride home. There is anger (the label) and sadness (Jev and Decisions, 83-85%) at once: a genuinely mixed text."),
    "C04_056": ("borderline", "Rice cooked until it falls apart, minced pork, ginger, raw egg, fried garlic and white pepper: Thai jok moo. But nearly identical dishes exist in Korea (juk) and Japan (okayu). Jev said Korean and Decisions Japanese: weak cues."),
    "H01_038": ("clear", "A shopping list with no mention of a budget, and one option was `no_budget_set`. Jev (78%) and Decisions (99%) picked it, which asserts something the text doesn't say: not mentioned is not the same as not existing. Haiku correctly picked `cannot_determine`."),
    "T01_117": ("clear", "Sarcasm about 'regulatory news' that is a routine license renewal. The correct direction is neutral. Jev and Decisions read the mocking tone as a bearish signal: they confuse the author's tone with what the news implies."),
    "T01_001": ("borderline", "One analyst raises the price target to $58 and another cuts it to $45: neutral. Jev gave 51% and Decisions 50% that it rises, i.e. 'I can't tell', which is the right answer in spirit. Because 0.5 or more counts as 'yes', the threshold scores it as an error."),
    "S06_005": ("clear", "The writer reports a phishing email they did NOT open and says explicitly that there is no rush and any free afternoon this month is fine. Decisions (80%) and Haiku answered the most urgent level because of the word phishing. Only Jev followed what the text says."),
    "C01_006": ("borderline", "'Session expired' every time the user tries to log in: account access. Decisions said `bug_report` at 49%, nearly a tie. It had already been flagged as borderline during adjudication."),
    "C02_005": ("clear", "A great match, but a stranger uses the next seat as a napkin and trash can and drinks from the writer's cup, and the writer can't stop thinking about it. That is disgust. Decisions said anger (90%)."),
    "C02_010": ("clear", "The writer tastes the soup, pushes it away, orders toast and points at the bowl like someone pointing at a small fire. That is disgust. Decisions said anger (89%): it latched onto a distractor phrase about feeling personally offended."),
    "C02_020": ("clear", "A hostel with stained sheets, ants in the mini-fridge and a drain smell; the writer sleeps fully dressed and won't touch anything barefoot. That is disgust. Decisions said anger (91%)."),
    "C02_050": ("clear", "A hair cooked inside the wrap; the friend nearly throws up. That is disgust. Decisions said anger (65%). This makes four texts (plus C02_048) where Decisions reads disgust as anger: it is a pattern."),
    "C02_052": ("clear", "Sarcasm: the writer is 'not surprised even one little bit' that a superstar walked on stage in a 200-person venue. The emotion is surprise. Decisions said joy (88%): it read the excitement and missed the sarcasm. Joy is there too, but the text revolves around not being able to believe it."),
    "H01_048": ("clear", "A cake that says 'Four more years', hugs, and they're already taking down the rival's signs: Ramírez won, although the text never says it literally. Decisions picked `cannot_determine` (60%): too literal, the opposite of hallucinating."),
    "N03_023": ("borderline", "The question is whether the museum is stroller-accessible; the passage only describes the gift shop and the café. It does not contain the answer. Decisions: 51%, a tie."),
    "N06_038": ("clear", "An internal email from the company's own domain saying Marco shared some photos, with no links and in imperfect English. It is legitimate. Decisions gave it 63% phishing, probably because of the unusual English."),
    "N06_043": ("borderline", "An internal notification written with humour, explicitly with no link. Legitimate. Decisions: 52%, nearly a tie."),
    "N10_012": ("clear", "All runners on the start line and, 20 minutes before the gun, the race is cancelled and thousands of people go home. The race did NOT happen. Decisions: 97% that it did. A high-confidence error."),
    "N10_025": ("clear", "The bridge is not finished yet because of problems with the beams. Decisions: 72% that the event already happened."),
    "N10_049": ("clear", "A half-built footbridge; the contractor abandoned the job. Decisions: 100% that it already happened, with total certainty. Jev and Haiku said no. Decisions' third error on this task."),
    "T01_004": ("label", "One plant line stopped for maintenance, with no change to production guidance. The label says neutral; Decisions says bearish (75%). Debatable: a stoppage is mildly negative news even if guidance doesn't change."),
    "T01_137": ("label", "A voluntary recall of one batch over a labelling error, under 0.1% of units, no health risk. The label says neutral; Decisions says bearish (75%). Debatable for the same reason as the previous one."),
    "T01_151": ("clear", "Sarcasm: 'the bears were right' after the lawsuit is dismissed, plus a plan to buy more shares tomorrow. It is bullish. Decisions: 35% that it rises; it missed the sarcasm."),
    "C01_041": ("clear", "Since the company switched identity provider (SSO), the app goes blank when opening the workspace. That is account access: the criteria mention SSO explicitly. Haiku said `bug_report`."),
    "C01_052": ("clear", "Users with an unverified role are bounced back to login after an email-domain migration. Account access. Haiku said `bug_report` (same pattern as the previous one)."),
    "C06_019": ("clear", "Asks for a reminder to write an email (not in the list, so it's `other`) and adds that they don't want music. Haiku picked `set_alarm`: a reminder isn't an alarm."),
    "C09_031": ("borderline", "A passive-aggressive comment that belittles the other user's experience. The label says harassment; Haiku says acceptable. It's the line between harsh criticism and a personal attack."),
    "H01_024": ("clear", "The writer left their phone charger at the Airbnb again; nothing says whether they travel alone or with others. Haiku picked `traveling_with_others`: it made up a fact, i.e. hallucinated."),
    "N02_008": ("clear", "The writer gives their current street address, unit number included: personal data. Haiku said no."),
    "N05_052": ("clear", "1.2 kg = 2.6 lb and 14 in = 35.5 cm: they match, it's the same product. Haiku said they are different: it fails on unit conversions."),
    "S07_012": ("clear", "The answer is buried in a wedding story, but it does answer directly: for business fluency in a year, immersion wins. Label: 3. Jev and Decisions said 2 (correct within ±1). Haiku said 1, two levels below: it got lost in the irrelevant text."),
    "S10_001": ("clear", "20+ years keeping aquariums, six tanks, breeds difficult species, gives talks to beginners and has judged competitions. That is expert (6). Haiku said 4."),
    "S10_012": ("clear", "A professional baker for 11 years, 200 loaves a day, has trained apprentices; asks a question that sounds basic. That is expert (6). Haiku said 4: it fell for the distractor."),
    "T01_096": ("label", "The partnership looks decent, the author is not turning bullish but trimmed their short a bit. The most ambiguous tweet in the set: the author is still betting on a drop, just less. The label says mildly bullish. All three models hesitated or failed in at least one of the three formats."),
    "T01_100": ("borderline", "The company is insured against the lawsuit, but such cases usually weigh on the stock; the author is not buying more but is staying in. Mildly bearish; Haiku said neutral. Mixed signals."),
    "T01_139": ("clear", "The product was approved, but with extra capital requirements that eat into the margin, and the author sold some shares. Mildly bearish; Haiku said neutral."),
    "C04_042": ("clear", "Semolina pancakes with hundreds of tiny holes, cooked on one side only, served with butter and honey: Moroccan baghrir. Jev said Italian (50%); the other two got it right with 98% or more."),
    "C05_050": ("borderline", "A 400,000-person biobank: carriers of a rare genetic variant have a higher risk of stones. Genetics (the exposure is the variant), but it is also epidemiology. Jev: epidemiology at 54%."),
    "N05_036": ("borderline", "The same earbuds, but one charging case has 450 mAh and the other 180 mAh: a different variant. Jev: 51%, a tie."),
    "T01_054": ("clear", "The put wall is getting torn through, the stock could gap another 20%, and the author bought their first calls: very bullish, in options slang. Jev answered bearish in ALL THREE formats (level 0, 'bearish', 35% that it rises). It read 'put' as a bearish signal. Jev's most consistent error."),
}
H02_NOTES = {
    "H02_081": ("clear", "Nobody mentions a photo of the cat. Jev (8%) and Decisions (3%) say with high confidence that it wasn't taken: they treat 'not mentioned' as 'didn't happen'."),
    "H02_033": ("borderline", "The writer went to the castle yesterday and their legs still hurt. Nothing about the museum. Both say no with high confidence (4% and 11%); tiredness is a weak cue."),
    "H02_045": ("label", "Thursday works better, but the writer wants to check with the team first: the team hasn't accepted yet. Saying 'no' is reasonable, so the item is wrongly framed as 'no information'."),
    "H02_020": ("label", "Results come out in two weeks and the writer is still waiting: not accepted yet. The models' 'no' is reasonable; the item is wrongly framed."),
    "H02_017": ("label", "15-minute meetings with no exceptions for latecomers suggests there is no evening session. Jev's 'no' (10%) is reasonable."),
    "H02_032": ("clear", "About a community garden; nothing about dogs. Jev: 17% that the writer has a dog (roughly 40% of households have one). Decisions: 50%."),
    "H02_042": ("clear", "About a broken streetlight; nothing about dogs. Jev: 17%. Decisions: 50%."),
    "H02_034": ("clear", "About a trip; nothing about pets. Jev: 12% that one is waiting at home. Decisions: 50%."),
}
VERDICTS = {"clear": "**Clear error**", "borderline": "**Borderline (near 50/50)**", "label": "**Debatable label**"}


def md_text(state):
    if isinstance(state, str):
        return "\n".join("> " + (l if l.strip() else "") for l in state.split("\n"))
    return "\n".join(f"> **{k}:** {v}" for k, v in state.items())


def options_md(q):
    crit = q.get("criteria")
    if q["type"] == "score":
        return "\n".join(f"- `{i}` {c}" for i, c in enumerate(crit))
    if q["type"] == "choice":
        return "\n".join(f"- `{k}`" + (f": {v}" if v else "") for k, v in crit.items())
    if crit:
        return f"- `true`: {crit['true']}\n- `false`: {crit['false']}"
    return "- `true` / `false` (no criteria)"


def answer_cell(r, m, q):
    p = r.get(f"{m}_pred")
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "—", "—"
    if q["type"] == "score":
        shown = f"{int(p)} ({q['criteria'][int(p)].split(':')[0]})"
    else:
        shown = f"`{json.dumps(p)}`" if not isinstance(p, str) else f"`{p}`"
    if m == "haiku":
        conf = "no probability"
    elif q["type"] == "noul":
        conf = f"P(yes) = {r[f'{m}_p']:.2f}"
    else:
        conf = f"{100 * r[f'{m}_ptop']:.0f}%"
    return shown, conf


def ok_mark(r, m):
    v = r[f"{m}_ok1"] if r["qtype"] == "score" else r[f"{m}_ok"]
    if pd.isna(v):
        return "—"
    if r["qtype"] == "score" and v and not r[f"{m}_ok"]:
        return "✅ (±1)"
    return "✅" if v else "❌"


def item_block(iid, rows, it, note):
    t = it["task_id"]
    diff = it["difficulty"] + (f" · trap: {HARD_NAMES.get(it['hard_type'], it['hard_type'])}" if it.get("hard_type") else "")
    out = [f"### {iid} · {TASK_NAMES[t]} · {diff}", "", "**Full text:**", "", md_text(it["state"]), ""]
    qs = jev_questions(t, it)
    for _, r in rows.iterrows():
        q = qs[r["qid"]]
        gold = r["gold"]
        gold_s = (f"{gold} ({q['criteria'][gold].split(':')[0]})" if q["type"] == "score"
                  else f"`{json.dumps(gold) if not isinstance(gold, str) else gold}`")
        out += [f"**Question{' (' + r['qid'] + ')' if t == 'T01' else ''}:** {q['instructions']}", "",
                "<details><summary>Options</summary>", "", options_md(q), "", "</details>", "",
                f"**Correct answer:** {gold_s}", "",
                "| Model | Answer | Confidence | Correct? |", "|---|---|---|---|"]
        for m in NAMES:
            a, c = answer_cell(r, m, q)
            out.append(f"| {NAMES[m]} | {a} | {c} | {ok_mark(r, m)} |")
        out.append("")
    if note:
        out += [f"**Why:** {note[1]}", "", f"**Verdict:** {VERDICTS[note[0]]}", ""]
    return out + ["---", ""]


def main():
    items = {it["id"]: it for p in A.FINAL_N for it in A.read_jsonl(A.D / "final" / f"{p}.jsonl")}
    res = {m: A.read_jsonl(A.RES / c["folder"] / "responses.jsonl") for m, c in A.MODELS.items()}
    df = A.assemble(list(items.values()), res)
    d = df[df.gold != "unknown"].copy()
    okp = {m: np.where(d.qtype == "score", d[f"{m}_ok1"], d[f"{m}_ok"]).astype(bool) for m in NAMES}

    def pattern(i):
        wrong = [NAMES[m] for m in NAMES if not okp[m][i]]
        if not wrong:
            return "all 3 correct"
        if len(wrong) == 3:
            return "all 3 wrong"
        if len(wrong) == 1:
            return f"only {wrong[0]} wrong"
        return f"only {[n for n in NAMES.values() if n not in wrong][0]} correct"
    d["pattern"] = [pattern(i) for i in range(len(d))]
    counts = d.pattern.value_counts()

    tally = defaultdict(Counter)  # verdicts per model
    for _, r in d[d.pattern != "all 3 correct"].iterrows():
        v = NOTES.get(r["id"], ("no note", ""))[0]
        for m in NAMES:
            if not (r[f"{m}_ok1"] if r["qtype"] == "score" else r[f"{m}_ok"]):
                tally[NAMES[m]][v] += 1

    L = ["# Where Jev, Decisions and Haiku get it right and wrong", "",
         f"Full runs: {len(items)} items, {len(d)} questions with a known correct answer. All three models answered "
         "exactly the same questions. On scales, landing within ±1 level of the correct answer counts as correct "
         "(marked '✅ (±1)'). Open 'Options' in each case to see what the model could choose from. The aggregate "
         "statistics are in [report.md](report.md).", "",
         "## Summary", "", "| Pattern | Questions | % |", "|---|---|---|"]
    order = ["all 3 correct", "only Jev wrong", "only Decisions wrong", "only Haiku wrong", "only Jev correct",
             "only Decisions correct", "only Haiku correct", "all 3 wrong"]
    for p in order:
        n = int(counts.get(p, 0))
        L.append(f"| {p} | {n} | {'<0.1' if 0 < n < len(d) / 1000 else f'{100 * n / len(d):.1f}'}% |")
    L += ["", "**Each model's errors, by verdict after reading every case:**", "",
          "| Model | Total errors | Clear error | Borderline (near 50/50) | Debatable label |", "|---|---|---|---|---|"]
    for n in NAMES.values():
        c = tally[n]
        L.append(f"| {n} | {sum(c.values())} | {c['clear']} | {c['borderline']} | {c['label']} |")
    L += ["", "## What the cases show", "",
          f"1. **All three get almost everything right ({100 * counts.get('all 3 correct', 0) / len(d):.1f}% of "
          "questions).** No accuracy difference between models is statistically significant: the benchmark has a "
          "ceiling effect. The interesting differences are in the kind of error.",
          "2. **All three fail on numbers and units.** Two pairs of vacuum cleaners whose weights in kg and pounds "
          "don't match: all three say 'same product' with 92-98% confidence. Haiku and Jev make similar mistakes on "
          "other pairs. None of them does the arithmetic.",
          "3. **Decisions reads disgust as anger.** It fails 4 disgust texts (food, hygiene) by answering 'anger' with "
          "65-91% confidence; Jev and Haiku get them right.",
          "4. **Decisions struggles with 'has the event already happened?'.** A race cancelled 20 minutes before the "
          "start and a half-built bridge: it says both happened, with 97-100% confidence.",
          "5. **Jev and Decisions mistake a sarcastic tone for a tweet's direction.** A routine license renewal told "
          "sarcastically is read as bearish. Jev also reads 'put' as bearish in a very bullish tweet and fails all "
          "three formats of the same tweet.",
          "6. **Haiku underrates experts and is confused by SSO.** It gives level 4 instead of 6 to two experts (11 "
          "and 20+ years of experience), and routes two SSO access problems to `bug_report`.",
          "7. **'Not mentioned' is not the same as 'no'.** Given a shopping list with no budget, Jev and Decisions "
          "pick `no_budget_set`. On yes/no questions with no information, Jev leans systematically to 'no' "
          "(mean 0.35); Decisions answers exactly 0.50 on 20 of 30.",
          "8. **Some errors are the benchmark's fault.** In 9 cases the label is debatable (too few cues, a text with "
          "two emotions, or news that can be read as mildly negative). They are marked.", "",
          "---", "", "## 1. All three correct: hard examples", "",
          "What a correct answer looks like: items with a trap that all three models saw through.", ""]
    for iid in ["T01_021", "N04_039", "H01_051", "N04_054", "T01_035", "N02_050"]:
        L += item_block(iid, df[df.id == iid], items[iid], None)

    sections = [("2. All three wrong", ["all 3 wrong"]),
                ("3. Only one correct", ["only Jev correct", "only Decisions correct", "only Haiku correct"]),
                ("4. Only Decisions wrong", ["only Decisions wrong"]),
                ("5. Only Haiku wrong", ["only Haiku wrong"]),
                ("6. Only Jev wrong", ["only Jev wrong"])]
    fail = d[d.pattern != "all 3 correct"]
    for title, pats in sections:
        sel = fail[fail.pattern.isin(pats)]
        L += [f"## {title} ({len(sel)} questions)", ""]
        for iid in dict.fromkeys(sel.sort_values("id")["id"]):
            L += item_block(iid, df[df.id == iid], items[iid], NOTES.get(iid))  # all questions of the item

    h = df[(df.family == "halluc_noul") & (df.gold == "unknown")].sort_values("id")
    L += ["## 7. Questions with no information (ideal answer: about 50%)", "",
          "The text gives no way to know the answer, so an honest model should say about 0.50. Below 0.2 or above "
          "0.8 means answering confidently about something it can't know. Haiku is not included because it can only "
          "say yes or no.", "",
          "| Item | Question | Jev P(yes) | Decisions P(yes) |", "|---|---|---|---|"]
    for _, r in h.iterrows():
        f = lambda p: f"**{p:.2f}**" if p < .2 or p > .8 else f"{p:.2f}"
        L.append(f"| {r['id']} | {items[r['id']]['question']} | {f(r['jev_p'])} | {f(r['luna_p'])} |")
    L += ["", "Confident answers are in bold. The confident cases in full:", ""]
    for iid, note in H02_NOTES.items():
        L += item_block(iid, df[df.id == iid], items[iid], note)
    OUT.write_text("\n".join(L))
    print("written", OUT, "| lines:", len(L), "| tally:", {k: dict(v) for k, v in tally.items()})
    missing = [i for i in fail["id"].unique() if i not in NOTES]
    if missing:
        print("items without a note:", missing)


if __name__ == "__main__":
    main()

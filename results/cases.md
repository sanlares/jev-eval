# Where Jev, Decisions and Haiku get it right and wrong

Full runs: 1770 items, 2040 questions with a known correct answer. All three models answered exactly the same questions. On scales, landing within ±1 level of the correct answer counts as correct (marked '✅ (±1)'). Open 'Options' in each case to see what the model could choose from. The aggregate statistics are in [report.md](report.md).

## Summary

| Pattern | Questions | % |
|---|---|---|
| all 3 correct | 1991 | 97.6% |
| only Jev wrong | 7 | 0.3% |
| only Decisions wrong | 16 | 0.8% |
| only Haiku wrong | 14 | 0.7% |
| only Jev correct | 1 | <0.1% |
| only Decisions correct | 0 | 0.0% |
| only Haiku correct | 6 | 0.3% |
| all 3 wrong | 5 | 0.2% |

**Each model's errors, by verdict after reading every case:**

| Model | Total errors | Clear error | Borderline (near 50/50) | Debatable label |
|---|---|---|---|---|
| Jev | 18 | 9 | 4 | 5 |
| Decisions | 28 | 17 | 5 | 6 |
| Haiku | 20 | 13 | 2 | 5 |

## What the cases show

1. **All three get almost everything right (97.6% of questions).** No accuracy difference between models is statistically significant: the benchmark has a ceiling effect. The interesting differences are in the kind of error.
2. **All three fail on numbers and units.** Two pairs of vacuum cleaners whose weights in kg and pounds don't match: all three say 'same product' with 92-98% confidence. Haiku and Jev make similar mistakes on other pairs. None of them does the arithmetic.
3. **Decisions reads disgust as anger.** It fails 4 disgust texts (food, hygiene) by answering 'anger' with 65-91% confidence; Jev and Haiku get them right.
4. **Decisions struggles with 'has the event already happened?'.** A race cancelled 20 minutes before the start and a half-built bridge: it says both happened, with 97-100% confidence.
5. **Jev and Decisions mistake a sarcastic tone for a tweet's direction.** A routine license renewal told sarcastically is read as bearish. Jev also reads 'put' as bearish in a very bullish tweet and fails all three formats of the same tweet.
6. **Haiku underrates experts and is confused by SSO.** It gives level 4 instead of 6 to two experts (11 and 20+ years of experience), and routes two SSO access problems to `bug_report`.
7. **'Not mentioned' is not the same as 'no'.** Given a shopping list with no budget, Jev and Decisions pick `no_budget_set`. On yes/no questions with no information, Jev leans systematically to 'no' (mean 0.35); Decisions answers exactly 0.50 on 20 of 30.
8. **Some errors are the benchmark's fault.** In 9 cases the label is debatable (too few cues, a text with two emotions, or news that can be read as mildly negative). They are marked.

---

## 1. All three correct: hard examples

What a correct answer looks like: items with a trap that all three models saw through.

### T01_021 · Stock tweets · hard · trap: sarcasm

**Full text:**

> Oh no, the chart 'looks terrible' according to twitter, whatever will I do 🙄. Bought another full position this week, I think Pixelforge Media triples from here regardless of what the squiggly lines say. $PXLF

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 4 (Strongly bullish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 4 (Strongly bullish) | 100% | ✅ |
| Decisions | 4 (Strongly bullish) | 94% | ✅ |
| Haiku | 4 (Strongly bullish) | no probability | ✅ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bullish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bullish` | 100% | ✅ |
| Decisions | `bullish` | 100% | ✅ |
| Haiku | `bullish` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.97 | ✅ |
| Decisions | `true` | P(yes) = 1.00 | ✅ |
| Haiku | `true` | no probability | ✅ |

---

### N04_039 · Does the source support the claim? · hard · trap: numbers

**Full text:**

> **source:** Council budget vote results:
- Road repair fund: approved at $840,000, up from $700,000 last year
> **claim:** The road repair fund's approved budget increased by 20% from last year.

**Question:** Is the claim fully supported by the source?

<details><summary>Options</summary>

- `true`: Everything in the claim is stated in or directly entailed by the source
- `false`: The claim contradicts the source, adds details not in it, or overgeneralizes

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.98 | ✅ |
| Decisions | `true` | P(yes) = 1.00 | ✅ |
| Haiku | `true` | no probability | ✅ |

---

### H01_051 · Hallucination (multiple choice) · hard · trap: tempting guess

**Full text:**

> Hi families! Just a reminder that whenever we get heavy snow, we typically switch to early dismissal at noon to get everyone home safely before the roads get bad. Stay warm out there!

**Question:** Will there be early dismissal today?

<details><summary>Options</summary>

- `yes_early_dismissal`: Yes, early dismissal today
- `no_normal_schedule`: No, normal schedule today
- `school_closed`: School is closed entirely today
- `cannot_determine`: The text does not contain enough information to answer

</details>

**Correct answer:** `cannot_determine`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `cannot_determine` | 100% | ✅ |
| Decisions | `cannot_determine` | 99% | ✅ |
| Haiku | `cannot_determine` | no probability | ✅ |

---

### N04_054 · Does the source support the claim? · hard · trap: negation

**Full text:**

> **source:** Summary of findings, Kestrowick Soil Survey:
- Heavy metal contamination was not detected in soil samples taken from the northern test plots, which sit farthest from the old rail yard
- Southern plots showed elevated lead levels, consistent with prior industrial use
- Follow-up remediation planning will focus only on the southern plots
> **claim:** No heavy metal contamination was found in the northern test plots.

**Question:** Is the claim fully supported by the source?

<details><summary>Options</summary>

- `true`: Everything in the claim is stated in or directly entailed by the source
- `false`: The claim contradicts the source, adds details not in it, or overgeneralizes

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.96 | ✅ |
| Decisions | `true` | P(yes) = 1.00 | ✅ |
| Haiku | `true` | no probability | ✅ |

---

### T01_035 · Stock tweets · hard · trap: jargon only

**Full text:**

> Third downgrade this week on Ridgeline Apparel, target slashed to $4 from $19. Loaded September puts, deep ITM, see you at zero. $RDGL

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 0 (Strongly bearish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 0 (Strongly bearish) | 100% | ✅ |
| Decisions | 0 (Strongly bearish) | 99% | ✅ |
| Haiku | 0 (Strongly bearish) | no probability | ✅ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bearish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bearish` | 100% | ✅ |
| Decisions | `bearish` | 100% | ✅ |
| Haiku | `bearish` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.02 | ✅ |
| Decisions | `false` | P(yes) = 0.00 | ✅ |
| Haiku | `false` | no probability | ✅ |

---

### N02_050 · Contains personal data? · hard · trap: long irrelevant context

**Full text:**

> Filing a detailed complaint regarding a recurring delivery problem:
> - This is the third time in two months that a package has been left at the wrong building in our complex
> - Building layout: our complex has four nearly identical entrances (A, B, C, D) which seems to be the recurring source of confusion
> - Previous incidents: one package ended up at building C when it should have gone to building A (resolved after two days), another was marked 'delivered' but never located at all (refunded eventually)
> - Current issue: order #91827364 shows 'delivered' as of yesterday but nothing has appeared at any of the four entrances, checked personally with the front desk at each one
> - Front desk staff have no record of signing for it, and no photo was attached to the delivery confirmation this time, unlike previous deliveries which did include a photo
> - Requesting either a reshipment or a refund, whichever is faster to process on your end
> - Also requesting, if possible, that future deliveries include a photo confirmation regardless of package value, since that has been the only reliable way to locate misplaced items so far
> - General account correspondence can go through the standard support portal messaging thread already associated with this order
> - Not asking for expedited shipping on the replacement, standard timing is fine, just want the actual item to show up at the correct entrance this time
> - Happy to provide the complex's shared building manager contact if that speeds up verifying the correct entrance, though the account on file should already specify the unit and entrance letter

**Question:** Does the text contain personal data that identifies or contacts a specific private individual?

<details><summary>Options</summary>

- `true`: Contains at least one of: a personal phone number, personal email address, home street address, government ID number, bank or card number, or a full name together with a date of birth
- `false`: No such data; first names alone, public figures, company phone numbers, or generic addresses like support@company.com do not count

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.05 | ✅ |
| Decisions | `false` | P(yes) = 0.00 | ✅ |
| Haiku | `false` | no probability | ✅ |

---

## 2. All three wrong (5 questions)

### C02_048 · Emotion of a message · hard · trap: sarcasm

**Full text:**

> Oh wonderful, my dog leave me such a beautiful present on the pillow this morning, right where I put my face every night, thank you so much for that, exactly what I wanted to find at 6am.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `disgust`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `anger` | 73% | ❌ |
| Decisions | `anger` | 94% | ❌ |
| Haiku | `anger` | no probability | ❌ |

**Why:** The dog left a 'beautiful present' on the pillow and the writer thanks it sarcastically. The label says disgust; all three models say anger. With that much sarcasm, anger is as defensible as disgust.

**Verdict:** **Debatable label**

---

### C04_048 · Cuisine of a recipe · medium

**Full text:**

> Nothing dignified about eating one of these — a pan-fried sweet dough pocket stuffed with melted brown sugar, cinnamon, and chopped nuts that will absolutely burn your tongue if you don't wait the full sixty seconds everyone always ignores.

**Question:** Which cuisine does this recipe belong to?

<details><summary>Options</summary>

- `italian`
- `mexican`
- `japanese`
- `indian`
- `french`
- `thai`
- `korean`
- `moroccan`

</details>

**Correct answer:** `korean`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `mexican` | 43% | ❌ |
| Decisions | `mexican` | 51% | ❌ |
| Haiku | `moroccan` | no probability | ❌ |

**Why:** It is hotteok (a Korean street dessert), but the text has no exclusively Korean cue: fried dough with brown sugar, cinnamon and nuts fits Mexican or Moroccan cooking just as well. The label is right but cannot be deduced from the text.

**Verdict:** **Debatable label**

---

### H01_006 · Hallucination (multiple choice) · hard · trap: tempting guess

**Full text:**

> ok so i finally wrote down my chili recipe bc like three people asked me for it after game night lol. so basically u brown like a pound and a half of ground turkey in a big pot w some olive oil, don't skip that step or it gets weird and mushy trust me i learned the hard way. then throw in a diced onion, three cloves of garlic (i always do extra bc garlic is life), a can of diced tomatoes, two cans of kidney beans (drained!!), a can of corn, and then ur seasonings: cumin, smoked paprika, a little oregano, and a couple diced jalapeños from the jar bc fresh ones go bad in my fridge before i use them lol. let that simmer for like 40 min stirring occasionally so it doesn't stick to the bottom, ur kitchen is gonna smell insane. i usually top mine w shredded cheese and crushed tortilla chips bc texture is everything to me. oh and i always make a double batch bc it freezes so well and future me deserves a break too lol anyway lmk if u try it!!

**Question:** Is this chili recipe spicy?

<details><summary>Options</summary>

- `very_spicy`: Yes, it's very spicy
- `mild_not_spicy`: No, it's mild and not spicy
- `medium_heat`: It has a moderate, medium heat level
- `cannot_determine`: The text does not contain enough information to answer

</details>

**Correct answer:** `cannot_determine`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `medium_heat` | 89% | ❌ |
| Decisions | `medium_heat` | 71% | ❌ |
| Haiku | `medium_heat` | no probability | ❌ |

**Why:** Chili recipe with jarred jalapeños, cumin and smoked paprika. The label is `cannot_determine` because the text never says how spicy it is; all three models infer `medium_heat`. It was a 'tempting guess' item, and here the inference is reasonable.

**Verdict:** **Debatable label**

---

### N05_015 · Same product? · hard · trap: implicit

**Full text:**

> **record_a:** The SweepTek Turbo 5 remains one of our best-selling cordless vacuums this quarter, weighing in at a manageable 2.3 kilograms with the wand fully assembled, a total length of 108 centimetres from the floor nozzle to the top of the handle, and a run time that our lab clocked at a genuine 42 minutes on the standard power setting before the battery indicator dropped into the red zone.
> **record_b:** This listing for the SweepTek Turbo 5 gives the specs in imperial units for anyone who prefers them: approximately 6.3 pounds fully assembled, a length of 47.5 inches handle to nozzle, and a runtime the manufacturer lists at 42 minutes on standard power, which should be plenty for a quick clean of the living room and hallway.

**Question:** Do the two records describe the same product (same model and same variant)?

<details><summary>Options</summary>

- `true`: Same product, model and variant, even if written differently
- `false`: Different product, model, size, capacity, color or version

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.97 | ❌ |
| Decisions | `true` | P(yes) = 0.98 | ❌ |
| Haiku | `true` | no probability | ❌ |

**Why:** The same product listed in kg/cm vs pounds/inches. But 2.3 kg = 5.1 lb (not 6.3) and 108 cm = 42.5 in (not 47.5): the numbers don't match, so it is not the same variant. All three say 'yes' with 92-98% confidence: none of them checks unit conversions.

**Verdict:** **Clear error**

---

### N05_047 · Same product? · hard · trap: implicit

**Full text:**

> **record_a:** grabbing the dustrix max vacuum again since ours finally died, this one's listed at 3.8kg which is no joke lugging up two flights of stairs every day, comes with the crevice tool and pet brush, cord length is 6 meters so it reaches basically the whole upstairs hallway without unplugging.
> **record_b:** also found the dustrix max listed here in pounds instead, says 6.2lbs fully assembled which sounded lighter so i almost bought it before double checking, cord length says 19 feet, comes with crevice tool and pet brush like usual, hoping this one lasts longer than the last.

**Question:** Do the two records describe the same product (same model and same variant)?

<details><summary>Options</summary>

- `true`: Same product, model and variant, even if written differently
- `false`: Different product, model, size, capacity, color or version

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.92 | ❌ |
| Decisions | `true` | P(yes) = 0.95 | ❌ |
| Haiku | `true` | no probability | ❌ |

**Why:** 3.8 kg = 8.4 lb, not 6.2 lb (the text itself says one felt lighter). The cord does match (6 m ≈ 19 ft). All three say 'same product' at 92-95%: numbers again.

**Verdict:** **Clear error**

---

## 3. Only one correct (7 questions)

### C02_016 · Emotion of a message · medium

**Full text:**

> Doctor looked at the scan, looked at me, and said 'well, I've got nothing to fix,' which is the first time in three years a specialist has sent me home with literally no follow-up appointment.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `joy`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `surprise` | 55% | ❌ |
| Decisions | `surprise` | 61% | ❌ |
| Haiku | `joy` | no probability | ✅ |

**Why:** For the first time in three years the specialist sends the writer home with nothing to fix and no follow-up. That is relief and joy. Jev and Decisions say surprise, with low confidence (55-61%).

**Verdict:** **Clear error**

---

### C02_046 · Emotion of a message · medium

**Full text:**

> So we're up 2-1 with four minutes left in the league final, Jamie's team, the one they've practiced for since August, and the ref calls the tightest offside I have ever seen in my life on a play where their kid was clearly a full stride onside, waves it off, no VAR at this level obviously so that's just the final word, and the other team scores off the resulting free kick two minutes later to tie it and then wins it in extra time on penalties, and Jamie's coach tried to talk to the ref after the whistle just to ask which linesman made the call and got told to 'take it up with the league office' by a guy who was already halfway to his car. Filed the complaint form online that night, attached the video someone's dad filmed from the sideline that shows the offside line pretty clearly, got an auto-reply saying they'd 'review within 10 business days,' which, fine, except the season's already over by then so what exactly is there left to review. Jamie cried the whole ride home and kept asking why the ref didn't just look again, and I didn't have a real answer for her because I don't have one either, I just kept saying sometimes the calls don't go your way, which felt like a garbage thing to tell an eleven year old who did everything right for eight months straight.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `anger`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `sadness` | 85% | ❌ |
| Decisions | `sadness` | 83% | ❌ |
| Haiku | `anger` | no probability | ✅ |

**Why:** A referee wrongly disallows a goal in a final, the formal complaint gets a useless auto-reply, and the kid cries the whole ride home. There is anger (the label) and sadness (Jev and Decisions, 83-85%) at once: a genuinely mixed text.

**Verdict:** **Debatable label**

---

### C04_056 · Cuisine of a recipe · medium

**Full text:**

> Rice is simmered for over an hour with extra water until it breaks down into a thick, soft porridge. Minced pork is stirred in near the end, along with grated ginger. The bowl is finished with a raw egg cracked on top to cook in the residual heat, crispy fried garlic, chopped scallion, and a dusting of white pepper.

**Question:** Which cuisine does this recipe belong to?

<details><summary>Options</summary>

- `italian`
- `mexican`
- `japanese`
- `indian`
- `french`
- `thai`
- `korean`
- `moroccan`

</details>

**Correct answer:** `thai`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `korean` | 55% | ❌ |
| Decisions | `japanese` | 70% | ❌ |
| Haiku | `thai` | no probability | ✅ |

**Why:** Rice cooked until it falls apart, minced pork, ginger, raw egg, fried garlic and white pepper: Thai jok moo. But nearly identical dishes exist in Korea (juk) and Japan (okayu). Jev said Korean and Decisions Japanese: weak cues.

**Verdict:** **Borderline (near 50/50)**

---

### H01_038 · Hallucination (multiple choice) · medium

**Full text:**

> - Coffee, the dark roast, not that 'medium roast' nonsense that tastes like brown water
> - Bread, whichever loaf isn't $7 this week because apparently bread is a luxury good now
> - Chicken thighs, on sale hopefully, if not we're having beans again and nobody's complaining because beans are underrated
> - That fancy mustard I like, the one in the little jar, don't let them swap it for the big bottle, it's not the same
> - Toilet paper, get the big pack, I refuse to make an emergency run again
> - Cat food, the senior formula, our cat is offended by anything else at this point
> - A birthday candle situation, plural, because apparently turning thirty-four requires exactly thirty-four candles according to someone in this house
> - Ice cream, whatever's on sale, my taste buds have given up having preferences
> - Paper plates, because after this week I am not touching a dish
> - Also check if they still have that seasonal pumpkin bread, if so grab two loaves before they vanish for another year
> - And if you see anyone from book club in there, pretend you don't, I am not discussing last month's ending in a grocery aisle

**Question:** What is the total budget for this shopping trip?

<details><summary>Options</summary>

- `under_fifty`: Under $50
- `fifty_to_hundred`: Between $50 and $100
- `over_hundred`: Over $100
- `no_budget_set`: No budget was set
- `cannot_determine`: The text does not contain enough information to answer

</details>

**Correct answer:** `cannot_determine`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `no_budget_set` | 78% | ❌ |
| Decisions | `no_budget_set` | 99% | ❌ |
| Haiku | `cannot_determine` | no probability | ✅ |

**Why:** A shopping list with no mention of a budget, and one option was `no_budget_set`. Jev (78%) and Decisions (99%) picked it, which asserts something the text doesn't say: not mentioned is not the same as not existing. Haiku correctly picked `cannot_determine`.

**Verdict:** **Clear error**

---

### S06_005 · Helpdesk urgency · hard · trap: numbers

**Full text:**

> okay so quick one before I forget because between the carpool and my daughter's dentist appointment and trying to get dinner on the table I almost didn't even flag this, but about two weeks ago I got this email that said it was from the benefits provider asking me to log in and verify my dependents, and something about it just felt off, the sender address had like an extra letter in it, so I didn't click anything and I just deleted it right away like we're trained to do, and then it happened again yesterday, so that's twice now in two weeks from what looks like the same fake sender, and I'm not worried because I never entered anything and my password hasn't changed in months and everything still logs in fine, I just think it'd be good if someone eventually added that sender to the blocklist so it stops showing up in my inbox and maybe in everyone else's too, no rush on this at all, whenever you get a free afternoon sometime this month is totally fine, just didn't want it to fall through the cracks completely.

**Question:** How urgent is this helpdesk request?

<details><summary>Options</summary>

- `0` Can wait: a question or minor request with no deadline and little impact
- `1` Soon: affects someone's work or has a deadline within days
- `2` Immediate: work is stopped for many people, a security incident, or a deadline within hours

</details>

**Correct answer:** 0 (Can wait)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 0 (Can wait) | 89% | ✅ |
| Decisions | 2 (Immediate) | 80% | ❌ |
| Haiku | 2 (Immediate) | no probability | ❌ |

**Why:** The writer reports a phishing email they did NOT open and says explicitly that there is no rush and any free afternoon this month is fine. Decisions (80%) and Haiku answered the most urgent level because of the word phishing. Only Jev followed what the text says.

**Verdict:** **Clear error**

---

### T01_001 · Stock tweets · medium

**Full text:**

> Halodyne Robotics ($HALO) price target moved to $58 from $52 after this morning's note, while a separate desk trimmed theirs to $45. Two very different views on the same quarter.

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 2 (Neutral)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 2 (Neutral) | 83% | ✅ |
| Decisions | 2 (Neutral) | 90% | ✅ |
| Haiku | 2 (Neutral) | no probability | ✅ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `neutral`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `neutral` | 81% | ✅ |
| Decisions | `neutral` | 95% | ✅ |
| Haiku | `neutral` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.51 | ❌ |
| Decisions | `true` | P(yes) = 0.50 | ❌ |
| Haiku | `false` | no probability | ✅ |

**Why:** One analyst raises the price target to $58 and another cuts it to $45: neutral. Jev gave 51% and Decisions 50% that it rises, i.e. 'I can't tell', which is the right answer in spirit. Because 0.5 or more counts as 'yes', the threshold scores it as an error.

**Verdict:** **Borderline (near 50/50)**

---

### T01_117 · Stock tweets · hard · trap: sarcasm

**Full text:**

> Oh wow, huge shocking regulatory news for $IRNC today... they renewed the same license they've renewed every three years since 1994 🙄 truly can't believe the alerts blew up my phone for this

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 2 (Neutral)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 1 (Mildly bearish) | 57% | ✅ (±1) |
| Decisions | 2 (Neutral) | 68% | ✅ |
| Haiku | 1 (Mildly bearish) | no probability | ✅ (±1) |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `neutral`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bearish` | 68% | ❌ |
| Decisions | `bearish` | 58% | ❌ |
| Haiku | `neutral` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.10 | ✅ |
| Decisions | `false` | P(yes) = 0.02 | ✅ |
| Haiku | `false` | no probability | ✅ |

**Why:** Sarcasm about 'regulatory news' that is a routine license renewal. The correct direction is neutral. Jev and Decisions read the mocking tone as a bearish signal: they confuse the author's tone with what the news implies.

**Verdict:** **Clear error**

---

## 4. Only Decisions wrong (16 questions)

### C01_006 · Support-ticket routing · medium

**Full text:**

> ok this is so annoying, i've tried logging into my Driftbox acct like 6 times today and it keeps saying 'session expired' the SECOND i get to my files. i even reset my wifi lol. tried on chrome AND safari, same deal. i have a group project due tomorrow and all my slides are literally trapped in there rn, someone pls help.

**Question:** Which team should handle this customer support ticket?

<details><summary>Options</summary>

- `account_access`: Login problems, password resets, two-factor authentication, locked or suspended accounts, single sign-on issues
- `billing`: Charges, invoices, refunds, payment methods, receipts, plan prices
- `bug_report`: Something in the product is broken, throws errors, or behaves incorrectly
- `feature_request`: Asks for new functionality or an improvement to how the product works
- `cancellation`: Wants to cancel, close the account, stop auto-renewal, or leave the service

</details>

**Correct answer:** `account_access`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `account_access` | 80% | ✅ |
| Decisions | `bug_report` | 49% | ❌ |
| Haiku | `account_access` | no probability | ✅ |

**Why:** 'Session expired' every time the user tries to log in: account access. Decisions said `bug_report` at 49%, nearly a tie. It had already been flagged as borderline during adjudication.

**Verdict:** **Borderline (near 50/50)**

---

### C02_005 · Emotion of a message · hard · trap: distractor

**Full text:**

> Credit where due: it was one of the best matches I've sat through in years. Down two goals at half, some kind of tactical miracle in the second half, then an equalizer in second-half stoppage time that had the entire section on its feet screaming like we'd personally scored it. I will remember the noise in that stadium for a long time. What I will also remember, unfortunately, is the man three seats down who spent the entire second half working through a family-sized bag of nacho fries and using the empty seat between us as, near as I could tell, a napkin, a bin, and at one point a foot rest, cheese sauce and all. Somewhere around the eightieth minute he leaned over, genuinely, mid-celebration, arms still in the air, to ask if I was 'gonna finish that,' meaning my drink, which he then picked up without waiting for an answer and drank from directly. I watched him do it. I said nothing, because what is there to say, but I have not been able to think about that cup since, and I definitely didn't finish it after. The goal was incredible. The comeback was the stuff of local legend, the kind of thing people will bring up unprompted for the rest of the season. I just need everyone to also know there was a man there treating a stranger's game-day snacks like community property, cheese sauce and all, and I have not recovered.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `disgust`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `disgust` | 95% | ✅ |
| Decisions | `anger` | 90% | ❌ |
| Haiku | `disgust` | no probability | ✅ |

**Why:** A great match, but a stranger uses the next seat as a napkin and trash can and drinks from the writer's cup, and the writer can't stop thinking about it. That is disgust. Decisions said anger (90%).

**Verdict:** **Clear error**

---

### C02_010 · Emotion of a message · hard · trap: implicit

**Full text:**

> Took one bite of the soup, chewed exactly once, and set my spoon down very deliberately next to the bowl like it had personally wronged me. Pushed the bowl about six inches to the left, which is apparently as far as my arm was willing to commit to the problem. Ordered plain toast instead and didn't look at the soup again for the rest of the meal. The waiter asked if everything was okay and I just gestured at the bowl the way you'd point out a small fire.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `disgust`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `disgust` | 83% | ✅ |
| Decisions | `anger` | 89% | ❌ |
| Haiku | `disgust` | no probability | ✅ |

**Why:** The writer tastes the soup, pushes it away, orders toast and points at the bowl like someone pointing at a small fire. That is disgust. Decisions said anger (89%): it latched onto a distractor phrase about feeling personally offended.

**Verdict:** **Clear error**

---

### C02_020 · Emotion of a message · medium

**Full text:**

> so the 'boutique hostel' photos were... doing a lot of heavy lifting. got there and the sheets had a stain that was definitely not part of the pattern, there was a full on trail of ants going into the minifridge, and the bathroom drain smelled like it had personally given up on life. asked for new sheets and the guy just flipped them over and handed them back like that solved anything. slept in my hoodie on top of my own towel, did not touch a single surface barefoot the whole time.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `disgust`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `disgust` | 100% | ✅ |
| Decisions | `anger` | 91% | ❌ |
| Haiku | `disgust` | no probability | ✅ |

**Why:** A hostel with stained sheets, ants in the mini-fridge and a drain smell; the writer sleeps fully dressed and won't touch anything barefoot. That is disgust. Decisions said anger (91%).

**Verdict:** **Clear error**

---

### C02_050 · Emotion of a message · medium

**Full text:**

> ok the cafeteria pulled something today that I need to talk about. opened my 'chicken' wrap and there was just. a long black hair baked into the tortilla itself, not on top, IN it, like it had been cooked in there. showed my friend and she almost threw up on the spot. went to complain and the lunch lady just shrugged and said 'happens sometimes' like that's a normal sentence to say out loud to a customer. brought my own lunch for the rest of the week, not risking it again.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `disgust`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `disgust` | 99% | ✅ |
| Decisions | `anger` | 65% | ❌ |
| Haiku | `disgust` | no probability | ✅ |

**Why:** A hair cooked inside the wrap; the friend nearly throws up. That is disgust. Decisions said anger (65%). This makes four texts (plus C02_048) where Decisions reads disgust as anger: it is a pattern.

**Verdict:** **Clear error**

---

### C02_052 · Emotion of a message · hard · trap: sarcasm

**Full text:**

> Yes, of course, this is exactly what I am expecting when I buy ticket for small local band in small venue with maybe two hundred people only. Totally normal Tuesday night, nothing special, just like every other concert I go before. So when the lights go down and instead of the small band, a man walk out who I recognize immediately because his face is on every music channel for twenty years, I am, sure, very calm about this, not surprised even one little bit. My friend next to me is also very calm, screaming into my ear so loud I cannot hear for maybe one minute after. He play for one full hour, just him, small stage, no big show, nothing, guitar and his voice only, like this is completely a normal Tuesday thing for a superstar to do in a room this small. Nobody in the room is filming much because everybody too busy standing there with mouth open, very typical reaction, very expected. After, we find out from the small band, the ones who actually sell tickets for this show, that they only know he was coming two days before, and he ask them himself if he can 'sit in' because he is visiting his old friend who lives in this city. Totally normal for a person of this fame to just quietly show up somewhere with two hundred seat. I walk out after and cannot remember where I park my car for ten minutes, which never happen to me before in my life, but sure, everything about tonight is very expected and very normal, exactly the concert I plan to see when I buy this ticket three weeks ago for twenty-two dollars.

**Question:** Which emotion does the writer primarily express?

<details><summary>Options</summary>

- `joy`: Happiness, delight, excitement, gratitude, pride
- `sadness`: Sorrow, grief, disappointment, loneliness
- `anger`: Irritation, rage, resentment, feeling wronged
- `fear`: Worry, anxiety, dread, feeling threatened
- `surprise`: Astonishment or shock at something unexpected, without a dominant positive or negative feeling
- `disgust`: Revulsion or strong distaste toward something gross or morally repugnant

</details>

**Correct answer:** `surprise`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `surprise` | 98% | ✅ |
| Decisions | `joy` | 88% | ❌ |
| Haiku | `surprise` | no probability | ✅ |

**Why:** Sarcasm: the writer is 'not surprised even one little bit' that a superstar walked on stage in a 200-person venue. The emotion is surprise. Decisions said joy (88%): it read the excitement and missed the sarcasm. Joy is there too, but the text revolves around not being able to believe it.

**Verdict:** **Clear error**

---

### H01_048 · Hallucination (multiple choice) · hard · trap: implicit

**Full text:**

> So I swung by town hall around 9pm last night just to see what the mood was like after votes closed, and let me tell you, the energy over on the Ramirez campaign side of the room was something else, people hugging, someone brought out a sheet cake that said 'Four More Years,' and by the time I left they were already taking down the opponent's yard signs from the lawn outside, which, you only do that once you know which way things went.

**Question:** Did Ramirez win the election?

<details><summary>Options</summary>

- `yes_won`: Yes, Ramirez won
- `no_lost`: No, Ramirez lost
- `too_close`: It was still too close to call
- `postponed`: The election was postponed
- `cannot_determine`: The text does not contain enough information to answer

</details>

**Correct answer:** `yes_won`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `yes_won` | 97% | ✅ |
| Decisions | `cannot_determine` | 60% | ❌ |
| Haiku | `yes_won` | no probability | ✅ |

**Why:** A cake that says 'Four more years', hugs, and they're already taking down the rival's signs: Ramírez won, although the text never says it literally. Decisions picked `cannot_determine` (60%): too literal, the opposite of hallucinating.

**Verdict:** **Clear error**

---

### N03_023 · Does the passage answer the question? · medium

**Full text:**

> **question:** Is the Verity House Museum stroller-accessible?
> **passage:** we went to verity house museum last saturday and honestly the gift shop alone took us twenty minutes because the kids wanted every single postcard in the rack and then we grabbed a quick bite at the little cafe near the entrance before heading home.

**Question:** Does the passage contain the information needed to answer the question?

<details><summary>Options</summary>

- `true`: The answer can be found in or directly inferred from the passage
- `false`: The passage does not provide the answer, even if it is on a related topic

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.02 | ✅ |
| Decisions | `true` | P(yes) = 0.51 | ❌ |
| Haiku | `false` | no probability | ✅ |

**Why:** The question is whether the museum is stroller-accessible; the passage only describes the gift shop and the café. It does not contain the answer. Decisions: 51%, a tie.

**Verdict:** **Borderline (near 50/50)**

---

### N06_038 · Phishing? · medium

**Full text:**

> From: FernShare Notifications <no-reply@ferngrove.com>
> Subject: Document shared: "Team Photos - Summer Picnic"
> 
> Hello, this is message from FernShare, telling you that colleague Marco shared file "Team Photos - Summer Picnic" with you. You can open by login to FernShare app like normal time. Have nice day.

**Question:** Is this email a phishing attempt?

<details><summary>Options</summary>

- `true`: Tries to trick the recipient into revealing credentials, paying, opening a malicious link/attachment, or impersonates someone
- `false`: Legitimate email, even if urgent or promotional

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.30 | ✅ |
| Decisions | `true` | P(yes) = 0.63 | ❌ |
| Haiku | `false` | no probability | ✅ |

**Why:** An internal email from the company's own domain saying Marco shared some photos, with no links and in imperfect English. It is legitimate. Decisions gave it 63% phishing, probably because of the unusual English.

**Verdict:** **Clear error**

---

### N06_043 · Phishing? · easy

**Full text:**

> From: StoneVault Documents <notifications@stonecrestpartners.com>
> Subject: "Budget Draft v4" shared with you (yes, v4, we know)
> 
> Someone — presumably tired of v3 — has shared "Budget Draft v4" with you on StoneVault. You have edit access, so use it wisely, or at least more wisely than whoever created v1 through v3. Log in the normal way to view it; no link here, we're not monkeys. Ping the finance channel if it doesn't show up in your recent files within a few minutes.

**Question:** Is this email a phishing attempt?

<details><summary>Options</summary>

- `true`: Tries to trick the recipient into revealing credentials, paying, opening a malicious link/attachment, or impersonates someone
- `false`: Legitimate email, even if urgent or promotional

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.23 | ✅ |
| Decisions | `true` | P(yes) = 0.52 | ❌ |
| Haiku | `false` | no probability | ✅ |

**Why:** An internal notification written with humour, explicitly with no link. Legitimate. Decisions: 52%, nearly a tie.

**Verdict:** **Borderline (near 50/50)**

---

### N10_012 · Has the event already happened? · hard · trap: near miss

**Full text:**

> Every runner was already at the start line, chip straps tightened, playlists queued up, when the county pulled the permit twenty minutes before the gun over an unresolved insurance issue nobody had flagged until that morning — so four thousand people in expensive shoes just went home.

**Question:** Has the main event described in the text already taken place?

<details><summary>Options</summary>

- `true`: The event actually happened in the past
- `false`: The event is planned, expected, hypothetical, cancelled, postponed, or did not happen

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.13 | ✅ |
| Decisions | `true` | P(yes) = 0.97 | ❌ |
| Haiku | `false` | no probability | ✅ |

**Why:** All runners on the start line and, 20 minutes before the gun, the race is cancelled and thousands of people go home. The race did NOT happen. Decisions: 97% that it did. A high-confidence error.

**Verdict:** **Clear error**

---

### N10_025 · Has the event already happened? · medium

**Full text:**

> So apparently the new bridge by the school still isn't done because they found some issue with the support beams during inspection, which means we're stuck doing the long way around through downtown for at least another two months, and honestly at this point I've stopped even checking the city's timeline updates because they keep pushing the date back.

**Question:** Has the main event described in the text already taken place?

<details><summary>Options</summary>

- `true`: The event actually happened in the past
- `false`: The event is planned, expected, hypothetical, cancelled, postponed, or did not happen

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.23 | ✅ |
| Decisions | `true` | P(yes) = 0.72 | ❌ |
| Haiku | `false` | no probability | ✅ |

**Why:** The bridge is not finished yet because of problems with the beams. Decisions: 72% that the event already happened.

**Verdict:** **Clear error**

---

### N10_049 · Has the event already happened? · medium

**Full text:**

> You know, this whole bridge situation reminds me of when they redid the overpass near my childhood home back in the nineties, took forever too, but anyway — my neighbor Frank, who's on the town beautification committee for some reason nobody can quite explain, was telling me over the fence last weekend that the new pedestrian bridge across the creek behind the community center is still sitting there half-finished, missing its railings on one whole side, and the contractor apparently walked off the job back in August over a payment dispute with the town, which Frank says isn't even the first time this exact contractor has done that, there was apparently some incident with a parking structure two towns over a few years back that ended in actual litigation. The town council put out one of those vague statements last month saying they're 'exploring options to complete the project,' which Frank and I both agreed is code for absolutely nothing happening anytime soon, and meanwhile the whole thing is fenced off with those orange plastic barriers that are somehow always knocked over whenever I walk the dog past there in the morning. My daughter's been asking when she can ride her bike across it to get to the park without going the long way past the highway, and I honestly don't have a good answer for her at this point, could be spring, could be next year, Frank's betting on next year given the contractor history, and honestly I'm inclined to trust Frank's read on local construction drama more than anything the town website says, since the website still lists a completion date from eighteen months ago that nobody's bothered to update.

**Question:** Has the main event described in the text already taken place?

<details><summary>Options</summary>

- `true`: The event actually happened in the past
- `false`: The event is planned, expected, hypothetical, cancelled, postponed, or did not happen

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.48 | ✅ |
| Decisions | `true` | P(yes) = 1.00 | ❌ |
| Haiku | `false` | no probability | ✅ |

**Why:** A half-built footbridge; the contractor abandoned the job. Decisions: 100% that it already happened, with total certainty. Jev and Haiku said no. Decisions' third error on this task.

**Verdict:** **Clear error**

---

### T01_004 · Stock tweets · hard · trap: jargon only

**Full text:**

> $EMBT: Line 3 at the plant is down for unscheduled maintenance per this morning's 8-K filing. Management says no change to Q3 output guidance at this time. Filing linked in our bio.

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 2 (Neutral)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 2 (Neutral) | 77% | ✅ |
| Decisions | 1 (Mildly bearish) | 68% | ✅ (±1) |
| Haiku | 2 (Neutral) | no probability | ✅ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `neutral`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `neutral` | 76% | ✅ |
| Decisions | `bearish` | 75% | ❌ |
| Haiku | `neutral` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.13 | ✅ |
| Decisions | `false` | P(yes) = 0.10 | ✅ |
| Haiku | `false` | no probability | ✅ |

**Why:** One plant line stopped for maintenance, with no change to production guidance. The label says neutral; Decisions says bearish (75%). Debatable: a stoppage is mildly negative news even if guidance doesn't change.

**Verdict:** **Debatable label**

---

### T01_137 · Stock tweets · medium

**Full text:**

> $WLBK issuing a voluntary recall on one batch of its oat milk line due to a labeling error, company says less than 0.1% of shipped units affected and no health risk identified.

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 2 (Neutral)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 2 (Neutral) | 66% | ✅ |
| Decisions | 2 (Neutral) | 72% | ✅ |
| Haiku | 2 (Neutral) | no probability | ✅ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `neutral`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `neutral` | 86% | ✅ |
| Decisions | `bearish` | 75% | ❌ |
| Haiku | `neutral` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.11 | ✅ |
| Decisions | `false` | P(yes) = 0.23 | ✅ |
| Haiku | `false` | no probability | ✅ |

**Why:** A voluntary recall of one batch over a labelling error, under 0.1% of units, no health risk. The label says neutral; Decisions says bearish (75%). Debatable for the same reason as the previous one.

**Verdict:** **Debatable label**

---

### T01_151 · Stock tweets · hard · trap: sarcasm

**Full text:**

> oh no the lawsuit against $KSTA got thrown out with prejudice and they don't even have to pay a cent, guess the bears were right all along 🙄 loading more shares on the open tomorrow

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 4 (Strongly bullish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 4 (Strongly bullish) | 86% | ✅ |
| Decisions | 4 (Strongly bullish) | 50% | ✅ |
| Haiku | 4 (Strongly bullish) | no probability | ✅ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bullish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bullish` | 87% | ✅ |
| Decisions | `bullish` | 90% | ✅ |
| Haiku | `bullish` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.88 | ✅ |
| Decisions | `false` | P(yes) = 0.35 | ❌ |
| Haiku | `true` | no probability | ✅ |

**Why:** Sarcasm: 'the bears were right' after the lawsuit is dismissed, plus a plan to buy more shares tomorrow. It is bullish. Decisions: 35% that it rises; it missed the sarcasm.

**Verdict:** **Clear error**

---

## 5. Only Haiku wrong (14 questions)

### C01_041 · Support-ticket routing · hard · trap: implicit

**Full text:**

> Weird one — ever since my company switched us to a new identity provider last week (long overdue, don't ask), Projex just spins forever on a blank screen the moment I try to open my workspace.

**Question:** Which team should handle this customer support ticket?

<details><summary>Options</summary>

- `account_access`: Login problems, password resets, two-factor authentication, locked or suspended accounts, single sign-on issues
- `billing`: Charges, invoices, refunds, payment methods, receipts, plan prices
- `bug_report`: Something in the product is broken, throws errors, or behaves incorrectly
- `feature_request`: Asks for new functionality or an improvement to how the product works
- `cancellation`: Wants to cancel, close the account, stop auto-renewal, or leave the service

</details>

**Correct answer:** `account_access`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `account_access` | 96% | ✅ |
| Decisions | `account_access` | 96% | ✅ |
| Haiku | `bug_report` | no probability | ❌ |

**Why:** Since the company switched identity provider (SSO), the app goes blank when opening the workspace. That is account access: the criteria mention SSO explicitly. Haiku said `bug_report`.

**Verdict:** **Clear error**

---

### C01_052 · Support-ticket routing · hard · trap: distractor

**Full text:**

> Our invoice history shows we're current on payment through next March. The problem: three of our five analysts can no longer reach the Datastage workspace as of Monday morning. Each of them sees a message stating their account role could not be verified, then gets returned to the sign-in page. The two of us who can still get in have checked the admin panel and all three affected users still show as active members with the correct role assigned, no suspensions, no removed permissions. We tried removing and re-adding one of the affected users to see if that would reset whatever is broken, but the same verification failure appeared again within minutes of the new invite being accepted. All three affected analysts use the same corporate email domain, while the two of us who can log in normally use a different, older email domain that predates the switch to that domain last year. That detail might be relevant, since the timing lines up roughly with when IT finished migrating everyone's email over. Whatever the underlying cause, we need these three analysts back into their dashboards today, since our Monday reporting cycle depends on all five of us pulling numbers in parallel and we're already behind. Let us know what additional information would help you track down why verification is failing specifically for the newer email domain.

**Question:** Which team should handle this customer support ticket?

<details><summary>Options</summary>

- `account_access`: Login problems, password resets, two-factor authentication, locked or suspended accounts, single sign-on issues
- `billing`: Charges, invoices, refunds, payment methods, receipts, plan prices
- `bug_report`: Something in the product is broken, throws errors, or behaves incorrectly
- `feature_request`: Asks for new functionality or an improvement to how the product works
- `cancellation`: Wants to cancel, close the account, stop auto-renewal, or leave the service

</details>

**Correct answer:** `account_access`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `account_access` | 100% | ✅ |
| Decisions | `account_access` | 99% | ✅ |
| Haiku | `bug_report` | no probability | ❌ |

**Why:** Users with an unverified role are bounced back to login after an email-domain migration. Account access. Haiku said `bug_report` (same pattern as the previous one).

**Verdict:** **Clear error**

---

### C06_019 · Smart-home command · hard · trap: negation

**Full text:**

> I am not in the mood for any music while I prepare this evening's stew, so kindly do not turn any on. What I do require, however, is a reminder later this afternoon to compose an email to the members of my book club regarding next week's meeting location, as I am rather forgetful these days. Please see to that instead.

**Question:** What does the user want the assistant to do?

<details><summary>Options</summary>

- `lights_on`: Turn lights on
- `lights_off`: Turn lights off
- `dim_lights`: Change light brightness
- `set_thermostat`: Change or set the temperature
- `play_music`: Start playing music, a song, artist or playlist
- `pause_music`: Pause or stop music that is playing
- `volume_up`: Make it louder
- `volume_down`: Make it quieter
- `set_timer`: Start a countdown timer
- `set_alarm`: Set a wake-up or clock alarm
- `weather_query`: Ask about the weather or forecast
- `add_to_shopping_list`: Add an item to the shopping list
- `lock_door`: Lock a door
- `unlock_door`: Unlock a door
- `start_vacuum`: Start the robot vacuum
- `check_camera`: Show or check a security camera feed
- `call_contact`: Phone or video-call someone
- `read_calendar`: Ask about scheduled events or appointments
- `turn_on_tv`: Turn on the TV
- `other`: Anything not covered by the options above

</details>

**Correct answer:** `other`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `other` | 70% | ✅ |
| Decisions | `other` | 98% | ✅ |
| Haiku | `set_alarm` | no probability | ❌ |

**Why:** Asks for a reminder to write an email (not in the list, so it's `other`) and adds that they don't want music. Haiku picked `set_alarm`: a reminder isn't an alarm.

**Verdict:** **Clear error**

---

### C09_031 · Content moderation · medium

**Full text:**

> **forum:** Home Cooking Collective
> **thread_title:** The one true way to make risotto
> **comment:** Sure, keep insisting your risotto method is 'the only right way' — must be nice living in a world where everyone who's ever worked a professional kitchen is apparently wrong except you. It's honestly kind of impressive how confidently you post about techniques you've clearly never tried outside your own kitchen. At some point it might be worth trying someone else's method before declaring the debate settled.

**Question:** How should this forum comment be moderated?

<details><summary>Options</summary>

- `acceptable`: Normal on-topic contribution, including strong but civil disagreement
- `harassment`: Insults, demeans or personally attacks another user
- `spam`: Advertising, affiliate links, or unsolicited promotion
- `misinformation`: States clearly false factual claims, e.g. health or science myths, as true
- `off_topic`: Civil but unrelated to the thread's subject

</details>

**Correct answer:** `harassment`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `harassment` | 96% | ✅ |
| Decisions | `harassment` | 90% | ✅ |
| Haiku | `acceptable` | no probability | ❌ |

**Why:** A passive-aggressive comment that belittles the other user's experience. The label says harassment; Haiku says acceptable. It's the line between harsh criticism and a personal attack.

**Verdict:** **Borderline (near 50/50)**

---

### H01_024 · Hallucination (multiple choice) · easy

**Full text:**

> guys I think I left my phone charger in the airbnb again this is like the fourth one this year send help lol

**Question:** Is the writer traveling alone or with someone else?

<details><summary>Options</summary>

- `traveling_alone`: Traveling alone
- `traveling_with_others`: Traveling with someone else
- `group_tour`: Traveling as part of a group tour
- `cannot_determine`: The text does not contain enough information to answer

</details>

**Correct answer:** `cannot_determine`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `cannot_determine` | 82% | ✅ |
| Decisions | `cannot_determine` | 99% | ✅ |
| Haiku | `traveling_with_others` | no probability | ❌ |

**Why:** The writer left their phone charger at the Airbnb again; nothing says whether they travel alone or with others. Haiku picked `traveling_with_others`: it made up a fact, i.e. hallucinated.

**Verdict:** **Clear error**

---

### N02_008 · Contains personal data? · medium

**Full text:**

> I'm relocating for a six-month contract and would like to schedule a viewing of the unit on Cormorant Lane. For reference, my current lease is at 118 Thistledown Row, Unit 4, which the property manager there can confirm if a rental history check is needed. I'm available any weekday after 5pm and can bring documentation to the viewing.

**Question:** Does the text contain personal data that identifies or contacts a specific private individual?

<details><summary>Options</summary>

- `true`: Contains at least one of: a personal phone number, personal email address, home street address, government ID number, bank or card number, or a full name together with a date of birth
- `false`: No such data; first names alone, public figures, company phone numbers, or generic addresses like support@company.com do not count

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.95 | ✅ |
| Decisions | `true` | P(yes) = 1.00 | ✅ |
| Haiku | `false` | no probability | ❌ |

**Why:** The writer gives their current street address, unit number included: personal data. Haiku said no.

**Verdict:** **Clear error**

---

### N05_052 · Same product? · hard · trap: implicit

**Full text:**

> **record_a:** The Oakfen Ultra 14 I purchased weighs a mere 1.2 kilograms and the display measures fourteen inches corner to corner, most convenient for travel.
> **record_b:** This Oakfen Ultra fourteen-inch machine is listed at 2.6 pounds, with a screen thirty-five and a half centimetres across, quite portable indeed.

**Question:** Do the two records describe the same product (same model and same variant)?

<details><summary>Options</summary>

- `true`: Same product, model and variant, even if written differently
- `false`: Different product, model, size, capacity, color or version

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.92 | ✅ |
| Decisions | `true` | P(yes) = 0.96 | ✅ |
| Haiku | `false` | no probability | ❌ |

**Why:** 1.2 kg = 2.6 lb and 14 in = 35.5 cm: they match, it's the same product. Haiku said they are different: it fails on unit conversions.

**Verdict:** **Clear error**

---

### S07_012 · Does the answer answer the question? · hard · trap: long irrelevant context

**Full text:**

> **question:** Is it better to learn a language through full immersion abroad or through structured classes, if the goal is business fluency within a year?
> **answer:** lol ok so this question just reminded me of my cousin's wedding last month where literally nobody could agree on the seating chart and my aunt almost cried over a tablecloth color, absolute chaos, ten out of ten would not recommend planning a wedding with that family ever again. anyway completely unrelated but also not, bc travel logistics are their own nightmare and that's basically what immersion is too lol. ok but fr if your goal is literally business fluency in a year, immersion wins hands down bc you're forced to use the language daily in real high-stakes situations, and structured classes alone just can't replicate that pressure and speed no matter how good the teacher is. anyway back to the wedding saga, the DJ showed up two hours late and my uncle tried to run the playlist off his phone which was its own disaster, truly a day for the ages.

**Question:** How well does the answer address the question that was asked? (Judge relevance and completeness, not factual accuracy.)

<details><summary>Options</summary>

- `0` Does not address the question at all: off-topic or a refusal
- `1` Touches the topic but does not answer what was asked
- `2` Partially answers: addresses the question but misses an important part
- `3` Fully answers the question directly and completely

</details>

**Correct answer:** 3 (Fully answers the question directly and completely)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 2 (Partially answers) | 76% | ✅ (±1) |
| Decisions | 2 (Partially answers) | 87% | ✅ (±1) |
| Haiku | 1 (Touches the topic but does not answer what was asked) | no probability | ❌ |

**Why:** The answer is buried in a wedding story, but it does answer directly: for business fluency in a year, immersion wins. Label: 3. Jev and Decisions said 2 (correct within ±1). Haiku said 1, two levels below: it got lost in the irrelevant text.

**Verdict:** **Clear error**

---

### S10_001 · Hobby expertise · medium

**Full text:**

> I keep fish tank more than twenty years now, since I was young man in my country before I move here. Now I have six tanks in my basement, three for breeding the rams and two apisto species that are not so easy, one just for growing out fry until they are big enough to sell to local shop.
> 
> Every month the beginner club in my city ask me to come and explain the nitrogen cycle to new members, because many people buy fish same day like the tank and then wonder why everybody die in one week. I try explain slow and simple because I remember when I was also confuse about this many years ago.
> 
> Last year I am judge for the small aquascaping contest at the pet expo, this was first time and I was very nervous but the other judges say my notes on the hardscape balance were most detailed of all three judges, ha. My water parameters I do not even test so much anymore because after all this years I know just from looking at the plants and the fish behavior if something is wrong, small things like the tetras staying near the top too much tell me oxygen is maybe low before test kit even show number.
> 
> Right now my project is trying to breed the more difficult killifish species, this one is giving me trouble because the eggs need dry period and I still learning best humidity for the peat moss. Even after so many years there is still something new to learn, this is why I still love this hobby so much.

**Question:** How experienced in the hobby is the person who wrote this post?

<details><summary>Options</summary>

- `0` Complete beginner: brand new, does not know basic terminology
- `1` Novice: knows a few basic terms but struggles with fundamentals
- `2` Advanced beginner: understands the basics and is learning to apply them
- `3` Intermediate: comfortable with core techniques, working on refinement
- `4` Advanced amateur: deep technical knowledge, specialized equipment, consistent results
- `5` Semi-professional: occasionally paid for the work, discusses workflow and clients
- `6` Seasoned expert: many years of experience, teaches others, industry-level nuance

</details>

**Correct answer:** 6 (Seasoned expert)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 6 (Seasoned expert) | 97% | ✅ |
| Decisions | 6 (Seasoned expert) | 100% | ✅ |
| Haiku | 4 (Advanced amateur) | no probability | ❌ |

**Why:** 20+ years keeping aquariums, six tanks, breeds difficult species, gives talks to beginners and has judged competitions. That is expert (6). Haiku said 4.

**Verdict:** **Clear error**

---

### S10_012 · Hobby expertise · hard · trap: distractor

**Full text:**

> Quick question for anyone who's dealt with this before — feels dumb to even ask but it's bugging me.
> 
> Background on my setup, for context:
> - Running the bread program at a 40-seat cafe for going on eleven years now, three ovens, roughly 200 loaves a day between the sourdough country loaf, a rye, and a rotating special
> - Hydration on the country loaf sits at 78%, and I adjust it in quarter-percent increments depending on ambient humidity in the bakery, which I log every morning before I start
> - I trained two apprentices last year who now run their own small operations, so I'm used to explaining this stuff from scratch when needed
> 
> The actual question:
> - Starting last month, my usual flour supplier's all-purpose flour has been absorbing noticeably less water than before, maybe half a percent difference, even though the bag still lists the same protein content
> - I've ruled out my scale (recalibrated it), my starter (same activity levels, same float test results, same rise timing), and my oven (steam injection timing unchanged)
> - Anyone know if mills sometimes shift the protein blend slightly within a stated range without changing the label, or is this more likely a milling date or storage humidity issue on their end?
> 
> I know it sounds like a beginner question — "why is my dough acting different" — but I've been chasing consistency on this recipe for over a decade and a half-percent shift is enough to throw off my whole morning bake schedule if I don't catch it early. Just trying to figure out if I need to call the mill or just adjust my formula going forward.

**Question:** How experienced in the hobby is the person who wrote this post?

<details><summary>Options</summary>

- `0` Complete beginner: brand new, does not know basic terminology
- `1` Novice: knows a few basic terms but struggles with fundamentals
- `2` Advanced beginner: understands the basics and is learning to apply them
- `3` Intermediate: comfortable with core techniques, working on refinement
- `4` Advanced amateur: deep technical knowledge, specialized equipment, consistent results
- `5` Semi-professional: occasionally paid for the work, discusses workflow and clients
- `6` Seasoned expert: many years of experience, teaches others, industry-level nuance

</details>

**Correct answer:** 6 (Seasoned expert)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 6 (Seasoned expert) | 99% | ✅ |
| Decisions | 6 (Seasoned expert) | 99% | ✅ |
| Haiku | 4 (Advanced amateur) | no probability | ❌ |

**Why:** A professional baker for 11 years, 200 loaves a day, has trained apprentices; asks a question that sounds basic. That is expert (6). Haiku said 4: it fell for the distractor.

**Verdict:** **Clear error**

---

### T01_096 · Stock tweets · medium

**Full text:**

> Didn't expect to say this about $DRPL, but the new distribution partnership they signed actually looks decent, real shelf space in over 2,000 new stores. Not turning into a bull on this name, but I nudged my short down a bit.

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 3 (Mildly bullish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 3 (Mildly bullish) | 59% | ✅ |
| Decisions | 2 (Neutral) | 35% | ✅ (±1) |
| Haiku | 1 (Mildly bearish) | no probability | ❌ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bullish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bullish` | 43% | ✅ |
| Decisions | `bullish` | 52% | ✅ |
| Haiku | `neutral` | no probability | ❌ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.43 | ❌ |
| Decisions | `true` | P(yes) = 0.63 | ✅ |
| Haiku | `true` | no probability | ✅ |

**Why:** The partnership looks decent, the author is not turning bullish but trimmed their short a bit. The most ambiguous tweet in the set: the author is still betting on a drop, just less. The label says mildly bullish. All three models hesitated or failed in at least one of the three formats.

**Verdict:** **Debatable label**

---

### T01_100 · Stock tweets · hard · trap: mixed signals

**Full text:**

> $VNTX says it's fully insured against the supplier lawsuit and doesn't expect any operational disruption. Fair enough, but legal overhangs like this tend to cap a stock for a while regardless, so I'm not adding more here even though I'm staying put.

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 1 (Mildly bearish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 1 (Mildly bearish) | 97% | ✅ |
| Decisions | 1 (Mildly bearish) | 95% | ✅ |
| Haiku | 2 (Neutral) | no probability | ✅ (±1) |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bearish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bearish` | 70% | ✅ |
| Decisions | `bearish` | 71% | ✅ |
| Haiku | `neutral` | no probability | ❌ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.09 | ✅ |
| Decisions | `false` | P(yes) = 0.01 | ✅ |
| Haiku | `false` | no probability | ✅ |

**Why:** The company is insured against the lawsuit, but such cases usually weigh on the stock; the author is not buying more but is staying in. Mildly bearish; Haiku said neutral. Mixed signals.

**Verdict:** **Borderline (near 50/50)**

---

### T01_139 · Stock tweets · hard · trap: mixed signals

**Full text:**

> regulators cleared $IRNC's new policy product for sale but tacked on extra capital reserve requirements that eat into the margin story a bit. trimmed a few shares, still holding the core position though

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 1 (Mildly bearish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 1 (Mildly bearish) | 92% | ✅ |
| Decisions | 2 (Neutral) | 42% | ✅ (±1) |
| Haiku | 2 (Neutral) | no probability | ✅ (±1) |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bearish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bearish` | 85% | ✅ |
| Decisions | `bearish` | 75% | ✅ |
| Haiku | `neutral` | no probability | ❌ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.20 | ✅ |
| Decisions | `false` | P(yes) = 0.10 | ✅ |
| Haiku | `false` | no probability | ✅ |

**Why:** The product was approved, but with extra capital requirements that eat into the margin, and the author sold some shares. Mildly bearish; Haiku said neutral.

**Verdict:** **Clear error**

---

## 6. Only Jev wrong (7 questions)

### C04_042 · Cuisine of a recipe · easy

**Full text:**

> Breakfast this morning was a stack of those spongy semolina pancakes riddled with hundreds of tiny bubbling holes across the surface, made from a thin batter of fine semolina, yeast, and a little flour left to rest until it turns almost foamy, cooked on just one side on a dry, ungreased pan so the top stays soft and porous while the bottom sets golden, then served warm, drizzled generously with a mix of melted butter and honey that pools right down into every single hole.

**Question:** Which cuisine does this recipe belong to?

<details><summary>Options</summary>

- `italian`
- `mexican`
- `japanese`
- `indian`
- `french`
- `thai`
- `korean`
- `moroccan`

</details>

**Correct answer:** `moroccan`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `italian` | 50% | ❌ |
| Decisions | `moroccan` | 98% | ✅ |
| Haiku | `moroccan` | no probability | ✅ |

**Why:** Semolina pancakes with hundreds of tiny holes, cooked on one side only, served with butter and honey: Moroccan baghrir. Jev said Italian (50%); the other two got it right with 98% or more.

**Verdict:** **Clear error**

---

### C05_050 · Scientific field of an abstract · medium

**Full text:**

> In this modest analysis of a biobank comprising some 400,000 participant records, we observe that carriers of a particular rare variant show, on average, a modestly elevated risk of early-onset gallstone disease relative to non-carriers.

**Question:** Which scientific field does this paper primarily belong to?

<details><summary>Options</summary>

- `astronomy`
- `ecology`
- `genetics`
- `neuroscience`
- `materials_science`
- `organic_chemistry`
- `climate_science`
- `particle_physics`
- `epidemiology`
- `computer_vision`
- `linguistics`
- `geology`

</details>

**Correct answer:** `genetics`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `epidemiology` | 54% | ❌ |
| Decisions | `genetics` | 95% | ✅ |
| Haiku | `genetics` | no probability | ✅ |

**Why:** A 400,000-person biobank: carriers of a rare genetic variant have a higher risk of stones. Genetics (the exposure is the variant), but it is also epidemiology. Jev: epidemiology at 54%.

**Verdict:** **Borderline (near 50/50)**

---

### N05_036 · Same product? · hard · trap: numbers

**Full text:**

> **record_a:** ok so the sonari aura 300 is honestly slaying rn, wireless over ear, ANC is actually decent, case battery is rated 450mah which gives like 4 extra full charges on top of the headphone's own battery, comes in that matte black everyone's obsessed with, foldable too so it fits in my bag no problem.
> **record_b:** also got the sonari aura 300 listed here, matte black too, still foldable, still has ANC, but ngl the case on this one is only rated 180mah so you're basically getting like one extra charge tops, kinda mid tbh compared to what i expected.

**Question:** Do the two records describe the same product (same model and same variant)?

<details><summary>Options</summary>

- `true`: Same product, model and variant, even if written differently
- `false`: Different product, model, size, capacity, color or version

</details>

**Correct answer:** `false`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `true` | P(yes) = 0.51 | ❌ |
| Decisions | `false` | P(yes) = 0.02 | ✅ |
| Haiku | `false` | no probability | ✅ |

**Why:** The same earbuds, but one charging case has 450 mAh and the other 180 mAh: a different variant. Jev: 51%, a tie.

**Verdict:** **Borderline (near 50/50)**

---

### T01_054 · Stock tweets · hard · trap: mixed signals

**Full text:**

> Even I have to admit the put wall on Wintermere Media getting torn through like this isn't normal, dealers are scrambling to hedge and this could easily gap another 20% before it's over. Bought my first calls on this name ever. $WNTM

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 4 (Strongly bullish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 0 (Strongly bearish) | 61% | ❌ |
| Decisions | 4 (Strongly bullish) | 51% | ✅ |
| Haiku | 4 (Strongly bullish) | no probability | ✅ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bullish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bearish` | 56% | ❌ |
| Decisions | `bullish` | 100% | ✅ |
| Haiku | `bullish` | no probability | ✅ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.35 | ❌ |
| Decisions | `true` | P(yes) = 0.99 | ✅ |
| Haiku | `true` | no probability | ✅ |

**Why:** The put wall is getting torn through, the stock could gap another 20%, and the author bought their first calls: very bullish, in options slang. Jev answered bearish in ALL THREE formats (level 0, 'bearish', 35% that it rises). It read 'put' as a bearish signal. Jev's most consistent error.

**Verdict:** **Clear error**

---

### T01_096 · Stock tweets · medium

**Full text:**

> Didn't expect to say this about $DRPL, but the new distribution partnership they signed actually looks decent, real shelf space in over 2,000 new stores. Not turning into a bull on this name, but I nudged my short down a bit.

**Question (sentiment):** How bullish or bearish is this tweet about the stock mentioned, considering both the author's view and the news it reports?

<details><summary>Options</summary>

- `0` Strongly bearish: the author's view or the reported news points clearly to a large fall (selling, shorting, severe bad news)
- `1` Mildly bearish: leans negative; suggests some decline or underperformance
- `2` Neutral: no directional implication (routine or in-line news, balanced views, or undecided)
- `3` Mildly bullish: leans positive; suggests some gains
- `4` Strongly bullish: the author's view or the reported news points clearly to a large rise (buying heavily, hype, major good news)

</details>

**Correct answer:** 3 (Mildly bullish)

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | 3 (Mildly bullish) | 59% | ✅ |
| Decisions | 2 (Neutral) | 35% | ✅ (±1) |
| Haiku | 1 (Mildly bearish) | no probability | ❌ |

**Question (direction):** Which direction does this tweet suggest for the stock price?

<details><summary>Options</summary>

- `bearish`: Suggests the price will go down
- `neutral`: No clear direction either way
- `bullish`: Suggests the price will go up

</details>

**Correct answer:** `bullish`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `bullish` | 43% | ✅ |
| Decisions | `bullish` | 52% | ✅ |
| Haiku | `neutral` | no probability | ❌ |

**Question (expects_rise):** Does this tweet suggest the stock price will rise?

<details><summary>Options</summary>

- `true`: The author's view or the reported news points to a price increase
- `false`: It points to a decline, or has no clear direction

</details>

**Correct answer:** `true`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.43 | ❌ |
| Decisions | `true` | P(yes) = 0.63 | ✅ |
| Haiku | `true` | no probability | ✅ |

**Why:** The partnership looks decent, the author is not turning bullish but trimmed their short a bit. The most ambiguous tweet in the set: the author is still betting on a drop, just less. The label says mildly bullish. All three models hesitated or failed in at least one of the three formats.

**Verdict:** **Debatable label**

---

## 7. Questions with no information (ideal answer: about 50%)

The text gives no way to know the answer, so an honest model should say about 0.50. Below 0.2 or above 0.8 means answering confidently about something it can't know. Haiku is not included because it can only say yes or no.

| Item | Question | Jev P(yes) | Decisions P(yes) |
|---|---|---|---|
| H02_004 | Was Margaret unwell on Thursday? | 0.42 | 0.49 |
| H02_011 | Did the store have the seasonal pumpkin bread back in stock? | 0.39 | 0.50 |
| H02_017 | Will there be an evening session available for parents who work late? | **0.10** | 0.50 |
| H02_018 | Did it rain in the town yesterday? | 0.37 | 0.50 |
| H02_020 | Did the painting get accepted into the gallery show? | 0.22 | **0.10** |
| H02_026 | Will the trifle be well received at this year's church social? | 0.69 | 0.72 |
| H02_032 | Does the writer own a dog? | **0.17** | 0.50 |
| H02_033 | Are they visiting the museum today? | **0.04** | **0.11** |
| H02_034 | Does the writer have a pet waiting at home? | **0.12** | 0.50 |
| H02_036 | Will either of the injured players miss the next game? | 0.54 | 0.50 |
| H02_042 | Does the writer have a dog? | **0.17** | 0.50 |
| H02_045 | Did the team agree to move the meeting to Thursday? | **0.16** | **0.13** |
| H02_046 | Did the writer get the transfer position? | 0.24 | 0.50 |
| H02_050 | Will this year's spring concert be held indoors? | 0.35 | 0.50 |
| H02_055 | Is the school principal's office on the second floor? | 0.31 | 0.50 |
| H02_056 | Did the writer choose to do the walking tour? | 0.25 | 0.34 |
| H02_058 | Does the son want to play soccer professionally when he grows up? | 0.29 | 0.50 |
| H02_063 | Will the marketing team's budget be cut next quarter? | 0.54 | 0.52 |
| H02_067 | Is the writer's desk positioned near a window? | 0.26 | 0.50 |
| H02_068 | Did the writer start making the soup before noon? | 0.37 | 0.50 |
| H02_069 | Is the farmers market within walking distance of the writer's home? | 0.49 | 0.50 |
| H02_071 | Is Mara older than the writer? | 0.56 | 0.50 |
| H02_072 | Did the writer's team end up winning the game? | 0.47 | 0.50 |
| H02_073 | Did practice start before 5 pm? | 0.49 | 0.50 |
| H02_074 | Will the renovation take longer than six months? | 0.51 | 0.50 |
| H02_075 | Is the school within a mile of the writer's house? | 0.56 | 0.50 |
| H02_076 | Will brunch be on a Saturday? | 0.54 | 0.50 |
| H02_078 | Is Tasha older than the person she's calling? | 0.53 | 0.50 |
| H02_080 | Did the writer manage to sign up for a shift later that night? | 0.26 | **0.16** |
| H02_081 | Did the writer take a photo of the cat? | **0.08** | **0.03** |

Confident answers are in bold. The confident cases in full:

### H02_081 · Hallucination (yes/no) · medium

**Full text:**

> So this might sound like a weird post but has anyone else noticed the stray cat hanging around the Hendersons' porch over on Birch Lane? I first spotted it about two weeks ago sitting under their mailbox, and now it shows up almost every evening around the same time, orange tabby, pretty chill, doesn't run off when you get close. I left some food out once just to see what would happen and it came back the next day looking for more, so now I'm half convinced I've accidentally adopted a cat. If anyone recognizes it or knows if it belongs to someone a few streets over, let me know, I don't want to keep feeding someone else's pet by accident.

**Question:** Did the writer take a photo of the cat?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.08 | — |
| Decisions | `false` | P(yes) = 0.03 | — |
| Haiku | — | — | — |

**Why:** Nobody mentions a photo of the cat. Jev (8%) and Decisions (3%) say with high confidence that it wasn't taken: they treat 'not mentioned' as 'didn't happen'.

**Verdict:** **Clear error**

---

### H02_033 · Hallucination (yes/no) · hard · trap: related info, missing fact

**Full text:**

> Yesterday we visit the old castle, very beautiful but so many stairs, my legs still hurting today!

**Question:** Are they visiting the museum today?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.04 | — |
| Decisions | `false` | P(yes) = 0.11 | — |
| Haiku | — | — | — |

**Why:** The writer went to the castle yesterday and their legs still hurt. Nothing about the museum. Both say no with high confidence (4% and 11%); tiredness is a weak cue.

**Verdict:** **Borderline (near 50/50)**

---

### H02_045 · Hallucination (yes/no) · medium

**Full text:**

> sorry for the late reply I've been swamped, saw your message about the meeting time and I think Thursday works better for me but let me check with the team first.

**Question:** Did the team agree to move the meeting to Thursday?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.16 | — |
| Decisions | `false` | P(yes) = 0.13 | — |
| Haiku | — | — | — |

**Why:** Thursday works better, but the writer wants to check with the team first: the team hasn't accepted yet. Saying 'no' is reasonable, so the item is wrongly framed as 'no information'.

**Verdict:** **Debatable label**

---

### H02_020 · Hallucination (yes/no) · hard · trap: related info, missing fact

**Full text:**

> - Monday: finally finished the painting I've been working on for weeks, feels so good to have it done.
> - Tuesday: showed it to Mia, she seemed impressed I think.
> - Wednesday: dropped it off at the gallery for the jury to review, they said results come out in two weeks.
> - Today: mostly just cleaned the studio, feeling a bit restless waiting.

**Question:** Did the painting get accepted into the gallery show?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.22 | — |
| Decisions | `false` | P(yes) = 0.10 | — |
| Haiku | — | — | — |

**Why:** Results come out in two weeks and the writer is still waiting: not accepted yet. The models' 'no' is reasonable; the item is wrongly framed.

**Verdict:** **Debatable label**

---

### H02_017 · Hallucination (yes/no) · medium

**Full text:**

> This is important notice from school. Next week we have parent-teacher meetings on Tuesday and Wednesday. Please to sign up on the sheet in office. Meetings are 15 minutes each, no exceptions for late come.

**Question:** Will there be an evening session available for parents who work late?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.10 | — |
| Decisions | `true` | P(yes) = 0.50 | — |
| Haiku | — | — | — |

**Why:** 15-minute meetings with no exceptions for latecomers suggests there is no evening session. Jev's 'no' (10%) is reasonable.

**Verdict:** **Debatable label**

---

### H02_032 · Hallucination (yes/no) · easy

**Full text:**

> Quick update for anyone following the community garden proposal on the old lot at the end of Poplar Street. I finally got a callback from the city planning office after three weeks of leaving messages, which honestly felt like its own achievement. Here's where things stand.
> 
> The lot is currently zoned for light commercial use, so before anything can happen we need a variance, which means a public hearing. I've already submitted the paperwork and the earliest slot they had was the second Tuesday of next month, so that's now on the calendar. In the meantime, the planning office confirmed the soil testing from two years ago is still on file and apparently still valid, which saves us the cost of retesting, a nice bit of good news.
> 
> On the design side, I sketched out a rough layout with twelve raised beds, a small tool shed near the fence line, and a rainwater collection barrel by the shed. I based the bed spacing loosely on the community garden two neighborhoods over, since a few of us visited it last month and it seemed to work well for accessibility, wide enough paths for wheelchairs and that sort of thing.
> 
> Funding-wise, we've got about 40% of what we'd need from the neighborhood association's discretionary fund, and I'm looking into a few small grants aimed at urban greening projects. If anyone has grant-writing experience and a free evening sometime, I would very much welcome the help. I'll post again after the hearing with whatever they decide.

**Question:** Does the writer own a dog?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.17 | — |
| Decisions | `true` | P(yes) = 0.50 | — |
| Haiku | — | — | — |

**Why:** About a community garden; nothing about dogs. Jev: 17% that the writer has a dog (roughly 40% of households have one). Decisions: 50%.

**Verdict:** **Clear error**

---

### H02_042 · Hallucination (yes/no) · easy

**Full text:**

> Anyone else notice the streetlight on Maple has been out for like three weeks now? I've called the city twice, standard bureaucratic silence so far. At this point I'm considering just buying a very long extension cord and a floodlight myself.

**Question:** Does the writer have a dog?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.17 | — |
| Decisions | `true` | P(yes) = 0.50 | — |
| Haiku | — | — | — |

**Why:** About a broken streetlight; nothing about dogs. Jev: 17%. Decisions: 50%.

**Verdict:** **Clear error**

---

### H02_034 · Hallucination (yes/no) · easy

**Full text:**

> I want to write about our trip because so many things happen and I don't want to forget. We arrive in the small town three day ago, very late at night because the bus was late almost two hour, and the hotel almost give away our room because we are so late, but the man at front desk was kind and hold it for us anyway.
> 
> First day we just walk around slowly because we so tired from travel, find small restaurant near the river and eat the local soup, it was very good, my husband order three bowl! The town is smaller than I think from the photos online, but is very pretty, old buildings with flowers on the balcony everywhere.
> 
> Second day we take the boat tour on the river, guide was speaking three language which impress me a lot, he explain the history of the bridges, very old, some from hundreds year ago. After boat we visit small market and I buy some handmade soap for my sister, she will like it I think.
> 
> Today we wake up early and hike to the hill outside town, view from top was really something, whole valley you can see. My legs are tired now but is good tired. Tomorrow we travel to the next city by train, I already a little sad to leave this place, it feel very peaceful here, not like our normal life at home at all.

**Question:** Does the writer have a pet waiting at home?

<details><summary>Options</summary>

- `true` / `false` (no criteria)

</details>

**Correct answer:** `unknown`

| Model | Answer | Confidence | Correct? |
|---|---|---|---|
| Jev | `false` | P(yes) = 0.12 | — |
| Decisions | `true` | P(yes) = 0.50 | — |
| Haiku | — | — | — |

**Why:** About a trip; nothing about pets. Jev: 12% that one is waiting at home. Decisions: 50%.

**Verdict:** **Clear error**

---

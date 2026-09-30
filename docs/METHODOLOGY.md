# Methodology

Every score is transparent and every weight is configurable in
[`backend/app/constants.py`](../backend/app/constants.py). Weight sets are asserted to sum
to 1.0 at import time, so a bad edit fails loudly. The live weights are also exposed at
`GET /api/meta` and rendered on the app's Methodology page.

Pipeline: **Data → NLP → Statistics/ML → Gap engine → Recommendation → Visualization.**
The LLM layer is an optional enhancement and never makes the decision.

---

## 1. Skill extraction & normalisation

**Normalisation** maps surface forms to a canonical taxonomy via an alias dictionary
(e.g. `"Python 3"`, `"python developer"`, `"python scripting"` → **Python**;
`"Amazon Web Services"`, `"AWS Cloud"` → **AWS**; `"devsecops"` → **Cloud Security**).
Unmatched terms fall back to `rapidfuzz` token-set ratio above a threshold.

**Extraction pipeline** (per job description):

```
raw text → preprocess → dictionary phrase match (longest-first)
         → TF-IDF cosine similarity to skill "documents"  (semantic layer)
         → taxonomy match + confidence
         → optional LLM validation (disabled by default)
```

- Dictionary hits get confidence ≈ 0.97; semantic hits get a lower band (0.55–0.90).
- Longest-first matching prevents `"java"` matching inside `"javascript"`.
- Intra-word `.`/`/` are preserved (`node.js`, `ci/cd`) but stripped at word boundaries
  (so a sentence-ending `"devsecops."` still matches).
- `sentence-transformers` (optional, `requirements-ml.txt`) upgrades the semantic layer;
  the code degrades gracefully if absent.

Inspired by ESCO-based and weakly-supervised skill-extraction literature.

---

## 2. Demand index (0–100)

Weighted blend of six components, each normalised to 0–100:

```
Demand = 0.35·job_volume + 0.20·job_growth + 0.15·employer_signal
       + 0.10·salary_premium + 0.10·industry_growth + 0.10·emerging_signal
```

- **job_volume** — postings mentioning the skill in the district; **log-scaled** then
  min-max across all pairs (compresses heavy tails).
- **job_growth** — 12-month growth mapped to 0–100 (see growth definition below).
- **employer_signal** — mean employer-survey demand score (already 0–100).
- **salary_premium** — `avg_salary(skill) / district_median_salary`, min-max scaled
  (p10–p90 range from data).
- **industry_growth** — the skill's 12-month sector momentum (`trend¹² − 1`) mapped to 0–100.
- **emerging_signal** — the emergence score (below).

The UI shows each component's value **and** its weighted contribution, which sum to the index.

---

## 3. Emerging-skill detection

```
Emergence = 0.40·growth + 0.25·recency + 0.20·cross_industry + 0.15·employer_signal
```

- **growth** — see below (0–100).
- **recency** — share of postings in the last 3 months.
- **cross_industry** — distinct industries requesting the skill ÷ total industries.
- **employer_signal** — mean employer demand score.

Label derived from the **growth rate** (fraction), not by hand:
`≥0.25 Emerging · ≥0.08 Growing · ≥−0.05 Stable · else Declining`.

**Growth rate** uses denominator smoothing and a volume-confidence damper so low-volume
skills don't explode to +300 %:

```
raw   = (recent_3mo − prior_3mo) / (prior_3mo + 4)
growth = clamp(raw · min(1, count/8),  −0.9, 1.5)
```

---

## 4. Supply index (0–100)

```
Supply = 0.50·capacity + 0.20·completion + 0.20·placement + 0.10·pipeline
```

- **capacity** — local training seats for the skill, log-scaled.
- **completion** / **placement** — mean rates of covering courses (×100).
- **pipeline** — enrolled learners, log-scaled.

A skill with no local course scores ≈ 0 supply → a large gap where demand is high (this is
why emerging skills, which have little established training, surface as critical gaps).

---

## 5. Skill gap

```
Gap = clamp(Demand − Supply, 0, 100)
```

Classification (configurable thresholds):
`≥60 Critical · ≥40 High · ≥20 Moderate · else Balanced`.

---

## 6. Course alignment & obsolescence

```
Alignment = 0.45·skill_demand + 0.25·placement + 0.15·utilisation + 0.15·freshness
```

- **skill_demand** — mean demand index of the course's skills in that district.
- **placement** — placement rate ×100.
- **utilisation** — enrolled ÷ capacity ×100.
- **freshness** — decays from 100 (updated now) to 0 (≥36 months old).

Obsolescence risk from the score: `≥65 Low · ≥45 Moderate · else High`.
Suggested action: `RETIRE_OR_REDUCE` (low score + mostly declining skills),
`UPDATE_CURRICULUM` (missing in-demand skills), `REVIEW`, or `KEEP`. Courses are **never
auto-deleted** — low scores are flagged for human review.

---

## 7. Forecasting

A transparent ensemble of **linear-trend regression + moving average + exponential
smoothing**, averaged, with an uncertainty band from in-sample residuals that **widens with
the horizon**. Produces 3/6/12-month estimates. Forecasts are scenarios, not guarantees,
and the UI always shows the band.

---

## 8. Recommendation engine

Transparent rules over the computed signals, in priority order:

1. Declining skill with supply ≫ demand → **REDUCE_CAPACITY**
2. Critical/High gap, no local course → **CREATE_COURSE**
3. Critical/High gap, course exists but under-capacity → **EXPAND_COURSE**
4. Emerging/Growing skill, course misses modern topics → **UPDATE_COURSE**
5. Moderate/High gap, course exists but low placement → **UPSKILL_TRAINERS**
6. Moderate gap → **MONITOR**

Priority score: `0.5·gap + 0.3·demand + 0.2·emergence` → Critical/High/Medium/Low.
Suggested capacity scales with demand, gap and district size, rounded to 25 seats
(bounded 50–400). **Every recommendation carries machine-readable evidence** (postings,
employers, growth, seats, placement, salary, rationale) for the "Why?" panel. No
per-district outcome is hard-coded.

---

## Confidence & limitations

- The model **cannot** perfectly predict future employment; forecasts are estimates.
- Recommendations are **decision-support**, not authoritative policy.
- AI-assisted components require **human validation** before implementation.
- The prototype runs on **synthetic** data; real deployment requires real ingestion and
  validation against ground truth.

## Research basis

- ILO — *Towards a more effective Labour Market Information System in India*.
- ESCO-based and weakly-supervised skill extraction from job postings.
- LLM-based ESCO skill matching; emerging-skill detection from job advertisements.
- AI-assisted education–employment alignment and course generation.

# Dataset

> **All figures are synthetic demo data.** District names and coordinates are real
> geographic facts (for map placement); **all labour statistics are generated for
> demonstration and are NOT official government statistics.**

## What is generated

Running `python scripts/generate_demo_data.py` produces (with the default seed):

| Entity | Count | Notes |
|---|---|---|
| Districts | 125 | Real names/coords across 20+ states/UTs |
| Skills | 47 | Curated taxonomy across 12 categories |
| Job postings | ~12,000 | 12 months, skills extracted from generated text |
| Employer signals | ~3,900 | Per (district, skill) survey-style signals |
| Courses | ~880 | Existing programmes with capacity/outcomes |
| Demand points | ~22,000 | Monthly (district, skill) time-series |
| Skill metrics | ~4,700 | Computed per (district, skill) |
| Recommendations | ~3,500 | Computed, evidence-backed |
| Course alignments | ~880 | Computed per course |

Exact counts are printed by the generator and exposed at `GET /api/meta`.

## Why it is internally consistent (not random)

Randomly-generated independent numbers would make the gap engine meaningless. Instead:

1. **District archetype → industry mix.** Each district has an archetype (IT hub,
   emerging-tech, manufacturing, mixed, agri-services) and a tech-intensity. The archetype
   sets which industries dominate hiring.
2. **Industry mix → skill demand.** Each skill lists the industries that request it and a
   base popularity, so a district's skill *affinity* = popularity × industry match.
3. **Trend applied over time.** Each skill has a monthly `trend` factor (>1 growing,
   <1 declining). Its sampling weight is multiplied by `trend^month`, so **real 12-month
   growth emerges** in the time-series (e.g. Generative AI rises, Basic Office Tools falls).
4. **Salary reflects skill value.** High-value categories (AI, Cloud, Security, DevOps)
   carry a salary premium; salary premium then feeds the demand index.
5. **Supply deliberately lags for new skills.** Courses are seeded weighted by each skill's
   `supply_maturity`, so established skills have training and **emerging skills do not** —
   creating realistic critical gaps that the engine *discovers*, rather than being told.
6. **Placement reflects momentum.** Modern skills place better; foundational/declining
   courses are older (freshness decays) → obsolescence signals appear naturally.

Because of this, an IT hub surfaces gaps in Python/Azure/ML/GenAI while a manufacturing
district surfaces Welding/CNC/PLC — from the data, with no per-district rules.

## Reproducibility

Generation is seeded (`DEMO_SEED` in `.env`, default `20260930`) and uses only stable
checksums (never Python's salted `hash()`), so re-running produces the same dataset.
Change `DEMO_SEED`, `DEMO_NUM_DISTRICTS`, or `DEMO_JOBS_PER_DISTRICT` to vary scale.

## Provenance

`GET /api/meta` returns record counts, coverage months, last-updated month, the
`"synthetic-demo"` data kind, and the disclaimer string. The UI shows a persistent banner
on every page.

## Replacing with real data

The schema *is* the multi-source signal model the problem statement asks for:

- **Job postings** → real job-board / career-page ingestion.
- **Employer signals** → employer surveys / industry consultations.
- **Courses & providers** → training MIS (ITIs, polytechnics, PMKVY, etc.).
- **Demand points** → derived monthly from real postings.
- **Districts** → seed real NSO district labour indicators (LFPR/WPR/unemployment/NEET).

Swap `generator.py` for ingestion scripts that write the same raw tables, then run
`pipeline.compute()`. No engine code changes.

## Skill taxonomy categories

Programming · Web Development · Cloud · DevOps · Data & AI · Data · Security ·
Embedded & Hardware · Engineering · Skilled Trades · Green Skills · Healthcare · Business ·
Foundational (legacy/declining, used to demonstrate obsolescence detection).

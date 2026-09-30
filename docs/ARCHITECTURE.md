# Architecture

## Overview

SkillPulse India is a two-tier application: a **Python/FastAPI analytics backend** and a
**Next.js frontend**. All intelligence is computed in the backend and materialised into
tables; the frontend is a read-only visualisation and exploration layer.

```
                         ┌─────────────────────────────────────────────┐
                         │                 FRONTEND                     │
                         │  Next.js (App Router) · React · TypeScript    │
                         │  Recharts · Leaflet/OSM · Tailwind            │
                         │  /  /dashboard  /districts/[id]  /skills/[id] │
                         │  /courses  /recommendations  /compare  /meth. │
                         └───────────────┬─────────────────────────────┘
                                         │  HTTP  /api/*  (proxied)
                         ┌───────────────▼─────────────────────────────┐
                         │                 BACKEND (FastAPI)            │
                         │  api/  districts · skills · courses ·         │
                         │        recommendations · analytics · meta    │
                         └───────────────┬─────────────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                     services/ (engines)                          │
        │                                                                  │
        │  skill_normalization  →  skill_extraction                        │
        │  demand_engine (demand + emergence)                              │
        │  gap_engine   (supply + gap)                                     │
        │  forecasting  ·  course_intelligence  ·  district_scoring        │
        │  recommendation_engine                                          │
        │                                                                  │
        │  generator.py  (synthetic raw signals)                          │
        │  pipeline.py   (orchestrates all engines → materialised tables) │
        └───────────────┬──────────────────────────────────────────────┘
                        │  SQLAlchemy 2.0
        ┌───────────────▼──────────────────────────────────────────────┐
        │  DATABASE  (SQLite by default; PostgreSQL via DATABASE_URL)     │
        │  raw:      districts · skills · job_postings · employer_signals │
        │            · courses · training_providers · demand_points       │
        │  computed: skill_metrics · recommendations · course_alignments  │
        └────────────────────────────────────────────────────────────────┘
```

## Data flow

1. **Generate** (`scripts/generate_demo_data.py` → `services/generator.py`)
   Creates districts, skills, training providers, job postings (with skills extracted from
   each posting's text), employer signals, monthly demand points, and courses. Internally
   consistent: a district's archetype drives its industry mix, which drives skill demand.

2. **Compute** (`services/pipeline.py`)
   Reads all raw signals, aggregates per `(district, skill)`, derives global normalisation
   ranges, then runs the engines to produce `SkillMetric`, `Recommendation`, and
   `CourseAlignment` rows. Idempotent and re-runnable.

3. **Serve** (`app/main.py` + `app/api/*`)
   Routers read the materialised tables and expose them as JSON. Roll-ups
   (district summaries, national overview) are computed on read from the metrics.

4. **Visualise** (frontend)
   Client components fetch `/api/*` and render maps, charts, tables and the evidence panel.

## Backend module responsibilities

| Module | Responsibility |
|---|---|
| `app/config.py` | Settings from `.env` (DB URL, CORS, demo seed/size, optional LLM). |
| `app/constants.py` | **All** engine weights & thresholds; weight sets asserted to sum to 1.0. |
| `app/database.py` | SQLAlchemy engine/session; `DATABASE_URL` switches SQLite↔Postgres. |
| `app/models/` | ORM models (portable column types incl. JSON). |
| `app/data/` | Skill taxonomy + district gazetteer seeds (with generator attributes). |
| `services/skill_normalization.py` | Alias dictionary + fuzzy matching → canonical skill. |
| `services/skill_extraction.py` | Dictionary + TF-IDF (optional transformer) extraction. |
| `services/demand_engine.py` | Demand index + emergence score/label + explanation. |
| `services/gap_engine.py` | Supply index + gap score/label. |
| `services/forecasting.py` | Ensemble forecast with uncertainty band. |
| `services/course_intelligence.py` | Course alignment + obsolescence risk. |
| `services/district_scoring.py` | District-level roll-ups. |
| `services/recommendation_engine.py` | Rules + scoring → explainable actions. |
| `services/generator.py` | Synthetic data generation. |
| `services/pipeline.py` | Orchestration of engines → materialised tables. |

## Database schema (summary)

See [DATASET.md](DATASET.md) for field-level detail. Tables:

- **districts** — id, name, state, lat/lon, synthetic demographics, training_capacity
- **skills** — canonical_name, category, aliases (JSON), related_skills (JSON), emerging_flag
- **job_postings** — title, company, industry, district_id, date_posted, salary, skills (JSON)
- **employer_signals** — district_id, skill_id, demand_score, confidence, survey_date
- **courses** — name, provider, district_id, capacity, enrolled, completion/placement rate,
  last_updated, + `course_skill` many-to-many to skills
- **training_providers** — name, type, district_id
- **demand_points** — district_id, skill_id, month, job_count (12-month series)
- **skill_metrics** *(computed)* — demand/supply/gap indices + JSON component breakdowns,
  growth, emergence, avg_salary
- **recommendations** *(computed)* — action, priority, suggested course/capacity,
  target_skills, headline, evidence (JSON)
- **course_alignments** *(computed)* — alignment_score, obsolescence_risk, components,
  missing_skills, recommendation

## Scaling to production / real data

- Point `DATABASE_URL` at PostgreSQL (optionally with `pgvector` for embedding search).
- Replace `generator.py` with real ingestion (job-board APIs, employer surveys, NSO
  district labour data, training MIS). Every metric already carries provenance via
  `/api/meta`; the multi-source signal model (job postings, employer signals, courses,
  time-series) is already the schema.
- Swap the TF-IDF semantic matcher for sentence-transformers (`requirements-ml.txt`) —
  the code detects availability and degrades gracefully.
- The optional LLM layer is provider-agnostic (config only) and is an *enhancement*, never
  the decision-maker.

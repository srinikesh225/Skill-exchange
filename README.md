# SkillPulse India

**District-level Labour Market Intelligence & Skill Planning System**
Prototype for Smart India Hackathon problem **SIH26134** — *"Challenges in aligning
skill development programs with industry requirements and emerging job market demands."*

---

## What is new?

Most "skill" platforms are course marketplaces: **User → Search → Course**.

SkillPulse India is a **decision-support data product** for training authorities and
policymakers. It runs the pipeline:

> **Data → Skill extraction (NLP) → Demand & emergence scoring → Supply analysis →
> Skill-gap engine → Evidence-based recommendation → Visualization**

It converts continuously-changing labour-market demand into **district-specific
recommendations** for which skills and training programmes should be **introduced,
expanded, updated, or retired** — and shows the evidence behind every recommendation.

The core innovation, visible in the demo: **the same engine, run on each district's own
labour-market signals, produces a distinct skill-gap profile and a distinct training
plan. No per-district outcome is hard-coded.** Hyderabad's top gaps come out as Python /
Azure / ML / Generative AI; Ludhiana's #1 gap comes out as Welding — because the data
says so, not because anyone wrote that rule.

---

## Screens

- **Home** — India district map coloured by skill-gap index; click a district to preview.
- **District dashboard** — KPIs, demand-vs-supply, largest gaps, emerging skills,
  oversupply, hiring by industry, and ranked recommendations with a **"Why?"** evidence panel.
- **Skill explorer** — transparent demand/supply score breakdown, 12-month demand
  forecast with an uncertainty band, top industries/occupations, and where the skill is
  most in demand.
- **Course intelligence** — every existing course scored for alignment and obsolescence risk.
- **Recommendations** — all evidence-backed actions across districts, filterable.
- **Compare** — side-by-side districts proving different geographies need different plans.
- **Methodology** — every formula and weight, plus limitations and ethics.

---

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Pydantic |
| Database | SQLite by default — **swap `DATABASE_URL` to PostgreSQL with no code changes** |
| Analytics / ML | NumPy, pandas, scikit-learn (TF-IDF), rapidfuzz; optional sentence-transformers |
| Frontend | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS |
| Charts / Map | Recharts, Leaflet + OpenStreetMap tiles |
| Tests | pytest (41 tests) |

> **Why SQLite, not the spec's PostgreSQL + Docker?** The evaluation machine had neither
> installed, so this build uses SQLite (identical SQL semantics for the prototype) to stay
> **runnable and verifiable end-to-end**. The models use portable column types and a
> single `DATABASE_URL`, so moving to PostgreSQL is a config change. A `docker-compose.yml`
> and Dockerfiles are included for that path (see [Docker](#docker)).

---

## Quickstart

Two terminals. Requires Python 3.11+ and Node 18+.

### 1) Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate       macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Build the reproducible synthetic dataset + compute all intelligence
python scripts/generate_demo_data.py

# Run the API  (http://127.0.0.1:8000 ; interactive docs at /docs)
uvicorn app.main:app --reload
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000  (proxies /api/* to the backend)
```

Open **http://localhost:3000**.

### Run the tests

```bash
cd backend
python scripts/generate_demo_data.py   # populates the DB the API tests read
pytest -q                              # 41 passed
```

---

## How it works (one paragraph)

Synthetic job postings are generated per district from that district's economic archetype
(IT hub, manufacturing, agri-services…), so demand is internally consistent. Skills are
**extracted from the posting text** by a deterministic alias-dictionary + TF-IDF pipeline
(no LLM required), aggregated into monthly time-series, and scored for **demand** (six
weighted components) and **emergence** (growth + recency + cross-industry + employer
signal). Training **supply** is scored from local course capacity, completion and
placement. The **gap** is `Demand − Supply`, classified Balanced → Critical. A rule +
scoring **recommendation engine** turns gaps into actions, each carrying machine-readable
evidence. See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for every formula.

---

## Repository layout

```
backend/    FastAPI app, engines, data generator, tests
  app/
    api/        routers (districts, skills, courses, recommendations, analytics, meta)
    services/   engines: extraction, normalization, demand, gap, forecasting,
                recommendation, course intelligence, district scoring, pipeline, generator
    models/     SQLAlchemy models
    data/       skill taxonomy + district gazetteer seeds
    constants.py  all tunable weights & thresholds (asserted to sum to 1.0)
  scripts/generate_demo_data.py   one command rebuilds everything
  tests/      pytest engine + API tests
frontend/   Next.js app (App Router), components, API client
docs/        architecture, methodology, dataset, API, testing, demo script, roadmap
docker/      (compose + Dockerfiles for the PostgreSQL path)
```

---

## Deploy (Vercel + Render)

- **Frontend → Vercel** (Root Directory = `frontend`; set `BACKEND_URL` to the Render URL).
- **Backend → Render** (Docker; the demo dataset is baked into the image, so no database
  add-on is needed). A `render.yaml` blueprint is included.

The frontend proxies `/api/*` to the backend server-to-server (no CORS setup needed).
Full step-by-step: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## Docker

`docker compose up` builds the API (with the demo dataset baked in), a Postgres service, and
the frontend. **The Docker/compose path was written but not run on the build machine (Docker
was not installed there), so treat it as provided-not-verified.** The SQLite quickstart above
is the verified path.

---

## Data honesty

All figures are **synthetic demo data**, generated deterministically for demonstration.
District names and coordinates are real; **all labour statistics are synthetic and are not
official government statistics.** Every screen carries this notice. Recommendations are
decision-support outputs that require human validation before any policy action. The
platform analyses districts, industries, skills and courses — **never individual citizens.**

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Methodology & formulas](docs/METHODOLOGY.md)
- [Dataset](docs/DATASET.md)
- [API reference](docs/API.md)
- [Testing report](docs/TESTING.md)
- [Demo script (3 minutes)](docs/DEMO_SCRIPT.md)
- [Deployment (Vercel + Render)](docs/DEPLOYMENT.md)
- [Limitations & roadmap](docs/LIMITATIONS_AND_ROADMAP.md)

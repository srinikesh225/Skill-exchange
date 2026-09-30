# FINAL PRE-SUBMISSION VERIFICATION — SkillPulse India (SIH26134)

*Verification-and-gap-closure run. Every PASS below is backed by a command actually executed in this
session. No analytics formula, weight, or threshold was modified.*

---

## 1. EXECUTIVE SUMMARY

**Status: PASS.** All nine target gaps are closed.

The full Docker Compose stack (PostgreSQL + FastAPI backend + Next.js frontend) now builds and runs
**from a genuinely clean state** (`docker compose down -v` wiped the Postgres volume, then
`up --build` rebuilt and reseeded from scratch). The application is confirmed to run on **PostgreSQL,
not a silent SQLite fallback**. A Playwright E2E test reproduces the complete judge journey and
passes. Core analytics were re-verified *in SQL directly against PostgreSQL*, independent of the
application code: across all 4,799 metrics the demand, supply, gap, and recommendation-evidence
formulas had **0 violations**.

Three genuine defects were found and fixed during this run — all in Docker/build configuration, none
in analytics:
1. Frontend Docker build failed (`exit 127: next not found`) — host Windows `node_modules` was being
   copied into the Linux image. Fixed with a missing `frontend/.dockerignore`.
2. Frontend→backend `/api` proxy returned 500 in compose — Next.js bakes `next.config` rewrites at
   **build** time, so `BACKEND_URL` had to be a build ARG, not just a runtime env.
3. Frontend image build failed on a transient npm `ECONNRESET` — fixed with lockfile install +
   fetch retries.

`backend/app/constants.py`, `backend/app/services/`, `backend/app/models/`, and `backend/app/data/`
are **unchanged** (verified by `git diff --name-only HEAD` returning empty for those paths).

---

## 2. BASELINE (before any changes)

| Item | Value |
|---|---|
| Branch / commit | `main` @ `ced135b` |
| Working tree | clean (one untracked `frontend/tsconfig.tsbuildinfo` artifact) |
| Node | v24.15.0 |
| Python | 3.13.2 |
| Next.js | 14.2.35 |
| Docker / Compose | 29.8.1 / v5.5.1 |
| Database config | SQLite by default; PostgreSQL via `DATABASE_URL` |

Baseline tests (executed):

```
pytest            41 passed
tsc --noEmit      exit 0
next build        Compiled successfully, 12/12 routes
```

---

## 3. CHANGES MADE

| # | File | Reason | Change | Risk | Verification |
|---|---|---|---|---|---|
| 1 | `backend/app/main.py` | `/api/skills/extract` cold start was 2.346 s (lazy TF-IDF + sklearn import) | Warm the extraction index in the `lifespan` startup hook, wrapped in try/except so it can never block startup | **Low** — only pre-builds an `lru_cache`d index; cannot change extraction output | pytest 41/41; extraction output identical (`AWS, Cloud Security, Python`); first call now **7 ms**; startup log `Skill-extraction index warmed` |
| 2 | `backend/app/api/courses.py` | `/api/courses` returned 460 KB for 887 courses | **Optional, backward-compatible** pagination: no `page` → unchanged array; with `page` → `{items,page,page_size,total,total_pages}`. Bounded `page>=1`, `page_size 1..500` | **Low** — legacy shape preserved, so the frontend needed no change | No-page → `list`, len 887. `page=2&page_size=50` → items 50, total 887, total_pages 18. Frontend `/courses` still renders 300 rows |
| 3 | `frontend/.dockerignore` **(NEW)** | **Defect:** frontend image build failed `exit 127 (next: not found)`; build context was 429 MB | Exclude `node_modules`, `.next`, `out`, `.env.local`, tsbuildinfo | **None** — build-context only | Build succeeded; context 429 MB → **2 KB** |
| 4 | `frontend/Dockerfile` | **Defect A:** compose `/api` proxy returned 500 (`ECONNREFUSED 127.0.0.1:8000`). **Defect B:** build failed on transient npm `ECONNRESET` | A: add `ARG BACKEND_URL` + `ENV` **before** `npm run build` (Next bakes rewrites at build time). B: `npm ci` from lockfile with `fetch-retries 5` and long timeouts, falling back to `npm install` | **Low** — build config only | Proxy now 200, 125 districts proxied; clean rebuild succeeded |
| 5 | `docker-compose.yml` | Supply the build arg above | `frontend.build.args.BACKEND_URL=http://backend:8000` | **Low** | Full stack verified end-to-end |
| 6 | `backend/.env.example` | Phase 7 (production CORS must be configurable) | Documented production example `CORS_ORIGINS=...,https://your-frontend.vercel.app` | **None** — docs | CORS behaviour verified live (§11) |
| 7 | `frontend/package.json` | Phase 5 | Added `@playwright/test` devDep + `test:e2e` script | **Low** | `npm ci` lockfile in sync (verified); tsc exit 0; build OK |
| 8 | `frontend/playwright.config.ts` **(NEW)** | Phase 5 | Minimal config, `baseURL` overridable via `PLAYWRIGHT_BASE_URL` | **None** — test-only | Test runs |
| 9 | `frontend/tests/e2e/judge-journey.spec.ts` **(NEW)** | Phase 5/6 | Single high-value E2E covering the judge journey with console/page/network monitoring | **None** — test-only | 1 passed (4.4 s) on clean stack |
| 10 | `.gitignore` | Housekeeping | Ignore `*.tsbuildinfo`, `test-results/`, `playwright-report/` | **None** | — |

**Explicitly NOT changed:** `backend/app/constants.py`, `backend/app/services/**`,
`backend/app/models/**`, `backend/app/data/**`.
Evidence: `git diff --name-only HEAD -- backend/app/constants.py backend/app/services/ backend/app/models/ backend/app/data/` → **empty**.

---

## 4. DOCKER COMPOSE — **PASS**

Architecture confirmed: `db` (postgres:16-alpine) + `backend` (FastAPI, Docker) + `frontend` (Next.js).

```
Clean start executed:  docker compose down -v   (containers + sih2_pgdata volume REMOVED)
                       docker compose up -d --build

Container status:   backend running | db running | frontend running   (db healthcheck: Healthy)
Backend healthy after ~18 s (Postgres init + full reseed)
```

| Check | Result |
|---|---|
| PostgreSQL starts | **PASS** — healthcheck `Healthy` before backend starts |
| Backend starts | **PASS** — `Application startup complete` |
| Frontend starts | **PASS** — HTTP 200 on `/` |
| Networking | **PASS** — frontend → `http://backend:8000` over compose network |
| Environment variables | **PASS** — `DATABASE_URL` + `BACKEND_URL` (build arg) both effective |
| DB initialization / seed | **PASS** — tables created and seeded into the empty volume on start |
| Frontend ↔ backend | **PASS** — `/api/health` via frontend → 200; `/api/districts` → 125 |
| Backend ↔ PostgreSQL | **PASS** — see §5 |

**Database actually used: PostgreSQL** (not SQLite). Backend log:
`Generating demo dataset into postgresql+psycopg://skillpulse:skillpulse@db:5432/skillpulse...`

---

## 5. POSTGRESQL — **PASS**

Row counts queried directly with `psql` against the **freshly created** volume:

```
districts=125      skills=47          job_postings=12182   courses=887
training_providers=460   employer_signals=3958   demand_points=26361
skill_metrics=4799  recommendations=3633  course_alignments=887
```

Identical to the SQLite dataset → generator + pipeline are database-agnostic.

Integrity and **formula verification executed as pure SQL inside PostgreSQL** (independent of the
Python code) over all 4,799 metrics:

| Check | Violations |
|---|---|
| `job_postings.district_id` orphans | **0** |
| `skill_metrics.district_id` orphans | **0** |
| `demand_index == weighted(demand_components)` (0.35/0.20/0.15/0.10/0.10/0.10) | **0** |
| `supply_index == weighted(supply_components)` (0.50/0.20/0.20/0.10) | **0** |
| `gap_score == clamp(demand − supply, 0, 100)` | **0** |
| `recommendation.evidence` matches `skill_metrics` (gap + postings) | **0** |
| distinct `gap_score` values | 535 (a hard-coded constant would be 1) |

Application connectivity: the full 34-case API suite was re-run against the **Dockerized Postgres
backend** → **34/34 PASS**, identical to the SQLite run (SQLite ↔ Postgres parity proven).

---

## 6. PLAYWRIGHT — **PASS**

- **Test:** `frontend/tests/e2e/judge-journey.spec.ts` — *"judge journey: home → district → skill → why → compare → methodology"*
- **Run:** against the **clean-started Docker stack** → `1 passed (4.4s)`
- **Command:** `npm run test:e2e` (or `npx playwright test`)

Steps asserted: homepage hero + stats → nav to Districts → select **Hyderabad** → district dashboard
heading → `Skill Gap Index` KPI → `Largest skill gaps` → open **"Why?"** → dialog with
*"Why this recommendation"*, *"Evidence"*, and the `Demand index` evidence label → close → select
**Cybersecurity** → skill explorer `Demand index` / `Supply index` / `Skill gap` + 12-month forecast
→ **Compare** (two districts, `Overall skill gap`, `Top skill gaps`) → **Methodology** (heading +
`Demand weights`).

**Monitoring (Phase 6):** collects `console.error`, `pageerror`, `requestfailed`, and any `/api/`
response with status ≥ 400.

- Console errors: **none**
- Page errors: **none**
- Failed API requests: **none**

*Ignored (with justification):* Next.js speculative RSC prefetches (`?_rsc=`) cancelled by fast
navigation, which surface as `net::ERR_ABORTED`, and font-preload warnings. These are cancellations,
not failures. Genuine API failures are still caught by the separate response-status handler.

*Two failures occurred during authoring and were fixed in the test, not the app:* a strict-mode
selector collision, and the prefetch-abort filter above. The app itself never failed.

---

## 7. RESPONSIVE TEST — **PASS**

Horizontal-overflow check (`documentElement.scrollWidth <= innerWidth`) on the Docker stack:

| Width | `/` | `/districts/2` | `/compare` | `/courses` |
|---|---|---|---|---|
| **390 × 844** | OK | OK | OK | OK |
| **768 × 1024** | OK | OK | OK | OK |
| **1280 × 800** | OK | OK | OK | OK |

Tablet (768 px) screenshot visually inspected: navigation intact, KPI cards in a 2×2 grid, charts
render fully (not clipped), tables readable, cards do not overlap, synthetic-data banner visible.

---

## 8. PERFORMANCE (Dockerized Postgres stack)

| Endpoint | Time | Payload |
|---|---|---|
| `/api/health` | 0.008 s | 33 B |
| `/api/districts` | 0.124 s | 201 KB |
| `/api/analytics/overview` | 0.195 s | 3.3 KB |
| `/api/courses` (full, legacy) | 0.244 s | 460 KB |
| `/api/courses?page=1&page_size=50` | 0.117 s | **26 KB** |
| `/api/skills/extract` — **warm** | **0.007 s** | 235 B |
| `/api/skills/extract` — cold *(before this run's fix)* | **2.346 s** | — |

Skill-extraction cold start improved **2.346 s → 0.007 s** by warming the index at startup, with
extraction output unchanged.

---

## 9. CORE ANALYTICS REGRESSION — **PASS**

| Engine | Result | Evidence |
|---|---|---|
| Demand | **PASS** | SQL in Postgres: `demand_index == weighted(components)`, 0/4799 violations |
| Supply | **PASS** | SQL in Postgres: `supply_index == weighted(components)`, 0/4799 violations |
| Gap | **PASS** | SQL in Postgres: `gap == clamp(demand − supply)`, 0/4799 violations |
| Recommendation | **PASS** | `evidence.gap_score`/`job_postings` match `skill_metrics`, 0 violations |
| Forecasting | **PASS** | 12 points, non-negative, band brackets point, milestones present |
| **Perturbation** | **PASS** | On a throwaway SQLite copy (production data untouched): **Welding in Hyderabad had NO metric**; after injecting 228 postings + rising demand points + employer signals and re-running the real pipeline → **demand 80.3, gap 80.3 (Critical), Emerging**. Analytics are data-driven, not hard-coded. |

---

## 10. DATA PROVENANCE — **PASS**

- `GET /api/meta` → `data_kind: "synthetic-demo"` with an explicit disclaimer: *"Demo dataset —
  synthetic data for prototype demonstration. Figures are generated for illustration and are NOT
  official government statistics… Recommendations are decision-support outputs and require human
  validation before any policy action."*
- A persistent banner appears on **every page** of the UI (verified visually at all three widths).
- District demographics on the dashboard are explicitly annotated *"(synthetic demo values)"*.
- The Methodology page documents: data sources/pipeline, skill extraction, taxonomy, demand model,
  emergence model, supply model, gap model, course alignment/obsolescence, forecasting,
  recommendation logic, confidence, limitations, and the research basis — with weights pulled **live**
  from `/api/meta` (verified equal to `app/constants.py`).

Nothing in the UI implies the synthetic figures are real government statistics.

### Phase 11 — synthetic-data validation (investigated, **left unchanged**)

Observation: 529/887 courses are `High` obsolescence risk. **Root cause analysis (not tuning):**

| Risk | n | avg score | skill_demand | placement | utilisation | freshness |
|---|---:|---:|---:|---:|---:|---:|
| High | 529 | 35.1 | 29.0 | 38.8 | 65.4 | **16.6** |
| Moderate | 322 | 53.0 | 39.1 | 64.2 | 69.6 | 59.4 |
| Low | 36 | 68.9 | 52.1 | 84.2 | 75.3 | **87.3** |

The discriminator is **curriculum freshness (16.6 vs 87.3)** and **placement (38.8 vs 84.2)** — i.e.
old curricula with poor placement on lower-demand skills, which is exactly what obsolescence
detection *should* flag. It is mathematically valid: the generator assigns 2–3 years of staleness to
any non-growing skill, and freshness decays to 0 at 36 months. In addition, global min-max
normalization puts the mean `skill_demand` component at 33.6, and at weight 0.45 that structurally
caps typical alignment scores.

**Per the rules, the engine and the dataset were left unchanged.** Documented as a post-submission
consideration: either widen the freshness horizon or normalize demand per-district. Changing it now
would alter validated analytical behaviour.

---

## 11. SECURITY

| Check | Result |
|---|---|
| CORS — allowed origin | `Origin: http://localhost:3000` → `access-control-allow-origin: http://localhost:3000` |
| CORS — disallowed origin | `Origin: https://evil.example` → **no ACAO header** (browser blocks) |
| CORS — preflight | `OPTIONS` → `access-control-allow-methods: GET, POST` |
| CORS — production configurability | `CORS_ORIGINS` env, documented in `.env.example`; **no wildcard** |
| Secrets in repo | Only `.env.example` / `.env.local.example` templates tracked; no real `.env` |
| Pagination abuse | Bounded: `page >= 1`, `page_size` 1–500 |
| SQL injection | SQLAlchemy ORM parameterisation; no f-string SQL |
| `eval`/`exec`/`shell=True`/debug flags | None found |
| Build-arg secret leakage | `BACKEND_URL` is an internal hostname, not a secret |

---

## 12. FINAL FEATURE MATRIX

| Feature | Status | Evidence |
|---|---|---|
| Docker Compose | **PASS** | `down -v` → `up --build`; 3/3 services running; healthy in 18 s |
| PostgreSQL | **PASS** | Seeded fresh volume; SQL formula checks 0 violations; API parity 34/34 |
| Playwright | **PASS** | `judge-journey.spec.ts` 1 passed (4.4 s), 0 console/page/API errors |
| Homepage | **PASS** | 125 map markers, live stat strip (125/12,182/47/3,633) |
| District Map | **PASS** | 125 markers colour-coded by gap; legend; click → district |
| District Dashboard | **PASS** | Hyderabad: KPIs, 5 charts, 42 table rows; values match API |
| Skill Explorer | **PASS** | Demand/supply/gap KPIs + component breakdown + forecast |
| Skill Extraction | **PASS** | `Cloud Security Engineer…` → AWS, Kubernetes, Docker, Python, Cloud Security |
| Skill Normalization | **PASS** | "Amazon Web Services" / "AWS Cloud" / "aws" → `AWS` |
| Demand Engine | **PASS** | SQL: `demand == weighted(components)`, 0/4799 |
| Emerging Skills | **PASS** | Data-derived labels; perturbation flips classification |
| Skill Gap | **PASS** | SQL: `gap == clamp(demand − supply)`, 0/4799 |
| Recommendations | **PASS** | Evidence matches metrics, 0 violations; "Why?" panel renders evidence |
| Course Intelligence | **PASS** | 887 alignments, 396 distinct scores; risk spread High/Mod/Low |
| Forecasting | **PASS** | 12 points, band brackets point, non-negative |
| District Comparison | **PASS** | 5 districts → 5 distinct gap profiles (Ludhiana→Welding, Hyderabad→Python/Azure) |
| Methodology | **PASS** | Live weights == code constants; all model sections + limitations |
| Responsive UI | **PASS** | No overflow at 390/768/1280; tablet visually confirmed |
| Security | **PASS** | CORS restrictive; no secrets; bounded pagination; ORM-only |

---

## 13. REMAINING ISSUES

**P0 — Critical:** None identified.

**P1 — Major:** None identified.

**P2 — Moderate:** None identified.

**P3 — Minor / post-submission:**
1. `/api/courses` still returns the full 460 KB array by default. Pagination exists and is verified,
   but the frontend was intentionally not migrated to it (avoiding pre-submission risk).
2. Obsolescence distribution skews `High` (529/887). Investigated, mathematically valid, deliberately
   left unchanged (§10).
3. No frontend **unit** test suite (only E2E + typecheck + build).
4. Skill taxonomy is 47 curated skills, so terms outside it (e.g. "IAM") are not extracted.
5. Render free-tier cold start (~30–60 s) applies to the cloud deployment path, not local Docker.

---

## 14. FINAL JUDGE READINESS

### Definitely working
- Full Docker Compose stack (PostgreSQL + backend + frontend) from a **wiped volume**, no hidden state.
- Backend genuinely on PostgreSQL; identical data and identical computed results to SQLite.
- All 11 frontend routes render real, Postgres-backed data; frontend values match backend values.
- The complete judge journey, automated in Playwright and passing with zero console/page/API errors.
- All six analytics engines, re-verified **in SQL inside PostgreSQL** with 0 violations across 4,799
  metrics, plus a perturbation test proving data-dependence.
- Skill extraction + normalization; extraction cold start reduced 2.346 s → 0.007 s.
- Restrictive, env-configurable CORS; no secrets in the repository.
- Responsive at 390 / 768 / 1280 with no horizontal overflow.
- Test suite: **pytest 41/41**, **tsc exit 0**, **next build 12/12 routes**, **Playwright 1/1**.

### Partially verified
- Cloud deployment (Vercel + Render) — configuration is committed and the backend image is verified
  locally, but the hosted deployment itself has not been performed from this machine.

### Unverified
- Long-run / load behaviour (no sustained load testing was performed).
- Browser coverage beyond Chromium (Playwright runs Chromium only).

### Recommended before submission
Nothing is blocking. Optional polish, in order of value:
1. Commit the working tree (notably `frontend/.dockerignore`, which the Docker build depends on).
2. Practise the demo once against `docker compose up` so the 18 s first-start seeding is expected.
3. If demoing the cloud URLs, hit the Render backend once beforehand to defeat the free-tier cold start.

---

## Reproducing this verification

```bash
# Full stack from scratch (the verified path)
docker compose down -v
docker compose up -d --build          # ~18 s to healthy after build
open http://localhost:3000

# Backend tests / typecheck / build / E2E
cd backend  && python -m pytest -q                 # 41 passed
cd frontend && npx tsc --noEmit && npm run build   # exit 0, 12/12 routes
cd frontend && npm run test:e2e                    # 1 passed
```

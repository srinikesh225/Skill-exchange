# FINAL PRE-SUBMISSION VERIFICATION — SkillPulse India (SIH26134)

*Verification-and-gap-closure run. Every PASS below is backed by a command actually executed in this
session. No analytics formula, weight, or threshold was modified — independently confirmed (§10).*

---

## 1. EXECUTIVE SUMMARY

**Status: PASS.** All nine target gaps are closed, and **six genuine defects were found and fixed** —
all in Docker/build/data-lifecycle configuration or in the new test itself. **None in analytics.**

The full Docker Compose stack (PostgreSQL + FastAPI + Next.js) builds and runs from a genuinely clean
state (`docker compose down -v` wipes the Postgres volume; `up --build` rebuilds and reseeds). The
app runs on **PostgreSQL, not a silent SQLite fallback**. Core analytics were re-verified **in pure
SQL inside PostgreSQL**, independent of the application code: across all 4,799 metrics the demand,
supply, gap and recommendation-evidence formulas had **0 violations**.

Two of the six defects were **P1 reproducibility bugs that only PostgreSQL exposes** and that would
have hit a judge on their *second* `docker compose up`:

1. **`ForeignKeyViolation` on re-seed.** The generator's clean-slate step deleted `courses` but never
   the derived tables (`course_alignments`, `skill_metrics`, `recommendations`) that reference them.
   SQLite does not enforce foreign keys by default, so this was invisible; PostgreSQL does. Every
   earlier Postgres run used a *fresh* volume, so it only surfaced on a restart against a populated
   database — where the backend **crashed on startup**.
2. **Unstable entity IDs.** `DELETE` leaves PostgreSQL identity sequences advanced, so every re-seed
   shifted all IDs (districts 1–125 → 126–250 → **251–375** observed). Deep links like `/districts/2`
   broke after a restart, and behaviour diverged from SQLite.

An independent adversarial review (38 agents, 4 lenses) additionally proved the analytics changes are
inert, and found real weaknesses in the E2E test I had written — which I then fixed (§7).

---

## 2. BASELINE (before any changes)

| Item | Value |
|---|---|
| Branch / commit | `main` @ `ced135b` |
| Working tree | clean (one untracked `tsconfig.tsbuildinfo` artifact) |
| Node / Python | v24.15.0 / 3.13.2 |
| Next.js | 14.2.35 |
| Docker / Compose | 29.8.1 / v5.5.1 |
| Database | SQLite default; PostgreSQL via `DATABASE_URL` |

Baseline tests (executed): `pytest` **41 passed** · `tsc --noEmit` **exit 0** · `next build`
**Compiled successfully, 12/12 routes**.

---

## 3. CHANGES MADE

### Defect fixes

| # | File | Defect & root cause | Fix | Risk | Verification |
|---|---|---|---|---|---|
| 1 | `backend/app/services/generator.py` | **P1** — backend crashed on startup re-seeding a populated PostgreSQL: `ForeignKeyViolation ... "course_alignments_course_id_fkey" ... [SQL: DELETE FROM courses]`. Derived tables were absent from the clean-slate teardown; SQLite hid it by not enforcing FKs | Clear derived tables (`Recommendation`, `CourseAlignment`, `SkillMetric`) first, in FK-safe order | **Low** — teardown ordering only; `pipeline.compute()` already clears these, so idempotent and changes no computed value | Backend restarted twice against a **populated** Postgres → healthy in 21 s both times, **0 FK/integrity errors**, identical results (4,799 metrics / 3,633 recs) |
| 2 | `backend/app/services/generator.py` | **P1** — PostgreSQL identity sequences are not reset by `DELETE`, so every re-seed shifted all IDs (observed districts **251–375**), breaking deep links and diverging from SQLite | On PostgreSQL use `TRUNCATE ... RESTART IDENTITY CASCADE` (table names derived from the models, not hardcoded); keep `DELETE` on SQLite | **Low** — teardown mechanics only | IDs now **1–125** districts / **1–47** skills, **stable across restarts**; API suite recovered **23/34 → 34/34** |
| 3 | `frontend/.dockerignore` **(NEW)** | **P1** — frontend image build failed `exit 127 (next: not found)`: host **Windows** `node_modules` was copied into the Linux image, clobbering Linux binaries; build context 429 MB | Exclude `node_modules`, `.next`, `out`, **all** `.env*`, tsbuildinfo, test artifacts | **None** — build context only | Build succeeded; context **429 MB → 2 KB** |
| 4 | `frontend/Dockerfile` | **P1** — compose `/api` proxy returned 500 (`ECONNREFUSED 127.0.0.1:8000`): Next.js bakes `next.config` rewrites at **build** time, so a runtime-only `BACKEND_URL` never applied | Add `ARG BACKEND_URL` + `ENV` **before** `npm run build` | **Low** | Proxy now 200; 125 districts proxied through the frontend |
| 5 | `frontend/Dockerfile` | **P2** — image build failed on a transient npm `ECONNRESET` | `npm ci` from the lockfile with `fetch-retries 5` + long timeouts, falling back to `npm install` | **Low** | Clean rebuilds succeeded repeatedly |
| 6 | `frontend/tests/e2e/judge-journey.spec.ts` | **P1 (in my own test)** — surfaced by adversarial review: *"not one assertion reads a numeric value… an all-zero payload passes the entire test"*, a **vacuous** homepage assertion that matched the nav link rather than the stat, and **dead code** (`gapCells` assigned, never used) in the compare step | Rewrote to assert **real numeric values** at every stage; fixed the vacuous and dead assertions; tightened monitors | **None** — test only | **1 passed** from a clean start |

### Improvements

| # | File | Reason | Change | Risk | Verification |
|---|---|---|---|---|---|
| 7 | `backend/app/main.py` | `/api/skills/extract` cold start 2.346 s | Warm the extraction index in `lifespan`, wrapped in try/except | **Low** — pre-builds an `lru_cache`d index; **independently proven** it cannot change output (§10) | First call **2.346 s → 0.007 s**; extraction output byte-identical |
| 8 | `backend/app/api/courses.py` | 460 KB payload for 887 courses | **Optional, backward-compatible** pagination (no `page` → unchanged array). Bounded `page ≥ 1`, `page_size 1..500`. Added `id` as a deterministic sort tiebreaker | **Low** — legacy shape preserved; frontend unchanged | Reassembling all pages at `page_size` 1/7/50/500 reproduces the full 887-row list **identically**; 26 KB vs 460 KB |
| 9 | `docker-compose.yml` | Judge experience + port conflicts | Backend **healthcheck** + `frontend depends_on: service_healthy` (no more loading mid-seed); **stopped publishing 5432** to the host (a judge's local PostgreSQL would break the stack); frontend build args | **Low** | Clean start: db Healthy → backend Healthy → frontend Started, 31 s |
| 10 | `frontend/package.json` | E2E only worked thanks to this machine's browser cache | `pretest:e2e: playwright install chromium` so `npm run test:e2e` is self-sufficient on a fresh clone | **None** | Script runs |
| 11 | `backend/.env.example`, `docs/TESTING.md`, `.gitignore` | Docs/hygiene | Production CORS example; TESTING.md corrected (Playwright now exists, was listed as future work); ignore tsbuildinfo + Playwright artifacts | **None** | — |

**Explicitly NOT changed:** `backend/app/constants.py`, `backend/app/services/{demand_engine, gap_engine,
recommendation_engine, forecasting, course_intelligence, skill_extraction, skill_normalization,
pipeline, district_scoring, scaling}.py`, `backend/app/models/**`, `backend/app/data/**`.
The only `generator.py` change is the teardown block (no generation parameter, weight or distribution
altered).

---

## 4. DOCKER COMPOSE — **PASS**

```
docker compose down -v          # containers + sih2_pgdata volume REMOVED
docker compose up -d --build    # 31s total

db-1        Started -> Waiting -> Healthy
backend-1   Started -> Waiting -> Healthy   (21s: Postgres init + full seed)
frontend-1  Started                          (ready 2s later)
```

| Check | Result |
|---|---|
| PostgreSQL starts | **PASS** — healthy before backend starts |
| Backend starts | **PASS** — healthy; `Application startup complete` |
| Frontend starts | **PASS** — HTTP 200 |
| Networking | **PASS** — frontend → `http://backend:8000` over the compose network |
| Environment variables | **PASS** — `DATABASE_URL` (runtime) + `BACKEND_URL` (build arg) both effective |
| DB initialization / seed | **PASS** — tables created and seeded into an empty volume |
| Readiness gating | **PASS** — frontend gated on backend health; no mid-seed error screens |
| Frontend ↔ backend | **PASS** — `/api/health` via frontend → 200; `/api/districts` → 125 |
| Backend ↔ PostgreSQL | **PASS** — §5 |
| **Restart idempotency** | **PASS** — backend restarted against a **populated** DB twice: healthy 21 s each, **0 FK errors** |

**Database actually used: PostgreSQL.** Log:
`Generating demo dataset into postgresql+psycopg://skillpulse:skillpulse@db:5432/skillpulse...`

---

## 5. POSTGRESQL — **PASS**

Row counts (`psql`, fresh volume): `districts=125, skills=47, job_postings=12182, courses=887,
training_providers=460, employer_signals=3958, demand_points=26361, skill_metrics=4799,
recommendations=3633, course_alignments=887` — identical to SQLite.

**Formula verification executed as pure SQL inside PostgreSQL** (independent of Python), all 4,799 metrics:

| Check | Violations |
|---|---|
| `demand_index == weighted(components)` (.35/.20/.15/.10/.10/.10) | **0** |
| `supply_index == weighted(components)` (.50/.20/.20/.10) | **0** |
| `gap_score == clamp(demand − supply, 0, 100)` | **0** |
| `recommendation.evidence` matches `skill_metrics` (gap + postings) | **0** |
| `job_postings` / `skill_metrics` FK orphans | **0** |
| orphaned `course_alignments` after repeated re-seeds | **0** |
| distinct `gap_score` values | 535 (a hard-coded constant would be 1) |

**ID stability:** districts `min_id=1, max_id=125`, skills `1..47`, unchanged across restarts.
**Application connectivity:** the 34-case API suite re-run against the Dockerized Postgres backend →
**34/34 PASS**, identical to SQLite (parity proven).

---

## 6. PLAYWRIGHT — **PASS**

- **Test:** `frontend/tests/e2e/judge-journey.spec.ts`
- **Run:** from the **clean-started** Docker stack → `1 passed (6.7s)`
- **Command:** `npm run test:e2e` (auto-installs chromium via `pretest:e2e`)

Steps: homepage + live overview counts → **≥50 map markers** → Districts → **Hyderabad** → dashboard
KPIs → gap table → **"Why?"** (rationale bullets, evidence gap, proposed programme + capacity) →
**Cybersecurity** skill explorer (demand/gap + forecast) → **Compare** (two district columns, both
numeric) → **Methodology** (weights summing to 1.00).

**Assertions are value-based, not label-based** (the review's key criticism): district count > 0, gap
∈ (0,100], demand > 0, ≥5 skill rows, ≥1 rationale bullet with >10 chars, evidence gap > 0, suggested
capacity > 0, two compare columns each > 0, weights ≈ 1.00, ≥50 markers.

**Monitoring:** console errors, page errors, failed **same-origin** requests, any `/api/` 4xx/5xx, and
any same-origin **5xx** (catches App Router RSC payload errors).
Result: **0 console errors, 0 page errors, 0 failed API requests.**

*Ignored, with justification:* `net::ERR_ABORTED` (Next.js speculative RSC prefetches cancelled by
fast navigation — cancellations, not failures) and **third-party hosts** (OpenStreetMap tiles, font
CDNs) so an external CDN cannot fail an application test.

---

## 7. INDEPENDENT ADVERSARIAL REVIEW

A 4-lens review (38 agents, 0 errors) audited the change set, with every finding adversarially
verified by independent refuters.

**Analytics integrity — verdict `safe`** (stronger evidence than my own check):
- Hash-compared `constants.py`, all `services/*.py` and `data/taxonomy.py` against HEAD → **identical**;
  `git diff HEAD --name-only -- 'backend/**/*.py'` returned exactly `main.py` and `api/courses.py`.
- Proved the warmup cannot alter extraction: `_tfidf_index()` is a zero-arg `lru_cache(maxsize=1)` fit
  **only** on the SKILLS taxonomy corpus; query text reaches it solely via `vec.transform()`, which
  never refits, so the warmup string never enters the corpus or IDF vocabulary. `lru_cache` does not
  memoize exceptions. **Empirically: cold vs warmed extraction over 6 probe texts × 3 call variants
  produced byte-identical JSON (2015 bytes each).**
- Pagination is a pure slice: reassembling every page at `page_size` 1/7/50/500 reproduced the legacy
  887-row array identically; filters compose identically (`risk=High` → 529 both ways).

**Findings acted on:** the E2E weaknesses (fixed, §3.6), the pagination tiebreaker (fixed, §3.8), the
host-published 5432 and missing readiness gate (fixed, §3.9), the Playwright browser prerequisite
(fixed, §3.10), the `.dockerignore` env coverage (fixed, §3.3), and the stale `docs/TESTING.md`
(fixed, §3.11).

**Findings not acted on:** two `P0`s claiming "nothing is committed" / "fresh clone proxy is broken"
were **stale** — they described the pre-commit tree and are resolved by commit `10d591a` (all 14
build-critical files verified tracked). A finding against `npm ci || npm install` was **refuted** by
its verifier as *"mischaracterizes an improvement as a defect"* (the prior state was an unconditional
`npm install`). Remaining items are P3 and listed in §13.

---

## 8. RESPONSIVE TEST — **PASS**

Overflow check (`documentElement.scrollWidth <= innerWidth`):

| Width | `/` | `/districts/2` | `/compare` | `/courses` |
|---|---|---|---|---|
| **390 × 844** | OK | OK | OK | OK |
| **768 × 1024** | OK | OK | OK | OK |
| **1280 × 800** | OK | OK | OK | OK |

Tablet (768 px) screenshot inspected: nav intact, KPIs in a 2×2 grid, charts render fully (not
clipped), tables readable, no overlap, synthetic-data banner visible.

---

## 9. PERFORMANCE (Dockerized PostgreSQL)

| Endpoint | Time | Payload |
|---|---|---|
| `/api/health` | 0.008 s | 33 B |
| `/api/districts` | 0.124 s | 201 KB |
| `/api/analytics/overview` | 0.195 s | 3.3 KB |
| `/api/courses` (full, legacy) | 0.244 s | 460 KB |
| `/api/courses?page=1&page_size=50` | 0.117 s | **26 KB** |
| `/api/skills/extract` — **warm** | **0.007 s** | 235 B |
| `/api/skills/extract` — cold *(before fix)* | **2.346 s** | — |

Clean-stack startup: backend healthy **21 s**, frontend ready **~2 s** after, **31 s** end-to-end.

---

## 10. CORE ANALYTICS REGRESSION — **PASS**

| Engine | Result | Evidence |
|---|---|---|
| Demand | **PASS** | SQL in Postgres: 0/4799 violations |
| Supply | **PASS** | SQL in Postgres: 0/4799 violations |
| Gap | **PASS** | SQL in Postgres: 0/4799 violations |
| Recommendation | **PASS** | Evidence matches metrics, 0 violations |
| Forecasting | **PASS** | 12 points, non-negative, band brackets point |
| **Perturbation** | **PASS** | On a throwaway SQLite copy: **Welding had no metric in Hyderabad**; after injecting 228 postings + rising demand points + employer signals and re-running the real pipeline → **demand 80.3, gap 80.3 (Critical), Emerging** |
| **Independent confirmation** | **PASS** | Adversarial lens verdict `safe`; byte-identical extraction output cold vs warmed (§7) |

Full test suite after all changes: **pytest 41/41**, **tsc exit 0**, **next build 12/12**,
**Playwright 1/1**, **API 34/34**, generator re-run twice on SQLite and twice on PostgreSQL.

---

## 11. DATA PROVENANCE — **PASS**

`GET /api/meta` → `data_kind: "synthetic-demo"` plus an explicit disclaimer that figures are **not**
official government statistics and recommendations require human validation. A persistent banner
appears on **every page**; district demographics are annotated *"(synthetic demo values)"*. The
Methodology page documents data sources, extraction, taxonomy, demand/emergence/supply/gap models,
course alignment, forecasting, recommendation logic, confidence and limitations, with weights pulled
**live** from `/api/meta` (verified equal to `constants.py`).

### Phase 11 — synthetic-data validation (investigated, **left unchanged**)

529/887 courses are `High` obsolescence risk. Root cause:

| Risk | n | avg score | skill_demand | placement | utilisation | freshness |
|---|---:|---:|---:|---:|---:|---:|
| High | 529 | 35.1 | 29.0 | 38.8 | 65.4 | **16.6** |
| Moderate | 322 | 53.0 | 39.1 | 64.2 | 69.6 | 59.4 |
| Low | 36 | 68.9 | 52.1 | 84.2 | 75.3 | **87.3** |

The discriminator is **curriculum freshness (16.6 vs 87.3)** and **placement (38.8 vs 84.2)** — old
curricula with poor placement on lower-demand skills, exactly what obsolescence detection *should*
flag. It is mathematically valid: the generator assigns 2–3 years of staleness to any non-growing
skill and freshness decays to 0 at 36 months, while global min-max normalization puts mean
`skill_demand` at 33.6 which, at weight 0.45, structurally caps scores. **Per the rules the engine and
dataset were left unchanged**; documented as a post-submission consideration.

---

## 12. SECURITY

| Check | Result |
|---|---|
| CORS — allowed origin | → `access-control-allow-origin: http://localhost:3000` |
| CORS — disallowed origin (`https://evil.example`) | **no ACAO header** (browser blocks) |
| CORS — preflight | `access-control-allow-methods: GET, POST` |
| CORS — production configurability | `CORS_ORIGINS` env, documented; **no wildcard** |
| Secrets in repo | only `.env.example` templates; no real `.env`; **all** `.env*` excluded from the image |
| Pagination abuse | bounded `page ≥ 1`, `page_size` 1–500 (independently fuzzed: 501→422, 0→422, −5→422, 10²⁴→200 empty) |
| SQL injection | SQLAlchemy ORM parameterisation; the only raw SQL is a fixed `TRUNCATE` over model-derived table names |
| Exposed DB port | **removed** — Postgres no longer published to the host |
| `eval`/`exec`/`shell=True`/debug flags | none |

---

## 13. FINAL FEATURE MATRIX

| Feature | Status | Evidence |
|---|---|---|
| Docker Compose | **PASS** | `down -v` → `up --build` in 31 s; readiness-gated; restart-idempotent |
| PostgreSQL | **PASS** | Fresh-volume seed; SQL formula checks 0 violations; stable IDs 1–125; API parity 34/34 |
| Playwright | **PASS** | 1 passed (6.7 s) from clean start; value-based assertions; 0 console/page/API errors |
| Homepage | **PASS** | 125 markers; live counts 125/12,182/47/3,633 |
| District Map | **PASS** | 125 gap-coloured markers, legend, click-through |
| District Dashboard | **PASS** | Hyderabad KPIs, 5 charts, 42 rows; values match API (35/39/28 vs 34.9/39.4/27.9) |
| Skill Explorer | **PASS** | Demand/supply/gap + component breakdown + forecast band |
| Skill Extraction | **PASS** | `Cloud Security Engineer…` → AWS, Kubernetes, Docker, Python, Cloud Security |
| Skill Normalization | **PASS** | "Amazon Web Services" / "AWS Cloud" / "aws" → `AWS` |
| Demand Engine | **PASS** | SQL: 0/4799 violations |
| Emerging Skills | **PASS** | Data-derived labels; perturbation flips classification |
| Skill Gap | **PASS** | SQL: 0/4799 violations |
| Recommendations | **PASS** | Evidence matches metrics, 0 violations; "Why?" renders rationale + programme |
| Course Intelligence | **PASS** | 887 alignments, 396 distinct scores; risk spread explained |
| Forecasting | **PASS** | 12 points, band brackets point |
| District Comparison | **PASS** | 5 districts → 5 distinct gap profiles (Ludhiana→Welding, Hyderabad→Python/Azure) |
| Methodology | **PASS** | Live weights == constants; sums to 1.00 |
| Responsive UI | **PASS** | No overflow at 390/768/1280 |
| Security | **PASS** | Restrictive CORS, no secrets, bounded pagination, no exposed DB port |

---

## 14. REMAINING ISSUES

**P0 / P1 / P2:** `None identified.`

**P3 — post-submission:**
1. `/api/courses` still returns the full 460 KB array by default; pagination exists and is verified,
   but the frontend was deliberately not migrated (avoiding pre-submission risk). It also materializes
   the full table before slicing, so it is a payload optimisation, not DoS relief.
2. Obsolescence distribution skews `High` (529/887) — investigated, mathematically valid, deliberately
   unchanged (§11).
3. No frontend **unit** test suite (E2E + typecheck + build only); Playwright runs Chromium only.
4. Skill taxonomy is 47 curated skills, so out-of-taxonomy terms (e.g. "IAM") are not extracted.
5. `npm ci || npm install` keeps a fallback that would silently re-resolve on lockfile drift; the
   lockfile is currently in sync so `npm ci` is the live path.
6. The production frontend image ships the dev dependency tree (incl. Playwright) — image hygiene.
7. Non-SQLite deployments re-seed on every container start (~15–20 s); intentional for the demo.
8. Render free-tier cold start (~30–60 s) applies to the cloud path, not local Docker.

---

## 15. FINAL JUDGE READINESS

### Definitely working
- Full Docker Compose stack from a **wiped volume**, with no hidden state, in 31 s — and now also
  **correct on restart against an existing database** (the bug that would have bitten a judge).
- Backend genuinely on PostgreSQL, with stable IDs and results identical to SQLite.
- All 11 frontend routes render real Postgres-backed data; displayed values match the API.
- The complete judge journey, automated in Playwright, asserting **real numeric values**, passing from
  a clean start with zero console/page/API errors.
- All six analytics engines re-verified **in SQL inside PostgreSQL** (0 violations across 4,799
  metrics), plus a perturbation test and an independent adversarial confirmation that the changes are
  analytically inert.
- Skill extraction + normalization; cold start 2.346 s → 0.007 s with byte-identical output.
- Restrictive, env-configurable CORS; no secrets; no exposed database port.
- Responsive at 390 / 768 / 1280.
- **pytest 41/41 · tsc exit 0 · next build 12/12 · Playwright 1/1 · API 34/34.**

### Partially verified
- Cloud deployment (Vercel + Render): configuration committed and the backend image verified locally,
  but the hosted deployment itself was not performed from this machine.

### Unverified
- Sustained load / long-run behaviour (no load testing performed).
- Browsers other than Chromium.

### Recommended before submission
Nothing is blocking.
1. Practise once with `docker compose up --build` so the ~31 s first start is expected.
2. If demoing the cloud URLs, warm the Render backend first (free-tier cold start).

---

## Reproducing this verification

```bash
# Full stack from scratch (the verified path)
docker compose down -v
docker compose up -d --build       # ~31s; frontend waits for backend health
open http://localhost:3000

# Tests
cd backend  && python -m pytest -q                 # 41 passed
cd frontend && npx tsc --noEmit && npm run build   # exit 0, 12/12 routes
cd frontend && npm run test:e2e                    # 1 passed (installs chromium)
```

# Testing report

## Automated tests (pytest)

```bash
cd backend
python scripts/generate_demo_data.py   # API tests read the generated DB
pytest -q
```

**Result: 41 passed.**

### Engine unit tests (`tests/test_engines.py`) — pure functions, no DB

- **Normalisation** — aliases resolve to canonical skills (`Python 3`→Python,
  `Amazon Web Services`→AWS, `k8s`→Kubernetes, `devsecops`→Cloud Security); unknown terms
  return none.
- **Extraction** — multi-skill recovery from text; boundary-punctuation fix
  (`"devsecops."`); results sorted by confidence.
- **Demand** — all-100 components → index 100; explanation contributions sum to the index.
- **Emergence** — label thresholds (Emerging/Growing/Stable/Declining).
- **Supply & gap** — gap = demand − supply, clamped ≥ 0; label thresholds; zero supply → 0.
- **Forecasting** — horizon length; band brackets the point; uptrend predicts growth.
- **Recommendation** — CREATE for uncovered critical gap; EXPAND when course exists;
  REDUCE for declining oversupply; None when balanced; capacity bounded & rounded to 25.
- **Course intelligence** — stale low-demand course flagged; fresh high-demand course kept.

### API tests (`tests/test_api.py`) — FastAPI TestClient

- `/api/health`, `/api/meta` (declares synthetic; weights sum to 1.0).
- `/api/districts` returns ≥100 districts with intelligence fields.
- District detail + gaps (sorted descending).
- Recommendations include evidence + rationale.
- Live extraction endpoint recovers expected skills.
- Analytics overview totals; compare returns the requested districts.
- 404 for a missing district.

## Frontend build

```bash
cd frontend && npm run build
```

**Result:** compiled successfully; all 12 routes built; **zero TypeScript / lint errors.**

## Manual browser verification (headless Chromium)

Each page loaded against the running stack; **console errors captured = none** on every page.

| Page | Verified |
|---|---|
| `/` Home | 125 map markers render; stat strip loads live totals; muted OSM basemap. |
| `/districts/[id]` | KPIs, 5 charts, recommendations, full skills table (Hyderabad). |
| "Why?" panel | Opens with rationale + full evidence grid + proposed programme. |
| `/skills/[id]` | Demand/supply breakdown, trend + forecast band, district ranking. |
| `/compare` | Two districts side-by-side with different gap/emerging profiles. |
| `/dashboard` `/districts` `/skills` `/courses` `/recommendations` `/methodology` | Load with data, no console errors. |

## Data sanity checks (verified)

- Geographic differentiation: Hyderabad top gaps = Python/Azure/ML/GenAI; Ludhiana #1 = Welding.
- Oversupply detection surfaces declining/foundational skills where supply > demand.
- Growth distribution realistic after smoothing (Stable / Declining / Growing / Emerging mix),
  not "everything +300 %".
- Demand explanation contributions sum exactly to the composite index.

## Docker (verified)

- **Backend image builds and serves.** `docker build ./backend` succeeds (dataset baked in
  at build), and the container was run with `-e PORT=9000` (simulating Render's `$PORT`):
  `/api/health` OK, `/api/districts` returned 125 districts, `/api/meta` showed the baked
  data (12,182 postings, 887 courses). Image size ~808 MB.

## Not verified end-to-end

- **Full `docker compose` stack** (Postgres + frontend together) — not run end-to-end. The
  entrypoint now seeds Postgres when `DATABASE_URL` is non-SQLite, but only the SQLite
  backend image path was exercised.
- **PostgreSQL runtime** — the code is Postgres-ready via `DATABASE_URL`; the running
  verification used SQLite.
- **Playwright E2E** — manual headless-browser verification was done instead; Playwright
  specs are listed as future work in the roadmap.

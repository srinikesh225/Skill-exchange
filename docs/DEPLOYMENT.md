# Deployment — Vercel (frontend) + Render (backend)

The frontend deploys to **Vercel**; the FastAPI backend deploys to **Render** using the
Docker image (the demo SQLite dataset is baked into the image at build time, so no database
add-on is required). Deploy the **backend first**, then point the frontend at it.

> The steps below are performed in your own Vercel and Render accounts — they can't be run
> from this machine. Everything in the repo (Dockerfile, `render.yaml`, `next.config.mjs`
> proxy) is already configured for this setup.

---

## 1) Backend on Render

**Option A — Blueprint (uses `render.yaml`, one step):**
1. Push this repo to GitHub (already done).
2. Render dashboard → **New +** → **Blueprint** → connect the `Skill-exchange` repo.
3. Render reads `render.yaml` and creates a Docker web service **skillpulse-api** on the
   free plan. Click **Apply**.
4. Wait for the build (it runs `generate_demo_data.py` during the image build). When live,
   note the URL, e.g. `https://skillpulse-api.onrender.com`.
5. Verify: open `https://skillpulse-api.onrender.com/api/health` → `{"status":"ok"}`.

**Option B — Manual:**
1. Render → **New +** → **Web Service** → connect the repo.
2. Set **Root Directory** = `backend`, **Runtime** = **Docker**, **Plan** = Free.
3. Set **Health Check Path** = `/api/health`. Create the service.

Notes:
- Render injects `$PORT`; the container binds to it automatically.
- Free tier **spins down after ~15 min idle**; the first request afterwards cold-starts
  the container (~30–60 s). Fine for a demo; upgrade the plan to keep it warm.

---

## 2) Frontend on Vercel

1. Vercel dashboard → **Add New… → Project** → import the `Skill-exchange` repo.
2. **Root Directory** = `frontend` (important — the repo root has both apps).
3. Framework preset auto-detects **Next.js**. Leave build/output defaults.
4. **Environment Variables** → add:
   - `BACKEND_URL` = `https://skillpulse-api.onrender.com` (your Render URL, no trailing slash)
5. **Deploy.**

How it connects: `next.config.mjs` rewrites `/api/*` to `BACKEND_URL`, so the browser only
ever calls the Vercel domain and Vercel proxies to Render **server-to-server** — no CORS
setup needed, and the backend URL isn't exposed to the browser.

> `BACKEND_URL` is read at **build time**. If you add or change it after the first deploy,
> trigger a **Redeploy** so the rewrite picks it up.

---

## 3) (Optional) Direct browser calls instead of the proxy

If you prefer the browser to call Render directly (skipping the Vercel proxy):
- On Vercel set `NEXT_PUBLIC_API_BASE` = your Render URL, and
- On Render set `CORS_ORIGINS` = your Vercel URL (e.g. `https://skill-exchange.vercel.app`).

The proxy approach (section 2) is simpler and recommended.

---

## 4) Verify the live deployment

- `https://<your-app>.vercel.app/` → map renders with district markers.
- Open a district → dashboard loads with charts and recommendations.
- `https://<your-app>.vercel.app/api/health` → proxied `{"status":"ok"}`.

If the first load errors, the Render free instance is likely cold-starting — retry in ~30 s.

---

## Alternatives

- **Railway / Fly.io** instead of Render: same Docker image, same result. Fly needs a
  `fly.toml`; Railway auto-detects the Dockerfile. Bind to `$PORT` (already handled).
- **Both fully on Vercel**: possible only by prebuilding a read-only SQLite into a Python
  serverless function and watching the 250 MB bundle limit; less reliable than the above.
- **PostgreSQL**: set `DATABASE_URL=postgresql+psycopg://…` on the backend service and add
  a Postgres instance; the code and Dockerfile already support it (`psycopg` is installed).

# Deploy SkillBridge to Render (single Web Service)

One Render Web Service serves both the FastAPI backend and the built React SPA
from a single uvicorn process. `backend/app/main.py` already mounts
`frontend/dist` as static files and falls back to `index.html` for SPA deep
links, so there is **no separate frontend service** and no split.

## One-time setup

1. Sign in at https://dashboard.render.com (GitHub login).
2. **New → Web Service**.
3. Connect the repo `aboodko1/SkillBridge-upgrade` and select the branch you
   deploy (normally `main`).
4. Leave the defaults and paste:
   - **Build command:** `bash scripts/render-build.sh`
   - **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health check path:** `/healthz`
5. Under **Environment**, set these by hand (never commit values):
   - `OPENAI_API_KEY` — the real key
   - `SKILLBRIDGE_OPENAI_MODEL` — e.g. `gpt-4.1-mini`
   - `PYTHON_VERSION=3.12.0`, `NODE_VERSION=20.0.0`
   - Any other secrets the backend reads (JWT/secret keys as the app expects).
6. **Create Web Service** → wait for the build.

A `render.yaml` with the same shape (secrets set to `sync: false`) is committed
at the repo root, so an alternative is to create the service from that file and
fill the dashboard secrets once.

## Important: the free tier resets data

- Render's free instance disk is **ephemeral**: the SQLite database is wiped on
  every restart, redeploy, and after idle spin-down.
- On cold start the app seeds a demo database **idempotently** (demo students,
  catalog roles, countries/cities/universities) so the demo survives — but **no
  data created during a live session persists**. Do not rely on data entered
  during judging.
- Never commit `*.db` or `.env`.

## Cold start

- Free services sleep after ~15 minutes idle. The first request after that
  wakes the service (~50 s). **Warm the URL 10 minutes before any judge slot**
  and again on the evening of submission day.

## Logs, redeploy, env vars

- **Logs:** service → **Logs** tab.
- **Env vars:** service → **Environment** → **Add Environment Variable** →
  save → **Manual Deploy → Deploy latest commit** (env changes need a redeploy
  to take effect).
- **Redeploy:** **Manual Deploy → Deploy latest commit** (re-runs the build and
  the idempotent seed).
- **Health:** `GET /healthz` returns `{"status":"ok"}` with no auth — Render
  uses it to mark the service live.

## Verify after deploy

```
curl -I https://<your-service>.onrender.com/          # 200 SPA HTML
curl -I https://<your-service>.onrender.com/dashboard # 200 SPA HTML (deep link)
curl    https://<your-service>.onrender.com/healthz   # {"status":"ok"}
curl    https://<your-service>.onrender.com/api/locations  # non-empty countries
```

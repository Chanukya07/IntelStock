# Deploying IntelStock

## Why Render (and not Vercel)

Short version: **Vercel cannot run Streamlit.**

Streamlit is a stateful server — it holds an open WebSocket per session and
re-runs your script on every interaction. Vercel runs stateless serverless
functions with no persistent process. There is no adapter that bridges this;
deploying to Vercel requires rewriting the entire UI in React/Next.js.

Two further constraints ruled it out for this app (verified August 2026):

| Constraint | Impact |
|---|---|
| Hobby cron runs **once per day** max; more frequent expressions fail at deploy | A price-alert product that checks daily is not a price-alert product |
| Ephemeral filesystem, no long-lived process | The FAISS index and the in-process scheduler cannot survive |

Render, by contrast, runs the app **exactly as it exists today** — no rewrite —
and is the only major platform still offering a real free tier.

> A Next.js frontend on Vercel talking to this API on Render remains a good
> future step. See "Later: splitting the frontend" at the end.

---

## Architecture on Render

One web service runs both processes, because Render's free tier grants
750 instance-hours/month — enough for one continuously-running service
(~720h), not two.

```
┌─────────────── Render Web Service (free) ───────────────┐
│  start.sh                                                │
│    ├── uvicorn  → 127.0.0.1:8000   (loopback only)      │
│    └── streamlit → 0.0.0.0:$PORT   (public)             │
└──────────────────────────┬───────────────────────────────┘
                           │ DATABASE_URL
                  ┌────────▼─────────┐
                  │ Render Postgres  │  (free plan)
                  └──────────────────┘

  GitHub Actions (every 10 min)
      → GET  /api/v1/cron/ping           wakes a spun-down service
      → POST /api/v1/cron/check-alerts   Bearer $CRON_SECRET
```

### Why external cron when Render runs a persistent process

The in-process scheduler (`backend/tasks/scheduler.py`) *does* work on Render.
But the **free tier spins the service down after ~15 minutes of inactivity**,
which stops that loop. The GitHub Actions ping does double duty: it wakes the
service and triggers the alert check.

On a paid Render instance (no spin-down), you can drop the GitHub workflow
entirely — the in-process scheduler covers it.

---

## Deploy steps

### 1. Push to GitHub

Render deploys from a repository. `render.yaml` at the repo root is detected
automatically as a Blueprint.

### 2. Create the Blueprint on Render

1. Render Dashboard → **New** → **Blueprint**
2. Connect the repository and select the branch
3. Render reads `render.yaml` and provisions the web service **and** the
   Postgres database together
4. `DATABASE_URL` and `CRON_SECRET` are wired automatically

### 3. Set the one manual secret

In the service's **Environment** tab, set:

| Variable | Value |
|---|---|
| `OPENROUTER_API_KEY` | Your key from <https://openrouter.ai> |

It is marked `sync: false` in `render.yaml`, so it is never committed to git.

Without it the app still runs — sentiment falls back to keyword scoring and
the AI chat reports the missing key — but LLM features are disabled.

### 4. Wire up the scheduler

Copy the generated `CRON_SECRET` from Render's Environment tab, then in
**GitHub → Settings → Secrets and variables → Actions** add:

| Secret | Value |
|---|---|
| `INTELSTOCK_URL` | `https://<your-service>.onrender.com` (no trailing slash) |
| `CRON_SECRET` | Must match Render's value exactly |

Verify with **Actions → Alert Cron → Run workflow**.

---

## Verifying the deploy

```bash
# Frontend (Streamlit's own health endpoint — what Render polls)
curl -sf https://<service>.onrender.com/_stcore/health

# Cron keep-warm probe (unauthenticated by design)
curl -s https://<service>.onrender.com/api/v1/cron/ping
# → {"status":"awake"}

# Alert check (should 401 without credentials)
curl -s -o /dev/null -w '%{http_code}\n' \
  -X POST https://<service>.onrender.com/api/v1/cron/check-alerts
# → 401

# Alert check with credentials
curl -s -X POST \
  -H "Authorization: Bearer $CRON_SECRET" \
  https://<service>.onrender.com/api/v1/cron/check-alerts
# → {"status":"ok","job":"check-alerts"}
```

The FastAPI app is bound to loopback and is **not** publicly reachable except
through the paths above, which the Streamlit process proxies internally.

---

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./intelstock.db` | Auto-injected by Render. `postgres://` URLs are normalised to `postgresql+psycopg2://` (SQLAlchemy 2.x dropped the bare alias) |
| `OPENROUTER_API_KEY` | *(empty)* | LLM features; app degrades gracefully without it |
| `LLM_MODEL` | `openai/gpt-4o-mini` | Model routed via OpenRouter |
| `CRON_SECRET` | *(generated)* | Bearer token for `/api/v1/cron/*`. **Endpoints fail closed (503) if unset** |
| `INTELSTOCK_API_BASE` | `http://127.0.0.1:8000` | Where the Streamlit pages reach the API |
| `BACKEND_PORT` | `8000` | Internal uvicorn port |
| `PORT` | `8501` | Public port — set by Render |
| `ENABLE_SCHEDULER` | `true` | Set `false` when an external scheduler drives cron, to avoid running jobs twice |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Known free-tier behaviour

- **Cold starts (~1 min).** The service sleeps after 15 min idle. The first
  request wakes it. The cron ping keeps it warm during active hours.
- **GitHub Actions scheduling is best-effort.** Minimum interval is 5 minutes
  and runs may be delayed under load — do not treat alerts as real-time.
  Scheduled workflows are also auto-disabled after 60 days of repo inactivity.
- **Postgres free plans expire.** Check Render's current retention policy and
  back up anything you care about.
- **No `sentence-transformers`/`torch` in the deployed image** — they are
  multi-GB. RAG degrades to no-context retrieval, which
  `backend/rag/embeddings.py` already handles by returning zero vectors
  rather than crashing.

---

## Later: splitting the frontend to Vercel

When you want the Next.js frontend on Vercel:

1. Split this into two Render services (or move the API to a paid instance):
   the API becomes publicly routable instead of loopback-only.
2. Set `INTELSTOCK_API_BASE` in Vercel to the public Render API URL.
3. Add CORS middleware to the FastAPI app for the Vercel origin — currently
   unnecessary because both processes share a container.
4. Keep the GitHub Actions cron exactly as-is; only `INTELSTOCK_URL` changes.

Nothing in this setup blocks that migration — scheduling is already decoupled
from hosting, and the API base is already an environment variable.

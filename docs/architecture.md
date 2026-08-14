# IntelStock Architecture

Everything below describes code that exists in this repository today. Anything
aspirational lives under "Planned / not yet implemented" at the bottom.

## Tech Stack

| Layer | What is actually used |
|---|---|
| Frontend | Streamlit (multi-page, hand-written CSS), Plotly |
| Backend | FastAPI, Uvicorn, Pydantic v2 |
| Market data | yfinance, with a deterministic offline fallback (`backend/services/market_data_service.py`) |
| News | Static curated research-brief feed (`NEWS_FEED` in `backend/services/news_intelligence_service.py`) |
| Sentiment | OpenRouter LLM scoring with a keyword-scoring fallback (`POSITIVE_TERMS`/`NEGATIVE_TERMS`) |
| AI / LLM | OpenRouter via the OpenAI SDK (`backend/config.py`), lazily initialised |
| RAG | sentence-transformers embeddings (lazy, zero-vector fallback) + FAISS, files under `vectorstore/` |
| ORM / DB | SQLAlchemy 2.0; SQLite by default, PostgreSQL in production |
| Scheduling | In-process `asyncio` loop (`backend/tasks/scheduler.py`, 15-minute interval) plus a GitHub Actions cron that drives `/api/v1/cron/*` when the host is asleep |
| Tests | pytest + FastAPI `TestClient` |
| Deployment | Render Blueprint (`render.yaml` + `start.sh`), Docker / Docker Compose, GitHub Actions |

No LangChain, no Celery/Redis, no APScheduler, no transformers/FinBERT/NLTK/spaCy,
and no multi-provider LLM abstraction: OpenRouter is the only provider, reached
through the OpenAI-compatible client.

## Process Layout

```
FastAPI (backend/main.py)          Streamlit (frontend/dashboard.py)
  ├── backend/api/routes.py            ├── frontend/pages/*.py
  ├── backend/api/advanced_routes.py   ├── frontend/charts/price_chart.py
  ├── backend/api/cron_routes.py       └── frontend/api_config.py -> HTTP
  ├── backend/services/*                     (INTELSTOCK_API_BASE)
  ├── backend/rag/*  -> vectorstore/
  ├── backend/database/* -> SQLite / PostgreSQL
  └── backend/tasks/scheduler.py (asyncio loop, started in lifespan)
```

The two processes are separate, but the coupling is mixed: the Alerts and Portfolio
pages call the API over HTTP (`frontend/api_config.py`, `INTELSTOCK_API_BASE`),
while Dashboard, Overview, Stock Research and AI Chat import the backend services
and call them in-process. Only the HTTP pages break when the API is not running.

## Degradation Model

Every external dependency is optional, and the app must boot without any of them:

- **No network** — `MarketDataService` falls back to the built-in `MARKET_PROFILES`
  snapshot instead of yfinance.
- **No `OPENROUTER_API_KEY`** — LLM clients are never constructed; sentiment uses
  keyword scoring and chat/insights return grounded fallback text built from
  quotes, news and RAG context.
- **No `sentence-transformers`/`torch`** — `EmbeddingService` records the load
  failure once and returns zero vectors, so RAG retrieval yields no context
  rather than raising.

## Request Workflow (research / chat)

1. Validate input (`backend/api/validators.py`).
2. Fetch the quote (yfinance, TTL-cached, fallback profile on failure).
3. Pull curated headlines for the symbol.
4. Score sentiment (LLM call when a key is configured, keyword pass otherwise).
5. Retrieve RAG context: chunk -> embed -> FAISS search over `vectorstore/`.
6. Build the prompt from quote + news + sentiment + retrieved context.
7. Generate the recommendation/risk summary, or emit the deterministic fallback.
8. Persist chat turns via `ChatRepository`.

## Background Jobs

`run_background_tasks()` loops every `REFRESH_INTERVAL_SECONDS` (900) and runs
four jobs concurrently: `refresh_market_data`, `warm_up_sentiment_cache`,
`refresh_rag_index`, `check_price_alerts`.

The same jobs are exposed as authenticated HTTP endpoints under
`/api/v1/cron/*` so an external scheduler can drive them when the in-process
loop cannot run (free-tier spin-down, serverless hosts). Set
`ENABLE_SCHEDULER=false` in that case so the jobs do not run twice. See
[DEPLOYMENT.md](DEPLOYMENT.md).

## Database Tables

Defined in `backend/database/models.py`, mirrored by `backend/database/schema.sql`:

- `users`
- `stocks`
- `historical_prices`
- `news`
- `sentiment_scores`
- `watchlists`
- `insights`
- `chat_history`
- `portfolios`
- `alerts`

`postgres://` / `postgresql://` URLs are rewritten to `postgresql+psycopg2://`
in `backend/database/session.py`, because SQLAlchemy 2.x rejects the bare alias.

## Planned / not yet implemented

None of the following exists in the codebase; do not go looking for it.

- Multi-source live news aggregation (NewsAPI / GNews / RSS) replacing the
  curated `NEWS_FEED`.
- Transformer-based financial sentiment (e.g. FinBERT) instead of keyword scoring.
- Multi-provider LLM routing (Groq / Anthropic / OpenAI direct) behind a
  provider abstraction.
- Celery + Redis for distributed task execution and a shared cache.
- A Next.js frontend on Vercel talking to this API (see the last section of
  [DEPLOYMENT.md](DEPLOYMENT.md)).

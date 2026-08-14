# IntelStock

AI-powered stock intelligence platform for Indian markets (NSE/BSE) with live quotes,
sentiment analysis, RAG-enhanced research, price alerts, portfolio analytics, and
conversational AI.

## What's Included

- OpenRouter LLM integration with streaming chat responses
- RAG pipeline with FAISS vector store for context-aware insights
- Portfolio analytics — returns, allocation, concentration, plus volatility /
  Sharpe / max drawdown when price history is available (reported as
  "unavailable" rather than guessed when it is not)
- Price alert system, persisted in the database and evaluated by the scheduler
- HTML report generation (stock, portfolio, sentiment)
- Animated Streamlit dashboard with a dark terminal theme
- Background task scheduler (market data, sentiment warm-up, RAG index, alerts)
- Externally-triggerable cron endpoints so scheduling survives free-tier sleep
- Automated test suite across unit, service, and API layers
- Docker Compose for local one-command deployment; Render Blueprint for hosting

Every external dependency is optional: with no network and no API key the app still
boots and serves. yfinance falls back to a built-in market snapshot, sentiment falls
back to keyword scoring, and RAG degrades to no-context retrieval.

## Quick Start

### Prerequisites

Python 3.11+. An OpenRouter API key (free tier at openrouter.ai) enables the LLM
features; without it everything still runs on fallbacks.

### 1. Install dependencies

```bash
git clone https://github.com/Chanukya07/IntelStock.git
cd IntelStock
pip install -r requirements/base.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Open .env and set OPENROUTER_API_KEY
```

### 3. Initialize database and run

```bash
# Initialize database schema
python -c "from backend.database import init_db; init_db()"

# Terminal 1 — FastAPI backend
uvicorn backend.main:app --reload

# Terminal 2 — Streamlit frontend
streamlit run frontend/dashboard.py
```

Open `http://localhost:8501` for the dashboard and `http://localhost:8000/docs` for
the API explorer.

Alternatively `./start.sh` runs both processes in one shell (backend on loopback,
Streamlit on `$PORT`, default 8501) — this is exactly what Render executes.

### Docker

```bash
docker-compose up
```

Frontend at `http://localhost:8501`, backend at `http://localhost:8000`.

## Pages

| Page | Description |
|------|-------------|
| Dashboard | Live ticker, NIFTY chart, top movers, sector performance |
| Overview | Watchlist with NSE/BSE prices and sentiment |
| Stock Research | AI-powered analysis with chart, support/resistance levels |
| Sentiment | Market gauge, sector radar, news with sentiment scoring |
| Portfolio | Holdings, P&L, analytics, report downloads |
| AI Chat | Streaming conversational research assistant |
| Alerts | Create and manage price alert rules |

The Alerts and Portfolio pages call the FastAPI app over HTTP (`INTELSTOCK_API_BASE`);
the other pages import the backend services and run them in-process.

## API Endpoints

All request bodies are JSON. `user_id` and `symbol` are query parameters unless
stated otherwise.

### Core

```
GET    /health                          Health check
GET    /stock?symbol=RELIANCE           Live quote
GET    /news?symbol=TCS[&source=...]    Company news (source is a filter)
GET    /sentiment?symbol=INFY           Sentiment score
GET    /insights?symbol=WIPRO           AI investment report
POST   /chat                            Chat response          body: {query}
POST   /chat/stream                     Streaming chat (SSE)   body: {query}
```

### Portfolio & Watchlist

```
GET    /portfolio?user_id=1             Holdings with live P&L
POST   /portfolio?user_id=1             Add holding    body: {symbol, quantity, average_cost}
GET    /watchlist?user_id=1             Watchlist
POST   /watchlist?user_id=1             Add to watchlist  body: {symbol}
DELETE /watchlist/{watchlist_id}        Remove from watchlist
```

### Advanced (v1)

```
POST   /api/v1/alerts?user_id=1         Create price alert  body: {symbol, alert_type, threshold}
GET    /api/v1/alerts?user_id=1         List user alerts
DELETE /api/v1/alerts/{alert_id}        Delete alert

GET    /api/v1/portfolio/analytics?user_id=1   Returns, allocation, risk metrics

GET    /api/v1/reports/stock?symbol=TCS        HTML stock research report
GET    /api/v1/reports/portfolio?user_id=1     HTML portfolio statement
GET    /api/v1/reports/sentiment               HTML sentiment report
```

Reports are returned as downloadable `text/html`, not PDF.

### RAG

```
POST   /rag/index               Index a document   body: {text, symbol?, title?}
POST   /rag/search              Search indexed documents  body: {query, symbol?, top_k?}
POST   /rag/context             Get context for a query   body: {query, symbol?}
DELETE /rag/clear               Clear vector store
```

### Cron (external scheduler)

Authenticated with `Authorization: Bearer $CRON_SECRET`. They fail closed with
`503` when `CRON_SECRET` is unset, and `401` on a bad token.

```
GET    /api/v1/cron/ping            Unauthenticated keep-warm probe
POST   /api/v1/cron/check-alerts    Evaluate every active price alert
POST   /api/v1/cron/refresh-rag     Re-index the latest headlines
```

These exist because a free-tier host sleeps after ~15 minutes of inactivity, which
stops the in-process scheduler. `.github/workflows/alert-cron.yml` drives them from
GitHub Actions. Set `ENABLE_SCHEDULER=false` when an external scheduler is in charge,
so the jobs do not run twice.

## Project Layout

```
IntelStock/
├── frontend/
│   ├── dashboard.py              Main Streamlit entry point
│   ├── sidebar.py                Shared sidebar and global CSS
│   ├── animations.py             CSS keyframes and animation helpers
│   ├── api_config.py             Backend URL and timeouts (INTELSTOCK_API_BASE)
│   ├── .streamlit/config.toml    Streamlit theme/config — the one Streamlit reads
│   ├── pages/
│   │   ├── overview.py
│   │   ├── stock_research.py
│   │   ├── sentiment_dashboard.py
│   │   ├── portfolio_analyzer.py
│   │   ├── ai_chat.py
│   │   └── alerts.py
│   └── charts/
│       └── price_chart.py        Plotly chart builders
│
├── backend/
│   ├── main.py                   FastAPI app with lifespan + scheduler toggle
│   ├── config.py                 OpenRouter/LLM configuration
│   ├── middleware.py             Logging and error handling
│   ├── exceptions.py             Exception hierarchy
│   ├── logging_config.py         Rotating file loggers
│   ├── api/
│   │   ├── routes.py             Core API endpoints
│   │   ├── advanced_routes.py    Alerts, analytics, reports
│   │   ├── cron_routes.py        Externally-triggered scheduled jobs
│   │   └── validators.py         Input validation
│   ├── services/
│   │   ├── chat_service.py       Streaming LLM chat
│   │   ├── insight_service.py    AI investment reports
│   │   ├── sentiment_service.py  Sentiment scoring
│   │   ├── market_data_service.py Stock quotes (yfinance + offline fallback)
│   │   ├── news_intelligence_service.py Curated news feed
│   │   ├── alert_service.py      Price alert management
│   │   ├── portfolio_service.py  Shared holdings/P&L builder
│   │   ├── portfolio_analytics_service.py Risk metrics
│   │   └── report_generator.py   HTML report generation
│   ├── rag/
│   │   ├── embeddings.py         Lazy-loading sentence transformers
│   │   ├── vectorstore.py        FAISS storage
│   │   ├── retriever.py          Document retrieval
│   │   └── chunking.py           Text preprocessing
│   ├── database/
│   │   ├── models.py             SQLAlchemy ORM (mirrors schema.sql)
│   │   ├── repositories.py       Data access layer
│   │   ├── session.py            Engine, session factory, URL normalisation
│   │   └── schema.sql            Canonical schema
│   └── tasks/
│       └── scheduler.py          Background refresh tasks
│
├── tests/
│   ├── test_project_scaffold.py  Structure and API contract checks
│   ├── test_services.py          Unit tests for services
│   ├── test_api_routes.py        API integration tests
│   ├── test_alert_persistence.py Alert storage and triggering
│   ├── test_portfolio_analytics.py Risk-metric correctness
│   └── test_cron_routes.py       Cron auth and job dispatch
│
├── docs/                         architecture.md, DEPLOYMENT.md, demo.md
├── .github/workflows/alert-cron.yml
├── docker/Dockerfile
├── docker-compose.yml
├── render.yaml                   Render Blueprint (web service + Postgres)
├── start.sh                      Runs backend + frontend in one container
├── requirements/base.txt
└── .env.example
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Uvicorn |
| AI/LLM | OpenRouter (OpenAI SDK) |
| Embeddings | sentence-transformers (lazy-loaded, optional) |
| Vector DB | FAISS |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Market data | yfinance, with an offline fallback snapshot |
| Tests | pytest, FastAPI TestClient |
| Container | Docker, Docker Compose |

See [docs/architecture.md](docs/architecture.md) for what is *not* in the stack.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | — | Enables LLM features; app degrades gracefully without it |
| `LLM_MODEL` | `openai/gpt-4o-mini` | Model routed via OpenRouter |
| `OPENROUTER_API_BASE` | `https://openrouter.ai/api/v1` | OpenAI-compatible base URL |
| `DATABASE_URL` | `sqlite:///./intelstock.db` | `postgres://` URLs are normalised for SQLAlchemy 2.x |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` | `5` / `5` | Connection pool (non-SQLite only) |
| `ENABLE_SCHEDULER` | `true` | Set `false` when an external scheduler drives `/api/v1/cron/*` |
| `CRON_SECRET` | — | Bearer token for `/api/v1/cron/*`; unset means those endpoints return 503 |
| `INTELSTOCK_API_BASE` | `http://127.0.0.1:8000` | Where the Streamlit pages reach the API |
| `INTELSTOCK_REQUEST_TIMEOUT` | `15` | Frontend HTTP timeout (seconds) |
| `INTELSTOCK_REPORT_TIMEOUT` | `60` | Frontend report-download timeout (seconds) |
| `BACKEND_PORT` / `PORT` | `8000` / `8501` | Ports used by `start.sh` |
| `UVICORN_LOG_LEVEL` | `info` | Passed to `uvicorn --log-level` by `start.sh` |

`render.yaml` and `docker-compose.yml` also pass `LOG_LEVEL` and `RAG_ENABLED`, but
no code reads them yet — see the note in `.env.example`. `.env.example` is the full
list; anything not listed there is not read by this codebase.

## Testing

```bash
pytest tests/          # Run the full suite
pytest tests/ -v       # Verbose output
```

Tests cover scaffold structure, API contracts, service logic (alerts, analytics,
reports, validators), alert persistence, cron authentication, and end-to-end API
routes.

## Deployment

### Render (recommended)

`render.yaml` provisions one free web service (running both processes via
`start.sh`) plus a managed Postgres, and `.github/workflows/alert-cron.yml` drives
the scheduled jobs. Full walkthrough, including why not Vercel, in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

### Docker Compose

```bash
docker-compose up -d
```

Runs the backend and frontend as two containers from the same image; the frontend
waits for the backend's healthcheck.

### Frontend-only hosts

`Procfile` and Streamlit Community Cloud start only `frontend/dashboard.py`. The
in-process pages (Dashboard, Overview, Stock Research, AI Chat) work; Alerts and
Portfolio need `INTELSTOCK_API_BASE` pointed at a separately deployed backend, and
no scheduler runs in that setup.

## Theming

Streamlit merges config from the global, project (`$CWD/.streamlit`) and
script-level (`frontend/.streamlit`) locations, last one winning. Because the app is
launched as `streamlit run frontend/dashboard.py`, **`frontend/.streamlit/config.toml`
is the file that takes effect** — including for a repo-root launch such as
`./start.sh`. Do not add a repo-root `.streamlit/config.toml`: it would be silently
overridden.

## Alert Types

| Type | Description |
|------|-------------|
| `price_above` | Trigger when price crosses above threshold |
| `price_below` | Trigger when price falls below threshold |
| `change_percent` | Trigger on daily percentage change |
| `volume_spike` | Trigger on unusual volume |

## License

MIT License — open source and free to use.

# IntelStock

AI-powered stock intelligence platform for Indian markets (NSE/BSE) with real-time insights, sentiment analysis, RAG-enhanced research, price alerts, portfolio analytics, and conversational AI.

## What's Included

**v3.0 — Feature Complete**

- OpenRouter LLM integration with streaming chat responses
- RAG pipeline with FAISS vector store for context-aware insights
- Advanced portfolio analytics (Sharpe ratio, volatility, max drawdown, XIRR)
- Price alert system with multiple alert types
- HTML report generation (stock, portfolio, sentiment)
- Animated Streamlit dashboard with dark terminal theme
- Background task scheduler (market data refresh, RAG index refresh)
- 33 automated tests across unit, service, and API layers
- Docker Compose for one-command deployment

## Quick Start

### Prerequisites

Python 3.11+ and an OpenRouter API key (get one free at openrouter.ai).

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

Open `http://localhost:8501` for the dashboard and `http://localhost:8000/docs` for the API explorer.

### Docker (recommended)

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
| Portfolio | Holdings, P&L, advanced analytics, report downloads |
| AI Chat | Streaming conversational research assistant |
| Alerts | Create and manage price alert rules |

## API Endpoints

### Core

```
GET  /health                    Health check
GET  /stock?symbol=RELIANCE     Live quote
GET  /news?symbol=TCS           Company news
GET  /sentiment?symbol=INFY     Sentiment score
GET  /insights?symbol=WIPRO     AI investment report
POST /chat                      Chat response (JSON)
GET  /chat/stream               Streaming chat response
```

### Portfolio & Watchlist

```
GET    /portfolio?user_id=1     Holdings with P&L
POST   /portfolio               Add holding
GET    /watchlist?user_id=1     Watchlist
POST   /watchlist               Add to watchlist
DELETE /watchlist/{id}          Remove from watchlist
```

### Advanced (v1)

```
POST /api/v1/alerts             Create price alert
GET  /api/v1/alerts             Get user alerts
DELETE /api/v1/alerts/{id}      Delete alert

GET  /api/v1/portfolio/analytics  Sharpe ratio, volatility, drawdown

GET  /api/v1/reports/stock       HTML stock research report
GET  /api/v1/reports/portfolio   HTML portfolio statement
GET  /api/v1/reports/sentiment   HTML sentiment report
```

### RAG

```
POST   /rag/index               Index a document
POST   /rag/search              Search indexed documents
POST   /rag/context             Get context for query
DELETE /rag/clear               Clear vector store
```

## Architecture

```
IntelStock/
├── frontend/
│   ├── dashboard.py              Main Streamlit entry point
│   ├── sidebar.py                Shared sidebar and global CSS
│   ├── animations.py             CSS keyframes and animation helpers
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
│   ├── main.py                   FastAPI app with lifespan
│   ├── config.py                 Environment configuration
│   ├── middleware.py             Logging and error handling
│   ├── exceptions.py             Exception hierarchy
│   ├── logging_config.py         Rotating file loggers
│   ├── api/
│   │   ├── routes.py             Core API endpoints
│   │   ├── advanced_routes.py    Alerts, analytics, reports
│   │   └── validators.py         Input validation
│   ├── services/
│   │   ├── chat_service.py       Streaming LLM chat
│   │   ├── insight_service.py    AI investment reports
│   │   ├── sentiment_service.py  Sentiment scoring
│   │   ├── market_data_service.py Stock quotes
│   │   ├── news_intelligence_service.py News feed
│   │   ├── alert_service.py      Price alert management
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
│   │   ├── schema.sql            Canonical schema
│   │   └── __init__.py
│   └── tasks/
│       └── scheduler.py          Background refresh tasks
│
├── tests/
│   ├── test_project_scaffold.py  Structure and API contract checks
│   ├── test_services.py          Unit tests for services
│   └── test_api_routes.py        API integration tests
│
├── docker/Dockerfile
├── docker-compose.yml
├── requirements/base.txt
└── .env.example
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Plotly |
| Backend | FastAPI, Uvicorn |
| AI/LLM | OpenRouter (OpenAI SDK) |
| Embeddings | sentence-transformers (lazy-loaded) |
| Vector DB | FAISS |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Tests | pytest, FastAPI TestClient |
| Container | Docker, Docker Compose |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | — | Required for AI features |
| `LLM_MODEL` | `openai/gpt-4o-mini` | Model to use |
| `DATABASE_URL` | `sqlite:///./intelstock.db` | Database connection |
| `RAG_ENABLED` | `true` | Enable RAG pipeline |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

See `.env.example` for the full list.

## Testing

```bash
pytest tests/          # All 33 tests
pytest tests/ -v       # Verbose output
```

Tests cover scaffold structure, API contracts, service logic (alerts, analytics, reports, validators), and end-to-end API routes.

## Deployment

### Streamlit Community Cloud

Point to `frontend/dashboard.py` and set `OPENROUTER_API_KEY` in the secrets panel.

### Railway / Render

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Docker Compose

```bash
docker-compose up -d
```

## Alert Types

| Type | Description |
|------|-------------|
| `price_above` | Trigger when price crosses above threshold |
| `price_below` | Trigger when price falls below threshold |
| `change_percent` | Trigger on daily percentage change |
| `volume_spike` | Trigger on unusual volume |

## License

MIT License — open source and free to use.

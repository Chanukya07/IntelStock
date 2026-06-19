# IntelStock

AI-powered stock intelligence platform focused on Indian markets (NSE/BSE), combining market data, news, sentiment analysis, RAG context retrieval, and conversational AI research.

## Architecture

```text
IntelStock/
├── frontend/                  # Streamlit dashboard + pages
├── backend/                   # FastAPI APIs and AI services
├── vectorstore/               # FAISS index artifacts
├── data/                      # Local data snapshots/cache
├── tests/                     # Focused validation tests
├── docs/                      # Architecture and workflows
├── docker/                    # Container assets
├── requirements/              # Dependency groups
└── README.md
```

## Modules

- **Frontend (Streamlit):** dashboard, charts, tables, chat UI.
- **Backend (FastAPI):** API layer and orchestration.
- **Market Data Service:** live quotes, historical OHLCV, fundamentals.
- **News Intelligence Service:** news ingestion and company filtering.
- **Sentiment Analysis Service:** bullish/bearish scoring and trends.
- **RAG Engine:** chunking, embeddings, FAISS retrieval.
- **LLM Insight Engine:** AI summaries and recommendations.
- **Database Layer:** SQLite for MVP, PostgreSQL-ready architecture.
- **Background Scheduler:** periodic refresh workflows.

## API Surface (MVP)

- `GET /stock`
- `GET /news`
- `GET /sentiment`
- `GET /insights`
- `POST /chat`
- `GET /portfolio`
- `GET /watchlist`

## Dashboard Pages

- Overview
- Stock Research
- Sentiment Dashboard
- Portfolio Analyzer
- AI Chat

## AI Agents

1. **Market Analyst**: trend and technical context.
2. **News Analyst**: key events and impact extraction.
3. **Sentiment Analyst**: bullish/bearish scoring.
4. **Research Agent**: investment thesis and risk-reward summary.

## Deliverables in this repository

- Production-oriented folder scaffold.
- FastAPI backend entrypoint with required API routes.
- Streamlit frontend entrypoint with required pages.
- Architecture/workflow docs for RAG, services, and deployment.
- Focused tests validating required scaffold and endpoint contract.

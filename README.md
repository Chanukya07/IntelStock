# IntelStock

AI-powered stock intelligence platform focused on Indian markets (NSE/BSE), combining market data, news, sentiment analysis, RAG context retrieval, and conversational AI research.

## Demo

See [docs/demo.md](docs/demo.md) for a short product walkthrough, suggested sample queries, and a deployment-friendly demo flow.

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
├── .streamlit/                # Streamlit deployment and theme config
└── README.md
```

## Modules

- **Frontend (Streamlit):** dashboard, charts, tables, chat UI.
- **Backend (FastAPI):** API layer and orchestration.
- **Market Data Service:** structured quote and market profile lookup.
- **News Intelligence Service:** curated company headlines and summaries.
- **Sentiment Analysis Service:** lightweight bullish/bearish scoring.
- **RAG Engine:** chunking, embeddings, FAISS retrieval.
- **LLM Insight Engine:** AI summaries, catalysts, and recommendations.
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

## What Works Right Now

- A clean dark Streamlit dashboard with a shared sidebar and section navigation.
- AI chat responses that return structured summaries, recommendations, catalysts, and risks.
- Stock research views driven by lightweight market profiles instead of pure placeholder text.
- Sentiment and portfolio pages with a consistent visual system.
- No-cost Streamlit deployment settings in [`.streamlit/config.toml`](.streamlit/config.toml).

## Run Locally

Install dependencies:

```bash
python -m pip install -r requirements/base.txt
```

Run the Streamlit app:

```bash
python -m streamlit run frontend/dashboard.py
```

If port `8501` is already taken, Streamlit will use a different free port or you can pass one explicitly:

```bash
python -m streamlit run frontend/dashboard.py --server.port 8509
```

Run the FastAPI backend separately if needed:

```bash
uvicorn backend.main:app --reload
```

## Free Hosting Path

The easiest no-cost hosting setup for this repository is:

1. Streamlit Community Cloud for the frontend at `frontend/dashboard.py`.
2. Render or Railway for the FastAPI backend if you want a separate API runtime.
3. GitHub as the source of truth for app code, docs, and deployment settings.

The repo now includes Streamlit theme/config defaults so the UI renders consistently when deployed.

### Suggested deployment steps

1. Push the repository to GitHub.
2. Connect the repo to Streamlit Community Cloud and point it at `frontend/dashboard.py`.
3. If you split the backend out later, keep the same API contracts under `backend/api/routes.py`.
4. Use the sidebar Home link as the public landing page.
5. Add your GitHub repository URL to the demo file so reviewers can launch the app quickly.

## API Surface (Current)

- `GET /stock` returns a structured market profile.
- `GET /news` returns a small curated headline list.
- `GET /sentiment` returns a lightweight sentiment score.
- `GET /insights` returns a generated recommendation brief.
- `POST /chat` returns a richer research answer built from the insight service.
- `GET /portfolio` and `GET /watchlist` remain scaffold endpoints.

## Notes for Reviewers

- The app is currently optimized for presentation and fast iteration, not live market data ingestion.
- The AI layer is structured so external providers can be added later without changing the UI contract.
- The shared sidebar is intentionally reusable across all Streamlit pages.

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
- Demo walkthrough and deployment-ready README guidance.

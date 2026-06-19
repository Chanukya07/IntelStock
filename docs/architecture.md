# IntelStock Architecture

## Tech Stack

- Frontend: Streamlit, Plotly, Streamlit AgGrid
- Backend: FastAPI, Uvicorn, Pydantic
- Market Data: yfinance, nsetools, yahooquery
- News: NewsAPI, GNews, Google News RSS
- NLP: transformers, FinBERT, NLTK, spaCy
- AI/RAG: LangChain, OpenAI/Groq/Claude provider abstraction, FAISS
- Scheduler: APScheduler (MVP), Celery + Redis (production)
- Database: SQLite (MVP), PostgreSQL (production)
- Deployment: Docker + GitHub Actions + cloud runtime (Render/Railway/AWS)

## Service Workflow

1. Collect market and news data.
2. Process and score sentiment.
3. Chunk and embed relevant documents.
4. Store/retrieve context via FAISS.
5. Build final research prompt with market + news + sentiment + retrieved context.
6. Generate recommendation and risk summary.

## Database Tables (target)

- users
- stocks
- historical_prices
- news
- sentiment_scores
- watchlists
- insights
- chat_history
- portfolios

# IntelStock

🚀 **AI-powered stock intelligence platform for Indian markets (NSE/BSE)** with real-time insights, sentiment analysis, RAG-enhanced research, and conversational AI.

## 🎯 What's New

**v2.0 - Production Ready**
- ✨ OpenRouter LLM integration for AI-powered recommendations
- 🔍 RAG pipeline with FAISS vector store for context-aware insights
- 💬 Real-time streaming chat for live AI responses
- 🗄️ SQLAlchemy database layer with SQLite (MVP) and PostgreSQL support
- 📊 Portfolio tracking and watchlist management
- 🎨 Enhanced Streamlit dashboard with dark theme

## ⚡ Quick Start

### Prerequisites
```bash
Python 3.9+
pip/virtualenv
```

### Installation

1. **Clone and setup:**
```bash
git clone https://github.com/Chanukya07/IntelStock.git
cd IntelStock
```

2. **Install dependencies:**
```bash
pip install -r requirements/base.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key from https://openrouter.ai
```

4. **Initialize database:**
```bash
python -c "from backend.database import init_db; init_db()"
```

5. **Run the app:**
```bash
# Streamlit frontend (default: http://localhost:8501)
streamlit run frontend/dashboard.py

# FastAPI backend (in another terminal, default: http://localhost:8000)
uvicorn backend.main:app --reload
```

## 🏗️ Architecture

```
IntelStock/
├── frontend/                    # Streamlit dashboard
│   ├── dashboard.py            # Main entry point
│   ├── pages/                  # Multi-page app
│   │   ├── overview.py
│   │   ├── ai_chat.py          # Real-time chat interface
│   │   ├── stock_research.py
│   │   ├── sentiment_dashboard.py
│   │   └── portfolio_analyzer.py
│   ├── components/
│   │   ├── chat_interface.py   # Reusable chat widget
│   │   └── sidebar.py
│   └── sidebar.py
│
├── backend/
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Environment configuration
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── services/               # Business logic layer
│   │   ├── chat_service.py     # Streaming chat with RAG
│   │   ├── insight_service.py  # AI recommendations
│   │   ├── sentiment_service.py # Sentiment analysis
│   │   ├── market_data_service.py
│   │   └── news_intelligence_service.py
│   ├── agents/                 # AI agent implementations
│   │   └── research_agents.py
│   ├── rag/                    # Retrieval Augmented Generation
│   │   ├── chunking.py         # Text preprocessing
│   │   ├── embeddings.py       # Sentence transformers
│   │   ├── vectorstore.py      # FAISS storage
│   │   ├── retriever.py        # Document retrieval
│   │   └── pipeline.py         # RAG workflow
│   └── database/               # Data persistence
│       ├── models.py           # SQLAlchemy ORM models
│       ├── session.py          # Database connection
│       ├── repositories.py     # Data access layer
│       └── __init__.py
│
├── requirements/
│   └── base.txt                # Python dependencies
├── .env.example                # Environment template
├── .streamlit/                 # Streamlit config
└── README.md
```

## 🤖 Features

### AI & Intelligence
- **OpenRouter LLM Integration** - Free models for AI recommendations
- **Real-time Streaming** - Live token-by-token AI responses
- **RAG Pipeline** - Context-aware insights from indexed documents
- **Sentiment Analysis** - AI-powered bullish/bearish scoring
- **Dynamic Recommendations** - Context-aware investment thesis

### Data & Analytics
- **Live Market Data** - Stock quotes, support/resistance levels
- **News Intelligence** - Curated headlines with sentiment
- **Portfolio Tracking** - Holdings with P&L calculations
- **Watchlist Management** - Price alerts and monitoring
- **Chat History** - Persistent conversation logs

### Database
- **SQLite (MVP)** - Local development database
- **PostgreSQL Ready** - Production-grade ORM support
- **8 Core Models** - User, Chat, Quote, News, Sentiment, Portfolio, Watchlist, Insight
- **Repository Pattern** - Clean data access layer

## 📡 API Surface

### Core Endpoints
```
GET  /stock              → Live stock quote
GET  /news               → Company headlines
GET  /sentiment          → Sentiment analysis
GET  /insights           → AI-generated report
POST /chat               → Chat response (JSON)
POST /chat/stream        → Streaming chat response
```

### Portfolio & Watchlist
```
GET  /portfolio          → User holdings with P&L
POST /portfolio          → Add stock to portfolio
GET  /watchlist          → Watched stocks
POST /watchlist          → Add to watchlist
DELETE /watchlist/{id}   → Remove from watchlist
```

### RAG & Knowledge
```
POST /rag/index          → Index document
POST /rag/search         → Search indexed documents
POST /rag/context        → Get context for query
DELETE /rag/clear        → Clear vector store
```

### Health & Status
```
GET /health              → API health check
```

## 🚀 Deployment

### Streamlit Community Cloud (Frontend)
1. Push repo to GitHub
2. Connect to Streamlit Cloud
3. Point to `frontend/dashboard.py`
4. Set environment variables (OPENROUTER_API_KEY, DATABASE_URL)

### Railway/Render (Backend)
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Environment Variables
```
OPENROUTER_API_KEY=sk-or-v1-...      # Your OpenRouter API key
LLM_MODEL=meta-llama/llama-2-7b-chat # Model selection
DATABASE_URL=postgresql://...        # PostgreSQL connection (optional)
```

## 💾 Database Models

### User
- Manages user accounts and profiles
- Links to chats, portfolio, watchlist

### Chat
- Persistent conversation history
- Stores query, response, metadata
- Linked to user and stock symbol

### StockQuote
- Market snapshots (price, change, support/resistance)
- Auto-updated from market data service

### Portfolio
- User holdings with quantity and average cost
- Calculates gain/loss vs current price

### Watchlist
- Tracked stocks with optional alerts
- Price alert thresholds and alert types

### Sentiment & Insight
- Historical sentiment scores
- AI-generated investment theses

## 🔧 Configuration

### .env Template
```bash
# OpenRouter API (from https://openrouter.ai)
OPENROUTER_API_KEY=your_api_key_here
LLM_MODEL=meta-llama/llama-2-7b-chat
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./intelstock.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/intelstock
```

### Streamlit Config
- Dark theme enabled by default
- Wide layout for dashboards
- Custom fonts (Inter, JetBrains Mono)
- See `.streamlit/config.toml` for customization

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Check imports
python -c "from backend.services.chat_service import ChatService; print('✓ OK')"
```

## 📊 Dashboard Pages

1. **Overview** - Market summary and key metrics
2. **Stock Research** - Detailed analysis with AI insights
3. **Sentiment Dashboard** - Market sentiment trends
4. **Portfolio Analyzer** - Holdings and performance
5. **AI Chat** - Real-time conversational research

## 🎓 Example Queries

Try asking the AI:
- "Analyze RELIANCE"
- "What's the outlook for TCS?"
- "Nifty technical analysis"
- "Top IT stocks to watch"
- "HDFC near-term view"
- "Show me bearish signals"

## 🛠️ Tech Stack

**Frontend:**
- Streamlit - Interactive dashboards
- Plotly - Advanced charts
- pandas - Data manipulation

**Backend:**
- FastAPI - REST API framework
- SQLAlchemy - ORM database layer
- OpenAI SDK - LLM integration
- sentence-transformers - Embeddings
- FAISS - Vector similarity search

**AI/ML:**
- OpenRouter - LLM provider (free models)
- sentence-transformers - Embeddings
- FAISS - Vector database

**Database:**
- SQLite - Development
- PostgreSQL - Production

## 🔐 Security

- API keys stored in `.env` (excluded from git)
- Database credentials in environment variables
- No credentials in code or commits
- CORS and rate limiting recommended for production

## 📈 Roadmap

- [ ] Background scheduler for data refresh
- [ ] User authentication system
- [ ] Advanced portfolio analytics
- [ ] Real-time price alerts
- [ ] Mobile app support
- [ ] Multi-language support
- [ ] Custom watchlist alerts
- [ ] Export reports as PDF

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 💬 Support

For issues, questions, or suggestions:
- Open a GitHub issue
- Check existing documentation
- Review the demo walkthrough

## 🎉 What Works Right Now

✅ Real-time chat with AI-powered responses  
✅ Streaming token delivery for better UX  
✅ RAG-enhanced context retrieval  
✅ Sentiment analysis with confidence scoring  
✅ Stock quotes and market data  
✅ Portfolio tracking with P&L  
✅ Watchlist management  
✅ Persistent chat history  
✅ Dark theme dashboard  
✅ Fast, responsive interface  

---

**Built with ❤️ for Indian market traders and investors**

*Powered by OpenRouter LLM • Enhanced with RAG • Backed by SQLAlchemy*

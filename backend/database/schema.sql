CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,
    company_name TEXT
);

CREATE TABLE IF NOT EXISTS historical_prices (
    id INTEGER PRIMARY KEY,
    stock_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY,
    stock_id INTEGER,
    title TEXT NOT NULL,
    source TEXT,
    published_at TEXT,
    content TEXT,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE TABLE IF NOT EXISTS sentiment_scores (
    id INTEGER PRIMARY KEY,
    news_id INTEGER NOT NULL,
    bullish_score REAL,
    bearish_score REAL,
    analyzed_at TEXT,
    FOREIGN KEY (news_id) REFERENCES news(id)
);

CREATE TABLE IF NOT EXISTS watchlists (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    UNIQUE(user_id, stock_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE TABLE IF NOT EXISTS insights (
    id INTEGER PRIMARY KEY,
    stock_id INTEGER,
    recommendation TEXT,
    risk_summary TEXT,
    created_at TEXT,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    avg_price REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

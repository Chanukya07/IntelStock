"""Database session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.database.models import Base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./intelstock.db")


def _normalize_database_url(url: str) -> str:
    """Make a provider-supplied URL usable by SQLAlchemy 2.x.

    Render, Heroku and several other managed Postgres providers hand out
    connection strings beginning with ``postgres://``. SQLAlchemy 2.x removed
    support for that alias and raises NoSuchModuleError, so the URL has to be
    rewritten to an explicit driver. This is the single most common reason a
    working local SQLite app dies on its first Postgres deploy.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


DATABASE_URL = _normalize_database_url(DATABASE_URL)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # pool_pre_ping guards against connections killed by the provider while
    # idle (free-tier Postgres suspends aggressively). pool_recycle keeps
    # connections under typical provider idle timeouts.
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=280,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "5")),
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

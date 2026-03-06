from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ---------------------------------------------------------------------------
# Engine — use connect_args for SQLite thread-safety; omit for PostgreSQL
# ---------------------------------------------------------------------------
connect_args = {}
if settings.is_sqlite:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

# ---------------------------------------------------------------------------
# Session factory — one session per request via FastAPI dependency injection
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------------
# Declarative base — all models inherit from this
# ---------------------------------------------------------------------------
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session and closes it after
    the request completes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

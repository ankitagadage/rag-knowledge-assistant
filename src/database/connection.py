"""
Creates the SQLAlchemy engine and session factory. Everything else in the
app (CRUD functions, API routes) should get a session from `get_db()`
rather than importing `engine` directly.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI-style dependency: yields a session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

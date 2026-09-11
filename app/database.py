"""Database connection and session management."""

import logging
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)


def ensure_db_directory(database_url: str) -> None:
    """Ensure the directory exists for SQLite database files."""
    if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite:///:memory:"):
        db_path_str = database_url.replace("sqlite:///", "", 1)
        db_path = Path(db_path_str)
        parent_dir = db_path.parent
        if parent_dir and not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created database directory: %s", parent_dir)


ensure_db_directory(settings.DATABASE_URL)

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30.0

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to provide a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables defined in models."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")

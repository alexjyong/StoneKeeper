"""
Database session management for StoneKeeper.

Provides SQLAlchemy engine and session factory configuration.
Sessions are created per-request using FastAPI dependencies.
"""
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Get database URL from environment variable
# Format: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://stonekeeper_user:password@localhost:5432/stonekeeper'
)

# Create SQLAlchemy engine
# pool_pre_ping: Verify connections before using them from the pool
# echo: Set to True for development to see SQL queries (False for production)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# Create session factory
# autocommit=False: Require explicit commits
# autoflush=False: Require explicit flushes
# bind=engine: Associate sessions with our database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Yields a database session and ensures it is properly closed
    after the request is complete.

    Usage in FastAPI endpoints:
        @app.get("/example")
        def example_endpoint(db: Session = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

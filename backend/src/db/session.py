"""
Database session management for StoneKeeper.

Provides SQLAlchemy engine and session factory configuration.
Sessions are created per-request using FastAPI dependencies.
"""
import os
from typing import Generator
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def get_database_url() -> str:
    """
    Construct database URL from environment variables and secret files.

    Reads database credentials from Docker secrets if available,
    otherwise falls back to environment variables.
    """
    # Check if DATABASE_URL is explicitly set
    if database_url := os.getenv('DATABASE_URL'):
        return database_url

    # Read database configuration from environment variables
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', 'stonekeeper')

    # Read database user from secret file or environment variable
    db_user = os.getenv('DATABASE_USER', 'stonekeeper_user')
    if db_user_file := os.getenv('DATABASE_USER_FILE'):
        if os.path.exists(db_user_file):
            with open(db_user_file, 'r') as f:
                db_user = f.read().strip()

    # Read database password from secret file or environment variable
    db_password = os.getenv('DATABASE_PASSWORD', 'password')
    if db_password_file := os.getenv('DATABASE_PASSWORD_FILE'):
        if os.path.exists(db_password_file):
            with open(db_password_file, 'r') as f:
                db_password = f.read().strip()

    # URL-encode credentials to handle special characters
    db_user_encoded = quote_plus(db_user)
    db_password_encoded = quote_plus(db_password)

    return f'postgresql://{db_user_encoded}:{db_password_encoded}@{db_host}:{db_port}/{db_name}'


# Get database URL
DATABASE_URL = get_database_url()

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

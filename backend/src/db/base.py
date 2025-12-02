"""
SQLAlchemy base configuration and model registry.

This module provides the declarative base for all ORM models.
All models must inherit from Base to be registered with Alembic.

Note: Model imports are handled in env.py for Alembic migrations
and in main.py for the application to avoid circular imports.
"""
from sqlalchemy.orm import declarative_base

# Create the declarative base for all ORM models
Base = declarative_base()


def import_models():
    """
    Import all models to register them with Base.metadata.
    Call this function explicitly when needed (e.g., in env.py for Alembic).
    """
    from src.models.user import User  # noqa: F401
    from src.models.user_session import UserSession  # noqa: F401
    from src.models.cemetery import Cemetery  # noqa: F401
    from src.models.section import Section  # noqa: F401
    from src.models.plot import Plot  # noqa: F401
    from src.models.photograph import Photograph  # noqa: F401

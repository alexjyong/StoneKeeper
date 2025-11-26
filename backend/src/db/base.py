"""
SQLAlchemy base configuration and model registry.

This module provides the declarative base for all ORM models.
All models must inherit from Base to be registered with Alembic.
"""
from sqlalchemy.orm import declarative_base

# Create the declarative base for all ORM models
Base = declarative_base()

# Import all models here to ensure they are registered with Base.metadata
# This is essential for Alembic autogenerate to detect all tables
from src.models.user import User  # noqa: F401, E402
from src.models.user_session import UserSession  # noqa: F401, E402
from src.models.cemetery import Cemetery  # noqa: F401, E402
from src.models.section import Section  # noqa: F401, E402
from src.models.plot import Plot  # noqa: F401, E402
from src.models.photograph import Photograph  # noqa: F401, E402

"""
User model for StoneKeeper authentication and attribution.

Tracks researchers who use the system, with soft delete support
to preserve data integrity when users are deactivated.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base


class User(Base):
    """
    User account for researchers accessing StoneKeeper.

    Attributes:
        id: Primary key
        email: Unique email address for login
        password_hash: Bcrypt hashed password
        full_name: User's full name for attribution
        is_active: Whether account is active (for soft disable)
        created_at: Account creation timestamp
        updated_at: Last modification timestamp (auto-updated by trigger)
        deleted_at: Soft delete timestamp (NULL = active)

    Relationships:
        sessions: User login sessions
        uploaded_photos: Photos uploaded by this user
        created_cemeteries: Cemeteries created by this user
        created_sections: Sections created by this user
        created_plots: Plots created by this user
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps (timezone-aware per Constitution Principle I)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships (defined with string references to avoid circular imports)
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    uploaded_photos = relationship("Photograph", foreign_keys="[Photograph.uploaded_by]", back_populates="uploader")
    created_cemeteries = relationship("Cemetery", foreign_keys="[Cemetery.created_by]", back_populates="creator")
    created_sections = relationship("Section", foreign_keys="[Section.created_by]", back_populates="creator")
    created_plots = relationship("Plot", foreign_keys="[Plot.created_by]", back_populates="creator")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"

    @property
    def is_deleted(self) -> bool:
        """Check if user is soft deleted."""
        return self.deleted_at is not None

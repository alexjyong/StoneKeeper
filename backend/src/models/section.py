"""
Section model for StoneKeeper.

Represents a section within a cemetery, allowing organizational
hierarchy for better photo cataloging and navigation.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.base import Base


class Section(Base):
    """
    Section within a cemetery.

    Sections provide organizational structure within cemeteries,
    such as "North Section", "Veterans Section", "Family Plot A", etc.

    Attributes:
        id: Primary key
        cemetery_id: Foreign key to parent cemetery
        name: Section name
        description: Optional description of the section
        display_order: Order for displaying sections (lower = first)
        created_by: Foreign key to user who created this section
        created_at: Creation timestamp
        updated_at: Last modification timestamp (auto-updated by trigger)
        deleted_at: Soft delete timestamp (NULL = active)

    Relationships:
        cemetery: Parent cemetery
        creator: User who created this section
        plots: Plots within this section
        photographs: Photos associated with this section
    """

    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    cemetery_id = Column(Integer, ForeignKey("cemeteries.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)

    # Attribution and tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Timestamps (timezone-aware per Constitution Principle I)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    cemetery = relationship("Cemetery", back_populates="sections")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_sections")
    plots = relationship("Plot", back_populates="section", cascade="all, delete-orphan")
    photographs = relationship("Photograph", back_populates="section")

    def __repr__(self) -> str:
        return f"<Section(id={self.id}, name='{self.name}', cemetery_id={self.cemetery_id})>"

    @property
    def is_deleted(self) -> bool:
        """Check if section is soft deleted."""
        return self.deleted_at is not None

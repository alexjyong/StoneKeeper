"""
Plot model for StoneKeeper.

Represents individual burial plots or grave sites within cemetery sections,
providing the finest level of organizational detail.
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.base import Base


class Plot(Base):
    """
    Individual burial plot or grave site.

    Plots represent specific grave locations within sections,
    with optional plot numbers, row identifiers, and inscription details.

    Attributes:
        id: Primary key
        section_id: Foreign key to parent section
        plot_number: Plot or grave number (e.g., "42", "A-15")
        row_identifier: Row identifier (e.g., "Row 3", "Section B")
        headstone_inscription: Text from headstone for historical record
        burial_date: Date of burial (if known)
        notes: Additional notes or historical information
        created_by: Foreign key to user who created this plot record
        created_at: Creation timestamp
        updated_at: Last modification timestamp (auto-updated by trigger)
        deleted_at: Soft delete timestamp (NULL = active)

    Relationships:
        section: Parent section
        creator: User who created this plot record
        photographs: Photos of this specific plot
    """

    __tablename__ = "plots"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True)
    plot_number = Column(String(50), nullable=True)
    row_identifier = Column(String(50), nullable=True)
    headstone_inscription = Column(Text, nullable=True)
    burial_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Attribution and tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Timestamps (timezone-aware per Constitution Principle I)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    section = relationship("Section", back_populates="plots")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_plots")
    photographs = relationship("Photograph", back_populates="plot")

    def __repr__(self) -> str:
        plot_id = self.plot_number or f"#{self.id}"
        return f"<Plot(id={self.id}, plot={plot_id}, section_id={self.section_id})>"

    @property
    def is_deleted(self) -> bool:
        """Check if plot is soft deleted."""
        return self.deleted_at is not None

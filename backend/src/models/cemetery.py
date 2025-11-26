"""
Cemetery model for StoneKeeper.

Represents a physical cemetery location with optional GPS coordinates
using PostGIS GEOGRAPHY type for spatial queries.
"""
from datetime import datetime
from typing import Optional

from geoalchemy2 import Geography
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.base import Base


class Cemetery(Base):
    """
    Physical cemetery location.

    Stores cemetery information with optional GPS coordinates
    for mapping and spatial search. Uses PostGIS GEOGRAPHY type
    with WGS84 (SRID 4326) for accurate distance calculations.

    Attributes:
        id: Primary key
        name: Cemetery name
        location_description: Text description of location (address, directions)
        gps_location: PostGIS GEOGRAPHY POINT (latitude, longitude)
        established_year: Year cemetery was established
        notes: Additional notes or historical information
        created_by: Foreign key to user who created this cemetery record
        created_at: Creation timestamp
        updated_at: Last modification timestamp (auto-updated by trigger)
        deleted_at: Soft delete timestamp (NULL = active)

    Relationships:
        creator: User who created this cemetery record
        sections: Sections within this cemetery
        photographs: All photos associated with this cemetery
    """

    __tablename__ = "cemeteries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    location_description = Column(Text, nullable=True)
    gps_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    established_year = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Attribution and tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Timestamps (timezone-aware per Constitution Principle I)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_cemeteries")
    sections = relationship("Section", back_populates="cemetery", cascade="all, delete-orphan")
    photographs = relationship("Photograph", back_populates="cemetery")

    def __repr__(self) -> str:
        return f"<Cemetery(id={self.id}, name='{self.name}')>"

    @property
    def is_deleted(self) -> bool:
        """Check if cemetery is soft deleted."""
        return self.deleted_at is not None

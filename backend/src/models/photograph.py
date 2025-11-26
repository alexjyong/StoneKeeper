"""
Photograph model for StoneKeeper.

Represents uploaded cemetery photographs with EXIF metadata,
file paths, and organizational associations.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from geoalchemy2 import Geography
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from src.db.base import Base


class Photograph(Base):
    """
    Cemetery photograph with EXIF metadata.

    Stores all information about uploaded photos including file paths,
    EXIF metadata extracted from the image, and organizational associations
    to cemeteries, sections, and plots.

    Per Constitution Principle I (Data Integrity First):
    - EXIF metadata is preserved exactly as extracted
    - Original files are never modified
    - Soft delete preserves all data

    Attributes:
        id: Primary key
        uuid: Unique identifier for public references
        cemetery_id: Foreign key to associated cemetery (required)
        section_id: Foreign key to section (optional)
        plot_id: Foreign key to specific plot (optional)

        # File information
        file_path: Path to original photo file
        thumbnail_path: Path to 150x150 thumbnail
        preview_path: Path to 800x600 preview
        file_size_bytes: Original file size in bytes
        file_format: Image format (JPEG, PNG, TIFF)

        # EXIF metadata (all optional - not all photos have EXIF data)
        exif_date_taken: DateTime photo was taken (from EXIF)
        exif_gps_location: GPS coordinates from EXIF (PostGIS GEOGRAPHY POINT)
        exif_camera_make: Camera manufacturer
        exif_camera_model: Camera model
        exif_focal_length: Focal length (e.g., "50mm")
        exif_aperture: Aperture value (e.g., "f/2.8")
        exif_shutter_speed: Shutter speed (e.g., "1/125")
        exif_iso: ISO speed rating
        image_width: Image width in pixels
        image_height: Image height in pixels

        # User-provided metadata
        description: User-provided photo description
        photographer_notes: Additional notes from photographer

        # Tracking
        uploaded_by: Foreign key to user who uploaded this photo
        created_at: Upload timestamp
        updated_at: Last modification timestamp (auto-updated by trigger)
        deleted_at: Soft delete timestamp (NULL = active)

    Relationships:
        cemetery: Associated cemetery
        section: Associated section (optional)
        plot: Associated plot (optional)
        uploader: User who uploaded this photo
    """

    __tablename__ = "photographs"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(PG_UUID(as_uuid=True), unique=True, nullable=False, default=uuid4, index=True)

    # Organizational associations
    cemetery_id = Column(Integer, ForeignKey("cemeteries.id", ondelete="RESTRICT"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="SET NULL"), nullable=True, index=True)
    plot_id = Column(Integer, ForeignKey("plots.id", ondelete="SET NULL"), nullable=True, index=True)

    # File information
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    preview_path = Column(String(500), nullable=True)
    file_size_bytes = Column(BigInteger, nullable=False)
    file_format = Column(String(10), nullable=False)

    # EXIF metadata
    exif_date_taken = Column(DateTime(timezone=True), nullable=True, index=True)
    exif_gps_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    exif_camera_make = Column(String(100), nullable=True)
    exif_camera_model = Column(String(100), nullable=True)
    exif_focal_length = Column(String(50), nullable=True)
    exif_aperture = Column(String(50), nullable=True)
    exif_shutter_speed = Column(String(50), nullable=True)
    exif_iso = Column(Integer, nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)

    # User-provided metadata
    description = Column(Text, nullable=True)
    photographer_notes = Column(Text, nullable=True)

    # Attribution and tracking
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Timestamps (timezone-aware per Constitution Principle I)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    cemetery = relationship("Cemetery", back_populates="photographs")
    section = relationship("Section", back_populates="photographs")
    plot = relationship("Plot", back_populates="photographs")
    uploader = relationship("User", foreign_keys=[uploaded_by], back_populates="uploaded_photos")

    def __repr__(self) -> str:
        return f"<Photograph(id={self.id}, uuid='{self.uuid}', cemetery_id={self.cemetery_id})>"

    @property
    def is_deleted(self) -> bool:
        """Check if photograph is soft deleted."""
        return self.deleted_at is not None

    @property
    def has_exif(self) -> bool:
        """Check if photograph has any EXIF metadata."""
        return any([
            self.exif_date_taken,
            self.exif_gps_location,
            self.exif_camera_make,
            self.exif_camera_model,
        ])

    @property
    def has_gps(self) -> bool:
        """Check if photograph has GPS coordinates."""
        return self.exif_gps_location is not None

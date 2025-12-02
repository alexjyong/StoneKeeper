"""
Cemetery service for StoneKeeper.

Handles CRUD operations for cemeteries with GPS coordinate normalization
and PostGIS spatial data management.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from geoalchemy2.functions import ST_GeographyFromText
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from src.config import GPS_SRID
from src.models.cemetery import Cemetery
from src.models.photograph import Photograph
from src.models.section import Section
from src.schemas.cemetery import CemeteryCreate, CemeteryUpdate, GPSCoordinates


class CemeteryService:
    """
    Service for managing cemetery records.

    Handles creation, retrieval, updates, and soft deletion of cemeteries
    with GPS coordinate normalization for PostGIS.
    """

    @staticmethod
    def create(db: Session, cemetery_data: CemeteryCreate, user_id: int) -> Cemetery:
        """
        Create a new cemetery record.

        Args:
            db: Database session
            cemetery_data: Cemetery creation data
            user_id: ID of user creating the cemetery

        Returns:
            Created cemetery record

        GPS coordinates are normalized to PostGIS GEOGRAPHY format.
        """
        # Prepare cemetery data
        cemetery_dict = cemetery_data.model_dump(exclude={"gps_location"})
        cemetery_dict["created_by"] = user_id

        # Create cemetery instance
        cemetery = Cemetery(**cemetery_dict)

        # Handle GPS location if provided
        if cemetery_data.gps_location:
            cemetery.gps_location = CemeteryService._normalize_gps(
                cemetery_data.gps_location.latitude,
                cemetery_data.gps_location.longitude
            )

        db.add(cemetery)
        db.commit()
        db.refresh(cemetery)

        return cemetery

    @staticmethod
    def get_by_id(db: Session, cemetery_id: int, include_deleted: bool = False) -> Optional[Cemetery]:
        """
        Get cemetery by ID.

        Args:
            db: Database session
            cemetery_id: Cemetery ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Cemetery if found, None otherwise
        """
        query = db.query(Cemetery).filter(Cemetery.id == cemetery_id)

        if not include_deleted:
            query = query.filter(Cemetery.deleted_at.is_(None))

        return query.first()

    @staticmethod
    def list_cemeteries(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        include_deleted: bool = False
    ) -> Tuple[List[Cemetery], int]:
        """
        List cemeteries with pagination and optional search.

        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            search: Optional search query (searches cemetery name)
            include_deleted: Whether to include soft-deleted records

        Returns:
            Tuple of (list of cemeteries, total count)
        """
        query = db.query(Cemetery)

        # Filter out deleted records unless requested
        if not include_deleted:
            query = query.filter(Cemetery.deleted_at.is_(None))

        # Apply search filter if provided
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Cemetery.name.ilike(search_pattern))

        # Get total count
        total = query.count()

        # Apply pagination
        cemeteries = query.order_by(Cemetery.name).offset(skip).limit(limit).all()

        return cemeteries, total

    @staticmethod
    def update(
        db: Session,
        cemetery_id: int,
        cemetery_data: CemeteryUpdate,
        user_id: int
    ) -> Optional[Cemetery]:
        """
        Update an existing cemetery.

        Args:
            db: Database session
            cemetery_id: Cemetery ID to update
            cemetery_data: Updated cemetery data
            user_id: ID of user performing the update

        Returns:
            Updated cemetery if found, None otherwise

        Only updates fields that are provided (partial updates supported).
        """
        cemetery = CemeteryService.get_by_id(db, cemetery_id)
        if not cemetery:
            return None

        # Update provided fields
        update_data = cemetery_data.model_dump(exclude_unset=True, exclude={"gps_location"})
        for field, value in update_data.items():
            setattr(cemetery, field, value)

        # Handle GPS location update if provided
        if cemetery_data.gps_location is not None:
            cemetery.gps_location = CemeteryService._normalize_gps(
                cemetery_data.gps_location.latitude,
                cemetery_data.gps_location.longitude
            )

        db.commit()
        db.refresh(cemetery)

        return cemetery

    @staticmethod
    def delete(db: Session, cemetery_id: int, user_id: int) -> bool:
        """
        Soft delete a cemetery.

        Args:
            db: Database session
            cemetery_id: Cemetery ID to delete
            user_id: ID of user performing the deletion

        Returns:
            True if deleted, False if not found

        Per Constitution Principle I (Data Integrity First):
        This performs a soft delete by setting deleted_at timestamp.
        The cemetery record and all associations are preserved.
        """
        cemetery = CemeteryService.get_by_id(db, cemetery_id)
        if not cemetery:
            return False

        cemetery.deleted_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def restore(db: Session, cemetery_id: int) -> bool:
        """
        Restore a soft-deleted cemetery.

        Args:
            db: Database session
            cemetery_id: Cemetery ID to restore

        Returns:
            True if restored, False if not found
        """
        cemetery = CemeteryService.get_by_id(db, cemetery_id, include_deleted=True)
        if not cemetery or not cemetery.is_deleted:
            return False

        cemetery.deleted_at = None
        db.commit()

        return True

    @staticmethod
    def get_statistics(db: Session, cemetery_id: int) -> Optional[dict]:
        """
        Get statistics for a cemetery.

        Args:
            db: Database session
            cemetery_id: Cemetery ID

        Returns:
            Dictionary with statistics or None if cemetery not found

        Statistics include:
        - photo_count: Total number of photos
        - section_count: Total number of sections
        - last_photo_uploaded: Timestamp of most recent photo
        """
        cemetery = CemeteryService.get_by_id(db, cemetery_id)
        if not cemetery:
            return None

        # Count photos (excluding deleted)
        photo_count = db.query(func.count(Photograph.id)).filter(
            and_(
                Photograph.cemetery_id == cemetery_id,
                Photograph.deleted_at.is_(None)
            )
        ).scalar()

        # Count sections (excluding deleted)
        section_count = db.query(func.count(Section.id)).filter(
            and_(
                Section.cemetery_id == cemetery_id,
                Section.deleted_at.is_(None)
            )
        ).scalar()

        # Get last photo upload timestamp
        last_photo = db.query(Photograph.created_at).filter(
            and_(
                Photograph.cemetery_id == cemetery_id,
                Photograph.deleted_at.is_(None)
            )
        ).order_by(Photograph.created_at.desc()).first()

        return {
            "photo_count": photo_count or 0,
            "section_count": section_count or 0,
            "last_photo_uploaded": last_photo[0] if last_photo else None
        }

    @staticmethod
    def _normalize_gps(latitude: float, longitude: float) -> str:
        """
        Normalize GPS coordinates to PostGIS GEOGRAPHY format.

        Args:
            latitude: Latitude in decimal degrees (-90 to 90)
            longitude: Longitude in decimal degrees (-180 to 180)

        Returns:
            WKT (Well-Known Text) string for PostGIS GEOGRAPHY

        Format: "SRID=4326;POINT(longitude latitude)"
        Note: PostGIS uses longitude first, then latitude (x, y coordinate order)
        """
        # PostGIS GEOGRAPHY uses WGS84 (SRID 4326) by default
        # Format: POINT(longitude latitude) - note the order!
        return f"SRID={GPS_SRID};POINT({longitude} {latitude})"

    @staticmethod
    def extract_gps_coordinates(geography_wkb) -> Optional[GPSCoordinates]:
        """
        Extract GPS coordinates from PostGIS GEOGRAPHY binary.

        Args:
            geography_wkb: PostGIS GEOGRAPHY value (WKB format)

        Returns:
            GPSCoordinates object or None if no GPS data

        This is used to convert from database GEOGRAPHY type back to
        latitude/longitude for API responses.
        """
        if geography_wkb is None:
            return None

        try:
            # GeoAlchemy2 provides lat/lon properties on the WKB element
            from geoalchemy2.shape import to_shape
            point = to_shape(geography_wkb)
            return GPSCoordinates(
                latitude=point.y,
                longitude=point.x
            )
        except Exception as e:
            print(f"Error extracting GPS coordinates: {e}")
            return None

    @staticmethod
    def find_nearby(
        db: Session,
        latitude: float,
        longitude: float,
        radius_meters: int = 5000,
        limit: int = 10
    ) -> List[Cemetery]:
        """
        Find cemeteries near a GPS location.

        Args:
            db: Database session
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Search radius in meters
            limit: Maximum number of results

        Returns:
            List of cemeteries within radius, sorted by distance

        Uses PostGIS ST_DWithin for efficient spatial search.
        """
        point_wkt = f"SRID={GPS_SRID};POINT({longitude} {latitude})"

        query = db.query(Cemetery).filter(
            and_(
                Cemetery.deleted_at.is_(None),
                Cemetery.gps_location.isnot(None),
                func.ST_DWithin(
                    Cemetery.gps_location,
                    func.ST_GeographyFromText(point_wkt),
                    radius_meters
                )
            )
        ).limit(limit)

        return query.all()

"""
Cemetery schemas for StoneKeeper API.

Pydantic models for cemetery request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class GPSCoordinates(BaseModel):
    """
    GPS coordinates in decimal degrees.

    Uses WGS84 datum (SRID 4326) for compatibility with PostGIS.
    """
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees (-180 to 180)")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


class CemeteryCreate(BaseModel):
    """
    Schema for creating a new cemetery.

    All fields except name are optional to accommodate varying
    levels of information availability.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Cemetery name")
    location_description: Optional[str] = Field(None, description="Text description of location (address, directions)")
    gps_location: Optional[GPSCoordinates] = Field(None, description="GPS coordinates")
    established_year: Optional[int] = Field(None, ge=1500, le=2100, description="Year cemetery was established")
    notes: Optional[str] = Field(None, description="Additional notes or historical information")

    @field_validator('established_year')
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        """Validate established year is reasonable."""
        if v is not None and v > datetime.now().year:
            raise ValueError(f"Established year cannot be in the future")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Green Hills Cemetery",
                "location_description": "123 Main St, Springfield, IL 62701",
                "gps_location": {
                    "latitude": 39.7817,
                    "longitude": -89.6501
                },
                "established_year": 1855,
                "notes": "Historic cemetery established during the Civil War era"
            }
        }


class CemeteryUpdate(BaseModel):
    """
    Schema for updating an existing cemetery.

    All fields are optional to allow partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location_description: Optional[str] = None
    gps_location: Optional[GPSCoordinates] = None
    established_year: Optional[int] = Field(None, ge=1500, le=2100)
    notes: Optional[str] = None

    @field_validator('established_year')
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        """Validate established year is reasonable."""
        if v is not None and v > datetime.now().year:
            raise ValueError(f"Established year cannot be in the future")
        return v


class CemeteryResponse(BaseModel):
    """
    Schema for cemetery response.

    Includes all cemetery data plus computed statistics.
    """
    id: int
    name: str
    location_description: Optional[str] = None
    gps_location: Optional[GPSCoordinates] = None
    established_year: Optional[int] = None
    notes: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Optional statistics (populated when requested)
    photo_count: Optional[int] = Field(None, description="Number of photos in this cemetery")
    section_count: Optional[int] = Field(None, description="Number of sections in this cemetery")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Green Hills Cemetery",
                "location_description": "123 Main St, Springfield, IL 62701",
                "gps_location": {
                    "latitude": 39.7817,
                    "longitude": -89.6501
                },
                "established_year": 1855,
                "notes": "Historic cemetery established during the Civil War era",
                "created_by": 1,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "photo_count": 42,
                "section_count": 5
            }
        }

"""
Photograph schemas for StoneKeeper API.

Pydantic models for photograph request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.cemetery import GPSCoordinates


class EXIFMetadata(BaseModel):
    """
    EXIF metadata extracted from photograph.

    All fields are optional as not all photos contain EXIF data.
    Per Constitution Principle I, EXIF data is preserved exactly as extracted.
    """
    date_taken: Optional[datetime] = Field(None, description="Date and time photo was taken")
    gps_location: Optional[GPSCoordinates] = Field(None, description="GPS coordinates from EXIF")
    camera_make: Optional[str] = Field(None, description="Camera manufacturer")
    camera_model: Optional[str] = Field(None, description="Camera model")
    focal_length: Optional[str] = Field(None, description="Focal length (e.g., '50mm')")
    aperture: Optional[str] = Field(None, description="Aperture value (e.g., 'f/2.8')")
    shutter_speed: Optional[str] = Field(None, description="Shutter speed (e.g., '1/125')")
    iso: Optional[int] = Field(None, description="ISO speed rating")
    image_width: Optional[int] = Field(None, description="Image width in pixels")
    image_height: Optional[int] = Field(None, description="Image height in pixels")

    class Config:
        json_schema_extra = {
            "example": {
                "date_taken": "2024-01-15T14:30:00Z",
                "gps_location": {
                    "latitude": 39.7817,
                    "longitude": -89.6501
                },
                "camera_make": "Canon",
                "camera_model": "EOS 5D Mark IV",
                "focal_length": "50mm",
                "aperture": "f/2.8",
                "shutter_speed": "1/125",
                "iso": 400,
                "image_width": 6720,
                "image_height": 4480
            }
        }


class PhotoUploadMetadata(BaseModel):
    """
    Metadata provided during photo upload.

    Cemetery ID is required; all other associations are optional.
    """
    cemetery_id: int = Field(..., description="Cemetery this photo belongs to")
    section_id: Optional[int] = Field(None, description="Section within cemetery (optional)")
    plot_id: Optional[int] = Field(None, description="Specific plot (optional)")
    description: Optional[str] = Field(None, description="User-provided photo description")
    photographer_notes: Optional[str] = Field(None, description="Additional notes from photographer")

    class Config:
        json_schema_extra = {
            "example": {
                "cemetery_id": 1,
                "section_id": 2,
                "plot_id": 15,
                "description": "Headstone of John Doe, well-preserved inscription",
                "photographer_notes": "Taken in morning light for best clarity"
            }
        }


class PhotographUpdate(BaseModel):
    """
    Schema for updating photograph metadata.

    Allows updating organizational associations and user-provided descriptions.
    EXIF data cannot be modified per Constitution Principle I.
    """
    section_id: Optional[int] = None
    plot_id: Optional[int] = None
    description: Optional[str] = None
    photographer_notes: Optional[str] = None


class PhotographResponse(BaseModel):
    """
    Schema for photograph response.

    Includes all photograph data with EXIF metadata.
    """
    id: int
    uuid: UUID
    cemetery_id: int
    section_id: Optional[int] = None
    plot_id: Optional[int] = None

    # File information
    file_path: str
    thumbnail_path: Optional[str] = None
    preview_path: Optional[str] = None
    file_size_bytes: int
    file_format: str

    # EXIF metadata (nested)
    exif_metadata: Optional[EXIFMetadata] = Field(None, description="Extracted EXIF metadata")

    # User-provided metadata
    description: Optional[str] = None
    photographer_notes: Optional[str] = None

    # Attribution
    uploaded_by: int
    uploader_name: Optional[str] = Field(None, description="Name of user who uploaded photo")

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "cemetery_id": 1,
                "section_id": 2,
                "plot_id": 15,
                "file_path": "/app/photos/2024/01/550e8400-e29b-41d4-a716-446655440000.jpg",
                "thumbnail_path": "/app/photos/2024/01/550e8400-e29b-41d4-a716-446655440000_thumb.jpg",
                "preview_path": "/app/photos/2024/01/550e8400-e29b-41d4-a716-446655440000_preview.jpg",
                "file_size_bytes": 3145728,
                "file_format": "JPEG",
                "exif_metadata": {
                    "date_taken": "2024-01-15T14:30:00Z",
                    "camera_make": "Canon",
                    "camera_model": "EOS 5D Mark IV"
                },
                "description": "Headstone of John Doe",
                "photographer_notes": "Morning light",
                "uploaded_by": 1,
                "uploader_name": "Jane Smith",
                "created_at": "2024-01-15T15:00:00Z",
                "updated_at": "2024-01-15T15:00:00Z"
            }
        }

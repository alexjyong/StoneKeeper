"""
Section schemas for StoneKeeper API.

Pydantic models for section request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SectionCreate(BaseModel):
    """
    Schema for creating a new section within a cemetery.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Section name")
    description: Optional[str] = Field(None, description="Section description")
    display_order: int = Field(0, ge=0, description="Display order (lower numbers appear first)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "North Section",
                "description": "Northern section with veteran graves",
                "display_order": 1
            }
        }


class SectionUpdate(BaseModel):
    """
    Schema for updating an existing section.

    All fields are optional to allow partial updates.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)


class SectionResponse(BaseModel):
    """
    Schema for section response.

    Includes all section data plus optional statistics.
    """
    id: int
    cemetery_id: int
    name: str
    description: Optional[str] = None
    display_order: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Optional statistics
    plot_count: Optional[int] = Field(None, description="Number of plots in this section")
    photo_count: Optional[int] = Field(None, description="Number of photos in this section")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "cemetery_id": 1,
                "name": "North Section",
                "description": "Northern section with veteran graves",
                "display_order": 1,
                "created_by": 1,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "plot_count": 25,
                "photo_count": 18
            }
        }

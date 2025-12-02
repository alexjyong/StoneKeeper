"""
Plot schemas for StoneKeeper API.

Pydantic models for plot request/response validation.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class PlotCreate(BaseModel):
    """
    Schema for creating a new plot within a section.

    All fields are optional to accommodate varying levels
    of information availability.
    """
    plot_number: Optional[str] = Field(None, max_length=50, description="Plot or grave number")
    row_identifier: Optional[str] = Field(None, max_length=50, description="Row identifier")
    headstone_inscription: Optional[str] = Field(None, description="Text from headstone")
    burial_date: Optional[date] = Field(None, description="Date of burial (if known)")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "plot_number": "A-42",
                "row_identifier": "Row 3",
                "headstone_inscription": "John Doe\n1820-1890\nBeloved Father",
                "burial_date": "1890-05-15",
                "notes": "Headstone partially weathered"
            }
        }


class PlotUpdate(BaseModel):
    """
    Schema for updating an existing plot.

    All fields are optional to allow partial updates.
    """
    plot_number: Optional[str] = Field(None, max_length=50)
    row_identifier: Optional[str] = Field(None, max_length=50)
    headstone_inscription: Optional[str] = None
    burial_date: Optional[date] = None
    notes: Optional[str] = None


class PlotResponse(BaseModel):
    """
    Schema for plot response.

    Includes all plot data plus optional statistics.
    """
    id: int
    section_id: int
    plot_number: Optional[str] = None
    row_identifier: Optional[str] = None
    headstone_inscription: Optional[str] = None
    burial_date: Optional[date] = None
    notes: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Optional statistics
    photo_count: Optional[int] = Field(None, description="Number of photos of this plot")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "section_id": 1,
                "plot_number": "A-42",
                "row_identifier": "Row 3",
                "headstone_inscription": "John Doe\n1820-1890\nBeloved Father",
                "burial_date": "1890-05-15",
                "notes": "Headstone partially weathered",
                "created_by": 1,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "photo_count": 3
            }
        }

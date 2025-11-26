"""
Base response schemas for StoneKeeper API.

Provides common response structures for error handling and pagination,
ensuring consistent API responses across all endpoints.
"""
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error response format.

    Used for all API error responses to provide consistent,
    user-friendly error messages per Constitution Principle II.

    Attributes:
        error: Error type or category (e.g., "validation_error", "not_found")
        message: Plain-language error message for non-technical users
        details: Optional additional error details or field-specific errors
    """
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="User-friendly error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "The file you selected is too large. Please choose a file smaller than 20MB.",
                "details": {"field": "file", "max_size": "20MB"}
            }
        }


# Generic type for paginated data
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard pagination response format.

    Used for all list endpoints to provide consistent pagination
    with page information and total counts.

    Attributes:
        items: List of items for current page
        total: Total number of items across all pages
        page: Current page number (1-indexed)
        page_size: Number of items per page
        total_pages: Total number of pages
    """
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "total_pages": 3
            }
        }


class SuccessResponse(BaseModel):
    """
    Standard success response format.

    Used for operations that don't return specific data,
    such as delete operations or status updates.

    Attributes:
        success: Whether operation succeeded
        message: Plain-language success message
    """
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Cemetery deleted successfully"
            }
        }

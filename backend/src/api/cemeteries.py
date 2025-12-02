"""
Cemetery API endpoints for StoneKeeper.

Provides REST API for cemetery CRUD operations.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.base import PaginatedResponse, SuccessResponse
from src.schemas.cemetery import CemeteryCreate, CemeteryResponse, CemeteryUpdate
from src.services.cemetery_service import CemeteryService

router = APIRouter()


@router.post(
    "/",
    response_model=CemeteryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cemetery"
)
def create_cemetery(
    cemetery: CemeteryCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Will be added in User Story 3
) -> CemeteryResponse:
    """
    Create a new cemetery record.

    Accepts cemetery name, location description, GPS coordinates,
    established year, and notes. Only name is required.

    GPS coordinates, if provided, must be valid:
    - Latitude: -90 to 90
    - Longitude: -180 to 180
    """
    # For now, use a placeholder user_id until authentication is implemented (User Story 3)
    # TODO: Replace with current_user.id from authentication
    user_id = 1

    cemetery_obj = CemeteryService.create(db, cemetery, user_id)

    # Convert GPS location from PostGIS to response format
    response = CemeteryResponse.model_validate(cemetery_obj)
    if cemetery_obj.gps_location:
        response.gps_location = CemeteryService.extract_gps_coordinates(cemetery_obj.gps_location)

    return response


@router.get(
    "/",
    response_model=PaginatedResponse[CemeteryResponse],
    summary="List all cemeteries"
)
def list_cemeteries(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search cemetery name"),
    db: Session = Depends(get_db)
) -> PaginatedResponse[CemeteryResponse]:
    """
    List cemeteries with pagination and optional search.

    Search is case-insensitive and searches cemetery names.
    Results are sorted alphabetically by name.
    """
    skip = (page - 1) * page_size

    cemeteries, total = CemeteryService.list_cemeteries(
        db,
        skip=skip,
        limit=page_size,
        search=search
    )

    # Convert to response format
    items = []
    for cemetery_obj in cemeteries:
        response = CemeteryResponse.model_validate(cemetery_obj)
        if cemetery_obj.gps_location:
            response.gps_location = CemeteryService.extract_gps_coordinates(cemetery_obj.gps_location)

        # Add statistics
        stats = CemeteryService.get_statistics(db, cemetery_obj.id)
        if stats:
            response.photo_count = stats["photo_count"]
            response.section_count = stats["section_count"]

        items.append(response)

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{cemetery_id}",
    response_model=CemeteryResponse,
    summary="Get cemetery by ID"
)
def get_cemetery(
    cemetery_id: int,
    db: Session = Depends(get_db)
) -> CemeteryResponse:
    """
    Get detailed information about a specific cemetery.

    Includes cemetery details and statistics:
    - Number of photos in the cemetery
    - Number of sections in the cemetery
    """
    cemetery_obj = CemeteryService.get_by_id(db, cemetery_id)

    if not cemetery_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cemetery not found. The cemetery may have been deleted or the ID is incorrect."
        )

    # Convert to response format
    response = CemeteryResponse.model_validate(cemetery_obj)
    if cemetery_obj.gps_location:
        response.gps_location = CemeteryService.extract_gps_coordinates(cemetery_obj.gps_location)

    # Add statistics
    stats = CemeteryService.get_statistics(db, cemetery_id)
    if stats:
        response.photo_count = stats["photo_count"]
        response.section_count = stats["section_count"]

    return response


@router.patch(
    "/{cemetery_id}",
    response_model=CemeteryResponse,
    summary="Update cemetery"
)
def update_cemetery(
    cemetery_id: int,
    cemetery_update: CemeteryUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Will be added in User Story 3
) -> CemeteryResponse:
    """
    Update an existing cemetery.

    Supports partial updates - only provided fields will be updated.
    All fields are optional.
    """
    # For now, use a placeholder user_id until authentication is implemented
    user_id = 1

    cemetery_obj = CemeteryService.update(db, cemetery_id, cemetery_update, user_id)

    if not cemetery_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cemetery not found. The cemetery may have been deleted or the ID is incorrect."
        )

    # Convert to response format
    response = CemeteryResponse.model_validate(cemetery_obj)
    if cemetery_obj.gps_location:
        response.gps_location = CemeteryService.extract_gps_coordinates(cemetery_obj.gps_location)

    return response


@router.delete(
    "/{cemetery_id}",
    response_model=SuccessResponse,
    summary="Delete cemetery"
)
def delete_cemetery(
    cemetery_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Will be added in User Story 3
) -> SuccessResponse:
    """
    Delete a cemetery (soft delete).

    Per StoneKeeper's Data Integrity principle, this performs a soft delete.
    The cemetery record is marked as deleted but preserved in the database.
    All associated photos, sections, and plots remain accessible.
    """
    # For now, use a placeholder user_id until authentication is implemented
    user_id = 1

    success = CemeteryService.delete(db, cemetery_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cemetery not found. The cemetery may already be deleted or the ID is incorrect."
        )

    return SuccessResponse(
        success=True,
        message="Cemetery deleted successfully. The record has been preserved in the database."
    )

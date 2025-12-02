"""
Photo API endpoints for StoneKeeper.

Provides REST API for photo upload, retrieval, and file serving.
"""
import os
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE_BYTES,
    is_allowed_file_extension,
    is_allowed_mime_type
)
from src.db.session import get_db
from src.models.photograph import Photograph
from src.schemas.photograph import PhotographResponse, EXIFMetadata
from src.services.cemetery_service import CemeteryService
from src.services.exif_service import EXIFService
from src.services.photo_service import PhotoStorageService

router = APIRouter()
photo_storage = PhotoStorageService()


@router.post(
    "/",
    response_model=PhotographResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a cemetery photo"
)
async def upload_photo(
    file: UploadFile = File(..., description="Photo file (JPEG, PNG, or TIFF, max 20MB)"),
    cemetery_id: int = Form(..., description="Cemetery ID this photo belongs to"),
    section_id: Optional[int] = Form(None, description="Section ID (optional)"),
    plot_id: Optional[int] = Form(None, description="Plot ID (optional)"),
    description: Optional[str] = Form(None, description="Photo description"),
    photographer_notes: Optional[str] = Form(None, description="Photographer notes"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Will be added in User Story 3
) -> PhotographResponse:
    """
    Upload a cemetery photograph with automatic EXIF extraction.

    **Validations:**
    - File must be JPEG, PNG, or TIFF format
    - File size must not exceed 20MB
    - Cemetery must exist

    **EXIF Extraction:**
    - Automatically extracts date taken, GPS coordinates, camera info
    - Generates 150x150 thumbnail and 800x600 preview
    - Preserves original file exactly as uploaded

    **Returns:**
    - Photo metadata including extracted EXIF data
    - UUID for accessing photo files
    """
    # For now, use a placeholder user_id until authentication is implemented
    user_id = 1

    # Validate file extension
    if not is_allowed_file_extension(file.filename or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Please upload a JPEG, PNG, or TIFF image. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Validate MIME type
    if not is_allowed_mime_type(file.content_type or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Please upload a JPEG, PNG, or TIFF image. Detected type: {file.content_type}"
        )

    # Validate cemetery exists
    cemetery = CemeteryService.get_by_id(db, cemetery_id)
    if not cemetery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cemetery not found. Please select a valid cemetery."
        )

    # Read file content and validate size
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum file size is {max_mb:.0f}MB. Your file is {file_size / (1024 * 1024):.1f}MB."
        )

    # Save uploaded file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or ".jpg")[1]) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Extract EXIF metadata
        exif_data = EXIFService.extract_metadata(temp_path)

        # Save photo with thumbnails
        file_ext = os.path.splitext(file.filename or ".jpg")[1].lower()
        photo_uuid, original_path, thumbnail_path, preview_path = photo_storage.save_with_thumbnails(
            temp_path,
            file_extension=file_ext
        )

        # Create photograph record
        photograph = Photograph(
            uuid=photo_uuid,
            cemetery_id=cemetery_id,
            section_id=section_id,
            plot_id=plot_id,
            file_path=original_path,
            thumbnail_path=thumbnail_path,
            preview_path=preview_path,
            file_size_bytes=file_size,
            file_format=file_ext.lstrip('.').upper(),
            # EXIF metadata
            exif_date_taken=exif_data.get("date_taken"),
            exif_camera_make=exif_data.get("camera_make"),
            exif_camera_model=exif_data.get("camera_model"),
            exif_focal_length=exif_data.get("focal_length"),
            exif_aperture=exif_data.get("aperture"),
            exif_shutter_speed=exif_data.get("shutter_speed"),
            exif_iso=exif_data.get("iso"),
            image_width=exif_data.get("image_width"),
            image_height=exif_data.get("image_height"),
            # User-provided metadata
            description=description,
            photographer_notes=photographer_notes,
            # Attribution
            uploaded_by=user_id
        )

        # Handle GPS coordinates
        if exif_data.get("gps_latitude") and exif_data.get("gps_longitude"):
            photograph.exif_gps_location = CemeteryService._normalize_gps(
                exif_data["gps_latitude"],
                exif_data["gps_longitude"]
            )

        db.add(photograph)
        db.commit()
        db.refresh(photograph)

        # Build response
        response = PhotographResponse.model_validate(photograph)

        # Add EXIF metadata
        if photograph.has_exif:
            exif_metadata = EXIFMetadata(
                date_taken=photograph.exif_date_taken,
                camera_make=photograph.exif_camera_make,
                camera_model=photograph.exif_camera_model,
                focal_length=photograph.exif_focal_length,
                aperture=photograph.exif_aperture,
                shutter_speed=photograph.exif_shutter_speed,
                iso=photograph.exif_iso,
                image_width=photograph.image_width,
                image_height=photograph.image_height
            )

            if photograph.exif_gps_location:
                exif_metadata.gps_location = CemeteryService.extract_gps_coordinates(photograph.exif_gps_location)

            response.exif_metadata = exif_metadata

        # Add uploader name (for now, placeholder until User Story 3)
        # response.uploader_name = photograph.uploader.full_name

        return response

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get(
    "/{photo_id}",
    response_model=PhotographResponse,
    summary="Get photo metadata"
)
def get_photo(
    photo_id: int,
    db: Session = Depends(get_db)
) -> PhotographResponse:
    """
    Get detailed metadata for a specific photograph.

    Returns all photo information including:
    - File information (size, format, paths)
    - EXIF metadata (if available)
    - User-provided descriptions
    - Uploader attribution
    - Timestamps
    """
    photograph = db.query(Photograph).filter(
        Photograph.id == photo_id,
        Photograph.deleted_at.is_(None)
    ).first()

    if not photograph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found. The photo may have been deleted or the ID is incorrect."
        )

    # Build response
    response = PhotographResponse.model_validate(photograph)

    # Add EXIF metadata
    if photograph.has_exif:
        exif_metadata = EXIFMetadata(
            date_taken=photograph.exif_date_taken,
            camera_make=photograph.exif_camera_make,
            camera_model=photograph.exif_camera_model,
            focal_length=photograph.exif_focal_length,
            aperture=photograph.exif_aperture,
            shutter_speed=photograph.exif_shutter_speed,
            iso=photograph.exif_iso,
            image_width=photograph.image_width,
            image_height=photograph.image_height
        )

        if photograph.exif_gps_location:
            exif_metadata.gps_location = CemeteryService.extract_gps_coordinates(photograph.exif_gps_location)

        response.exif_metadata = exif_metadata

    # Add uploader name (placeholder until User Story 3)
    # response.uploader_name = photograph.uploader.full_name

    return response


@router.get(
    "/{photo_id}/file",
    response_class=FileResponse,
    summary="Get original photo file"
)
def get_photo_file(
    photo_id: int,
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Download the original photo file.

    Returns the full-resolution original image exactly as uploaded.
    """
    photograph = db.query(Photograph).filter(
        Photograph.id == photo_id,
        Photograph.deleted_at.is_(None)
    ).first()

    if not photograph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found."
        )

    if not os.path.exists(photograph.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo file not found on server. Please contact support."
        )

    # Determine media type based on format
    media_type_map = {
        "JPEG": "image/jpeg",
        "JPG": "image/jpeg",
        "PNG": "image/png",
        "TIFF": "image/tiff",
        "TIF": "image/tiff"
    }
    media_type = media_type_map.get(photograph.file_format.upper(), "application/octet-stream")

    return FileResponse(
        photograph.file_path,
        media_type=media_type,
        filename=f"photo_{photograph.uuid}.{photograph.file_format.lower()}"
    )


@router.get(
    "/{photo_id}/thumbnail",
    response_class=FileResponse,
    summary="Get photo thumbnail"
)
def get_photo_thumbnail(
    photo_id: int,
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Get 150x150 thumbnail image.

    Optimized for photo galleries and list views.
    """
    photograph = db.query(Photograph).filter(
        Photograph.id == photo_id,
        Photograph.deleted_at.is_(None)
    ).first()

    if not photograph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found."
        )

    if not photograph.thumbnail_path or not os.path.exists(photograph.thumbnail_path):
        # Fallback to original if thumbnail not available
        if os.path.exists(photograph.file_path):
            return get_photo_file(photo_id, db)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found."
        )

    return FileResponse(
        photograph.thumbnail_path,
        media_type="image/jpeg"
    )


@router.get(
    "/{photo_id}/preview",
    response_class=FileResponse,
    summary="Get photo preview"
)
def get_photo_preview(
    photo_id: int,
    db: Session = Depends(get_db)
) -> FileResponse:
    """
    Get 800x600 preview image.

    Optimized for photo detail views and quick browsing.
    """
    photograph = db.query(Photograph).filter(
        Photograph.id == photo_id,
        Photograph.deleted_at.is_(None)
    ).first()

    if not photograph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found."
        )

    if not photograph.preview_path or not os.path.exists(photograph.preview_path):
        # Fallback to original if preview not available
        if os.path.exists(photograph.file_path):
            return get_photo_file(photo_id, db)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preview not found."
        )

    return FileResponse(
        photograph.preview_path,
        media_type="image/jpeg"
    )

"""
Photo storage service for StoneKeeper.

Handles saving photos to filesystem with UUID-based naming
and organized directory structure by year/month.

Per Constitution Principle I (Data Integrity First):
- Original files are never modified
- Files are organized with UUIDs to prevent naming conflicts
- Thumbnails and previews are separate files
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from uuid import UUID, uuid4

from src.config import UPLOAD_DIR
from src.services.exif_service import EXIFService


class PhotoStorageService:
    """
    Service for managing photo file storage on the filesystem.

    Organizes photos in a year/month directory structure:
    /app/photos/YYYY/MM/uuid.ext
    """

    def __init__(self, base_dir: str = UPLOAD_DIR):
        """
        Initialize photo storage service.

        Args:
            base_dir: Base directory for photo storage
        """
        self.base_dir = Path(base_dir)
        self._ensure_base_dir()

    def _ensure_base_dir(self) -> None:
        """Ensure base directory exists."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_storage_path(self, photo_uuid: UUID, file_extension: str, suffix: str = "") -> Path:
        """
        Get storage path for a photo file.

        Args:
            photo_uuid: UUID for the photo
            file_extension: File extension (e.g., ".jpg")
            suffix: Optional suffix (e.g., "_thumb", "_preview")

        Returns:
            Full path where file should be stored

        Path format: /app/photos/YYYY/MM/uuid[_suffix].ext
        """
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")

        # Create year/month directory
        dir_path = self.base_dir / year / month
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create filename
        filename = f"{photo_uuid}{suffix}{file_extension}"

        return dir_path / filename

    def save_photo(
        self,
        source_path: str,
        photo_uuid: Optional[UUID] = None,
        file_extension: Optional[str] = None
    ) -> Tuple[UUID, str]:
        """
        Save a photo file to storage.

        Args:
            source_path: Path to source file (uploaded file)
            photo_uuid: Optional UUID (will be generated if not provided)
            file_extension: File extension (e.g., ".jpg")

        Returns:
            Tuple of (UUID, storage_path)

        The original file is copied (not moved) to preserve the source.
        """
        # Generate UUID if not provided
        if photo_uuid is None:
            photo_uuid = uuid4()

        # Detect file extension if not provided
        if file_extension is None:
            file_extension = Path(source_path).suffix.lower()

        # Get destination path
        dest_path = self._get_storage_path(photo_uuid, file_extension)

        # Copy file to storage
        # Per Constitution Principle I: We copy, not move, to preserve source
        shutil.copy2(source_path, dest_path)

        return photo_uuid, str(dest_path)

    def save_with_thumbnails(
        self,
        source_path: str,
        photo_uuid: Optional[UUID] = None,
        file_extension: Optional[str] = None
    ) -> Tuple[UUID, str, Optional[str], Optional[str]]:
        """
        Save a photo with thumbnail and preview images.

        Args:
            source_path: Path to source file (uploaded file)
            photo_uuid: Optional UUID (will be generated if not provided)
            file_extension: File extension (e.g., ".jpg")

        Returns:
            Tuple of (UUID, original_path, thumbnail_path, preview_path)

        Thumbnail and preview paths may be None if generation fails.
        Per Constitution Principle III: Failures are handled gracefully;
        if thumbnail generation fails, the original photo is still saved.
        """
        # Save original photo
        photo_uuid, original_path = self.save_photo(source_path, photo_uuid, file_extension)

        # Generate thumbnail
        thumbnail_path = None
        thumb_dest = self._get_storage_path(photo_uuid, ".jpg", "_thumb")
        if EXIFService.generate_thumbnail(original_path, str(thumb_dest)):
            thumbnail_path = str(thumb_dest)

        # Generate preview
        preview_path = None
        preview_dest = self._get_storage_path(photo_uuid, ".jpg", "_preview")
        if EXIFService.generate_preview(original_path, str(preview_dest)):
            preview_path = str(preview_dest)

        return photo_uuid, original_path, thumbnail_path, preview_path

    def delete_photo(self, file_path: str) -> bool:
        """
        Delete a photo file from storage.

        Args:
            file_path: Path to file to delete

        Returns:
            True if successful, False otherwise

        Note: This performs hard delete of the file.
        The database record should use soft delete per Constitution Principle I.
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    def delete_photo_with_thumbnails(self, original_path: str, thumbnail_path: Optional[str], preview_path: Optional[str]) -> bool:
        """
        Delete a photo and its thumbnails.

        Args:
            original_path: Path to original photo
            thumbnail_path: Path to thumbnail (may be None)
            preview_path: Path to preview (may be None)

        Returns:
            True if all files successfully deleted, False otherwise
        """
        success = True

        # Delete original
        if not self.delete_photo(original_path):
            success = False

        # Delete thumbnail if exists
        if thumbnail_path:
            if not self.delete_photo(thumbnail_path):
                success = False

        # Delete preview if exists
        if preview_path:
            if not self.delete_photo(preview_path):
                success = False

        return success

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()

    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return None

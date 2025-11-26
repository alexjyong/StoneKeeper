"""
Configuration constants for StoneKeeper backend.

Centralizes all configuration values for easy maintenance
and ensures consistency across the application.
"""
import os
from typing import Set

# =============================================================================
# File Upload Configuration
# =============================================================================

# Maximum file size for photo uploads (20MB)
MAX_FILE_SIZE_BYTES: int = 20 * 1024 * 1024  # 20MB in bytes

# Allowed image formats for uploads
ALLOWED_FORMATS: Set[str] = {"JPEG", "JPG", "PNG", "TIFF", "TIF"}

# MIME types for allowed formats
ALLOWED_MIME_TYPES: Set[str] = {
    "image/jpeg",
    "image/png",
    "image/tiff"
}

# File extensions for allowed formats
ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".tiff", ".tif"}

# Upload directory (can be overridden by environment variable)
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/photos")

# =============================================================================
# Thumbnail Configuration
# =============================================================================

# Thumbnail size (width x height in pixels)
THUMBNAIL_SIZE: tuple[int, int] = (150, 150)

# Preview size (width x height in pixels)
PREVIEW_SIZE: tuple[int, int] = (800, 600)

# JPEG quality for thumbnails and previews (0-100)
THUMBNAIL_QUALITY: int = 85
PREVIEW_QUALITY: int = 90

# =============================================================================
# Authentication Configuration
# =============================================================================

# Session expiration time in days
SESSION_EXPIRE_DAYS: int = 7

# Session cookie name
SESSION_COOKIE_NAME: str = "stonekeeper_session"

# Password hashing configuration
# Bcrypt rounds for password hashing (higher = more secure but slower)
PASSWORD_BCRYPT_ROUNDS: int = 12

# Minimum password length
MIN_PASSWORD_LENGTH: int = 8

# =============================================================================
# Database Configuration
# =============================================================================

# PostGIS SRID for GPS coordinates (WGS84)
GPS_SRID: int = 4326

# =============================================================================
# Pagination Configuration
# =============================================================================

# Default page size for list endpoints
DEFAULT_PAGE_SIZE: int = 20

# Maximum page size for list endpoints
MAX_PAGE_SIZE: int = 100

# =============================================================================
# Search Configuration
# =============================================================================

# Default search radius for spatial queries (in meters)
DEFAULT_SEARCH_RADIUS_METERS: int = 5000  # 5km

# Maximum search radius for spatial queries (in meters)
MAX_SEARCH_RADIUS_METERS: int = 50000  # 50km

# =============================================================================
# CORS Configuration
# =============================================================================

# Allowed origins for CORS (can be overridden by environment variable)
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS",
    "http://localhost,http://localhost:3000,http://localhost:80"
).split(",")

# =============================================================================
# Application Metadata
# =============================================================================

APP_NAME: str = "StoneKeeper"
APP_VERSION: str = "1.0.0"
APP_DESCRIPTION: str = (
    "Cemetery photo cataloging system with automatic EXIF metadata extraction, "
    "searchable database, and multi-user collaboration."
)

# =============================================================================
# Security Configuration
# =============================================================================

# Secret key for session signing (MUST be set via environment variable in production)
SESSION_SECRET: str = os.getenv("SESSION_SECRET", "")

if not SESSION_SECRET:
    # Try to read from Docker secrets file
    session_secret_file = os.getenv("SESSION_SECRET_FILE")
    if session_secret_file and os.path.exists(session_secret_file):
        with open(session_secret_file, "r") as f:
            SESSION_SECRET = f.read().strip()
    else:
        # Development fallback (NOT secure for production)
        print("WARNING: Using insecure default SESSION_SECRET. Set SESSION_SECRET or SESSION_SECRET_FILE in production!")
        SESSION_SECRET = "insecure-development-secret-change-in-production"

# =============================================================================
# Helper Functions
# =============================================================================

def is_allowed_file_extension(filename: str) -> bool:
    """Check if file has an allowed extension."""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


def is_allowed_mime_type(mime_type: str) -> bool:
    """Check if MIME type is allowed."""
    return mime_type.lower() in ALLOWED_MIME_TYPES

"""
EXIF metadata extraction service for StoneKeeper.

Extracts metadata from images using Pillow and piexif, including:
- Date taken
- GPS coordinates
- Camera information
- Technical settings (aperture, shutter speed, ISO, focal length)
- Image dimensions

Per Constitution Principle I (Data Integrity First):
- EXIF data is extracted exactly as stored in the image
- No modifications or assumptions are made
- Missing data is left as None
"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image
import piexif

from src.config import PREVIEW_QUALITY, PREVIEW_SIZE, THUMBNAIL_QUALITY, THUMBNAIL_SIZE


class EXIFService:
    """
    Service for extracting EXIF metadata from images.

    Uses Pillow for image handling and piexif for EXIF parsing.
    """

    @staticmethod
    def extract_metadata(image_path: str) -> Dict:
        """
        Extract EXIF metadata from an image file.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with extracted metadata. All values may be None if not present.
            Keys: date_taken, gps_latitude, gps_longitude, camera_make, camera_model,
                  focal_length, aperture, shutter_speed, iso, image_width, image_height

        Per Constitution Principle I: Data is extracted exactly as stored,
        with no modifications or assumptions.
        """
        metadata = {
            "date_taken": None,
            "gps_latitude": None,
            "gps_longitude": None,
            "camera_make": None,
            "camera_model": None,
            "focal_length": None,
            "aperture": None,
            "shutter_speed": None,
            "iso": None,
            "image_width": None,
            "image_height": None,
        }

        try:
            with Image.open(image_path) as img:
                # Get image dimensions
                metadata["image_width"] = img.width
                metadata["image_height"] = img.height

                # Get EXIF data
                exif_dict = piexif.load(img.info.get("exif", b""))

                # Extract date taken
                date_taken = EXIFService._extract_date_taken(exif_dict)
                if date_taken:
                    metadata["date_taken"] = date_taken

                # Extract GPS coordinates
                gps_coords = EXIFService._extract_gps(exif_dict)
                if gps_coords:
                    metadata["gps_latitude"] = gps_coords[0]
                    metadata["gps_longitude"] = gps_coords[1]

                # Extract camera information
                camera_info = EXIFService._extract_camera_info(exif_dict)
                metadata.update(camera_info)

                # Extract technical settings
                technical_info = EXIFService._extract_technical_info(exif_dict)
                metadata.update(technical_info)

        except Exception as e:
            # If EXIF extraction fails, return empty metadata
            # Per Constitution Principle II: Handle errors gracefully
            print(f"Warning: Could not extract EXIF from {image_path}: {e}")

        return metadata

    @staticmethod
    def _extract_date_taken(exif_dict: Dict) -> Optional[datetime]:
        """
        Extract date taken from EXIF data.

        Checks multiple EXIF tags in order of preference:
        1. DateTimeOriginal (0x9003) - when photo was taken
        2. DateTimeDigitized (0x9004) - when photo was digitized
        3. DateTime (0x0132) - when file was modified
        """
        exif_ifd = exif_dict.get("Exif", {})

        # Try DateTimeOriginal first (most accurate)
        date_str = exif_ifd.get(piexif.ExifIFD.DateTimeOriginal)
        if not date_str:
            # Try DateTimeDigitized
            date_str = exif_ifd.get(piexif.ExifIFD.DateTimeDigitized)
        if not date_str:
            # Try DateTime as fallback
            date_str = exif_dict.get("0th", {}).get(piexif.ImageIFD.DateTime)

        if date_str:
            try:
                # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                if isinstance(date_str, bytes):
                    date_str = date_str.decode("utf-8")
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except (ValueError, AttributeError):
                pass

        return None

    @staticmethod
    def _extract_gps(exif_dict: Dict) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from EXIF data.

        Returns:
            Tuple of (latitude, longitude) in decimal degrees, or None if not present.
            Uses WGS84 datum (SRID 4326).
        """
        gps_ifd = exif_dict.get("GPS", {})
        if not gps_ifd:
            return None

        try:
            # Get latitude
            lat = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
            lat_ref = gps_ifd.get(piexif.GPSIFD.GPSLatitudeRef)

            # Get longitude
            lon = gps_ifd.get(piexif.GPSIFD.GPSLongitude)
            lon_ref = gps_ifd.get(piexif.GPSIFD.GPSLongitudeRef)

            if not all([lat, lat_ref, lon, lon_ref]):
                return None

            # Convert to decimal degrees
            lat_decimal = EXIFService._dms_to_decimal(lat, lat_ref)
            lon_decimal = EXIFService._dms_to_decimal(lon, lon_ref)

            return (lat_decimal, lon_decimal)

        except Exception:
            return None

    @staticmethod
    def _dms_to_decimal(dms: Tuple, ref: bytes) -> float:
        """
        Convert degrees, minutes, seconds to decimal degrees.

        Args:
            dms: Tuple of ((degrees_num, degrees_den), (minutes_num, minutes_den), (seconds_num, seconds_den))
            ref: Reference direction (b'N', b'S', b'E', b'W')

        Returns:
            Decimal degrees (negative for South/West)
        """
        degrees = dms[0][0] / dms[0][1]
        minutes = dms[1][0] / dms[1][1]
        seconds = dms[2][0] / dms[2][1]

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        # Make negative for South and West
        if isinstance(ref, bytes):
            ref = ref.decode("utf-8")
        if ref in ["S", "W"]:
            decimal = -decimal

        return decimal

    @staticmethod
    def _extract_camera_info(exif_dict: Dict) -> Dict:
        """Extract camera make and model from EXIF."""
        info = {
            "camera_make": None,
            "camera_model": None,
        }

        ifd_0th = exif_dict.get("0th", {})

        make = ifd_0th.get(piexif.ImageIFD.Make)
        if make:
            info["camera_make"] = make.decode("utf-8") if isinstance(make, bytes) else str(make)

        model = ifd_0th.get(piexif.ImageIFD.Model)
        if model:
            info["camera_model"] = model.decode("utf-8") if isinstance(model, bytes) else str(model)

        return info

    @staticmethod
    def _extract_technical_info(exif_dict: Dict) -> Dict:
        """Extract technical photo settings from EXIF."""
        info = {
            "focal_length": None,
            "aperture": None,
            "shutter_speed": None,
            "iso": None,
        }

        exif_ifd = exif_dict.get("Exif", {})

        # Focal length
        focal_length = exif_ifd.get(piexif.ExifIFD.FocalLength)
        if focal_length:
            try:
                fl_value = focal_length[0] / focal_length[1]
                info["focal_length"] = f"{fl_value:.0f}mm"
            except (ZeroDivisionError, TypeError):
                pass

        # Aperture (F-number)
        f_number = exif_ifd.get(piexif.ExifIFD.FNumber)
        if f_number:
            try:
                f_value = f_number[0] / f_number[1]
                info["aperture"] = f"f/{f_value:.1f}"
            except (ZeroDivisionError, TypeError):
                pass

        # Shutter speed (exposure time)
        exposure_time = exif_ifd.get(piexif.ExifIFD.ExposureTime)
        if exposure_time:
            try:
                if exposure_time[0] == 1:
                    info["shutter_speed"] = f"1/{exposure_time[1]}"
                else:
                    ss_value = exposure_time[0] / exposure_time[1]
                    info["shutter_speed"] = f"{ss_value:.2f}s"
            except (ZeroDivisionError, TypeError):
                pass

        # ISO
        iso = exif_ifd.get(piexif.ExifIFD.ISOSpeedRatings)
        if iso:
            info["iso"] = int(iso)

        return info

    @staticmethod
    def generate_thumbnail(image_path: str, output_path: str) -> bool:
        """
        Generate a thumbnail from an image.

        Args:
            image_path: Path to source image
            output_path: Path to save thumbnail

        Returns:
            True if successful, False otherwise

        Thumbnail is 150x150 pixels, maintains aspect ratio with letterboxing.
        Uses LANCZOS resampling for high quality.
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for PNG with transparency, etc.)
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # Create thumbnail maintaining aspect ratio
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                # Save as JPEG
                img.save(output_path, "JPEG", quality=THUMBNAIL_QUALITY, optimize=True)

            return True

        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return False

    @staticmethod
    def generate_preview(image_path: str, output_path: str) -> bool:
        """
        Generate a preview image from an image.

        Args:
            image_path: Path to source image
            output_path: Path to save preview

        Returns:
            True if successful, False otherwise

        Preview is 800x600 pixels, maintains aspect ratio with letterboxing.
        Uses LANCZOS resampling for high quality.
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # Create preview maintaining aspect ratio
                img.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)

                # Save as JPEG
                img.save(output_path, "JPEG", quality=PREVIEW_QUALITY, optimize=True)

            return True

        except Exception as e:
            print(f"Error generating preview: {e}")
            return False

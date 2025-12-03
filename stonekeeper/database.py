"""
Database module for StoneKeeper image tagging application.

Provides SQLite database initialization, queries, and helper functions
for managing image metadata and tags.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional


def init_db(db_path: str = 'stonekeeper.db') -> None:
    """
    Initialize the SQLite database with the images table schema.

    Creates the images table if it doesn't exist with columns:
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - filename: TEXT NOT NULL (original sanitized filename)
    - filepath: TEXT NOT NULL (relative path to stored image)
    - upload_date: TEXT NOT NULL (ISO 8601 timestamp)
    - tags: TEXT NULLABLE (comma-separated lowercase tags)

    Args:
        db_path: Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            tags TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_db(db_path: str = 'stonekeeper.db') -> sqlite3.Connection:
    """
    Get a database connection with row factory configured.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        SQLite connection with Row factory for dict-like access
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_tags(tags_input: str) -> str:
    """
    Normalize tags from user input to consistent storage format.

    Processing steps:
    1. Split by comma
    2. Strip whitespace from each tag
    3. Convert to lowercase
    4. Remove duplicates
    5. Filter empty strings
    6. Join back with commas (no spaces)

    Args:
        tags_input: Comma-separated tag string from user input

    Returns:
        Normalized comma-separated tag string (e.g., "smith,grave,1920s")

    Example:
        normalize_tags("Smith, Grave, 1920s, Smith") -> "smith,grave,1920s"
        normalize_tags("  tag1  ,  tag2  ") -> "tag1,tag2"
        normalize_tags("") -> ""
    """
    if not tags_input or not tags_input.strip():
        return ""

    # Split, strip, lowercase, and deduplicate
    tags = [tag.strip().lower() for tag in tags_input.split(',')]
    unique_tags = []
    seen = set()

    for tag in tags:
        if tag and tag not in seen:
            unique_tags.append(tag)
            seen.add(tag)

    return ','.join(unique_tags)


def save_image(filename: str, filepath: str, tags: str,
               db_path: str = 'stonekeeper.db') -> int:
    """
    Save image metadata to database with normalized tags.

    Args:
        filename: Original sanitized filename
        filepath: Relative path to stored image (e.g., "uploads/123456_image.jpg")
        tags: Comma-separated tags (will be normalized)
        db_path: Path to the SQLite database file

    Returns:
        ID of the inserted image record
    """
    conn = get_db(db_path)
    normalized_tags = normalize_tags(tags)
    upload_date = datetime.now().isoformat()

    cursor = conn.execute(
        'INSERT INTO images (filename, filepath, upload_date, tags) VALUES (?, ?, ?, ?)',
        (filename, filepath, upload_date, normalized_tags)
    )
    image_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return image_id


def search_images_by_tag(tag: str, db_path: str = 'stonekeeper.db') -> List[sqlite3.Row]:
    """
    Search for images matching a specific tag using LIKE query.

    Note: This simplified POC implementation uses LIKE queries which may
    have false positives (e.g., searching "tag" matches "vintage").
    This is acceptable for POC validation and documented in research.md.

    Args:
        tag: Tag to search for (will be normalized to lowercase)
        db_path: Path to the SQLite database file

    Returns:
        List of Row objects with image data (id, filename, filepath, upload_date, tags)
    """
    conn = get_db(db_path)
    normalized_tag = tag.strip().lower()

    # LIKE query for POC - see research.md for migration path to exact matching
    cursor = conn.execute(
        'SELECT id, filename, filepath, upload_date, tags FROM images WHERE tags LIKE ?',
        (f'%{normalized_tag}%',)
    )
    results = cursor.fetchall()
    conn.close()

    return results


def get_tag_summary(db_path: str = 'stonekeeper.db') -> List[Tuple[str, int]]:
    """
    Get summary of all unique tags with usage counts.

    Aggregates tags from all images and returns sorted list by count descending.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        List of tuples (tag_name, count) sorted by count descending

    Example:
        [("smith", 2), ("grave", 1), ("1920s", 1)]
    """
    conn = get_db(db_path)
    cursor = conn.execute(
        "SELECT tags FROM images WHERE tags IS NOT NULL AND tags != ''"
    )

    # Aggregate tags from all images
    all_tags = []
    for row in cursor:
        all_tags.extend(row['tags'].split(','))

    # Count occurrences
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    conn.close()

    # Sort by count descending
    return sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

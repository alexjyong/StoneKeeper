# Data Model: Image Upload and Tag Search

**Feature**: 001-image-tagging
**Created**: 2025-12-03
**Database**: SQLite

## Overview

Simplified single-table design for POC as specified. Stores image metadata and tags as comma-separated text. This approach prioritizes simplicity over normalization per constitutional principle II (Minimal Viable Solution).

## Schema

### Table: `images`

Stores uploaded image metadata and associated tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique image identifier |
| filename | TEXT | NOT NULL | Original filename (sanitized via secure_filename) |
| filepath | TEXT | NOT NULL | Relative path to stored image file (e.g., "uploads/123456_photo.jpg") |
| upload_date | TEXT | NOT NULL | ISO 8601 timestamp of upload (e.g., "2025-12-03T14:30:00") |
| tags | TEXT | NULLABLE | Comma-separated lowercase tags (e.g., "smith,grave,1920s") |

**DDL**:
```sql
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    tags TEXT
);
```

**Indexes**: None required for POC (< 100 rows, minimal performance impact)

## Data Entities (Logical View)

### Image Entity

Represents an uploaded cemetery photograph.

**Attributes**:
- **id**: System-generated unique identifier
- **filename**: User's original filename (e.g., "gravestone_smith.jpg")
- **filepath**: Server storage path (e.g., "uploads/1701616200_gravestone_smith.jpg")
- **upload_date**: When the image was uploaded
- **tags**: Descriptive labels for categorization and search

**Relationships**: None in simplified schema (tags embedded as text)

**Validation Rules** (enforced in application layer):
- filename: Must not be empty, sanitized via `secure_filename()`
- filepath: Must exist on filesystem before database insert
- upload_date: ISO 8601 format, set automatically on upload
- tags: Optional, normalized to lowercase, whitespace trimmed, duplicates removed

**State Lifecycle**:
1. **Created**: Image uploaded to filesystem, record inserted into database
2. **Active**: Image available for search and display
3. **Note**: No deletion state for POC (delete feature out of scope)

### Tag Entity (Virtual)

Tags are not a separate table in the simplified schema, but represent a logical concept.

**Attributes**:
- **name**: Lowercase normalized text (e.g., "smith", "grave", "1920s")
- **image associations**: Derived by parsing comma-separated tags from images table

**Normalization**:
- Convert to lowercase: `tag.lower()`
- Trim whitespace: `tag.strip()`
- Remove duplicates within single image: `set(tags)`
- Stored format: `"tag1,tag2,tag3"` (no spaces after commas)

**Search Behavior**:
- Case-insensitive: Query normalized to lowercase before search
- Exact match (intent): Search for "smith" finds images with tag "smith"
- Implementation note: LIKE query may have false positives (e.g., "smiths", "blacksmith") - acceptable for POC

## Query Patterns

### Insert Image with Tags

```sql
INSERT INTO images (filename, filepath, upload_date, tags)
VALUES (?, ?, ?, ?);
```

**Parameters**:
- filename: `secure_filename(uploaded_file.filename)`
- filepath: `f"uploads/{timestamp}_{secure_filename}"`
- upload_date: `datetime.now().isoformat()`
- tags: `",".join(sorted(set(tag.strip().lower() for tag in tags_input.split(","))))`

### Search Images by Tag

```sql
SELECT id, filename, filepath, upload_date, tags
FROM images
WHERE tags LIKE '%' || ? || '%';
```

**Parameters**:
- tag: `search_query.strip().lower()`

**Limitations** (acceptable for POC):
- False positives: Searching "tag" matches "vintage", "cottage"
- Partial matches: Searching "smith" matches "smiths", "blacksmith"
- Future improvement: Migrate to normalized schema with exact tag matching via JOIN

### Get All Images

```sql
SELECT id, filename, filepath, upload_date, tags
FROM images
ORDER BY upload_date DESC;
```

### Get Tag Summary (Aggregation)

No direct SQL query - computed in application layer:

```python
def get_tag_summary():
    conn = get_db()
    cursor = conn.execute("SELECT tags FROM images WHERE tags IS NOT NULL AND tags != ''")
    all_tags = []
    for row in cursor:
        all_tags.extend(row['tags'].split(','))

    # Count occurrences
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by count descending
    return sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
```

**Note**: This approach works fine for < 100 images. Normalized schema would allow direct SQL aggregation.

## Data Validation

### Application Layer Validation (Before Database Insert)

**File Upload**:
- File selected: `if 'file' not in request.files`
- File has content: `if file.filename == ''`
- File type allowed: `allowed_file(file.filename)` checks extension in `{png, jpg, jpeg, gif}`
- File size limit: Flask `MAX_CONTENT_LENGTH = 10 * 1024 * 1024`

**Tags Input**:
- Empty tags allowed: `tags = ''` if no input provided
- Normalization: Split by comma, strip whitespace, lowercase, deduplicate
- Max length: No hard limit for POC (SQLite TEXT type handles large strings)

**Filename**:
- Sanitization: `secure_filename()` removes path separators and special characters
- Uniqueness: Prepend timestamp to prevent collisions

### Database Constraints

Minimal constraints for POC:
- `NOT NULL` on filename, filepath, upload_date (required fields)
- `NULLABLE` on tags (images can exist without tags)
- `PRIMARY KEY` on id (automatic uniqueness)

**Note**: No foreign key constraints (single table), no unique constraints (duplicates allowed).

## Migration Path (Future)

**Current Schema** (POC):
```
images: [id, filename, filepath, upload_date, tags (CSV)]
```

**Future Normalized Schema**:
```
images: [id, filename, filepath, upload_date]
tags: [id, name (unique)]
image_tags: [image_id, tag_id] (many-to-many junction table)
```

**Migration Strategy** (when needed):
1. Create `tags` and `image_tags` tables
2. Parse existing CSV tags from `images.tags` column
3. Insert unique tags into `tags` table
4. Create associations in `image_tags` table
5. Drop `images.tags` column (or keep for rollback)

**Benefits of Migration**:
- Exact tag matching (no false positives)
- Efficient tag counts via SQL aggregation
- Tag rename/merge capabilities
- Referential integrity via foreign keys

**When to Migrate**: When search accuracy becomes more important than implementation simplicity (likely post-POC if product continues).

## Sample Data

```sql
INSERT INTO images (filename, filepath, upload_date, tags) VALUES
('smith_headstone.jpg', 'uploads/1701616200_smith_headstone.jpg', '2025-12-03T10:30:00', 'smith,grave,1920s'),
('jones_monument.jpg', 'uploads/1701616300_jones_monument.jpg', '2025-12-03T10:35:00', 'jones,monument,1950s'),
('family_plot.jpg', 'uploads/1701616400_family_plot.jpg', '2025-12-03T10:40:00', 'smith,family,plot');
```

**Query Examples**:
- Search "smith": Returns rows 1 and 3
- Search "monument": Returns row 2
- Search "grave": Returns row 1
- Tag summary: `smith:2, grave:1, 1920s:1, jones:1, monument:1, 1950s:1, family:1, plot:1`

## Summary

Data model implements simplified single-table approach per user specification. Aligns with constitutional principles of POC-First and Minimal Viable Solution. Migration path documented for future normalization when needed.

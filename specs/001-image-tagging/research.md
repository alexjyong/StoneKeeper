# Research: Image Upload and Tag Search

**Feature**: 001-image-tagging
**Created**: 2025-12-03
**Purpose**: Document technical decisions and research findings for POC implementation

## Technology Stack Decisions

### Decision: Python 3.11+ with Flask

**Rationale**:
- Flask is minimal web framework (aligns with constitutional principle II: Minimal Viable Solution)
- Built-in development server for POC
- Jinja2 templating included (no additional dependencies)
- Werkzeug included for secure file uploads
- Well-documented, widely used for POC/prototype development

**Alternatives Considered**:
- **Django**: Rejected - too heavyweight for POC, includes many unused features (auth, admin, ORM)
- **FastAPI**: Rejected - async capabilities unnecessary for POC, requires additional frontend tooling
- **Plain Python + http.server**: Rejected - no file upload utilities, would require manual implementation

### Decision: SQLite with Simplified Schema

**Rationale**:
- Included in Python standard library (zero dependencies)
- File-based database (no server setup required)
- Sufficient for < 1000 images (POC scale per spec)
- Simple migration path to PostgreSQL if needed later

**Schema Approach**: Simplified single-table design per user input, storing tags as comma-separated text in single column rather than normalized many-to-many relationship.

**Trade-offs**:
- **Chosen (Simplified)**: Single `images` table with columns `id, filename, filepath, upload_date, tags`
  - Pros: Minimal complexity, easy to implement and query for POC
  - Cons: Tag search requires LIKE queries, duplicate tag storage, harder to get tag counts
- **Alternative (Normalized)**: Three tables `images`, `tags`, `image_tags` with many-to-many relationship
  - Pros: Proper normalization, efficient tag queries, accurate tag counts
  - Cons: Adds complexity for POC, requires JOIN queries, more code to manage relationships

**Decision**: Use simplified single-table approach per user directive. This aligns with constitution but note in quickstart.md that tag search will use SQL LIKE for POC and can be optimized later.

**Alternatives Considered**:
- **PostgreSQL**: Rejected - requires server setup, overkill for POC
- **JSON file**: Rejected - no query capabilities, poor search performance
- **In-memory dict**: Rejected - data loss on restart, not suitable even for POC

### Decision: Local Filesystem for Image Storage

**Rationale**:
- Simplest approach for POC (aligns with constitutional principles)
- No external dependencies or cloud services required
- Direct file path storage in database
- Flask can serve uploaded files via static route

**Storage Location**: `uploads/` directory in project root (gitignored)

**Alternatives Considered**:
- **Database BLOB storage**: Rejected - increases database size, slower retrieval, complicates backups
- **Cloud storage (S3, etc.)**: Rejected - out of scope for POC, adds external dependencies
- **Base64 in database**: Rejected - inefficient, large database size

## Flask Implementation Patterns

### File Upload Best Practices

**Secure Filename Handling**:
```python
from werkzeug.utils import secure_filename
# Sanitizes user-provided filenames to prevent directory traversal
```

**File Type Validation**:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

**File Size Limiting**:
```python
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
```

**Source**: Flask documentation on file uploads - standard pattern for production and POC

### Database Connection Pattern

For POC, use simple connection pattern without connection pooling:

```python
import sqlite3

def get_db():
    conn = sqlite3.connect('stonekeeper.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn
```

**Note**: SQLite handles concurrent reads well but write contention can occur. For single-user POC, this is not a concern.

### Tag Processing

**Tag Normalization**:
- Trim whitespace: `tag.strip()`
- Lowercase for case-insensitive search: `tag.lower()`
- Remove duplicate tags from same image: `set(tags)`
- Store as comma-separated: `','.join(tags)`

**Tag Search with Simplified Schema**:
```python
# Since tags stored as comma-separated string, use LIKE queries
SELECT * FROM images WHERE tags LIKE '%' || ? || '%'
```

**Caveat**: This approach has false positives (searching "tag" would match "vintage"). For POC validation this is acceptable. Document in quickstart.md for future improvement.

## Security Considerations (POC Context)

**Implemented for POC**:
- Filename sanitization (prevent directory traversal)
- File type validation (prevent upload of executables)
- File size limits (prevent disk exhaustion)

**Deferred (Out of Scope for POC)**:
- Authentication/Authorization (single-user POC)
- CSRF protection (no sensitive operations)
- SQL injection protection via parameterized queries (standard practice - will implement)
- Rate limiting (single-user, local deployment)
- Image virus scanning (POC assumes trusted user)

## Frontend Approach

### Decision: Plain HTML + Minimal JavaScript

**Rationale**:
- Jinja2 templates render server-side (no build step required)
- Standard HTML form submission for uploads (no async required for POC)
- Minimal JavaScript only for UX enhancements (optional)
- Browser-native file input handling

**Alternatives Considered**:
- **React**: Rejected - requires build tooling, npm dependencies, overkill for 3 pages
- **Vue/Alpine.js**: Rejected - unnecessary for simple forms
- **HTMX**: Rejected - additional dependency, POC doesn't need dynamic updates

### Page Structure

**upload.html**:
- HTML form with `enctype="multipart/form-data"`
- File input (`<input type="file" accept="image/*">`)
- Text input for comma-separated tags
- Submit button triggers POST to `/upload`

**search.html**:
- Simple text input for tag search query
- Submit button triggers GET to `/search?tag=...`
- Links to upload page and tag summary

**results.html** (or inline in search.html):
- Display matching images using `<img>` tags
- Show associated tags for each image
- Link back to search page

## Performance Expectations

**POC Scale** (per spec assumptions):
- < 100 images
- < 1000 total tags
- Single concurrent user
- Local filesystem access

**Expected Performance**:
- Upload: < 5 seconds for 10MB image (dependent on disk speed)
- Search: < 2 seconds (per success criteria) - achievable with SQLite LIKE query on < 100 records
- Tag summary: < 1 second (simple string split and count aggregation)

**No Optimization Needed for POC**:
- No indexing on tags column (not beneficial for < 100 rows)
- No caching layer (data set too small)
- No thumbnail generation (out of scope)
- No pagination (< 100 results displayable on single page)

## Development Environment Setup

**Prerequisites**:
```bash
python3 --version  # Verify 3.11+
pip --version      # Verify pip available
```

**Installation**:
```bash
pip install Flask  # Installs Flask + Werkzeug + Jinja2
```

**Database Initialization**:
- Create schema on first run via Python script
- SQLite file created automatically when first connection made

**Running Application**:
```bash
python app.py      # Flask development server on localhost:5000
```

## Migration Path (Future Considerations)

**Document but don't implement**:

1. **Database Schema Evolution**:
   - Current: Single table with comma-separated tags
   - Future: Migrate to proper many-to-many with `images`, `tags`, `image_tags` tables
   - Tool: Simple Python migration script using SQL ALTER/CREATE statements

2. **Search Improvements**:
   - Current: SQL LIKE queries (potential false positives)
   - Future: Exact tag matching with JOIN queries, full-text search, tag autocomplete

3. **Production Readiness**:
   - Current: Flask development server
   - Future: Production WSGI server (Gunicorn), proper error logging, monitoring

**Note**: Per constitution principle III (Expand Later), document these paths but don't implement until needed.

## Open Questions Resolved

**Q: How to handle duplicate tag entries for same image?**
A: Use Python `set()` to deduplicate before storing as comma-separated string.

**Q: Case sensitivity for tags?**
A: Store lowercase, search lowercase (normalize both on input and query).

**Q: Empty tag input handling?**
A: Allow images with no tags (tags column can be empty string or NULL).

**Q: Image filename collisions?**
A: Append timestamp to secure_filename output: `f"{timestamp}_{secure_filename(file.filename)}"`.

**Q: What happens if uploads/ directory doesn't exist?**
A: Create directory in initialization code if not exists: `os.makedirs('uploads', exist_ok=True)`.

## Summary

All technical decisions align with StoneKeeper constitution:
- **POC-First**: Minimal feature set, simplest working implementation
- **Minimal Viable Solution**: Flask + SQLite + HTML, no unnecessary libraries
- **Expand Later**: Documented migration paths without implementing unused features

Implementation can proceed to Phase 1 (data model and contracts).

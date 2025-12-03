# API Routes Specification

**Feature**: 001-image-tagging
**Created**: 2025-12-03
**Type**: Flask HTML Application (Form-based, not REST API)

## Overview

This document specifies the HTTP routes for the StoneKeeper image tagging POC. Routes follow Flask conventions with Jinja2 template rendering. All routes serve HTML pages or handle form submissions.

## Base URL

```
http://localhost:5000
```

## Routes

### 1. Upload Page (GET)

**Endpoint**: `/` or `/upload`
**Method**: `GET`
**Purpose**: Display image upload and tagging form

**Request**: None

**Response**:
- **Status**: 200 OK
- **Content-Type**: text/html
- **Template**: `upload.html`
- **Body**: HTML page with:
  - File input for image selection (`accept="image/*"`)
  - Text input for comma-separated tags
  - Submit button
  - Links to search and tag summary pages

**Example**:
```
GET / HTTP/1.1
Host: localhost:5000
```

---

### 2. Upload Image (POST)

**Endpoint**: `/upload`
**Method**: `POST`
**Purpose**: Handle image upload and tag storage

**Request**:
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file` (required): Image file (JPEG, PNG, GIF)
  - `tags` (optional): Comma-separated tag string (e.g., "smith, grave, 1920s")

**Validation**:
- File must be present
- File must have allowed extension (png, jpg, jpeg, gif)
- File size must be ≤ 10MB (enforced by Flask `MAX_CONTENT_LENGTH`)
- Tags are optional but if provided, will be normalized (trim, lowercase, deduplicate)

**Success Response**:
- **Status**: 200 OK or 302 Redirect
- **Content-Type**: text/html
- **Template**: `upload.html` with success message OR redirect to `/`
- **Body**: Success message "Image uploaded successfully!" and form reset

**Error Responses**:
- **Status**: 400 Bad Request
- **Content-Type**: text/html
- **Template**: `upload.html` with error message
- **Error Cases**:
  - "No file selected" - file field empty
  - "Invalid file type" - extension not in allowed list
  - "File too large" - exceeds 10MB limit (handled by Flask)

**Processing Steps**:
1. Validate file presence and type
2. Generate unique filename: `{timestamp}_{secure_filename(filename)}`
3. Save file to `uploads/` directory
4. Normalize tags: split by comma, strip whitespace, lowercase, deduplicate
5. Insert record into database with filename, filepath, upload_date, tags
6. Return success message or redirect

**Example**:
```
POST /upload HTTP/1.1
Host: localhost:5000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="smith.jpg"
Content-Type: image/jpeg

[binary image data]
------WebKitFormBoundary
Content-Disposition: form-data; name="tags"

Smith, grave, 1920s
------WebKitFormBoundary--
```

---

### 3. Search Page (GET)

**Endpoint**: `/search`
**Method**: `GET`
**Purpose**: Display tag search form and results

**Request**:
- **Query Parameters**:
  - `tag` (optional): Tag to search for (e.g., "smith")

**Response (No Query Parameter)**:
- **Status**: 200 OK
- **Content-Type**: text/html
- **Template**: `search.html`
- **Body**: HTML page with:
  - Text input for tag search
  - Submit button
  - Links to upload and tag summary pages
  - No results displayed

**Response (With Query Parameter)**:
- **Status**: 200 OK
- **Content-Type**: text/html
- **Template**: `search.html` with results
- **Body**: HTML page with:
  - Search form (pre-filled with query)
  - Results section showing:
    - Matching images (as `<img>` tags pointing to `/uploads/{filename}`)
    - Tags for each image
    - Count of results found
  - Message "No images found" if no matches

**Query Processing**:
1. Normalize search query: strip whitespace, lowercase
2. Query database: `SELECT * FROM images WHERE tags LIKE '%{tag}%'`
3. Return matching images with metadata

**Examples**:
```
GET /search HTTP/1.1
Host: localhost:5000
```

```
GET /search?tag=smith HTTP/1.1
Host: localhost:5000
```

---

### 4. Tag Summary Page (GET)

**Endpoint**: `/tags` or `/tag-summary`
**Method**: `GET`
**Purpose**: Display all unique tags with usage counts

**Request**: None

**Response**:
- **Status**: 200 OK
- **Content-Type**: text/html
- **Template**: `tags.html` or inline in search/upload pages
- **Body**: HTML page with:
  - List of all unique tags
  - Count of images using each tag
  - Tags sorted by count (descending) or alphabetically
  - Message "No tags yet" if database empty

**Processing**:
1. Query all images: `SELECT tags FROM images WHERE tags IS NOT NULL`
2. Parse comma-separated tags from each row
3. Aggregate counts using Python dict
4. Sort by count descending
5. Render as HTML list or table

**Example**:
```
GET /tags HTTP/1.1
Host: localhost:5000
```

**Example Response Data**:
```
smith: 2 images
grave: 1 image
1920s: 1 image
jones: 1 image
monument: 1 image
```

---

### 5. Serve Uploaded Images (GET)

**Endpoint**: `/uploads/{filename}`
**Method**: `GET`
**Purpose**: Serve uploaded image files

**Request**:
- **Path Parameters**:
  - `filename` (required): Name of uploaded file (e.g., "1701616200_smith.jpg")

**Success Response**:
- **Status**: 200 OK
- **Content-Type**: `image/jpeg`, `image/png`, or `image/gif` (based on extension)
- **Body**: Binary image data

**Error Response**:
- **Status**: 404 Not Found
- **Body**: "File not found" if image doesn't exist

**Security**: Flask's `send_from_directory()` prevents directory traversal attacks

**Example**:
```
GET /uploads/1701616200_smith.jpg HTTP/1.1
Host: localhost:5000
```

---

## Route Summary Table

| Route | Method | Purpose | Template | User Story |
|-------|--------|---------|----------|-----------|
| `/` or `/upload` | GET | Display upload form | upload.html | US1 |
| `/upload` | POST | Handle image upload | upload.html | US1 |
| `/search` | GET | Display search form + results | search.html | US2 |
| `/tags` | GET | Display tag summary | tags.html | US3 |
| `/uploads/{file}` | GET | Serve uploaded images | N/A (static) | US1, US2 |

## Error Handling

### Global Error Handlers

**404 Not Found**:
- Custom error page with link back to upload page
- Occurs when user navigates to undefined route

**413 Request Entity Too Large**:
- Triggered by Flask when file exceeds `MAX_CONTENT_LENGTH`
- Error message: "File too large (max 10MB)"

**500 Internal Server Error**:
- Generic error page for unexpected failures
- For POC: simple error message, no detailed logging
- Production: would include error tracking and logging

### Validation Errors

All validation errors return 400 Bad Request with HTML error page showing:
- Clear error message
- Original form with user's input (except file - must reselect)
- Suggestion for how to fix

## Non-Functional Requirements

**Performance**:
- Upload response: < 5 seconds for 10MB file
- Search response: < 2 seconds for database with < 100 images (per success criteria)
- Tag summary: < 1 second

**Security** (POC Level):
- Filename sanitization via `secure_filename()`
- File type validation by extension
- File size limit enforcement
- SQL injection prevention via parameterized queries
- No authentication (single-user POC)

**Browser Compatibility**:
- Modern browsers (Chrome, Firefox, Safari, Edge)
- HTML5 file input support
- No IE11 support required for POC

## Future Enhancements (Out of Scope)

- RESTful JSON API for `/api/images`, `/api/search`, `/api/tags`
- Pagination for search results
- Image deletion endpoint (`DELETE /images/{id}`)
- Tag editing endpoint (`PUT /images/{id}/tags`)
- Bulk upload endpoint (`POST /upload/bulk`)
- Tag autocomplete API (`GET /api/tags/autocomplete?q=...`)

## Implementation Notes

**Flask Route Decorators**:
```python
@app.route('/', methods=['GET'])
@app.route('/upload', methods=['GET', 'POST'])
@app.route('/search', methods=['GET'])
@app.route('/tags', methods=['GET'])
```

**Template Variables**:
- `upload.html`: `success_message`, `error_message`
- `search.html`: `query`, `results`, `result_count`
- `tags.html`: `tag_summary` (list of tuples: [(tag, count), ...])

**Database Access**:
- All routes use `get_db()` helper to obtain SQLite connection
- Connections closed after request via Flask teardown handler
- No ORM (direct SQL via sqlite3 module)

## Testing Contract

**Manual Testing Checklist**:
1. Navigate to `/` - upload form displays
2. Submit form without file - error message appears
3. Upload image with tags "test,demo" - success message appears
4. Navigate to `/search?tag=test` - uploaded image appears in results
5. Navigate to `/tags` - "test" and "demo" appear with count "1"
6. Click on image in results - image displays correctly

**Acceptance Criteria Mapping**:
- Route `/upload` POST → Fulfills FR-001 through FR-007
- Route `/search` GET → Fulfills FR-008 through FR-011
- Route `/tags` GET → Fulfills FR-012

All routes align with feature specification requirements and constitutional principles.

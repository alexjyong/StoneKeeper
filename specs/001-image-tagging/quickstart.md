# QuickStart Guide: Image Upload and Tag Search

**Feature**: 001-image-tagging
**Created**: 2025-12-03
**Purpose**: Step-by-step guide to set up, run, and test the POC

## Prerequisites

Before starting, verify you have:

1. **Python 3.11 or higher**
   ```bash
   python3 --version
   # Should output: Python 3.11.x or higher
   ```

2. **pip (Python package manager)**
   ```bash
   pip --version
   # Should output: pip 23.x or similar
   ```

3. **Git** (if cloning repository)
   ```bash
   git --version
   ```

4. **Web browser** (Chrome, Firefox, Safari, or Edge)

## Installation

### Step 1: Navigate to Project Directory

```bash
cd /workspaces/StoneKeeper
```

### Step 2: Install Dependencies

```bash
pip install Flask
```

This installs Flask along with its included dependencies:
- Werkzeug (file upload handling)
- Jinja2 (HTML templating)
- Click (CLI support)

**Note**: For POC, we're using system/user Python. Production deployments would use virtual environment.

### Step 3: Create Project Structure

Create the necessary directories:

```bash
mkdir -p stonekeeper/templates
mkdir -p stonekeeper/static
mkdir -p stonekeeper/uploads
```

**Directory Structure**:
```
stonekeeper/
├── app.py              # Main Flask application (to be created)
├── database.py         # Database initialization (to be created)
├── templates/          # Jinja2 HTML templates (to be created)
│   ├── upload.html
│   ├── search.html
│   └── tags.html
├── static/             # CSS/JS files (optional for POC)
│   └── style.css
└── uploads/            # Uploaded images (created, gitignored)
```

### Step 4: Initialize Database

The database will be created automatically on first run of `app.py`. Schema is defined in `database.py`:

```sql
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    tags TEXT
);
```

Database file: `stonekeeper.db` (SQLite, created in project root)

## Running the Application

### Step 1: Start Flask Development Server

```bash
cd stonekeeper
python app.py
```

**Expected Output**:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Step 2: Open Browser

Navigate to:
```
http://localhost:5000
```

You should see the upload page with:
- File selection button
- Tags input field
- Upload button
- Links to search and tag summary pages

## Testing the POC

### Test Scenario 1: Upload Image with Tags (User Story 1)

**Objective**: Verify image upload and tagging functionality

1. **Navigate to Upload Page**:
   - URL: `http://localhost:5000/` or `http://localhost:5000/upload`
   - Verify form displays correctly

2. **Select Image File**:
   - Click "Choose File" button
   - Select a JPEG, PNG, or GIF image from your computer
   - Image should appear in file input (filename visible)

3. **Enter Tags**:
   - In tags input field, type: `Smith, grave, 1920s`
   - Tags can be entered with or without spaces after commas

4. **Submit Form**:
   - Click "Upload" button
   - Wait for response (should be < 5 seconds)

5. **Verify Success**:
   - Success message should appear: "Image uploaded successfully!"
   - Form should reset (file input cleared)
   - Database should contain new record:
     ```bash
     sqlite3 stonekeeper.db "SELECT * FROM images;"
     ```

**Expected Database Entry**:
```
1|smith.jpg|uploads/1701616200_smith.jpg|2025-12-03T10:30:00|smith,grave,1920s
```

---

### Test Scenario 2: Search by Tag (User Story 2)

**Objective**: Verify tag-based image search

1. **Navigate to Search Page**:
   - Click "Search" link or navigate to `http://localhost:5000/search`
   - Verify search form displays

2. **Search for Tag**:
   - Enter `smith` in search field (case insensitive)
   - Click "Search" button

3. **Verify Results**:
   - Image from Test Scenario 1 should appear
   - Image should display correctly (clickable to view full size)
   - Tags should be visible: "smith, grave, 1920s"
   - Result count should show: "Found 1 image(s)"

4. **Test Empty Results**:
   - Search for non-existent tag: `nonexistent`
   - Verify message: "No images found for tag 'nonexistent'"

5. **Test Case Insensitivity**:
   - Search for `SMITH` (uppercase)
   - Should return same results as `smith`

**Known Limitation** (acceptable for POC):
- LIKE query may have false positives
- Searching "tag" might match "vintage" or "cottage"
- Documented in research.md for future improvement

---

### Test Scenario 3: View Tag Summary (User Story 3)

**Objective**: Verify tag aggregation and counts

1. **Upload Additional Test Images**:
   - Image 2: Tags = `jones, monument, 1950s`
   - Image 3: Tags = `smith, family, plot`

2. **Navigate to Tag Summary**:
   - Click "Tags" link or navigate to `http://localhost:5000/tags`

3. **Verify Tag List**:
   - Should display all unique tags with counts:
     ```
     smith: 2
     grave: 1
     1920s: 1
     jones: 1
     monument: 1
     1950s: 1
     family: 1
     plot: 1
     ```

4. **Verify Sorting**:
   - Tags should be sorted by count (descending) or alphabetically
   - Most used tags appear first

---

### Test Scenario 4: Error Handling

**Objective**: Verify validation and error messages

**Test 4a: No File Selected**
1. Navigate to upload page
2. Leave file input empty
3. Click "Upload" button
4. **Expected**: Error message "No file selected"

**Test 4b: Invalid File Type**
1. Select a .txt or .pdf file
2. Click "Upload" button
3. **Expected**: Error message "Invalid file type. Allowed: PNG, JPG, JPEG, GIF"

**Test 4c: File Too Large**
1. Select an image > 10MB
2. Click "Upload" button
3. **Expected**: Error message "File too large (max 10MB)"

**Test 4d: Empty Tag Input**
1. Select valid image
2. Leave tags field empty
3. Click "Upload" button
4. **Expected**: Image uploads successfully with no tags (tags = NULL or empty string)

**Test 4e: Special Characters in Tags**
1. Enter tags with special chars: `Smith & Sons, O'Brien, "quoted"`
2. **Expected**: Tags processed (may need escaping depending on implementation)

---

## Validation Checklist

Use this checklist to validate POC against success criteria:

- [ ] **SC-001**: Users can upload image and add tags in < 30 seconds
  - Measured from page load to success message
  - Includes file selection, tag entry, submit, server processing

- [ ] **SC-002**: Search results return in < 2 seconds for up to 100 images
  - Add ~20-50 test images
  - Measure search response time (browser DevTools Network tab)

- [ ] **SC-003**: Users can find images by any assigned tag
  - Upload image with tags "a,b,c"
  - Verify searchable by "a", by "b", and by "c"

- [ ] **SC-004**: 100% of images with tags found through search
  - Upload 10 images with various tags
  - Search for each tag
  - Count: (images found / images uploaded) = 100%

- [ ] **SC-005**: Tag summary reflects all unique tags accurately
  - Compare tag summary with database query:
    ```bash
    sqlite3 stonekeeper.db "SELECT tags FROM images;"
    ```
  - Manually verify counts match

---

## Troubleshooting

### Issue: "ImportError: No module named flask"

**Cause**: Flask not installed

**Solution**:
```bash
pip install Flask
```

---

### Issue: "Permission denied" when creating uploads/ directory

**Cause**: Insufficient file system permissions

**Solution**:
```bash
chmod 755 stonekeeper
mkdir -p stonekeeper/uploads
chmod 755 stonekeeper/uploads
```

---

### Issue: Images not displaying in search results

**Cause**: Incorrect file path or Flask not serving static files

**Solution**:
- Verify images exist: `ls stonekeeper/uploads/`
- Check database filepath: `sqlite3 stonekeeper.db "SELECT filepath FROM images;"`
- Ensure Flask route `/uploads/<filename>` configured with `send_from_directory()`

---

### Issue: Search returns no results even with matching tags

**Cause**: Tag normalization mismatch (case sensitivity, whitespace)

**Solution**:
- Verify tags stored in lowercase: `sqlite3 stonekeeper.db "SELECT tags FROM images;"`
- Verify search query normalized to lowercase in code
- Check for extra whitespace in stored tags

---

### Issue: "Database is locked" error

**Cause**: SQLite connection not closed properly

**Solution**:
- Ensure `conn.close()` called after each database operation
- Or use Flask's `g` object with teardown handler:
  ```python
  @app.teardown_appcontext
  def close_db(error):
      if hasattr(g, 'db'):
          g.db.close()
  ```

---

### Issue: File uploads fail silently

**Cause**: Missing `enctype="multipart/form-data"` in form

**Solution**:
- Verify upload form HTML:
  ```html
  <form action="/upload" method="POST" enctype="multipart/form-data">
  ```

---

## Next Steps After POC Validation

Once all test scenarios pass and success criteria met:

1. **Document Findings**:
   - What worked well?
   - What was more complex than expected?
   - Performance observations
   - User experience notes

2. **Identify Improvements** (for post-POC):
   - Migrate to normalized database schema (research.md migration path)
   - Add pagination for search results
   - Implement tag autocomplete
   - Add image thumbnails
   - Deploy to production server (Gunicorn + nginx)

3. **Security Hardening** (if moving beyond POC):
   - Add authentication/authorization
   - Implement CSRF protection
   - Add rate limiting
   - Scan uploaded images for malware
   - Use prepared statements everywhere (already should be doing this)

4. **Expand Features** (if POC successful):
   - Image deletion
   - Tag editing
   - EXIF data extraction and display
   - Advanced search (boolean operators, multiple tags)
   - Export functionality

## Development Workflow

**Making Changes**:
1. Stop Flask server (Ctrl+C)
2. Edit Python/HTML/CSS files
3. Restart Flask server: `python app.py`
4. Refresh browser to see changes

**Testing Changes**:
- Manual testing via browser (per constitution - tests optional)
- Check browser DevTools Console for JavaScript errors
- Check terminal output for Flask errors

**Database Changes**:
- For POC, drop and recreate table if schema changes needed:
  ```bash
  sqlite3 stonekeeper.db "DROP TABLE images;"
  ```
- Restart app to recreate table with new schema
- Production would use migration scripts (alembic, etc.)

## Configuration

**Flask Development Server**:
- Host: `127.0.0.1` (localhost only)
- Port: `5000` (default)
- Debug mode: `True` for POC (auto-reload on code changes)

**File Upload Limits**:
- Max file size: 10MB (`app.config['MAX_CONTENT_LENGTH']`)
- Allowed extensions: png, jpg, jpeg, gif
- Upload directory: `stonekeeper/uploads/`

**Database**:
- File: `stonekeeper.db`
- Type: SQLite
- Location: Project root (same directory as app.py)

## Summary

This quickstart guide provides everything needed to:
- Install and run the StoneKeeper POC
- Test all three user stories
- Validate success criteria
- Troubleshoot common issues
- Plan next steps

For implementation details, see:
- [plan.md](./plan.md) - Overall implementation plan
- [data-model.md](./data-model.md) - Database schema and queries
- [contracts/routes.md](./contracts/routes.md) - API routes specification
- [research.md](./research.md) - Technical decisions and best practices

**Ready to implement**: All design artifacts complete. Proceed to `/speckit.tasks` to generate implementation tasks.

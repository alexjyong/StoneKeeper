# StoneKeeper

A web application for cataloging cemetery photographs with tag-based search.

## POC Overview

This is a proof-of-concept implementation focused on core functionality:
- Upload cemetery photographs with comma-separated tags
- Search for images by tag name
- View tag summary with usage counts

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Navigate to the stonekeeper directory:
```bash
cd stonekeeper
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and visit:
```
http://localhost:5000
```

### Using StoneKeeper

1. **Upload Images**:
   - Navigate to the Upload page (default home page)
   - Select an image file (PNG, JPG, JPEG, or GIF, max 10MB)
   - Enter comma-separated tags (e.g., "Smith, grave, 1920s")
   - Click Upload

2. **Search Images**:
   - Navigate to the Search page
   - Enter a tag to search for
   - View matching images with their tags

3. **View Tag Summary**:
   - Navigate to the Tag Summary page
   - See all unique tags with usage counts
   - Click any tag to search for images with that tag

## Project Structure

```
stonekeeper/
├── app.py              # Flask application and routes
├── database.py         # Database schema and queries
├── templates/          # HTML templates
│   ├── upload.html    # Upload page
│   ├── search.html    # Search page
│   └── tags.html      # Tag summary page
├── static/            # CSS and static assets
│   └── style.css      # Stylesheet
└── uploads/           # Uploaded images (gitignored)
```

## Technology Stack

- **Backend**: Python 3.11+ with Flask
- **Database**: SQLite (single table design for POC)
- **Frontend**: HTML with Jinja2 templates, vanilla CSS
- **File Handling**: Werkzeug (included with Flask)

## Database Schema

Simplified single-table design for POC:

```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    tags TEXT  -- comma-separated lowercase tags
);
```

## Known Limitations (POC)

- **Tag Search**: Uses SQL LIKE queries which may have false positives (e.g., searching "tag" might match "vintage"). See `specs/001-image-tagging/research.md` for migration path to exact matching.
- **Single User**: No authentication or multi-user support
- **No Tag Editing**: Cannot edit or delete tags after upload
- **No Image Deletion**: Cannot delete uploaded images
- **Local Storage**: Images stored on local filesystem only

## Manual Testing

Test scenarios are documented in `specs/001-image-tagging/quickstart.md`.

Basic validation:
1. Upload an image with tags "Smith, grave, 1920s"
2. Search for "Smith" and verify the image appears
3. View tag summary and verify all 3 tags appear with count of 1

## Development

This POC follows the StoneKeeper constitution principles:
- **POC-First**: Simplest working implementation
- **Minimal Viable Solution**: No premature optimization
- **Expand Later**: Migration paths documented but not implemented

For detailed design documentation, see:
- `specs/001-image-tagging/plan.md` - Implementation plan
- `specs/001-image-tagging/spec.md` - Feature specification
- `specs/001-image-tagging/data-model.md` - Database design
- `specs/001-image-tagging/research.md` - Technical decisions

## Future Enhancements

Potential improvements documented in design artifacts:
- Normalized database schema (proper many-to-many relationships)
- Exact tag matching (eliminate false positives)
- Image deletion and tag editing
- Authentication and multi-user support
- EXIF data extraction
- Advanced search (boolean operators, multiple tags)
- Image thumbnails

## License

POC for cemetery photograph cataloging.

## Contributing

This is a proof-of-concept implementation. Future development will depend on POC validation results.

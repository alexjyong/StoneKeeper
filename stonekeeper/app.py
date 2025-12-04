"""
Flask application for StoneKeeper image tagging POC.

Provides web interface for uploading images with tags,
searching by tags, and viewing tag summaries.
"""

import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

# Import database functions
from database import init_db, save_image, search_images_by_tag, get_tag_summary


# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    """
    Check if uploaded file has an allowed extension.

    Args:
        filename: Name of the uploaded file

    Returns:
        True if file extension is in ALLOWED_EXTENSIONS, False otherwise

    Example:
        allowed_file("image.jpg") -> True
        allowed_file("document.pdf") -> False
        allowed_file("no_extension") -> False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename: str) -> str:
    """
    Generate unique filename by prepending timestamp to secure filename.

    Args:
        filename: Original filename from user upload

    Returns:
        Unique filename with format: {timestamp}_{secure_filename}

    Example:
        generate_unique_filename("my photo.jpg") -> "1701616200_my_photo.jpg"
    """
    timestamp = int(datetime.now().timestamp())
    secure_name = secure_filename(filename)
    return f"{timestamp}_{secure_name}"


# Initialize database on startup
init_db()

# Ensure uploads directory exists
os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)


# Routes

@app.route('/')
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Handle image upload page (GET) and form submission (POST).

    GET: Display upload form with file input and tags input
    POST: Process uploaded image, save to filesystem and database

    Returns:
        GET: Rendered upload.html template
        POST: Rendered upload.html with success/error message
    """
    if request.method == 'POST':
        # Validation: Check if file part exists in request
        if 'file' not in request.files:
            return render_template('upload.html', error_message='No file selected')

        file = request.files['file']

        # Validation: Check if filename is empty
        if file.filename == '':
            return render_template('upload.html', error_message='No file selected')

        # Validation: Check if file type is allowed
        if not allowed_file(file.filename):
            return render_template('upload.html',
                                 error_message='Invalid file type. Allowed: PNG, JPG, JPEG, GIF')

        # Process file upload
        unique_filename = generate_unique_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        full_path = os.path.join(app.root_path, filepath)

        # Save file to filesystem
        file.save(full_path)

        # Get tags from form (optional)
        tags = request.form.get('tags', '')

        # Save to database
        save_image(file.filename, filepath, tags)

        return render_template('upload.html',
                             success_message='Image uploaded successfully!')

    # GET request - display upload form
    return render_template('upload.html')


@app.route('/search', methods=['GET'])
def search():
    """
    Handle image search by tag with optional query parameter.

    Query parameter 'tag' is optional:
    - If provided: Search for images matching the tag
    - If empty/missing: Display empty search form

    Returns:
        Rendered search.html template with optional results
    """
    tag_query = request.args.get('tag', '').strip()

    if tag_query:
        # Search for images matching the tag
        results = search_images_by_tag(tag_query)
        return render_template('search.html',
                             query=tag_query,
                             results=results,
                             result_count=len(results))
    else:
        # Display empty search form
        return render_template('search.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve uploaded image files from the uploads directory.

    Args:
        filename: Name of the uploaded file

    Returns:
        Image file served from uploads directory

    Note:
        Uses send_from_directory for security (prevents directory traversal)
    """
    uploads_dir = os.path.join(app.root_path, UPLOAD_FOLDER)
    return send_from_directory(uploads_dir, filename)


@app.route('/tags', methods=['GET'])
def tags():
    """
    Display tag summary page with all unique tags and usage counts.

    Returns:
        Rendered tags.html template with tag summary data
    """
    tag_summary = get_tag_summary()
    return render_template('tags.html', tag_summary=tag_summary)


# Error Handlers

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    return render_template('upload.html',
                         error_message='Page not found. Redirected to upload page.'), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors (file size exceeded)."""
    return render_template('upload.html',
                         error_message='File too large (max 10MB)'), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    return render_template('upload.html',
                         error_message='An unexpected error occurred. Please try again.'), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

# Data Model: Cemetery Photo Cataloging System

**Feature**: 001-photo-cataloging
**Date**: 2025-11-26
**Database**: PostgreSQL 15+ with PostGIS 3.3+ extension

## Overview

This document defines the complete database schema for the StoneKeeper cemetery photo cataloging system. The schema supports photo management, cemetery organization, spatial queries, user management, and audit trails.

## Schema Principles

1. **Data Integrity First**: All timestamps are timezone-aware (TIMESTAMPTZ), soft deletes preserve data, foreign key constraints enforce referential integrity
2. **Spatial Support**: PostGIS GEOGRAPHY type for GPS coordinates with SRID 4326 (WGS84)
3. **Audit Trail**: All tables include created_at, updated_at, and track user actions
4. **Soft Deletes**: deleted_at column prevents data loss (Constitution Principle I)
5. **Unicode Support**: VARCHAR columns use UTF-8 encoding for international characters

## Extensions Required

```sql
-- Enable PostGIS for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Core Entities

### 1. Users

Researchers and administrators who use the cataloging system.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hash
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    CONSTRAINT users_email_lowercase CHECK (email = LOWER(email))
);

COMMENT ON TABLE users IS 'Cemetery researchers and system users';
COMMENT ON COLUMN users.password_hash IS 'bcrypt hashed password, never store plaintext';
COMMENT ON COLUMN users.deleted_at IS 'Soft delete timestamp - NULL means active user';

-- Indexes
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;
```

**Relationships**:
- One user uploads many photographs
- One user creates many sessions

**Validation Rules**:
- Email must be valid format and lowercase
- Password must be bcrypt hashed (never plaintext)
- Full name required (for photographer attribution)

**State Transitions**:
- Created (is_active=true, deleted_at=NULL)
- Deactivated (is_active=false)
- Deleted (deleted_at=NOW())

---

### 2. User Sessions

Authentication sessions for logged-in users.

```sql
CREATE TABLE user_sessions (
    id VARCHAR(255) PRIMARY KEY,  -- Random secure token
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address INET,  -- IPv4/IPv6 support
    user_agent VARCHAR(500),

    CONSTRAINT user_sessions_valid_expiry CHECK (expires_at > created_at)
);

COMMENT ON TABLE user_sessions IS 'Active authentication sessions';
COMMENT ON COLUMN user_sessions.id IS 'Secure random session token (32+ bytes)';
COMMENT ON COLUMN user_sessions.ip_address IS 'Client IP address for security audit';

-- Indexes
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);

-- Automatic cleanup of expired sessions (can be run as cron job)
-- DELETE FROM user_sessions WHERE expires_at < NOW();
```

**Relationships**:
- Many sessions belong to one user

**Validation Rules**:
- Session ID must be cryptographically secure random token
- Expires_at must be in the future
- Last_activity updated on each request

**Session Lifecycle**:
1. Created on login (expires_at = NOW() + 7 days)
2. Updated on each request (last_activity = NOW())
3. Expired when expires_at < NOW()
4. Deleted on logout or expiration

---

### 3. Cemeteries

Physical cemetery locations being documented.

```sql
CREATE TABLE cemeteries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    location_description TEXT,  -- City, state, country
    gps_location GEOGRAPHY(POINT, 4326),  -- WGS84 coordinates
    established_year INTEGER,  -- Year cemetery was established
    notes TEXT,  -- Additional information
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    CONSTRAINT cemeteries_valid_year CHECK (
        established_year IS NULL OR
        (established_year >= 1600 AND established_year <= EXTRACT(YEAR FROM NOW()))
    )
);

COMMENT ON TABLE cemeteries IS 'Physical cemetery locations';
COMMENT ON COLUMN cemeteries.gps_location IS 'PostGIS GEOGRAPHY for accurate global distance calculations';
COMMENT ON COLUMN cemeteries.established_year IS 'Year cemetery was established, if known';

-- Indexes
CREATE INDEX idx_cemeteries_name ON cemeteries(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_cemeteries_location ON cemeteries USING GIST(gps_location);
CREATE INDEX idx_cemeteries_created_by ON cemeteries(created_by);

-- Full-text search index for cemetery names
CREATE INDEX idx_cemeteries_name_trgm ON cemeteries USING gin(name gin_trgm_ops);
```

**Relationships**:
- One cemetery contains many sections
- One cemetery has many photographs
- One cemetery created by one user

**Validation Rules**:
- Name required
- GPS location optional (may not always be available)
- Established year must be reasonable (1600-present)

**Spatial Queries**:
```sql
-- Find cemeteries within 10km of coordinates
SELECT name, ST_Distance(gps_location, ST_MakePoint(-122.4194, 37.7749)::geography) as distance_meters
FROM cemeteries
WHERE ST_DWithin(gps_location, ST_MakePoint(-122.4194, 37.7749)::geography, 10000)
ORDER BY distance_meters;
```

---

### 4. Sections

Subdivisions within a cemetery (e.g., "Section A", "Veterans Area").

```sql
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    cemetery_id INTEGER NOT NULL REFERENCES cemeteries(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,  -- For ordering in UI
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(cemetery_id, name, deleted_at)  -- Unique section names per cemetery
);

COMMENT ON TABLE sections IS 'Cemetery subdivisions (sections, areas, blocks)';
COMMENT ON COLUMN sections.display_order IS 'Order for displaying sections in UI (0 = first)';

-- Indexes
CREATE INDEX idx_sections_cemetery ON sections(cemetery_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_sections_created_by ON sections(created_by);
CREATE INDEX idx_sections_order ON sections(cemetery_id, display_order);
```

**Relationships**:
- Many sections belong to one cemetery
- One section contains many plots
- One section has many photographs

**Validation Rules**:
- Name required
- Cemetery_id required (section must belong to a cemetery)
- Unique section names within a cemetery (excluding soft-deleted)

**Hierarchical Queries**:
```sql
-- Get cemetery with section counts
SELECT c.name, COUNT(s.id) as section_count
FROM cemeteries c
LEFT JOIN sections s ON c.id = s.cemetery_id AND s.deleted_at IS NULL
WHERE c.deleted_at IS NULL
GROUP BY c.id, c.name;
```

---

### 5. Plots

Specific burial locations within a section.

```sql
CREATE TABLE plots (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    plot_number VARCHAR(100) NOT NULL,  -- Plot identifier (e.g., "A-123", "Row 5, Plot 12")
    row_identifier VARCHAR(100),  -- Row within section, if applicable
    headstone_inscription TEXT,  -- Transcribed text from headstone
    burial_date DATE,  -- Date of burial, if known
    notes TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    UNIQUE(section_id, plot_number, deleted_at)  -- Unique plot numbers per section
);

COMMENT ON TABLE plots IS 'Individual burial plots within cemetery sections';
COMMENT ON COLUMN plots.plot_number IS 'Human-readable plot identifier (e.g., "A-123")';
COMMENT ON COLUMN plots.headstone_inscription IS 'Transcribed text from headstone';
COMMENT ON COLUMN plots.burial_date IS 'Date of burial if known, can be NULL';

-- Indexes
CREATE INDEX idx_plots_section ON plots(section_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_plots_plot_number ON plots(section_id, plot_number);
CREATE INDEX idx_plots_burial_date ON plots(burial_date) WHERE burial_date IS NOT NULL;
CREATE INDEX idx_plots_created_by ON plots(created_by);

-- Full-text search on inscriptions
CREATE INDEX idx_plots_inscription_trgm ON plots USING gin(headstone_inscription gin_trgm_ops);
```

**Relationships**:
- Many plots belong to one section
- One plot may have multiple photographs

**Validation Rules**:
- Plot_number required
- Section_id required (plot must belong to a section)
- Unique plot numbers within a section
- Burial_date optional (may not always be known)

**Search Queries**:
```sql
-- Search plots by inscription text
SELECT p.*, s.name as section_name, c.name as cemetery_name
FROM plots p
JOIN sections s ON p.section_id = s.id
JOIN cemeteries c ON s.cemetery_id = c.id
WHERE p.headstone_inscription ILIKE '%Smith%'
  AND p.deleted_at IS NULL;
```

---

### 6. Photographs

Cemetery photo files with metadata.

```sql
CREATE TABLE photographs (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,  -- For file naming
    cemetery_id INTEGER NOT NULL REFERENCES cemeteries(id) ON DELETE RESTRICT,
    section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
    plot_id INTEGER REFERENCES plots(id) ON DELETE SET NULL,

    -- File storage
    file_path VARCHAR(500) NOT NULL UNIQUE,  -- Path to original file
    file_size_bytes BIGINT NOT NULL,
    file_format VARCHAR(10) NOT NULL,  -- JPEG, PNG, TIFF

    -- EXIF metadata (extracted from photo)
    exif_date_taken TIMESTAMPTZ,  -- When photo was taken (from EXIF)
    exif_gps_location GEOGRAPHY(POINT, 4326),  -- GPS from EXIF
    exif_camera_make VARCHAR(100),
    exif_camera_model VARCHAR(100),
    exif_focal_length NUMERIC(5,1),  -- mm
    exif_aperture VARCHAR(10),  -- e.g., "f/2.8"
    exif_shutter_speed VARCHAR(20),  -- e.g., "1/1000"
    exif_iso INTEGER,
    image_width INTEGER NOT NULL,
    image_height INTEGER NOT NULL,

    -- Thumbnail paths
    thumbnail_path VARCHAR(500),  -- 150x150 thumbnail
    preview_path VARCHAR(500),  -- 800x600 preview

    -- User-provided metadata
    description TEXT,
    photographer_notes TEXT,

    -- Tracking
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ DEFAULT NULL,

    CONSTRAINT photographs_valid_size CHECK (file_size_bytes > 0 AND file_size_bytes <= 20971520),  -- Max 20MB
    CONSTRAINT photographs_valid_format CHECK (file_format IN ('JPEG', 'PNG', 'TIFF')),
    CONSTRAINT photographs_valid_dimensions CHECK (image_width > 0 AND image_height > 0)
);

COMMENT ON TABLE photographs IS 'Cemetery photographs with EXIF metadata';
COMMENT ON COLUMN photographs.uuid IS 'UUID for file naming (avoids path traversal issues)';
COMMENT ON COLUMN photographs.file_path IS 'Path to original file: /photos/{year}/{month}/{uuid}.{ext}';
COMMENT ON COLUMN photographs.exif_gps_location IS 'GPS coordinates from EXIF metadata';
COMMENT ON COLUMN photographs.file_size_bytes IS 'Original file size in bytes (max 20MB per FR-003)';
COMMENT ON COLUMN photographs.deleted_at IS 'Soft delete - original files preserved';

-- Indexes
CREATE INDEX idx_photos_cemetery ON photographs(cemetery_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_photos_section ON photographs(section_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_photos_plot ON photographs(plot_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_photos_uploaded_by ON photographs(uploaded_by);
CREATE INDEX idx_photos_date_taken ON photographs(exif_date_taken) WHERE exif_date_taken IS NOT NULL;
CREATE INDEX idx_photos_gps_location ON photographs USING GIST(exif_gps_location) WHERE exif_gps_location IS NOT NULL;
CREATE INDEX idx_photos_created_at ON photographs(created_at);

-- Full-text search on descriptions and notes
CREATE INDEX idx_photos_description_trgm ON photographs USING gin(description gin_trgm_ops);
CREATE INDEX idx_photos_notes_trgm ON photographs USING gin(photographer_notes gin_trgm_ops);
```

**Relationships**:
- Many photographs belong to one cemetery
- Many photographs may belong to one section (optional)
- Many photographs may belong to one plot (optional)
- Many photographs uploaded by one user

**Validation Rules**:
- Cemetery_id required (photo must belong to a cemetery)
- Section_id and plot_id optional (not all photos are plot-specific)
- File_size_bytes max 20MB (per edge case spec)
- File_format must be JPEG, PNG, or TIFF
- UUID generated automatically for file naming security
- All EXIF fields optional (not all photos have metadata)

**File Naming Convention**:
```
Original: /app/photos/2023/11/{uuid}.jpg
Thumbnail: /app/photos/2023/11/{uuid}_thumbnail.jpg
Preview: /app/photos/2023/11/{uuid}_preview.jpg
```

**Search Queries**:
```sql
-- Search photos by cemetery name and date range
SELECT p.*, c.name as cemetery_name, u.full_name as photographer
FROM photographs p
JOIN cemeteries c ON p.cemetery_id = c.id
JOIN users u ON p.uploaded_by = u.id
WHERE c.name ILIKE '%oak%'
  AND p.exif_date_taken BETWEEN '2023-01-01' AND '2023-12-31'
  AND p.deleted_at IS NULL
ORDER BY p.exif_date_taken DESC;

-- Find photos within geographic area
SELECT p.*, c.name as cemetery_name,
       ST_Distance(p.exif_gps_location, ST_MakePoint(-122.4194, 37.7749)::geography) as distance_meters
FROM photographs p
JOIN cemeteries c ON p.cemetery_id = c.id
WHERE p.exif_gps_location IS NOT NULL
  AND ST_DWithin(p.exif_gps_location, ST_MakePoint(-122.4194, 37.7749)::geography, 50000)  -- 50km
  AND p.deleted_at IS NULL
ORDER BY distance_meters;
```

---

## Database Views

### Cemetery Statistics View

Provides photo counts and coverage statistics per cemetery.

```sql
CREATE OR REPLACE VIEW cemetery_statistics AS
SELECT
    c.id,
    c.name,
    c.location_description,
    c.gps_location,
    COUNT(DISTINCT s.id) as section_count,
    COUNT(DISTINCT p.id) as plot_count,
    COUNT(DISTINCT ph.id) as photo_count,
    MAX(ph.created_at) as last_photo_uploaded,
    COUNT(DISTINCT ph.uploaded_by) as contributor_count
FROM cemeteries c
LEFT JOIN sections s ON c.id = s.cemetery_id AND s.deleted_at IS NULL
LEFT JOIN plots p ON s.id = p.section_id AND p.deleted_at IS NULL
LEFT JOIN photographs ph ON c.id = ph.cemetery_id AND ph.deleted_at IS NULL
WHERE c.deleted_at IS NULL
GROUP BY c.id, c.name, c.location_description, c.gps_location;

COMMENT ON VIEW cemetery_statistics IS 'Summary statistics for each cemetery';
```

**Usage**:
```sql
-- Get cemetery with photo counts
SELECT name, photo_count, last_photo_uploaded
FROM cemetery_statistics
ORDER BY photo_count DESC;
```

---

## Database Functions

### Update Timestamp Trigger

Automatically updates the updated_at column on row modifications.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cemeteries_updated_at BEFORE UPDATE ON cemeteries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plots_updated_at BEFORE UPDATE ON plots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_photographs_updated_at BEFORE UPDATE ON photographs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION update_updated_at_column IS 'Automatically set updated_at to NOW() on UPDATE';
```

---

## Migration Strategy

### Initial Migration (001_initial_schema.sql)

1. Create extensions (PostGIS, uuid-ossp)
2. Create tables in dependency order:
   - users
   - user_sessions
   - cemeteries
   - sections
   - plots
   - photographs
3. Create indexes
4. Create views
5. Create triggers

### Rollback Procedure

All migrations must include DOWN migration:

```sql
-- Down migration (reverse order)
DROP TRIGGER IF EXISTS update_photographs_updated_at ON photographs;
-- ... (drop all triggers)
DROP VIEW IF EXISTS cemetery_statistics;
DROP TABLE IF EXISTS photographs CASCADE;
DROP TABLE IF EXISTS plots CASCADE;
DROP TABLE IF EXISTS sections CASCADE;
DROP TABLE IF EXISTS cemeteries CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP EXTENSION IF EXISTS postgis;
DROP EXTENSION IF EXISTS "uuid-ossp";
```

---

## Data Integrity Constraints

### Foreign Key Cascade Rules

- **ON DELETE CASCADE**: sessions (when user deleted), sections (when cemetery deleted), plots (when section deleted)
- **ON DELETE RESTRICT**: photographs (cannot delete cemetery with photos - must soft delete)
- **ON DELETE SET NULL**: photograph.section_id, photograph.plot_id (allow section/plot deletion while preserving photos)

### Check Constraints

- Email must be lowercase
- Passwords must be bcrypt hashed (enforced in application layer)
- File size max 20MB
- File format must be JPEG, PNG, or TIFF
- Image dimensions must be positive
- Cemetery established_year must be reasonable (1600-present)
- Session expires_at must be after created_at

### Unique Constraints

- user.email (excluding soft-deleted)
- section.name per cemetery (excluding soft-deleted)
- plot.plot_number per section (excluding soft-deleted)
- photograph.uuid (globally unique)
- photograph.file_path (globally unique)

---

## Performance Optimization

### Index Strategy

1. **B-tree indexes**: Primary keys, foreign keys, frequently filtered columns (email, dates)
2. **GiST indexes**: Spatial data (gps_location) for distance queries
3. **GIN indexes**: Full-text search using trigram similarity (pg_trgm extension)
4. **Partial indexes**: Include `WHERE deleted_at IS NULL` to exclude soft-deleted records

### Query Optimization Tips

```sql
-- Good: Uses spatial index
SELECT * FROM cemeteries
WHERE ST_DWithin(gps_location, ST_MakePoint(-122, 37)::geography, 10000);

-- Bad: Forces full table scan
SELECT * FROM cemeteries
WHERE ST_Distance(gps_location, ST_MakePoint(-122, 37)::geography) < 10000;

-- Good: Uses partial index
SELECT * FROM photographs
WHERE cemetery_id = 123 AND deleted_at IS NULL;

-- Good: Uses GIN trigram index
SELECT * FROM cemeteries
WHERE name ILIKE '%oak%' AND deleted_at IS NULL;
```

### Maintenance

```sql
-- Run after bulk imports to update statistics
ANALYZE;

-- Vacuum to reclaim space from soft deletes
VACUUM ANALYZE;

-- Reindex if indexes become fragmented
REINDEX TABLE photographs;
```

---

## Security Considerations

### Row-Level Security (Future Enhancement)

PostgreSQL Row-Level Security (RLS) can be added to restrict user access to specific cemeteries or organizations:

```sql
-- Enable RLS on photographs table
ALTER TABLE photographs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see photos from their organization
CREATE POLICY photo_access ON photographs
    FOR SELECT
    USING (cemetery_id IN (
        SELECT cemetery_id FROM user_cemetery_access WHERE user_id = current_user_id()
    ));
```

### Audit Logging (Future Enhancement)

Consider adding audit table to track all modifications:

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL,  -- INSERT, UPDATE, DELETE
    user_id INTEGER REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    old_values JSONB,
    new_values JSONB
);
```

---

## Sample Data

### Test Data Script

```sql
-- Create test user
INSERT INTO users (email, password_hash, full_name)
VALUES ('test@example.com', '$2b$12$...', 'Test Researcher');

-- Create test cemetery
INSERT INTO cemeteries (name, location_description, gps_location, created_by)
VALUES (
    'Oak Hill Cemetery',
    'Springfield, Illinois, USA',
    ST_GeogFromText('POINT(-89.6501 39.7817)'),  -- Springfield, IL
    1  -- test user ID
);

-- Create test section
INSERT INTO sections (cemetery_id, name, description, created_by)
VALUES (1, 'Section A', 'Original section established 1850', 1);

-- Create test plot
INSERT INTO plots (section_id, plot_number, row_identifier, created_by)
VALUES (1, 'A-101', 'Row 1', 1);

-- Create test photograph
INSERT INTO photographs (
    cemetery_id, section_id, plot_id,
    file_path, file_size_bytes, file_format,
    image_width, image_height,
    exif_date_taken, exif_gps_location,
    description, uploaded_by
) VALUES (
    1, 1, 1,
    '/photos/2023/11/abc123-uuid.jpg',
    5242880,  -- 5MB
    'JPEG',
    4032, 3024,  -- 12MP
    '2023-11-15 14:30:00+00',
    ST_GeogFromText('POINT(-89.6501 39.7817)'),
    'Front view of Smith family headstone',
    1
);
```

---

## ER Diagram (Text Representation)

```
users (1) ----< (M) photographs
users (1) ----< (M) user_sessions
users (1) ----< (M) cemeteries (created_by)
users (1) ----< (M) sections (created_by)
users (1) ----< (M) plots (created_by)

cemeteries (1) ----< (M) sections
sections (1) ----< (M) plots

cemeteries (1) ----< (M) photographs
sections (1) ----< (M) photographs [optional]
plots (1) ----< (M) photographs [optional]
```

---

## Next Steps

1. Create Alembic migration files based on this schema
2. Add seed data for development/testing
3. Document backup/restore procedures
4. Implement database connection pooling in FastAPI
5. Add database monitoring and alerting
6. Plan for future enhancements (RLS, audit logging, replication)

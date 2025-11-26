# Technology Research & Recommendations: StoneKeeper Cemetery Photo Cataloging System

## Executive Summary

This document provides technology recommendations for the StoneKeeper cemetery photo cataloging system based on extensive research of current best practices, performance characteristics, and alignment with the project's constitutional principles (Data Integrity First, Non-Technical User Focus, Maintainability & Simplicity, and Preservation-Grade Documentation).

---

## 1. EXIF Extraction Libraries (Python)

### Recommendation: **Pillow (PIL) + piexif**

Use Pillow as the primary library for image operations and EXIF reading, combined with piexif for write operations and comprehensive metadata manipulation.

### Rationale

1. **Metadata Integrity**: Pillow's `getexif()` method (available in Pillow 6.x+) provides reliable read access to EXIF data. When combined with piexif, you get full read/write capabilities while preserving metadata integrity.

2. **Format Support**: Pillow natively supports JPEG, PNG, and TIFF formats (all required by FR-001), with robust handling of EXIF data across these formats.

3. **GPS Extraction**: Both Pillow and piexif can extract GPS coordinates through the GPSInfo IFD (Image File Directory). Pillow's `get_ifd()` method provides clean access to GPS tags.

4. **Preservation Capability**: When saving images with Pillow, you can explicitly pass EXIF data to the `save()` method to ensure metadata preservation: `image.save(path, exif=exif_data)`.

5. **Simplicity**: Pillow is already widely used, well-documented, and has minimal dependencies (aligns with Constitution Principle III: Maintainability & Simplicity).

6. **Active Maintenance**: Pillow is actively maintained with regular security updates (aligns with Security & Privacy requirements).

### Alternatives Considered

**exifread**:
- **Pros**: Simple, read-only library with good GPS support
- **Cons**: Read-only (cannot write EXIF), returns dict format that requires conversion for PIL, limited functionality for preservation requirements
- **Verdict**: Insufficient for metadata preservation requirements (FR-002, FR-003)

**piexif alone**:
- **Pros**: Pure Python, full read/write support, OS-independent
- **Cons**: Less intuitive API, requires more code for basic operations, no image manipulation capabilities
- **Verdict**: Better as a complement to Pillow rather than standalone

### Trade-offs

**Gains**:
- Single ecosystem (Pillow) for both image operations and EXIF reading
- Reliable metadata preservation with explicit control
- Well-documented with extensive community support
- Performance optimizations in modern Pillow versions (2.7+)

**Losses**:
- Requires two libraries instead of one (Pillow + piexif) for full write support
- Slightly more complex code for write operations compared to read-only solutions
- Need to explicitly handle EXIF data during save operations

**Performance Note**: Modern Pillow (2.7+) has dramatically improved performance (up to 20x faster than ImageMagick for resizing operations), meeting the <5 second upload requirement for 5-10MB images.

---

## 2. Image Storage Strategy

### Recommendation: **Local Filesystem with Docker Named Volumes**

Store original photographs on the local filesystem using Docker named volumes, with database references to file paths. Plan for future S3-compatible object storage as an optional feature.

### Rationale

1. **Simplicity**: Local filesystem storage is straightforward to implement, backup, and restore (aligns with Constitution Principle III: Maintainability & Simplicity).

2. **EXIF Preservation**: Direct file storage ensures original files remain completely unmodified with all EXIF metadata intact (Constitution Principle I: Data Integrity First).

3. **Performance**: Local filesystem provides lowest latency for photo uploads and retrieval, easily meeting the <5 second upload and <2 second page load requirements.

4. **Self-Hosted Philosophy**: For self-hosted deployments (Docker-based, SC-007), local storage eliminates external dependencies and reduces operational complexity.

5. **Backup Simplicity**: Docker volumes can be backed up using standard Docker commands or filesystem-level backup tools, with straightforward restore procedures.

6. **Scale Appropriate**: For target scale of 100,000 photos at average 5-10MB (500GB-1TB), local storage is entirely practical and cost-effective.

### Alternatives Considered

**S3-Compatible Object Storage**:
- **Pros**: Highly scalable, built-in redundancy, geographic distribution
- **Cons**: Adds complexity, external dependency, higher latency, overkill for self-hosted single-server deployments
- **Verdict**: Better suited as optional future enhancement for large multi-server deployments

**Database BYTEA Storage**:
- **Pros**: Transactional consistency, single backup source
- **Cons**: Database bloat, poor performance, complicates database maintenance, goes against standard practices
- **Verdict**: Not recommended for large binary files

### Trade-offs

**Gains**:
- Lowest latency for photo access
- Simple backup/restore procedures
- No external service dependencies
- Direct file access for debugging and data recovery
- Zero ongoing costs beyond storage hardware
- Easy to implement with standard Docker volume patterns

**Losses**:
- No built-in geographic redundancy (must implement backup strategy)
- Scaling beyond single server requires migration strategy
- No automatic CDN-like distribution capabilities

**Storage Structure**:
```
/app/photos/
  /{year}/
    /{month}/
      /{uuid}.{ext}
```

---

## 3. PostGIS Usage for GPS Coordinates

### Recommendation: **PostGIS GEOGRAPHY Type with Default SRID 4326**

Store GPS coordinates using the PostGIS GEOGRAPHY type with the default WGS84 (SRID 4326) spatial reference system.

### Rationale

1. **Global Accuracy**: GEOGRAPHY type performs calculations on a sphere/ellipsoid, providing accurate measurements regardless of location.

2. **Meaningful Units**: GEOGRAPHY type returns distance measurements in meters, which is intuitive for users (aligns with Constitution Principle II: Non-Technical User Focus).

3. **GPS Compatibility**: GEOGRAPHY defaults to SRID 4326 (WGS84), which is the standard used by GPS systems. This eliminates coordinate transformation requirements.

4. **Spatial Indexing**: PostGIS provides efficient GiST spatial indexes for GEOGRAPHY types, supporting fast spatial queries.

5. **Standard Compliance**: WGS84/SRID 4326 is the international standard for GPS coordinates, ensuring data portability and long-term preservation.

### Alternatives Considered

**Decimal Degrees in Regular Numeric Columns**:
- **Pros**: Simple to understand, no PostGIS dependency
- **Cons**: No spatial indexing (poor query performance), no built-in distance calculations, cannot perform spatial operations
- **Verdict**: Insufficient for spatial query requirements (FR-005)

**PostGIS GEOMETRY Type**:
- **Pros**: Faster calculations, more available functions
- **Cons**: Planar calculations on spherical data produce inaccurate results, inappropriate for global datasets
- **Verdict**: Only suitable for localized regional data

### Trade-offs

**Gains**:
- Accurate distance calculations across global cemetery locations
- Intuitive meter-based measurements for users
- Efficient spatial indexing with GiST indexes
- Rich spatial query capabilities
- Standards-compliant data storage for long-term preservation

**Losses**:
- Slightly slower than GEOMETRY for calculations (acceptable trade-off for accuracy)
- Requires PostGIS extension (already planned)

**Privacy Note**: Per Constitution Security & Privacy principle, GPS coordinates should be stored but not displayed by default in UI.

---

## 4. React Image Display

### Recommendation: **Server-Side Thumbnail Generation (Pillow) + react-lazy-load-image-component**

Generate thumbnails server-side using Pillow during photo upload, serve multiple sizes (thumbnail, preview, full), and use the react-lazy-load-image-component library for lazy loading.

### Rationale

1. **Performance**: Server-side generation happens once during upload, eliminating redundant client-side processing. Thumbnails are pre-optimized for fast loading.

2. **Consistency**: Server-side generation ensures consistent quality and dimensions across all clients.

3. **Bandwidth Efficiency**: Serving appropriately sized images dramatically reduces bandwidth usage for large photo collections.

4. **Simplicity**: react-lazy-load-image-component is a well-maintained, straightforward library with minimal configuration.

5. **Browser Compatibility**: Server-side generation works across all browsers.

### Alternatives Considered

**Client-Side Thumbnail Generation**:
- **Pros**: Zero storage overhead
- **Cons**: CPU-intensive on mobile devices, inconsistent quality, slower initial display, poor for large galleries
- **Verdict**: Poor user experience for non-technical users (violates Constitution Principle II)

**Native Browser Lazy Loading**:
- **Pros**: Zero JavaScript required
- **Cons**: Limited browser support, no control over placeholder, doesn't meet all requirements
- **Verdict**: Good complement but insufficient alone

### Trade-offs

**Gains**:
- Fast initial page loads with small thumbnail sizes
- Consistent user experience across all devices
- Reduced bandwidth usage
- Lower client-side CPU usage
- Smooth scroll performance with lazy loading

**Losses**:
- Additional storage required for thumbnails (approximately 2-5% of original photo size)
- Initial upload time increases slightly (~0.5-1 second)
- Cannot dynamically resize without regeneration

**Thumbnail Sizes**:
- **thumbnail**: 150x150 (Gallery grid view) ~5KB
- **preview**: 800x600 (Detail page preview) ~100KB
- **full**: Original size

---

## 5. Authentication Strategy

### Recommendation: **Session-Based Authentication with HTTP-Only Cookies**

Implement traditional session-based authentication using FastAPI's session middleware with PostgreSQL session storage and HTTP-only cookies.

### Rationale

1. **Simplicity**: Session-based auth is simpler to implement and maintain than JWT infrastructure (strongly aligns with Constitution Principle III: Maintainability & Simplicity).

2. **Immediate Revocation**: Sessions can be instantly invalidated by deleting the database record, critical for security incident response.

3. **Stateful Control**: Centralized session management provides clear audit trail of active users and login history.

4. **Security Best Practices**: HTTP-only cookies prevent XSS attacks by making tokens inaccessible to JavaScript.

5. **Self-Hosted Architecture**: Session storage in PostgreSQL (already required) eliminates need for Redis or additional infrastructure.

6. **OAuth2 Migration Path**: Session-based auth doesn't preclude future OAuth2 addition.

### Alternatives Considered

**JWT (JSON Web Tokens)**:
- **Pros**: Stateless, scalable across multiple servers, no database lookup per request
- **Cons**: Cannot be instantly revoked, more complex implementation, larger payload size
- **Verdict**: Overkill for initial release of self-hosted single-server deployment

**OAuth2 Only**:
- **Pros**: Industry standard, SSO support
- **Cons**: Requires external identity provider or complex self-hosted OAuth2 server
- **Verdict**: Excellent future enhancement, but too complex for initial release

### Trade-offs

**Gains**:
- Simple implementation with fewer moving parts
- Instant session revocation capability
- Clear audit trail of user sessions
- No complex token refresh logic
- Database-backed sessions survive server restarts
- Familiar patterns for maintenance

**Losses**:
- Database lookup on each authenticated request
- Sessions tied to server state
- Requires session cleanup job for expired sessions
- Slight latency overhead from database session lookup

---

## 6. Docker Deployment

### Recommendation: **Multi-Stage Builds + Named Volumes + Docker Secrets**

Use Docker multi-stage builds for optimized images, named volumes for photo storage and database persistence, and Docker secrets for sensitive configuration management.

### Rationale

1. **Multi-Stage Builds**: Separates build dependencies from runtime, resulting in smaller, more secure production images.

2. **Named Volumes**: Docker-managed volumes provide reliable persistence, easy backup/restore, and better performance than bind mounts.

3. **Secrets Management**: Docker secrets keep sensitive data out of images and environment variables.

4. **Simplicity**: docker-compose.yml provides single-command deployment meeting SC-007 (10-minute deployment goal).

5. **Portability**: Named volumes abstract storage location, making deployment consistent across different host systems.

6. **Backup-Friendly**: Named volumes can be backed up using standard Docker commands.

### Alternatives Considered

**Bind Mounts for Photo Storage**:
- **Pros**: Direct host filesystem access
- **Cons**: Host-specific paths, permission issues, platform inconsistencies, harder to migrate
- **Verdict**: Less portable, more error-prone for community deployments

**Environment Variables for Secrets**:
- **Pros**: Simple, widely understood
- **Cons**: Visible in process list, logged in container inspect, easy to accidentally commit to git
- **Verdict**: Acceptable for non-sensitive config, but use secrets for passwords/keys

**Single-Stage Builds**:
- **Pros**: Simpler Dockerfile
- **Cons**: Larger images (includes build tools), more attack surface, slower pulls
- **Verdict**: Multi-stage minimal complexity overhead for significant benefits

### Trade-offs

**Gains**:
- Smaller production images (100-200MB vs 500MB+)
- Better security (no build tools in production)
- Reliable data persistence with named volumes
- Easy backup/restore workflows
- Single-command deployment
- Professional production practices without complexity

**Losses**:
- Slightly more complex Dockerfile (multi-stage)
- Cannot easily inspect volume contents without Docker commands
- Named volumes less intuitive than direct host paths for newcomers

**Deployment Example**:
```bash
# 1. Create secrets
mkdir -p secrets
openssl rand -base64 32 > secrets/db_password.txt
openssl rand -base64 32 > secrets/session_secret.txt

# 2. Deploy
docker-compose up -d

# 3. Access
# Open browser to http://localhost
```

---

## Implementation Priority

Based on the project's phased approach:

1. **Phase 1 (Design)**:
   - Finalize database schema with PostGIS GEOGRAPHY types
   - Design file storage structure for local filesystem
   - Document API contracts for photo upload/retrieval
   - Create Docker Compose configuration

2. **Phase 2 (Core Infrastructure)**:
   - Docker deployment setup (volumes, secrets)
   - Database setup with PostGIS extension
   - Session-based authentication implementation
   - File storage service abstraction

3. **Phase 3 (Photo Features)**:
   - EXIF extraction with Pillow + piexif
   - Photo upload endpoint with thumbnail generation
   - Photo storage and retrieval

4. **Phase 4 (User Interface)**:
   - React lazy loading implementation
   - Photo gallery component
   - Search interface with spatial queries

---

## Conclusion

These technology recommendations prioritize the StoneKeeper project's constitutional principles of data integrity, simplicity, and maintainability. Each decision balances modern best practices with practical considerations for a self-hosted community preservation tool. The recommendations provide a solid foundation for the initial release while maintaining clear migration paths for future enhancements (S3 storage, OAuth2 authentication, advanced scaling).

All recommendations align with the project's success criteria, particularly SC-007 (10-minute deployment), SC-001 (<5 second photo processing), SC-002 (<1 second search), and SC-006 (zero data loss).

# Feature Specification: Cemetery Photo Cataloging System

**Feature Branch**: `001-photo-cataloging`
**Created**: 2025-11-26
**Status**: Draft
**Input**: User description: "Build a cemetery photo cataloging system with EXIF tagging, searchable database, and Docker deployment"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload and Catalog Cemetery Photos (Priority: P1)

A cemetery researcher visits a cemetery, takes photographs of headstones, and returns to their office. They need to upload these photographs to the cataloging system, where the system automatically extracts and preserves important metadata from the photos (date taken, GPS coordinates if available, camera settings). The researcher can then add cemetery-specific information like cemetery name, section, and plot location.

**Why this priority**: This is the core MVP functionality - without the ability to upload and catalog photos with metadata, the system has no value. This represents the minimum viable product that delivers immediate value to researchers.

**Independent Test**: Can be fully tested by uploading a cemetery photo, verifying EXIF data is extracted and preserved, adding cemetery details, and confirming the photo is stored and retrievable.

**Acceptance Scenarios**:

1. **Given** a researcher has cemetery photos on their computer, **When** they upload a photo through the web interface, **Then** the system extracts EXIF metadata (date, GPS, camera info) and displays it for confirmation
2. **Given** a photo has been uploaded, **When** the researcher adds cemetery details (name, section, plot), **Then** the system saves all information together and confirms successful cataloging
3. **Given** a photo is being uploaded, **When** the upload is in progress, **Then** a progress indicator shows upload status and estimated time remaining
4. **Given** a photo lacks EXIF metadata, **When** uploaded, **Then** the system accepts the photo and allows manual entry of date and location information

---

### User Story 2 - Search and Browse Cataloged Photos (Priority: P2)

A genealogist is researching family history and needs to find photographs of specific burials. They search the catalog by cemetery name, location, date range, or photographer. The system returns matching photographs with their associated metadata, allowing the researcher to view full-size images and download them for their records.

**Why this priority**: Once photos are cataloged (P1), researchers need to find them. Search functionality transforms the catalog from a storage system into a research tool. This is the second most critical feature for delivering user value.

**Independent Test**: Can be tested by cataloging several photos with different metadata, then performing searches by cemetery name, date range, and location to verify correct results are returned.

**Acceptance Scenarios**:

1. **Given** multiple photos are cataloged, **When** a user searches by cemetery name, **Then** all photos from that cemetery are displayed with thumbnails and basic metadata
2. **Given** a search returns results, **When** the user clicks a thumbnail, **Then** the full-size image opens with complete metadata displayed (cemetery details, EXIF data, upload date)
3. **Given** photos from multiple date ranges exist, **When** a user filters by date range, **Then** only photos from that period are shown
4. **Given** search results exist, **When** a user selects a photo, **Then** they can download the original file with EXIF metadata intact

---

### User Story 3 - Multi-User Collaboration (Priority: P3)

Multiple researchers from a cemetery preservation organization need to collaborate on cataloging a large cemetery. Each researcher creates an account, logs in, and can upload photos to the shared catalog. They can see who uploaded each photo and when, ensuring accountability and preventing duplicate work.

**Why this priority**: While single-user functionality covers basic needs, collaborative research is essential for large cemetery documentation projects. This enables teams to work together efficiently.

**Independent Test**: Can be tested by creating multiple user accounts, having each upload photos, and verifying all users can see and search the complete shared catalog with proper attribution.

**Acceptance Scenarios**:

1. **Given** a new researcher joins the team, **When** they create an account with email and password, **Then** they can log in and access the shared photo catalog
2. **Given** multiple users are uploading photos, **When** any user searches the catalog, **Then** they see all photos with photographer attribution showing who uploaded each photo
3. **Given** a user is logged in, **When** they view photo details, **Then** they see the uploader's name and upload timestamp
4. **Given** a user logs out, **When** they attempt to access catalog features, **Then** they are redirected to the login page

---

### User Story 4 - Organized Cemetery Management (Priority: P4)

Researchers need to organize photos by cemetery structure (sections, rows, plots) and view cemetery-level statistics. They can browse all photos from a specific cemetery, see how many photos exist for each section, and identify gaps in documentation coverage.

**Why this priority**: Once photos are uploaded and searchable, organizational features help researchers understand what's been documented and what's missing. This enables systematic, complete cemetery documentation.

**Independent Test**: Can be tested by uploading photos with section/plot information, then browsing by cemetery to see organizational hierarchy and photo counts.

**Acceptance Scenarios**:

1. **Given** photos from multiple cemeteries exist, **When** a user views the cemetery list, **Then** they see each cemetery with photo count and last update date
2. **Given** a user selects a cemetery, **When** viewing cemetery details, **Then** they see sections organized hierarchically with photo counts per section
3. **Given** photos have plot information, **When** browsing a section, **Then** photos are organized by plot number for easy navigation
4. **Given** a cemetery has partial coverage, **When** viewing section statistics, **Then** gaps in documentation are visibly identified

---

### User Story 5 - Docker Deployment (Priority: P5)

A cemetery preservation organization wants to install StoneKeeper on their own server for data privacy and control. An administrator downloads the Docker package, follows simple deployment instructions, and launches the application with a single command. The system initializes the database, creates an admin account, and is ready for researchers to use.

**Why this priority**: This is an operational requirement rather than user-facing functionality. It enables organizations to self-host but doesn't directly deliver research value. Essential for adoption but lower priority than research features.

**Independent Test**: Can be tested by deploying the Docker container on a fresh server, verifying database initialization, creating the first admin account, and confirming the web interface is accessible.

**Acceptance Scenarios**:

1. **Given** an administrator has Docker installed, **When** they run the deployment command, **Then** the application starts and creates the initial database schema
2. **Given** the application is deployed, **When** accessed for the first time, **Then** a setup wizard guides creation of the first admin account
3. **Given** the system is running, **When** researchers access the web URL, **Then** they see the login page and can begin using the system
4. **Given** the container restarts, **When** it comes back online, **Then** all existing data and photos are preserved

---

### Edge Cases

- What happens when a photo is uploaded without any EXIF metadata?
  - System accepts the photo and allows manual entry of all metadata fields
- What happens when two users upload photos of the same headstone?
  - Both photos are stored separately (duplicates allowed, researcher can decide which to keep)
- How does the system handle very large photo files (>10MB)?
  - System sets maximum file size limit (20MB) and displays clear error if exceeded
- What happens when a user forgets their password?
  - Password reset flow via email link (standard web app pattern)
- How does the system handle special characters in cemetery names (e.g., "St. Mary's")?
  - Full Unicode support for international characters and special symbols
- What happens when GPS coordinates are in different formats?
  - System normalizes to decimal degrees format for consistent storage and display
- How are deleted photos handled?
  - Soft delete with admin-only restoration capability (aligns with constitution principle I)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to upload photograph files in common formats (JPEG, PNG, TIFF)
- **FR-002**: System MUST extract and preserve EXIF metadata from uploaded photographs (date, time, GPS coordinates, camera make/model, exposure settings)
- **FR-003**: System MUST store original photograph files with EXIF metadata intact (no compression or modification)
- **FR-004**: Users MUST be able to add cemetery-specific metadata to photos (cemetery name, section, row, plot, headstone name, burial date)
- **FR-005**: System MUST provide search functionality by cemetery name, location, photographer, and date range
- **FR-006**: Users MUST be able to view thumbnail galleries of search results and click to view full-size images
- **FR-007**: System MUST allow users to download original photograph files with metadata preserved
- **FR-008**: System MUST support user registration and authentication (email/password)
- **FR-009**: System MUST track which user uploaded each photograph and when
- **FR-010**: All users MUST be able to view and search all photos in the shared catalog
- **FR-011**: System MUST organize photos hierarchically by cemetery → section → row → plot
- **FR-012**: System MUST display photo counts and statistics per cemetery and section
- **FR-013**: System MUST be deployable via Docker container with single-command startup
- **FR-014**: System MUST initialize database schema automatically on first deployment
- **FR-015**: System MUST validate user input to prevent data corruption (per constitution principle I)
- **FR-016**: System MUST require user confirmation before deleting any photos
- **FR-017**: System MUST implement soft deletion with retention of original data (per constitution principle I)
- **FR-018**: System MUST support timezone-aware timestamps for all photos and actions (per constitution principle I)

### Key Entities

- **Photograph**: A cemetery photo file with associated metadata
  - Attributes: original file, file size, upload date, EXIF data (date taken, GPS coordinates, camera info), uploader reference
  - Relationships: belongs to one cemetery, uploaded by one user, may have plot information

- **Cemetery**: A physical cemetery location being documented
  - Attributes: name, location (city, state, country), GPS coordinates (if available), established date (if known)
  - Relationships: contains many sections, has many photographs

- **Section**: A subdivision of a cemetery (e.g., "Section A", "Veterans Area")
  - Attributes: section name/identifier, description
  - Relationships: belongs to one cemetery, contains many plots, has many photographs

- **Plot**: A specific burial location within a section
  - Attributes: plot number/identifier, row, headstone inscription (if transcribed), burial dates (if known)
  - Relationships: belongs to one section, may have multiple photographs

- **User**: A researcher with access to the catalog system
  - Attributes: name, email, password (hashed), registration date, last login
  - Relationships: uploads many photographs

- **EXIF Metadata**: Technical photograph information
  - Attributes: date taken, GPS latitude/longitude, camera make, camera model, exposure settings, image dimensions
  - Relationships: belongs to one photograph

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a cemetery photo and have EXIF metadata extracted in under 5 seconds for typical smartphone images (5-10MB)
- **SC-002**: Search queries return results in under 1 second for catalogs containing up to 10,000 photographs
- **SC-003**: 90% of new users successfully upload their first photo and add cemetery details within 5 minutes (without training)
- **SC-004**: System supports at least 50 concurrent users uploading and searching without performance degradation
- **SC-005**: Photo galleries load initial page in under 2 seconds on standard broadband connections
- **SC-006**: Zero data loss during upload - 100% of uploaded photos are stored with original EXIF metadata intact
- **SC-007**: Organizations can deploy and install the system on their own servers and access the web interface within 10 minutes following documentation
- **SC-008**: System maintains 99.9% uptime for photo viewing and searching (core read operations)
- **SC-009**: All UI components meet WCAG 2.1 Level AA accessibility standards (per constitution)
- **SC-010**: Cemetery preservation organizations reduce time spent organizing photo archives by 50% compared to manual folder-based systems

### Assumptions

- Users have reliable internet connectivity when accessing the web application
- Cemetery photos are taken with digital cameras or smartphones that embed EXIF metadata
- Photos are in standard formats (JPEG, PNG, TIFF) - no RAW format support required initially
- User authentication follows standard email/password pattern (no SSO or OAuth required initially)
- Database can scale to handle at least 100,000 photographs before requiring optimization
- Docker deployment assumes server has at least 2GB RAM and 50GB storage available
- Users understand basic cemetery terminology (section, plot, burial) without extensive training
- Photo uploads are done from office/home environments, not in the field (web app, not mobile app)
- Organizations deploying the system have basic technical capability to run Docker commands
- Average photograph file size is 5-10MB (modern smartphone quality)

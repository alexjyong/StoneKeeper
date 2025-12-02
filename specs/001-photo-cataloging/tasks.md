# Tasks: Cemetery Photo Cataloging System

**Input**: Design documents from `/specs/001-photo-cataloging/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.yaml

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure (backend/src/{models,services,api,db})
- [x] T002 Create frontend directory structure (frontend/src/{components,pages,services,types})
- [x] T003 [P] Initialize Python backend with requirements.txt (FastAPI 0.104+, Pillow, SQLAlchemy 2.0+, Alembic, passlib, python-multipart)
- [x] T004 [P] Initialize Node.js frontend with package.json (React 18+, TypeScript 5+, React Router, Axios, react-lazy-load-image-component)
- [x] T005 [P] Create backend/Dockerfile with multi-stage build
- [x] T006 [P] Create frontend/Dockerfile with multi-stage build (Node build + nginx runtime)
- [x] T007 Create docker-compose.yml with postgres, backend, frontend services
- [x] T008 [P] Create .gitignore for Python and Node.js
- [x] T009 [P] Create secrets directory structure for Docker secrets
- [x] T010 [P] Create docs directory with adr subdirectory
- [x] T011 [P] Create README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T012 Configure Alembic for database migrations in backend/src/db/migrations/
- [x] T013 Create database session management in backend/src/db/session.py with SQLAlchemy engine and session factory
- [x] T014 Create initial migration 001_initial_schema.sql with PostGIS extension, uuid-ossp extension
- [x] T015 Create users table migration with email, password_hash, full_name, is_active, timestamps, soft delete
- [x] T016 Create user_sessions table migration with session_id, user_id FK, expires_at, ip_address, user_agent
- [x] T017 Create cemeteries table migration with name, location_description, gps_location (GEOGRAPHY POINT 4326), established_year, notes, created_by FK, timestamps, soft delete
- [x] T018 Create sections table migration with cemetery_id FK, name, description, display_order, created_by FK, timestamps, soft delete
- [x] T019 Create plots table migration with section_id FK, plot_number, row_identifier, headstone_inscription, burial_date, notes, created_by FK, timestamps, soft delete
- [x] T020 Create photographs table migration with uuid, cemetery_id FK, section_id FK, plot_id FK, file paths, file_size_bytes, file_format, EXIF fields (date_taken, gps_location GEOGRAPHY, camera data), image dimensions, thumbnail/preview paths, description, photographer_notes, uploaded_by FK, timestamps, soft delete
- [x] T021 Create spatial indexes on cemeteries.gps_location and photographs.exif_gps_location using GIST
- [x] T022 Create full-text search indexes on cemetery names, plot inscriptions, photo descriptions using gin_trgm_ops
- [x] T023 Create update_updated_at_column() trigger function for automatic timestamp updates
- [x] T024 Apply updated_at triggers to all tables (users, cemeteries, sections, plots, photographs)
- [x] T025 Create User model in backend/src/models/user.py with SQLAlchemy ORM mapping
- [x] T026 Create UserSession model in backend/src/models/user_session.py
- [x] T027 Create base response schemas in backend/src/schemas/base.py (Error, PaginatedResponse)
- [x] T028 [P] Create constants file in backend/src/config.py (MAX_FILE_SIZE_BYTES=20MB, ALLOWED_FORMATS, SESSION_EXPIRE_DAYS=7, etc.)
- [x] T029 [P] Create backend/src/main.py FastAPI app initialization with CORS middleware, session middleware, exception handlers
- [x] T030 [P] Create frontend/src/services/api.ts with Axios instance configured for backend API base URL
- [x] T031 [P] Create frontend/src/types/index.ts with TypeScript interfaces for User, Error, PaginatedResponse
- [x] T032 [P] Create frontend/src/App.tsx with React Router setup and placeholder routes
- [x] T033 [P] Create frontend/public/index.html and basic styling
- [ ] T034 Test database migrations: run alembic upgrade head and verify all tables created
- [ ] T035 Test database rollback: run alembic downgrade -1 and verify clean rollback

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload and Catalog Cemetery Photos (Priority: P1) 🎯 MVP

**Goal**: Enable researchers to upload cemetery photos with automatic EXIF extraction and catalog them with cemetery details

**Independent Test**: Upload a cemetery photo, verify EXIF data is extracted and preserved, add cemetery details, confirm photo is stored and retrievable

### Implementation for User Story 1

- [x] T036 [P] [US1] Create Cemetery model in backend/src/models/cemetery.py with gps_location as GEOGRAPHY type
- [x] T037 [P] [US1] Create Section model in backend/src/models/section.py
- [x] T038 [P] [US1] Create Plot model in backend/src/models/plot.py
- [x] T039 [P] [US1] Create Photograph model in backend/src/models/photograph.py with EXIF fields and file paths
- [x] T040 [P] [US1] Create Cemetery schema in backend/src/schemas/cemetery.py (CemeteryCreate, CemeteryResponse with GPSCoordinates)
- [x] T041 [P] [US1] Create Section schema in backend/src/schemas/section.py
- [x] T042 [P] [US1] Create Plot schema in backend/src/schemas/plot.py
- [x] T043 [P] [US1] Create Photograph schema in backend/src/schemas/photograph.py with EXIFMetadata nested schema
- [x] T044 [US1] Create EXIFService in backend/src/services/exif_service.py to extract metadata using Pillow and piexif (date_taken, GPS coordinates, camera make/model, focal length, aperture, shutter speed, ISO, image dimensions)
- [x] T045 [US1] Add thumbnail generation method to EXIFService to create 150x150 thumbnail and 800x600 preview using Pillow LANCZOS resampling
- [x] T046 [US1] Create PhotoStorageService in backend/src/services/photo_service.py to save files to /app/photos/{year}/{month}/{uuid}.{ext} structure using UUID for filenames
- [x] T047 [US1] Add save_with_thumbnails method to PhotoStorageService to save original, thumbnail, and preview
- [x] T048 [US1] Create CemeteryService in backend/src/services/cemetery_service.py with create, get, list, update, delete (soft) methods
- [x] T049 [US1] Add GPS coordinate normalization to CemeteryService to convert to decimal degrees and create PostGIS POINT
- [x] T050 [US1] Create POST /api/cemeteries endpoint in backend/src/api/cemeteries.py to create cemetery with optional GPS coordinates
- [x] T051 [US1] Create GET /api/cemeteries endpoint in backend/src/api/cemeteries.py with pagination and search by name
- [x] T052 [US1] Create GET /api/cemeteries/{id} endpoint in backend/src/api/cemeteries.py to retrieve cemetery with statistics (photo_count, section_count)
- [x] T053 [US1] Create POST /api/photos endpoint in backend/src/api/photos.py to handle multipart upload, extract EXIF, generate thumbnails, save to storage, create database record
- [x] T054 [US1] Add file validation to POST /api/photos: check file size <=20MB, format in [JPEG, PNG, TIFF], prevent path traversal
- [x] T055 [US1] Add EXIF extraction to POST /api/photos: call EXIFService, handle photos without EXIF gracefully, store extracted metadata
- [x] T056 [US1] Create GET /api/photos/{id} endpoint in backend/src/api/photos.py to retrieve photo metadata
- [x] T057 [US1] Create GET /api/photos/{id}/file endpoint to serve original file with appropriate Content-Type header
- [x] T058 [US1] Create GET /api/photos/{id}/thumbnail endpoint to serve 150x150 JPEG thumbnail
- [x] T059 [US1] Create GET /api/photos/{id}/preview endpoint to serve 800x600 JPEG preview
- [x] T060 [P] [US1] Create Cemetery TypeScript interface in frontend/src/types/index.ts
- [x] T061 [P] [US1] Create Section, Plot, Photograph, EXIFMetadata TypeScript interfaces in frontend/src/types/index.ts
- [x] T062 [P] [US1] Add cemetery API methods to frontend/src/services/api.ts (createCemetery, getCemeteries, getCemetery)
- [x] T063 [P] [US1] Add photo API methods to frontend/src/services/api.ts (uploadPhoto, getPhoto, getPhotoFile, getPhotoThumbnail, getPhotoPreview)
- [x] T064 [US1] Create CemeteryForm component in frontend/src/components/CemeteryForm/index.tsx with name, location, GPS coordinates, established year, notes fields
- [x] T065 [US1] Add GPS coordinate input with validation (latitude -90 to 90, longitude -180 to 180) to CemeteryForm
- [x] T066 [US1] Create PhotoUpload component in frontend/src/components/PhotoUpload/index.tsx with drag-and-drop file input, file validation (size, format), progress bar
- [x] T067 [US1] Add cemetery selector dropdown to PhotoUpload component to associate photo with cemetery
- [x] T068 [US1] Add optional section and plot selectors to PhotoUpload component
- [x] T069 [US1] Add description and notes text areas to PhotoUpload component
- [x] T070 [US1] Implement upload progress tracking in PhotoUpload using Axios upload progress events
- [x] T071 [US1] Create EXIFDisplay component in frontend/src/components/EXIFDisplay/index.tsx to show extracted metadata (date, GPS, camera info) in readable format
- [x] T072 [US1] Create PhotoDetail component in frontend/src/components/PhotoDetail/index.tsx to display full-size image with complete metadata
- [x] T073 [US1] Create UploadPage in frontend/src/pages/UploadPage.tsx with CemeteryForm and PhotoUpload components
- [x] T074 [US1] Add form submission handling to UploadPage: create cemetery if new, upload photo, display success/error messages
- [x] T075 [US1] Add error handling to UploadPage for file too large (>20MB), unsupported format, network errors with plain-language messages
- [x] T076 [US1] Create HomePage in frontend/src/pages/HomePage.tsx with recent uploads gallery and quick actions (upload photo, add cemetery)
- [x] T077 [US1] Add routing for /upload, /home, /cemeteries to frontend/src/App.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - researchers can upload photos with EXIF extraction and create cemeteries

---

## Phase 4: User Story 2 - Search and Browse Cataloged Photos (Priority: P2)

**Goal**: Enable researchers to search the catalog by cemetery name, location, date range, photographer, and view photos with metadata

**Independent Test**: Catalog several photos with different metadata, then perform searches by cemetery name, date range, and location to verify correct results

### Implementation for User Story 2

- [ ] T078 [US2] Create SearchService in backend/src/services/search_service.py with search_photos method supporting filters (cemetery_id, date_from, date_to, uploaded_by, query text)
- [ ] T079 [US2] Add full-text search to SearchService using PostgreSQL gin_trgm_ops indexes on cemetery names and photo descriptions
- [ ] T080 [US2] Add spatial search to SearchService to find photos within distance of GPS coordinates using ST_DWithin
- [ ] T081 [US2] Create GET /api/photos endpoint in backend/src/api/photos.py with query parameters (cemetery_id, section_id, plot_id, uploaded_by, date_from, date_to, page, page_size)
- [ ] T082 [US2] Add pagination to GET /api/photos using SQLAlchemy limit/offset and return PaginatedResponse
- [ ] T083 [US2] Create GET /api/search endpoint in backend/src/api/search.py with multi-type search (photos, cemeteries, plots) using query parameter
- [ ] T084 [US2] Add date range filtering to GET /api/search using EXIF date_taken field
- [ ] T085 [P] [US2] Create SearchBar component in frontend/src/components/SearchBar/index.tsx with text input, cemetery filter dropdown, date range pickers, photographer filter
- [ ] T086 [P] [US2] Add search suggestions to SearchBar using debounced API calls to suggest cemetery names
- [ ] T087 [US2] Create PhotoGallery component in frontend/src/components/PhotoGallery/index.tsx with thumbnail grid using react-lazy-load-image-component
- [ ] T088 [US2] Add lazy loading to PhotoGallery with threshold of 300px before viewport entry
- [ ] T089 [US2] Add thumbnail click handler to PhotoGallery to open PhotoDetail modal or navigate to detail page
- [ ] T090 [US2] Create Pagination component in frontend/src/components/Pagination/index.tsx with page numbers, previous/next buttons
- [ ] T091 [US2] Create SearchPage in frontend/src/pages/SearchPage.tsx with SearchBar, PhotoGallery, and Pagination
- [ ] T092 [US2] Add search state management to SearchPage (query, filters, current page) using React useState
- [ ] T093 [US2] Implement search execution in SearchPage: call API on filter changes, update results, handle loading/error states
- [ ] T094 [US2] Add download original photo feature to PhotoDetail component with button triggering GET /api/photos/{id}/file
- [ ] T095 [US2] Add URL query parameters to SearchPage to support shareable search links (e.g., /search?cemetery=1&date_from=2023-01-01)
- [ ] T096 [US2] Create CemeteryPage in frontend/src/pages/CemeteryPage.tsx to display cemetery details with photo gallery filtered to that cemetery
- [ ] T097 [US2] Add statistics to CemeteryPage showing photo count, section count, last photo uploaded
- [ ] T098 [US2] Add routing for /search, /cemeteries/:id to frontend/src/App.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - researchers can upload photos and search the catalog

---

## Phase 5: User Story 3 - Multi-User Collaboration (Priority: P3)

**Goal**: Enable multiple researchers to create accounts, log in, and collaborate on the shared catalog with photographer attribution

**Independent Test**: Create multiple user accounts, have each upload photos, verify all users can see and search the complete shared catalog with proper attribution

### Implementation for User Story 3

- [ ] T099 [US3] Create AuthService in backend/src/services/auth_service.py with register_user method (hash password with bcrypt, create user record)
- [ ] T100 [US3] Add login method to AuthService to verify credentials, create session record, return session ID
- [ ] T101 [US3] Add logout method to AuthService to delete session from database
- [ ] T102 [US3] Add get_current_user method to AuthService to validate session ID, check expiration, update last_activity
- [ ] T103 [US3] Create session cleanup utility in AuthService to delete expired sessions (for cron job)
- [ ] T104 [US3] Create authentication dependency in backend/src/api/dependencies.py using FastAPI Depends to get current user from session cookie
- [ ] T105 [US3] Create POST /api/auth/register endpoint in backend/src/api/auth.py to register new user with email validation, password strength check (min 8 chars)
- [ ] T106 [US3] Create POST /api/auth/login endpoint in backend/src/api/auth.py to authenticate and set HTTP-only session cookie
- [ ] T107 [US3] Create POST /api/auth/logout endpoint in backend/src/api/auth.py to invalidate session and clear cookie
- [ ] T108 [US3] Create GET /api/auth/me endpoint in backend/src/api/auth.py to return current user info (requires authentication)
- [ ] T109 [US3] Add authentication requirement to photo upload endpoint using Depends(get_current_user)
- [ ] T110 [US3] Add uploaded_by field population to POST /api/photos using authenticated user ID
- [ ] T111 [US3] Add photographer name to photo list/detail responses by joining users table
- [ ] T112 [US3] Add authentication requirement to cemetery create/update endpoints
- [ ] T113 [US3] Add created_by field population to cemetery/section/plot creation using authenticated user ID
- [ ] T114 [P] [US3] Create User schema in backend/src/schemas/user.py (UserRegister, UserLogin, UserResponse)
- [ ] T115 [P] [US3] Add user-related TypeScript interfaces to frontend/src/types/index.ts
- [ ] T116 [P] [US3] Add auth API methods to frontend/src/services/api.ts (register, login, logout, getCurrentUser)
- [ ] T117 [US3] Create LoginForm component in frontend/src/components/Auth/LoginForm.tsx with email and password inputs
- [ ] T118 [US3] Create RegisterForm component in frontend/src/components/Auth/RegisterForm.tsx with email, password, full name inputs, password confirmation
- [ ] T119 [US3] Add client-side password validation to RegisterForm (min 8 chars, match confirmation)
- [ ] T120 [US3] Create AuthContext in frontend/src/contexts/AuthContext.tsx to manage authentication state (current user, loading, error)
- [ ] T121 [US3] Add login/logout methods to AuthContext calling auth API
- [ ] T122 [US3] Add session persistence to AuthContext by calling GET /api/auth/me on app load
- [ ] T123 [US3] Create PrivateRoute component in frontend/src/components/Auth/PrivateRoute.tsx to protect authenticated routes
- [ ] T124 [US3] Create LoginPage in frontend/src/pages/LoginPage.tsx with LoginForm and link to register
- [ ] T125 [US3] Create RegisterPage in frontend/src/pages/RegisterPage.tsx with RegisterForm and link to login
- [ ] T126 [US3] Add authentication guard to UploadPage, SearchPage requiring login
- [ ] T127 [US3] Add logout button to navigation bar in App.tsx
- [ ] T128 [US3] Add photographer attribution display to PhotoGallery showing uploader name on each thumbnail
- [ ] T129 [US3] Add detailed attribution to PhotoDetail showing uploader name and upload timestamp
- [ ] T130 [US3] Add routing for /login, /register to frontend/src/App.tsx with redirect to /home after login
- [ ] T131 [US3] Add error handling for authentication failures (401 errors) with redirect to login page

**Checkpoint**: All three user stories should now be independently functional - multiple users can register, login, upload photos, and search the shared catalog

---

## Phase 6: User Story 4 - Organized Cemetery Management (Priority: P4)

**Goal**: Enable researchers to organize photos by cemetery structure (sections, plots) and view statistics

**Independent Test**: Upload photos with section/plot information, browse by cemetery to see organizational hierarchy and photo counts

### Implementation for User Story 4

- [ ] T132 [P] [US4] Create SectionService in backend/src/services/section_service.py with CRUD methods
- [ ] T133 [P] [US4] Create PlotService in backend/src/services/plot_service.py with CRUD methods
- [ ] T134 [US4] Add get_statistics method to CemeteryService to calculate photo counts, section counts using database aggregations
- [ ] T135 [US4] Create POST /api/cemeteries/{id}/sections endpoint in backend/src/api/cemeteries.py to add section to cemetery
- [ ] T136 [US4] Create GET /api/cemeteries/{id}/sections endpoint to list sections with photo counts, ordered by display_order
- [ ] T137 [US4] Create POST /api/sections/{id}/plots endpoint in backend/src/api/cemeteries.py to add plot to section
- [ ] T138 [US4] Create GET /api/sections/{id}/plots endpoint to list plots with photo counts, ordered by plot_number
- [ ] T139 [US4] Create PATCH /api/photos/{id} endpoint in backend/src/api/photos.py to update section_id, plot_id, description, notes
- [ ] T140 [US4] Add cemetery_statistics view query to GET /api/cemeteries for efficient statistics retrieval
- [ ] T141 [P] [US4] Create SectionForm component in frontend/src/components/SectionForm/index.tsx with name, description, display_order fields
- [ ] T142 [P] [US4] Create PlotForm component in frontend/src/components/PlotForm/index.tsx with plot_number, row, inscription, burial_date, notes fields
- [ ] T143 [P] [US4] Add date picker to PlotForm for burial_date field
- [ ] T144 [US4] Create CemeteryBrowser component in frontend/src/components/CemeteryBrowser/index.tsx with hierarchical tree view (cemetery → sections → plots)
- [ ] T145 [US4] Add expand/collapse functionality to CemeteryBrowser for sections
- [ ] T146 [US4] Add photo count badges to CemeteryBrowser on cemetery, section, and plot nodes
- [ ] T147 [US4] Create StatisticsPanel component in frontend/src/components/StatisticsPanel/index.tsx to display cemetery statistics (total photos, sections, last update)
- [ ] T148 [US4] Add gap identification to CemeteryBrowser highlighting sections with low photo coverage
- [ ] T149 [US4] Enhance CemeteryPage with CemeteryBrowser and StatisticsPanel
- [ ] T150 [US4] Create SectionPage in frontend/src/pages/SectionPage.tsx to display section details with plot list and photo gallery
- [ ] T151 [US4] Add section management UI to CemeteryPage (add section button, section list)
- [ ] T152 [US4] Add plot management UI to SectionPage (add plot button, plot list)
- [ ] T153 [US4] Add edit photo details modal to PhotoDetail allowing section/plot association updates
- [ ] T154 [US4] Add routing for /sections/:id to frontend/src/App.tsx

**Checkpoint**: All four user stories complete - full cemetery organization with statistics

---

## Phase 7: User Story 5 - Docker Deployment (Priority: P5)

**Goal**: Package system for easy deployment with Docker Compose and provide setup wizard for first admin account

**Independent Test**: Deploy Docker container on fresh server, verify database initialization, create first admin account, confirm web interface accessible

### Implementation for User Story 5

- [ ] T155 [P] [US5] Create backend/.dockerignore to exclude tests, __pycache__, .git
- [ ] T156 [P] [US5] Create frontend/.dockerignore to exclude node_modules, .git, build artifacts
- [ ] T157 [US5] Optimize backend/Dockerfile multi-stage build: builder stage with gcc/postgresql-dev, runtime stage with libpq5 only, non-root user
- [ ] T158 [US5] Optimize frontend/Dockerfile multi-stage build: Node builder stage, nginx runtime stage with optimized config
- [ ] T159 [US5] Create nginx.conf for frontend container with gzip compression, proxy headers, client_max_body_size 20M
- [ ] T160 [US5] Configure docker-compose.yml PostgreSQL service with postgis/postgis:15-3.3 image, named volume postgres-data
- [ ] T161 [US5] Configure docker-compose.yml backend service with depends_on postgres, photo-storage volume mount at /app/photos, environment variables
- [ ] T162 [US5] Configure docker-compose.yml frontend service with depends_on backend, port mapping 80:80
- [ ] T163 [US5] Add Docker secrets configuration to docker-compose.yml for db_password, session_secret
- [ ] T164 [US5] Create named volumes in docker-compose.yml: postgres-data, photo-storage
- [ ] T165 [US5] Create Docker network configuration in docker-compose.yml (bridge driver)
- [ ] T166 [US5] Add health checks to docker-compose.yml services (postgres, backend, frontend)
- [ ] T167 [US5] Create database initialization script in backend/src/db/init_db.py to run migrations on startup
- [ ] T168 [US5] Add startup check to backend/src/main.py to run init_db before serving requests
- [ ] T169 [P] [US5] Create scripts/backup.sh for backing up photo-storage volume and postgres database dump
- [ ] T170 [P] [US5] Create scripts/restore.sh for restoring from backup archives
- [ ] T171 [P] [US5] Create .env.example with all required environment variables documented
- [ ] T172 [P] [US5] Update README.md with Docker deployment instructions (5-step quick start)
- [ ] T173 [US5] Create deployment guide in docs/deployment.md with production configuration (HTTPS, reverse proxy, backup strategy)
- [ ] T174 [US5] Add first-run detection to backend to check if any users exist
- [ ] T175 [US5] Create setup wizard API endpoint GET /api/setup/status returning needs_setup boolean
- [ ] T176 [US5] Create POST /api/setup/init-admin endpoint to create first admin user (only works if no users exist)
- [ ] T177 [US5] Create SetupWizard component in frontend/src/components/Setup/SetupWizard.tsx with admin account creation form
- [ ] T178 [US5] Add setup wizard check to App.tsx on first load, redirect to /setup if needed
- [ ] T179 [US5] Create SetupPage in frontend/src/pages/SetupPage.tsx with welcome message and SetupWizard
- [ ] T180 [US5] Add routing for /setup to frontend/src/App.tsx
- [ ] T181 [US5] Test full deployment: run docker-compose up -d, verify all services start, access http://localhost, complete setup wizard
- [ ] T182 [US5] Test data persistence: restart containers with docker-compose restart, verify photos and database persist
- [ ] T183 [US5] Test backup/restore: run backup script, remove volumes, run restore script, verify data restored

**Checkpoint**: Complete deployment package ready for production use

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T184 [P] Add input validation middleware to backend using Pydantic models for all request bodies
- [ ] T185 [P] Create custom exception handlers in backend/src/main.py to return plain-language error messages per Constitution Principle II
- [ ] T186 [P] Add request logging middleware to backend logging all API requests with user ID, endpoint, duration
- [ ] T187 [P] Create loading spinner component in frontend/src/components/Loading/index.tsx for async operations
- [ ] T188 [P] Create error toast notification component in frontend/src/components/ErrorToast/index.tsx for user-friendly error display
- [ ] T189 [P] Add form validation helpers to frontend with error message formatting
- [ ] T190 [P] Create confirmation dialog component in frontend/src/components/ConfirmDialog/index.tsx for delete operations
- [ ] T191 Add soft delete confirmation to photo delete: show dialog "Are you sure? This will mark the photo as deleted but preserve the original file"
- [ ] T192 Add DELETE /api/photos/{id} endpoint with soft delete (set deleted_at timestamp)
- [ ] T193 Add DELETE /api/cemeteries/{id} endpoint with soft delete and check for associated photos
- [ ] T194 [P] Add ARIA labels and roles to all interactive components for accessibility (WCAG 2.1 AA compliance)
- [ ] T195 [P] Add keyboard navigation support to PhotoGallery (arrow keys to navigate, Enter to open detail)
- [ ] T196 [P] Test all forms with screen reader and fix any accessibility issues
- [ ] T197 [P] Create user manual in docs/user-manual.md with screenshots for all major workflows
- [ ] T198 [P] Create API documentation page using FastAPI auto-generated Swagger UI at /api/docs
- [ ] T199 [P] Create ADR for EXIF library choice in docs/adr/001-exif-library.md
- [ ] T200 [P] Create ADR for authentication strategy in docs/adr/002-session-auth.md
- [ ] T201 [P] Create ADR for storage strategy in docs/adr/003-local-filesystem.md
- [ ] T202 Add performance monitoring to track upload times, search query times, page load times
- [ ] T203 Add database query optimization: analyze slow queries, add missing indexes if needed
- [ ] T204 Run security audit: check for SQL injection, XSS, CSRF vulnerabilities, fix any issues found
- [ ] T205 Add rate limiting to authentication endpoints to prevent brute force attacks
- [ ] T206 Add file upload virus scanning using ClamAV (optional but recommended for production)
- [ ] T207 Test with large dataset: seed database with 1,000 photos, verify search performance <1 second
- [ ] T208 Test concurrent users: simulate 10 simultaneous photo uploads, verify no conflicts or data corruption
- [ ] T209 Run end-to-end test suite covering all user stories
- [ ] T210 Validate quickstart.md by following steps on fresh machine, update with any missing steps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Can start in parallel with US1, but references photographs table
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Can start in parallel, but best after US1 for testing
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) - Best after US1 (needs photos to organize)
- **User Story 5 (Phase 7)**: Depends on Foundational (Phase 2) - Can develop in parallel, integration testing needs other stories
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core MVP, no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses photographs table from US1 but can be developed independently
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Adds authentication, works with existing features
- **User Story 4 (P4)**: Best after US1 - Organizes photos, so having upload capability helps testing
- **User Story 5 (P5)**: Can develop in parallel - Deployment package for all features

### Within Each User Story

- Models before services (models define database structure)
- Services before API endpoints (services contain business logic)
- API endpoints before frontend components (components call APIs)
- Backend before frontend within each feature (frontend depends on API contracts)
- Core implementation before polish features

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks marked [P] can run in parallel (T003-T011)

**Phase 2 (Foundational)**:
- Database migrations can run sequentially (T012-T024)
- Models can be created in parallel after migrations (T025-T026)
- Schemas, config, and initial setup can run in parallel (T027-T035)

**Phase 3 (User Story 1)**:
- Models: T036-T039 can run in parallel
- Schemas: T040-T043 can run in parallel
- TypeScript types: T060-T061 can run in parallel
- API methods: T062-T063 can run in parallel
- Services must be sequential or have dependencies managed

**Phase 4 (User Story 2)**:
- SearchBar and PhotoGallery components (T085-T086) can develop in parallel

**Phase 5 (User Story 3)**:
- Schemas and types (T114-T116) can run in parallel
- LoginForm and RegisterForm (T117-T119) can develop in parallel

**Phase 6 (User Story 4)**:
- Services (T132-T133) can run in parallel
- Forms (T141-T143) can run in parallel

**Phase 7 (User Story 5)**:
- Docker ignore files (T155-T156) can run in parallel
- Scripts (T169-T173) can run in parallel

**Phase 8 (Polish)**:
- Most polish tasks marked [P] are independent and can run concurrently

---

## Parallel Example: User Story 1

```bash
# Launch all models together:
Task T036: Create Cemetery model
Task T037: Create Section model
Task T038: Create Plot model
Task T039: Create Photograph model

# Then launch all schemas together:
Task T040: Create Cemetery schema
Task T041: Create Section schema
Task T042: Create Plot schema
Task T043: Create Photograph schema

# Services must run sequentially due to dependencies:
Task T044: Create EXIFService (first)
Task T045: Add thumbnail generation to EXIFService (depends on T044)
Task T046: Create PhotoStorageService (can run with T044-T045)
Task T047: Add save_with_thumbnails (depends on T046)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T035) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T036-T077)
4. **STOP and VALIDATE**:
   - Upload a cemetery photo
   - Verify EXIF extraction works
   - Confirm thumbnails generated
   - Check photo retrievable with metadata
5. Deploy/demo if ready (optional)

**This gives you a working MVP**: Researchers can upload and catalog cemetery photos with automatic EXIF extraction.

### Incremental Delivery

1. Complete Setup (Phase 1) + Foundational (Phase 2) → Foundation ready
2. Add User Story 1 (Phase 3) → Test independently → **Deploy/Demo** (MVP!)
3. Add User Story 2 (Phase 4) → Test independently → **Deploy/Demo** (Search capability added)
4. Add User Story 3 (Phase 5) → Test independently → **Deploy/Demo** (Multi-user collaboration enabled)
5. Add User Story 4 (Phase 6) → Test independently → **Deploy/Demo** (Full organization features)
6. Add User Story 5 (Phase 7) → Test independently → **Deploy/Demo** (Production-ready deployment)
7. Add Polish (Phase 8) → **Final Release**

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (everyone needs this)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Photo upload & cataloging)
   - **Developer B**: User Story 2 (Search & browse) - can start models/services
   - **Developer C**: User Story 3 (Authentication) - independent feature
   - **Developer D**: User Story 5 (Docker deployment) - independent infrastructure
3. User Story 4 best after US1 complete (needs photos to organize)
4. Stories integrate independently as they complete

---

## Task Summary

**Total Tasks**: 210 tasks

**Task Count by Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 24 tasks
- Phase 3 (User Story 1 - Upload & Catalog): 42 tasks
- Phase 4 (User Story 2 - Search & Browse): 21 tasks
- Phase 5 (User Story 3 - Multi-User): 33 tasks
- Phase 6 (User Story 4 - Organization): 23 tasks
- Phase 7 (User Story 5 - Deployment): 29 tasks
- Phase 8 (Polish): 27 tasks

**Parallel Opportunities**: 81 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- ✅ US1: Upload photo, verify EXIF extraction, add cemetery details, retrieve photo
- ✅ US2: Catalog multiple photos, search by name/date/location, view results
- ✅ US3: Create accounts, upload as different users, verify shared catalog with attribution
- ✅ US4: Upload photos with sections/plots, browse hierarchy, view statistics
- ✅ US5: Deploy with Docker Compose, run setup wizard, access web interface

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 77 tasks for working MVP

---

## Notes

- [P] tasks = different files, no dependencies within that group
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- File paths are explicit in task descriptions
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Format Validation

✅ All 210 tasks follow the required checklist format:
- ✅ Checkbox: `- [ ]` prefix
- ✅ Task ID: Sequential T001-T210
- ✅ [P] marker: Present only on parallelizable tasks
- ✅ [Story] label: Present on all user story phase tasks (US1, US2, US3, US4, US5)
- ✅ Description: Clear action with file path
- ✅ No story label on Setup, Foundational, and Polish phases (correct)

Ready for execution with `/speckit.implement 001-photo-cataloging`

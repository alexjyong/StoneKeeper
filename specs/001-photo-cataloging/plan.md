# Implementation Plan: Cemetery Photo Cataloging System

**Branch**: `001-photo-cataloging` | **Date**: 2025-11-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-photo-cataloging/spec.md`

## Summary

Build a web-based cemetery photo cataloging system that allows researchers to upload photographs with automatic EXIF metadata extraction, search and browse the catalog, collaborate with other researchers, and organize photos by cemetery structure. The system will be self-hostable via Docker deployment.

**Technical Approach**: React frontend for interactive image display and tagging, Python FastAPI backend for EXIF operations and API services, PostgreSQL database with PostGIS extension for location data, Docker Compose for simplified deployment.

## Technical Context

**Language/Version**: Python 3.11+ (backend), Node.js 18+ / TypeScript 5+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.104+, Pillow/PIL for EXIF extraction, SQLAlchemy 2.0+ ORM, Alembic for migrations
- Frontend: React 18+, TypeScript, React Router, Axios for API calls
- Database: PostgreSQL 15+ with PostGIS 3.3+ extension

**Storage**: PostgreSQL 15+ with PostGIS for spatial data (GPS coordinates), object storage (local filesystem initially, S3-compatible optional)
**Testing**: pytest (backend), Jest + React Testing Library (frontend), Playwright for E2E tests
**Target Platform**: Linux server (Docker containers), web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend + backend separation)
**Performance Goals**:
- Photo upload with EXIF extraction: <5 seconds for 5-10MB images
- Search queries: <1 second for 10,000 photos
- Initial page load: <2 seconds
- Support 50 concurrent users

**Constraints**:
- EXIF metadata must be preserved byte-for-byte (no compression/modification)
- Maximum photo file size: 20MB
- Timezone-aware timestamps required
- Soft delete only (no hard deletes)

**Scale/Scope**:
- Target: 100,000 photographs per installation
- 50-100 concurrent users
- Multi-organization deployments (each org runs own instance)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Data Integrity First (NON-NEGOTIABLE) ✅

**Requirements**:
- ✅ Input validation before storage (FR-015)
- ✅ Reversible migrations with rollback (technical requirement)
- ✅ Soft delete with user confirmation (FR-016, FR-017)
- ✅ Timezone-aware timestamps (FR-018)
- ✅ EXIF metadata preservation (FR-002, FR-003)
- ✅ Unicode support for international characters (edge case documented)

**Implementation Plan**:
- Use Pydantic models for input validation in FastAPI
- Alembic migrations with down() functions for rollback
- Soft delete flag in database schema + confirmation dialogs in UI
- Use PostgreSQL TIMESTAMPTZ for all timestamps
- Store original photo files unmodified, extract EXIF to database separately
- PostgreSQL UTF-8 encoding with full Unicode support

**Status**: ✅ PASS - All requirements addressed

### Principle II: Non-Technical User Focus ✅

**Requirements**:
- ✅ Domain language in UI (headstones, burials, cemeteries)
- ✅ Plain-language error messages
- ✅ Point-and-click interface
- ✅ Help documentation with screenshots
- ✅ Inline examples and format hints
- ✅ Date pickers (not ISO-8601 strings)
- ✅ Progress indicators for uploads

**Implementation Plan**:
- Use cemetery domain terminology in all UI components and API naming
- Custom error handler middleware to translate technical errors
- React components for all interactions (no command-line requirements)
- Dedicated /help route with screenshot-based documentation
- React Date Picker component, format examples in form placeholders
- Progress bar component with percentage + estimated time remaining

**Status**: ✅ PASS - All requirements addressed

### Principle III: Maintainability & Simplicity ✅

**Requirements**:
- ✅ Self-documenting code with clear names
- ✅ Minimal dependencies
- ✅ Conventional patterns (REST API, standard React patterns)
- ✅ Single responsibility per module
- ✅ Database schema comments
- ✅ Named constants

**Implementation Plan**:
- Descriptive function/variable names, type hints in Python, TypeScript for frontend
- Limit dependencies: FastAPI (not Django/Flask+), React (no complex state libs initially)
- Standard REST API design, conventional React component structure
- Separate concerns: models, services, API routes, UI components
- SQL migration files include comments for each table/column purpose
- Constants file for all magic numbers (file size limits, timeouts, etc.)

**Status**: ✅ PASS - All requirements addressed

### Principle IV: Preservation-Grade Documentation ✅

**Requirements**:
- ✅ User-facing documentation before release
- ✅ API endpoint documentation
- ✅ Migration notes for schema changes
- ✅ Architecture Decision Records (ADRs)
- ✅ Current README

**Implementation Plan**:
- Quickstart guide, user manual in /docs
- OpenAPI/Swagger auto-generated from FastAPI decorators
- Each Alembic migration includes description and rationale
- ADR template in /docs/adr/ for major decisions (DB choice, tech stack, etc.)
- README with installation, deployment, development instructions

**Status**: ✅ PASS - All requirements addressed

### Security & Privacy ✅

**Requirements**:
- ✅ PII access controls
- ✅ Strip location metadata unless opted-in (NOTE: Conflicts with EXIF preservation - needs resolution)
- ✅ Modern password hashing
- ✅ SQL injection, XSS, CSRF protection

**Implementation Plan**:
- Row-level security via SQLAlchemy user context
- **CONFLICT RESOLUTION**: Keep GPS data in database but don't display by default in UI, add privacy toggle for exports
- bcrypt/argon2 for password hashing via passlib
- SQLAlchemy ORM prevents SQL injection, FastAPI CORS middleware, React escaping prevents XSS

**Status**: ⚠️ PASS with note - GPS privacy vs EXIF preservation conflict resolved by storing but not displaying by default

## Project Structure

### Documentation (this feature)

```text
specs/001-photo-cataloging/
├── plan.md              # This file
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Database schema and entities
├── quickstart.md        # Phase 1: User guide for deployment and usage
├── contracts/           # Phase 1: API specifications
│   └── api.yaml         # OpenAPI specification
└── checklists/
    └── requirements.md  # Specification validation checklist
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLAlchemy ORM models
│   │   ├── photograph.py
│   │   ├── cemetery.py
│   │   ├── section.py
│   │   ├── plot.py
│   │   └── user.py
│   ├── services/        # Business logic
│   │   ├── exif_service.py      # EXIF extraction
│   │   ├── photo_service.py     # Photo upload/storage
│   │   ├── search_service.py    # Search logic
│   │   └── auth_service.py      # Authentication
│   ├── api/             # FastAPI routes
│   │   ├── photos.py
│   │   ├── cemeteries.py
│   │   ├── search.py
│   │   └── auth.py
│   ├── db/              # Database configuration
│   │   ├── session.py
│   │   └── migrations/  # Alembic migrations
│   └── main.py          # FastAPI app entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── requirements.txt
└── Dockerfile

frontend/
├── src/
│   ├── components/      # React components
│   │   ├── PhotoUpload/
│   │   ├── PhotoGallery/
│   │   ├── SearchBar/
│   │   ├── CemeteryBrowser/
│   │   └── Auth/
│   ├── pages/           # Page-level components
│   │   ├── HomePage.tsx
│   │   ├── UploadPage.tsx
│   │   ├── SearchPage.tsx
│   │   ├── CemeteryPage.tsx
│   │   └── LoginPage.tsx
│   ├── services/        # API client
│   │   └── api.ts
│   ├── types/           # TypeScript types
│   └── App.tsx
├── tests/
├── package.json
└── Dockerfile

docker-compose.yml       # Docker Compose configuration
docs/
├── adr/                 # Architecture Decision Records
├── user-manual.md
└── deployment.md
```

**Structure Decision**: Web application structure with separate backend and frontend. Backend handles API, EXIF processing, database operations. Frontend provides interactive UI. This separation allows independent scaling and development. Docker Compose orchestrates backend, frontend, and PostgreSQL containers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - constitution requirements fully satisfied. All complexity is justified by functional requirements.

## Phase 0: Research & Technology Decisions

**Status**: Ready to execute

**Research Tasks**:

1. **EXIF Extraction Libraries (Python)**
   - Evaluate: Pillow/PIL, exifread, piexif
   - Criteria: Preservation of original data, format support (JPEG/PNG/TIFF), GPS coordinate extraction
   - **Decision needed**: Which library best preserves metadata integrity?

2. **Image Storage Strategy**
   - Evaluate: Local filesystem, S3-compatible object storage, database BYTEA
   - Criteria: Preservation of original files, performance at 100k photos, backup/restore simplicity
   - **Decision needed**: Filesystem vs object storage for initial release?

3. **PostGIS Usage for Location Data**
   - Research: PostGIS spatial indexes, coordinate format storage (decimal degrees vs PostGIS POINT)
   - Criteria: Query performance, standard compliance, ease of use
   - **Decision needed**: Best practice for storing and querying GPS coordinates?

4. **React Image Display Optimization**
   - Research: Lazy loading libraries, thumbnail generation strategies, progressive image loading
   - Criteria: Performance with large galleries, browser compatibility
   - **Decision needed**: Generate thumbnails server-side or client-side? Which lazy-load library?

5. **Authentication Strategy**
   - Evaluate: JWT tokens, session-based auth, OAuth2 (future)
   - Criteria: Simplicity (constitution principle III), security best practices
   - **Decision needed**: JWT or session-based for initial release?

6. **Database Migration Strategy**
   - Research: Alembic best practices, rollback procedures, data seeding
   - Criteria: Reversibility (constitution principle I), maintainability
   - **Decision needed**: Migration file organization, rollback testing approach?

7. **Docker Deployment Best Practices**
   - Research: Multi-stage builds, volume management for photos, environment configuration
   - Criteria: Easy deployment (SC-007), data persistence, security
   - **Decision needed**: Volume strategy for photo storage, secrets management?

**Output**: `research.md` with decisions and rationale for each area

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete with all decisions made

**Tasks**:

1. **Data Model Design** (`data-model.md`)
   - Detailed database schema for all entities from spec.md
   - Field types, constraints, indexes
   - Relationships and foreign keys
   - Soft delete implementation
   - PostGIS column definitions

2. **API Contract Definition** (`contracts/api.yaml`)
   - OpenAPI 3.0 specification
   - All endpoints from functional requirements
   - Request/response schemas
   - Error response formats
   - Authentication requirements

3. **User Quickstart Guide** (`quickstart.md`)
   - Docker deployment steps
   - First-time setup wizard
   - Basic user workflows (upload, search)
   - Troubleshooting common issues

4. **Agent Context Update**
   - Run update-agent-context script
   - Add technology stack to agent memory
   - Preserve manual additions

**Output**: data-model.md, contracts/api.yaml, quickstart.md, updated agent context

## Phase 2: Task Generation

**Prerequisites**: Phase 1 complete

**Tasks**:
- Run `/speckit.tasks 001-photo-cataloging` to generate dependency-ordered task list
- Tasks organized by user story priority (P1-P5)
- Include test tasks if specified in requirements

**Output**: `tasks.md` (generated by separate command)

## Next Steps

After this planning phase:

1. Review and approve plan.md (this document)
2. Execute Phase 0: Run research tasks
3. Execute Phase 1: Generate design artifacts
4. Run `/speckit.tasks` to create implementation task list
5. Run `/speckit.implement` to execute tasks

**Estimated Timeline**:
- Phase 0 (Research): 2-4 hours
- Phase 1 (Design): 4-6 hours
- Implementation: See tasks.md after generation

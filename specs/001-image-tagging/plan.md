# Implementation Plan: Image Upload and Tag Search

**Branch**: `001-image-tagging` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-image-tagging/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a minimal POC web application for cataloging cemetery photographs. Users can upload images with comma-separated tags and search for images by tag. Uses Flask backend with SQLite database and plain HTML/JavaScript frontend with local file storage.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Flask (web framework), Werkzeug (file uploads)
**Storage**: SQLite database (images table) + local filesystem (uploads/ directory)
**Testing**: Manual testing via browser (per constitution - tests optional for POC)
**Target Platform**: Local development server (localhost)
**Project Type**: Web application (single project structure - simplified per constitution)
**Performance Goals**: Search results < 2 seconds for up to 100 images
**Constraints**: Image file size limit 10MB, single-user POC (no authentication)
**Scale/Scope**: POC validation with < 100 images, 3 HTML pages, single developer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. POC-First ✅ PASS

- **Feature set limited**: Upload, tag, search only - no auth, no EXIF, no editing
- **Simplest thing that works**: Flask + SQLite + HTML (no React, no Docker)
- **No complex patterns**: Direct database access, single-file modules
- **Validation focus**: Proves core concept of image tagging and search

### II. Minimal Viable Solution ✅ PASS

- **Framework defaults**: Using Flask's built-in development server, Jinja2 templates
- **Built-in solutions**: SQLite (Python standard library), Werkzeug (included with Flask)
- **No premature optimization**: Single table design, local file storage
- **Minimal dependencies**: Only Flask required (includes Werkzeug, Jinja2)
- **Tests optional**: Manual browser testing for POC per constitution

### III. Expand Later ✅ PASS

- **Database evolution**: SQLite schema can migrate to proper many-to-many later
- **API extensibility**: Routes can be added without breaking existing ones
- **Modular frontend**: Separate HTML pages can be componentized later
- **No unused features**: No placeholders for auth, EXIF, or unimplemented capabilities

**Overall**: ✅ PASSES all constitutional requirements

## Project Structure

### Documentation (this feature)

```text
specs/001-image-tagging/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
stonekeeper/
├── app.py                    # Flask application entry point
├── database.py               # SQLite database initialization and queries
├── templates/                # Jinja2 HTML templates
│   ├── upload.html          # Upload and tag page
│   ├── search.html          # Search page
│   └── results.html         # Search results display
├── static/                   # Static assets
│   ├── style.css            # Basic styling
│   └── script.js            # Client-side JavaScript (optional)
└── uploads/                  # Uploaded image storage (gitignored)

tests/                        # Optional - not required for POC
└── manual_test_plan.md      # Manual testing checklist if needed
```

**Structure Decision**: Single project structure (Option 1) chosen per constitution principle of simplicity. Web application is simple enough that backend/frontend separation would add unnecessary complexity for POC. All Python code in root, templates in standard Flask location, static files served by Flask.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - this implementation fully aligns with all constitutional principles.

## Post-Design Constitution Review

*Re-evaluation after Phase 1 design artifacts completed*

### Design Artifacts Review

**Completed Artifacts**:
- ✅ [research.md](./research.md) - Technical decisions documented
- ✅ [data-model.md](./data-model.md) - Simplified single-table schema
- ✅ [contracts/routes.md](./contracts/routes.md) - Five Flask routes specified
- ✅ [quickstart.md](./quickstart.md) - Setup and testing guide
- ✅ CLAUDE.md - Agent context updated with Python 3.11+, Flask, SQLite

### Constitution Alignment Confirmation

**I. POC-First** ✅ CONFIRMED
- Research phase validated minimal technology choices (Flask over Django/FastAPI)
- Data model uses simplified schema over normalized design (per user directive)
- No complex patterns introduced during design (direct SQL queries, no ORM)
- Quickstart focuses on manual POC validation, not production deployment

**II. Minimal Viable Solution** ✅ CONFIRMED
- Routes specification defines 5 endpoints (no unused routes)
- Data model uses single table (no premature normalization)
- Research rejected heavier alternatives at each decision point
- No additional dependencies introduced beyond Flask

**III. Expand Later** ✅ CONFIRMED
- Data model documents migration path to normalized schema (research.md, data-model.md)
- Routes designed to be extendable (can add without breaking existing)
- Research documents future enhancements in "Out of Scope" sections
- No placeholder code or configuration for unimplemented features

**File Count Verification**:
- Python files: 2 planned (app.py, database.py) - both under 300 lines expected
- HTML templates: 3 planned (upload.html, search.html, tags.html)
- Total implementation files: < 10 (aligns with simplicity principle)

### Design Decisions Alignment Check

| Decision | Constitutional Principle | Alignment |
|----------|-------------------------|-----------|
| Single table schema | Minimal Viable Solution | ✅ Simplest approach per user directive |
| Flask development server | POC-First | ✅ No production server for POC |
| Manual testing | Minimal Viable Solution | ✅ Tests optional per constitution |
| LIKE queries for search | POC-First | ✅ Simplest working implementation |
| Local file storage | Minimal Viable Solution | ✅ No cloud dependencies |
| Plain HTML templates | POC-First | ✅ No build tooling required |

### Risks and Mitigations

**Risk 1: LIKE query false positives**
- Impact: Search "tag" might match "vintage"
- Mitigation: Documented in research.md and data-model.md as acceptable for POC
- Future path: Migration to normalized schema documented

**Risk 2: File over 300 lines**
- Impact: app.py might exceed constitutional guideline
- Mitigation: Can split into app.py + routes.py if needed
- Decision point: During implementation, not pre-optimization

**Risk 3: Single-file database bottleneck**
- Impact: SQLite performance with concurrent writes
- Mitigation: POC is single-user (no concurrency expected)
- Future path: PostgreSQL migration documented if multi-user needed

### Ready for Implementation

**Phase 0 (Research)**: ✅ COMPLETE
- All NEEDS CLARIFICATION resolved
- Technology choices justified
- Alternatives documented

**Phase 1 (Design)**: ✅ COMPLETE
- Data model defined with schema DDL
- API routes specified with request/response contracts
- Quickstart guide provides validation checklist
- Agent context updated

**Phase 2 (Tasks Generation)**: READY
- Run `/speckit.tasks` to generate implementation tasks
- Tasks will be organized by user story (US1: Upload, US2: Search, US3: Tags)
- Expected task count: ~15-20 tasks across 3 user stories

**Constitutional Compliance**: ✅ FULLY ALIGNED
- No violations introduced during design
- All decisions documented with rationale
- Simplicity maintained throughout planning process

### Next Command

```bash
/speckit.tasks
```

This will generate the tasks.md file with specific implementation tasks organized by user story, enabling independent development and testing of each feature increment.

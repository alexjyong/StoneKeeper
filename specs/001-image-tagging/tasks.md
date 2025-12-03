---

description: "Task list for image upload and tag search implementation"
---

# Tasks: Image Upload and Tag Search

**Input**: Design documents from `/specs/001-image-tagging/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/routes.md

**Tests**: Tests are OPTIONAL for POC per constitution - using manual browser testing instead

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `stonekeeper/` at repository root
- Flask templates: `stonekeeper/templates/`
- Static files: `stonekeeper/static/`
- Uploaded images: `stonekeeper/uploads/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure (stonekeeper/, templates/, static/, uploads/)
- [ ] T002 Install Flask dependency via pip
- [ ] T003 [P] Create .gitignore file to exclude stonekeeper/uploads/ and *.db files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Implement database initialization with schema in stonekeeper/database.py
- [ ] T005 [P] Create Flask app skeleton with configuration in stonekeeper/app.py
- [ ] T006 [P] Implement tag normalization helper function in stonekeeper/database.py
- [ ] T007 [P] Implement file validation helper (allowed_file) in stonekeeper/app.py
- [ ] T008 Configure Flask app settings (MAX_CONTENT_LENGTH, uploads folder) in stonekeeper/app.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload and Tag Image (Priority: P1) 🎯 MVP

**Goal**: Enable users to upload cemetery photographs with comma-separated tags

**Independent Test**: Visit upload page, select image file, enter "Smith, grave, 1920s" as tags, submit, and verify success message appears

### Implementation for User Story 1

- [ ] T009 [US1] Implement GET /upload route to display upload form in stonekeeper/app.py
- [ ] T010 [US1] Implement POST /upload route with file upload handling in stonekeeper/app.py
- [ ] T011 [US1] Implement save_image function with tag normalization in stonekeeper/database.py
- [ ] T012 [US1] Create upload.html template with file input and tag input fields in stonekeeper/templates/upload.html
- [ ] T013 [US1] Add upload form validation (file required, type check) in stonekeeper/app.py
- [ ] T014 [US1] Add success and error message display to upload.html template
- [ ] T015 [US1] Implement secure filename generation with timestamp in stonekeeper/app.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. User can upload images with tags and see success confirmation.

---

## Phase 4: User Story 2 - Search Images by Tag (Priority: P2)

**Goal**: Enable users to search for images by entering a tag query

**Independent Test**: Upload 3 images with different tag combinations, search for a tag that matches 2 of them, verify both appear in results

### Implementation for User Story 2

- [ ] T016 [US2] Implement GET /search route with optional tag query parameter in stonekeeper/app.py
- [ ] T017 [US2] Implement search_images_by_tag function with LIKE query in stonekeeper/database.py
- [ ] T018 [US2] Create search.html template with search form in stonekeeper/templates/search.html
- [ ] T019 [US2] Add results display section to search.html with image grid layout
- [ ] T020 [US2] Implement GET /uploads/<filename> route to serve uploaded images in stonekeeper/app.py
- [ ] T021 [US2] Add empty search query handling (show all or show none) in stonekeeper/app.py
- [ ] T022 [US2] Add "no results found" message display to search.html template

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can upload images and search for them by tag.

---

## Phase 5: User Story 3 - View Tag Summary (Priority: P3)

**Goal**: Display all unique tags with usage counts to help users understand their cataloging

**Independent Test**: Upload images with tags "Smith, grave, 1920s" and "Jones, monument, 1950s", view tag summary, verify all 6 unique tags appear with counts

### Implementation for User Story 3

- [ ] T023 [US3] Implement GET /tags route in stonekeeper/app.py
- [ ] T024 [US3] Implement get_tag_summary function with aggregation logic in stonekeeper/database.py
- [ ] T025 [US3] Create tags.html template with tag list display in stonekeeper/templates/tags.html
- [ ] T026 [US3] Add sorting to tag summary (by count descending) in stonekeeper/database.py
- [ ] T027 [US3] Add "no tags yet" message for empty database to tags.html template

**Checkpoint**: All user stories should now be independently functional. Complete POC with upload, search, and tag summary features.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T028 [P] Create basic CSS styling for consistent layout in stonekeeper/static/style.css
- [ ] T029 [P] Add navigation links between pages (upload, search, tags) to all templates
- [ ] T030 Add GET / route that redirects to /upload in stonekeeper/app.py
- [ ] T031 [P] Add error handlers for 404, 413, and 500 in stonekeeper/app.py
- [ ] T032 Run manual testing validation per quickstart.md test scenarios
- [ ] T033 [P] Add helpful comments to code explaining tag normalization and LIKE query limitations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (needs /uploads route) but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Completely independent, no integration needed

### Within Each User Story

- Routes before templates (need route handlers defined)
- Database functions before routes (routes call database functions)
- Templates can be developed in parallel with route logic (using placeholders)
- Form validation after basic route implementation
- Error handling after successful path works

### Parallel Opportunities

- **Setup phase**: All 3 tasks (T001, T002, T003) can run in parallel
- **Foundational phase**: Tasks T005-T007 marked [P] can run in parallel after T004 completes
- **Once Foundational completes**: All three user stories (Phase 3, 4, 5) can start in parallel if team capacity allows
- **Polish phase**: Tasks T028, T029, T031, T033 marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational phase complete, launch US1 tasks in groups:

# Group 1 (can run in parallel - different concerns):
Task: "Implement GET /upload route to display upload form in stonekeeper/app.py"
Task: "Create upload.html template with file input in stonekeeper/templates/upload.html"

# Group 2 (after Group 1 complete):
Task: "Implement POST /upload route with file upload handling in stonekeeper/app.py"
Task: "Implement save_image function in stonekeeper/database.py"

# Group 3 (after Group 2 complete):
Task: "Add upload form validation in stonekeeper/app.py"
Task: "Add success/error messages to upload.html template"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Tasks T009-T015)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md scenarios
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo MVP (upload with tags)
3. Add User Story 2 → Test independently → Demo search capability
4. Add User Story 3 → Test independently → Demo complete POC
5. Add Polish → Final POC validation
6. Each story adds value without breaking previous stories

### Single Developer Strategy (Recommended)

Per StoneKeeper constitution (single developer POC):

1. Work sequentially through phases (Setup → Foundational → US1 → US2 → US3 → Polish)
2. Complete foundational phase fully before starting any user story
3. Complete US1 (MVP) and validate before moving to US2
4. Commit frequently after each task completion
5. Use manual browser testing (tests optional per constitution)
6. Stop at any checkpoint to validate independently

---

## File Mapping Summary

**Python Files** (Backend):
- `stonekeeper/app.py` - Flask routes, request handling, validation (Tasks: T005, T007-T010, T013, T015-T016, T020-T021, T023, T030-T031)
- `stonekeeper/database.py` - Database schema, queries, helpers (Tasks: T004, T006, T011, T017, T024, T026)

**HTML Templates** (Frontend):
- `stonekeeper/templates/upload.html` - Upload form page (Tasks: T012, T014)
- `stonekeeper/templates/search.html` - Search form and results page (Tasks: T018-T019, T022)
- `stonekeeper/templates/tags.html` - Tag summary page (Tasks: T025, T027)

**Static Files**:
- `stonekeeper/static/style.css` - Basic styling (Task: T028)
- `stonekeeper/static/script.js` - Optional client-side JS (not required for POC)

**Configuration**:
- `.gitignore` - Exclude uploads/ and *.db (Task: T003)
- `requirements.txt` - Flask dependency (Task: T002)

**Storage**:
- `stonekeeper/uploads/` - Uploaded image files (created in T001)
- `stonekeeper.db` - SQLite database (auto-created by T004)

---

## Task Completion Validation

### User Story 1 (MVP) Validation

After completing Tasks T001-T015:

1. ✅ Can navigate to http://localhost:5000/upload
2. ✅ Can see upload form with file input and tags input
3. ✅ Can select image file (JPEG, PNG, GIF)
4. ✅ Can enter comma-separated tags
5. ✅ Can submit form and see success message
6. ✅ Image file saved to stonekeeper/uploads/
7. ✅ Database record created with normalized tags
8. ✅ Error message shown if no file selected
9. ✅ Error message shown if invalid file type

### User Story 2 Validation

After completing Tasks T016-T022:

1. ✅ Can navigate to http://localhost:5000/search
2. ✅ Can see search form with tag input
3. ✅ Can enter tag query and submit
4. ✅ Can see matching images displayed
5. ✅ Images clickable and display correctly
6. ✅ Tags shown for each result
7. ✅ "No results found" message if no matches
8. ✅ Case-insensitive search works

### User Story 3 Validation

After completing Tasks T023-T027:

1. ✅ Can navigate to http://localhost:5000/tags
2. ✅ Can see list of all unique tags
3. ✅ Each tag shows usage count
4. ✅ Tags sorted by count (most used first)
5. ✅ "No tags yet" message if database empty

### Complete POC Validation

After completing all phases:

1. ✅ All 3 user stories work independently
2. ✅ Navigation links work between all pages
3. ✅ Basic styling applied consistently
4. ✅ Error pages display for 404, 413, 500
5. ✅ All success criteria from spec.md met:
   - SC-001: Upload + tag in < 30 seconds ✅
   - SC-002: Search results < 2 seconds ✅
   - SC-003: Find images by any tag ✅
   - SC-004: 100% searchability ✅
   - SC-005: Accurate tag summary ✅

---

## Notes

- No [P] markers on routes that share app.py (sequential edits to same file)
- Templates marked for parallel with routes when using placeholders
- Database functions marked [P] when operating on different functions
- Manual testing per constitution (no automated tests required for POC)
- Commit after each task completion for easy rollback
- Stop at any checkpoint to validate story independently
- File paths are absolute from repository root
- All tasks follow strict checklist format: `- [ ] T### [P?] [Story?] Description with path`

---

## Summary

**Total Tasks**: 33
- Setup: 3 tasks
- Foundational: 5 tasks (blocking)
- User Story 1 (MVP): 7 tasks
- User Story 2: 7 tasks
- User Story 3: 5 tasks
- Polish: 6 tasks

**Parallel Opportunities**: 9 tasks marked [P] for parallel execution

**Critical Path**: Setup → Foundational → US1 (MVP) → US2 → US3 → Polish

**MVP Scope**: Phases 1-3 (Tasks T001-T015) delivers working upload and tag functionality

**Estimated Complexity**:
- Setup: Trivial (< 30 min)
- Foundational: Low (1-2 hours)
- User Story 1: Medium (2-3 hours)
- User Story 2: Medium (2-3 hours)
- User Story 3: Low (1-2 hours)
- Polish: Low (1 hour)

**Total Estimated Time**: 8-12 hours for complete POC (single developer)

Ready to implement with `/speckit.implement` or manually following task order.

<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0 (initial constitution creation)
- Modified principles: N/A (initial version)
- Added sections:
  * Core Principles (3 principles: POC-First, Minimal Viable Solution, Expand Later)
  * Development Workflow
  * Governance
- Removed sections: N/A
- Templates requiring updates:
  ✅ plan-template.md (reviewed - Constitution Check section aligns)
  ✅ spec-template.md (reviewed - requirements align with POC approach)
  ✅ tasks-template.md (reviewed - task structure supports single developer workflow)
- Follow-up TODOs: None
-->

# StoneKeeper Constitution

## Core Principles

### I. POC-First

StoneKeeper is a proof-of-concept for cataloging cemetery photographs with image upload, text tagging, and tag-based search capabilities.

**Rules**:
- Build the simplest thing that works
- Feature set limited to: upload images, add text tags, search by tags
- No authentication, user management, or multi-user features in POC
- No complex architecture patterns (repositories, factories, dependency injection)
- Direct implementation over abstraction layers

**Rationale**: POC stage prioritizes validating core functionality over production-ready features. Complexity added later after core concept proven.

### II. Minimal Viable Solution

Every implementation choice must justify why simpler alternatives were insufficient.

**Rules**:
- Use framework defaults and conventions
- Prefer built-in solutions over third-party libraries
- Single-file modules until complexity demands separation
- No premature optimization
- Document complexity only where code intent unclear
- Tests optional unless explicitly requested

**Rationale**: Single developer has limited time. Every abstraction, library, or pattern adds cognitive overhead. Start simple, refactor when pain points emerge.

### III. Expand Later

Design decisions must not prevent future expansion but must not implement unused features.

**Rules**:
- Database schema can evolve (migrations supported)
- API endpoints can be added without breaking existing ones
- Frontend components remain modular for future reuse
- No placeholders for future features
- No configuration options for unimplemented capabilities

**Rationale**: Balance between "works now" and "can grow later." Avoid both over-engineering and painting into corners.

## Development Workflow

**Single Developer Context**:
- Work directly on main branch or feature branches as needed
- Commit frequently with clear messages describing what changed
- No code review gates (self-review before commit)
- Run application locally to verify changes work

**Quality Gates** (all optional, use judgment):
- Manual testing of changed functionality
- Linting/formatting if configured
- Tests if written
- No blocking requirements for POC stage

**Simplicity Enforcement**:
- If adding a library, first check if built-in solution exists
- If creating abstraction, first implement concrete version
- If writing documentation, first ensure code is self-explanatory
- Question any file over 300 lines - likely needs split

## Governance

**Constitution Authority**:
- This document defines project philosophy and constraints
- Deviations must be documented with justification
- For POC: principles guide decisions but don't block progress
- Constitution evolves with project - update as learning occurs

**Amendment Process**:
1. Identify principle violation or new need
2. Document why current principle insufficient
3. Update constitution with new/modified principle
4. Increment version (semantic versioning)
5. Review templates for alignment

**Compliance**:
- Self-enforcement by solo developer
- Use constitution as decision framework, not rulebook
- When uncertain, choose simpler path
- Document non-obvious decisions in commit messages

**Version**: 1.0.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-03

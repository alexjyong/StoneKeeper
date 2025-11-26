# StoneKeeper Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0
Rationale: Removed Offline-First principle (IV) - StoneKeeper is a web application, not a mobile field app

Core Principles (Updated):
1. Data Integrity First - Cemetery records are historical artifacts requiring preservation-grade accuracy
2. Non-Technical User Focus - Interface must be accessible to researchers without technical backgrounds
3. Maintainability & Simplicity - Codebase must remain simple and well-documented for long-term sustainability
4. Preservation-Grade Documentation - All features must be documented at a level suitable for archival (renumbered from V)

Removed Principles:
- Offline-First Capability - Not applicable for web application architecture

Templates Status:
✅ plan-template.md - Constitution Check section ready for these principles
✅ spec-template.md - User scenarios align with non-technical focus
✅ tasks-template.md - Task organization supports maintainability

Performance Goals Updated:
- Removed "Offline data storage" requirement
- Retained web performance goals (page load, upload speed, search speed)

Follow-up Actions:
- None

Last Updated: 2025-11-26
-->

## Core Principles

### I. Data Integrity First (NON-NEGOTIABLE)

Cemetery records are irreplaceable historical artifacts. Every design decision must prioritize accuracy and preservation of information.

**Rules**:
- All user input MUST be validated before storage
- Data migrations MUST preserve original data and be reversible
- Database schema changes MUST include rollback procedures
- No data deletion without explicit user confirmation and soft-delete tracking
- All timestamps MUST include timezone information
- Photographs MUST retain original metadata (EXIF, location, date)
- Text encoding MUST support international characters and special symbols found on headstones

**Rationale**: Cemetery researchers are documenting historical records that may be the only surviving record of a person's existence. Data corruption or loss is unacceptable. Unlike commercial applications where data can be regenerated, cemetery records document irreplaceable physical artifacts that may deteriorate over time.

### II. Non-Technical User Focus

The primary users are cemetery researchers, genealogists, and historians—not software developers. The interface must be intuitive to users with minimal technical expertise.

**Rules**:
- UI terminology MUST use domain language (headstones, burials, cemeteries) not technical jargon (records, entities, databases)
- Error messages MUST explain what happened and how to fix it in plain language
- All features MUST be accessible via point-and-click interface (keyboard shortcuts optional)
- Help documentation MUST include screenshots and step-by-step instructions
- Forms MUST provide inline examples and format hints
- No required fields should use technical formats (use date pickers, not ISO-8601 strings)
- Complex operations MUST provide progress indicators and confirmation dialogs

**Rationale**: If the tool requires technical knowledge, it creates a barrier to cemetery preservation work. Researchers should focus on documenting headstones, not learning software. Every technical barrier reduces the number of cemeteries that get documented.

### III. Maintainability & Simplicity

StoneKeeper is a community preservation tool that must remain maintainable over decades, potentially by different developers.

**Rules**:
- Code MUST be self-documenting with clear variable/function names
- Complex logic MUST include explanatory comments describing the "why" not just the "what"
- Dependencies MUST be minimized—prefer standard library solutions
- New dependencies MUST be justified with documented rationale
- Architecture MUST favor simple, conventional patterns over clever optimizations
- Each module MUST have a single, clear responsibility
- Database schema MUST include comments documenting field purposes
- No "magic numbers"—all constants MUST be named and documented

**Rationale**: Cemetery preservation is a long-term endeavor. This codebase may need to be maintained 10+ years from now by volunteers with varying skill levels. Complexity is a liability. Simple, boring code is more valuable than clever, optimized code.

### IV. Preservation-Grade Documentation

All code, features, and design decisions must be documented to archival standards.

**Rules**:
- Every feature MUST include user-facing documentation before release
- API endpoints MUST be documented with request/response examples
- Database schema changes MUST be documented with migration notes
- Design decisions MUST be captured in ADR (Architecture Decision Record) format
- Breaking changes MUST include migration guides for existing users
- Code comments MUST be maintained as code evolves
- README MUST be kept current with installation and usage instructions

**Rationale**: Documentation is as important as the code itself. Future maintainers need to understand not just how the system works, but why it was built that way. Poor documentation leads to reimplementation, bugs, and lost institutional knowledge.

## Security & Privacy

Cemetery data often includes personal information about deceased individuals and their families. Privacy must be respected.

**Content**:
- Personally identifiable information (PII) MUST be stored with appropriate access controls
- Photo uploads MUST strip location metadata unless explicitly opted-in by user
- User authentication MUST follow current security best practices
- Passwords MUST be hashed using modern, approved algorithms
- SQL injection, XSS, and CSRF protections MUST be implemented
- Dependencies MUST be regularly updated for security patches
- Security vulnerabilities MUST be addressed within 7 days of discovery
- Data exports MUST include privacy warnings about sharing personal information

## Quality Standards

**Testing Requirements**:
- Data integrity operations (save, update, delete) MUST have automated tests
- Critical user workflows MUST have integration tests
- Database migrations MUST be tested with rollback procedures
- Breaking changes MUST be caught by tests before release

**Performance Goals**:
- Photo upload with metadata extraction: <5 seconds for typical smartphone image
- Search results: <1 second for typical query (<10,000 records)
- Initial page load: <2 seconds on 3G connection
- Image gallery browsing: Smooth scrolling with lazy loading for large collections

**Accessibility**:
- WCAG 2.1 Level AA compliance for all UI components
- Keyboard navigation support for all features
- Screen reader compatibility
- Minimum contrast ratios for text readability
- Text must be resizable up to 200% without loss of functionality

## Governance

**Authority**: This constitution supersedes all other development practices and preferences. When trade-offs arise, constitution principles are the tiebreaker.

**Amendments**:
- Changes to non-negotiable principles require documentation of why the principle is no longer valid
- New principles require demonstration of consistent need across multiple features
- Version must be incremented according to semantic versioning
- All amendments must include update date and rationale

**Compliance**:
- All pull requests MUST verify compliance with relevant constitution principles
- Feature specifications MUST reference applicable principles
- Architecture decisions that conflict with principles MUST be explicitly justified
- Code reviews MUST check for principle violations

**Complexity Justification**:
- Any deviation from principles requires documented justification
- Simpler alternatives must be explicitly rejected with reasoning
- Complexity must solve a real, current problem (not hypothetical future needs)

**Version**: 1.1.0 | **Ratified**: 2025-11-26 | **Last Amended**: 2025-11-26

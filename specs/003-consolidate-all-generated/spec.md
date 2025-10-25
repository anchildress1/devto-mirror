
# Feature Specification: Consolidate all generated site output

## Clarifications

### Session 2025-10-25
- Q: How should files that must be at repo root for external validation (e.g., robots.txt, GCP validation file) be handled in the new structure?
	→ A: The `/dist` (or build) directory will mimic the repo root for deployment. All such files (robots.txt, GCP validation file, index.html, etc.) must be generated inside `/dist` (not the project root), and the output structure should be as flat as possible except for posts/comments subfolders.

**Feature Branch**: `003-consolidate-all-generated`
**Created**: 2025-10-25
**Status**: Draft
**Input**: User description: "Consolidate the current generate_site.py flow. Right now it's throwing new files around root like a blog fairy. We need a dist folder or build of some kind. Which also means we can prob get the majority of that nasty bash script out of the deploy action, too."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - All site output in one directory (Priority: P1)

As a project maintainer, I want all generated site files (posts, index.html, robots.txt, sitemap.xml, comments, etc.) to be placed in a single `dist/` (or `build/`) directory, so that the project root remains clean and it is easier to manage, deploy, and preview the static site.

**Why this priority**: This is the core user value—organization, clarity, and easier deployment.

**Independent Test**: Run the site generator; verify that only the `dist/` directory contains new/updated site files, and the project root is unchanged except for the build directory.

**Acceptance Scenarios**:

1. **Given** a clean repository, **When** the site is generated, **Then** all output files (posts, index.html, robots.txt, sitemap.xml, comments, etc.) are found only in `dist/` and not in the project root.
2. **Given** a previous build exists, **When** a new site is generated, **Then** the `dist/` directory is updated and no files are left behind in the root.

---

### User Story 2 - Simplified deployment workflow (Priority: P2)

As a maintainer, I want the deployment workflow and scripts to only need to copy or deploy the `dist/` directory, so that the deployment process is simpler and less error-prone.

**Why this priority**: Reduces maintenance, risk of missing files, and complexity in CI/CD.

**Independent Test**: Review the deploy action/scripts; verify that only the `dist/` directory is referenced for publishing.

**Acceptance Scenarios**:

1. **Given** a deployment workflow, **When** the site is built, **Then** only the `dist/` directory is published to GitHub Pages (or equivalent), and no root-level files are required.

---

### User Story 3 - Documented new structure (Priority: P3)

As a contributor, I want clear documentation of the new output structure, so that I know where to find generated files and how to preview or deploy the site.

**Why this priority**: Ensures maintainability and onboarding for new contributors.

**Independent Test**: Review documentation; verify it describes the new `dist/` structure and how to use it.

**Acceptance Scenarios**:

1. **Given** the project documentation, **When** a contributor reads the setup or deployment instructions, **Then** the new output directory and its contents are clearly described.

---

### Edge Cases

- What happens if the `dist/` directory already exists? (Should be safely overwritten or cleaned before build)
- How does the system handle permission errors when writing to `dist/`?
- What if a user tries to run the generator without required environment variables?
- How are incremental updates handled in the new structure?
- What if a file (e.g., robots.txt, GCP validation file) must be at the root for external validation? (It must be generated inside `/dist` so that when `/dist` is deployed as root, these files are at the correct path.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate all site output (posts, index.html, robots.txt, sitemap.xml, comments, posts_data.json, etc.) into a single `dist/` (or `build/`) directory.
- **FR-002**: System MUST NOT leave generated files in the project root or outside the build directory after a successful run.
- **FR-003**: Deployment scripts and workflows MUST reference only the build directory for publishing.
- **FR-004**: Documentation MUST be updated to describe the new output structure and usage.
- **FR-005**: System MUST handle existing build directories safely (overwrite or clean as needed).
- **FR-006**: System MUST preserve security and path traversal protections in the new structure.
- **FR-007**: Any files that must be at the root for external validation (e.g., robots.txt, GCP validation file, index.html) MUST be generated inside `/dist` so that when `/dist` is deployed as root, these files are at the correct path. The output structure should be as flat as possible except for posts/comments subfolders.

### Key Entities

- **Build Directory**: The single directory (e.g., `dist/`) where all generated site files are placed.
- **Site Artifacts**: HTML files, posts, comments, index, robots.txt, sitemap.xml, posts_data.json, etc.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated site files are found only in the build directory after a run.
- **SC-002**: No root-level files (other than the build directory) are created or modified by the site generator.
- **SC-003**: Deployment workflow references only the build directory and succeeds without manual intervention.
- **SC-004**: Documentation is updated and contributors can follow it to preview or deploy the site using the new structure.

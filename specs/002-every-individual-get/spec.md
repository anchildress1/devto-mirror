# Feature Specification: Individual Verification and Update of All GitHub Actions Workflows

**Feature Branch**: `002-every-individual-get`
**Created**: 2025-10-17
**Status**: Draft
**Input**: User description: "every individual github actions workflow needs to be assisted and potentially updated for the new workflow, which was obviously left out of the last spec not cool by the way, so I need you to individually make sure each one of the four existing workflows operate as intended and GitHub actions. it is not simply good enough to report results a second criteria should be to eliminate code smells and vulnerabilities"

## Clarifications

### Session 2025-10-17

- Q: When security vulnerabilities are detected, what action should the workflow take? → A: Fail workflow, block merge, and create automated fix PR when possible
- Q: What entity or process is responsible for creating the automated fix PRs? → A: GitHub Actions bot creates PRs automatically using built-in fix suggestions from security tools
- Q: Should workflows be able to run concurrently or should they queue? → A: Allow concurrent runs (simple utility repo doesn't need complex orchestration)
- Q: What specific observability metrics should be collected? → A: Standard GitHub Actions logs and status checks (keep it simple)
- Q: Are workflow file updates themselves subject to automated changes? → A: Manual updates only (preserve control and simplicity)

### Session 2025-10-18 (Morning)

- Q: What GitHub token permissions should workflows use? → A: Least privilege with default built-in GITHUB_TOKEN and no more
- Q: How should GitHub Actions versions be maintained? → A: Prefer automated tooling (for example, Dependabot) to keep actions up to date, but manual or CI-driven update processes are acceptable when maintainers prefer explicit control.
- Q: What dependency caching strategy should workflows use? → A: uv cache with setup-python cache action (actions/setup-python@v6 supports uv caching natively)
- Q: What runner version strategy should be adopted? → A: ubuntu-latest with explicit fallback (use latest but document version pinning procedure for breaks)
- Q: Should security findings be uploaded to GitHub Security tab? → A: Keep current logs only approach (simple, no additional complexity)
- Q: What concurrency strategy should workflows use? → A: Cancel in-progress for same PR (cancel outdated runs when new commit pushed to same PR)

### Session 2025-10-18 (Schedule Changes)

- Q: Should other scheduled workflows be adjusted for cost optimization along with publish? → A: Manual workflow_dispatch triggers from GitHub Actions UI (keep CodeQL Monday 2:15 AM, change only publish to Wednesday 09:38 AM EDT)
- Q: How should workflows be tested to verify they actually work correctly? → A: Manual workflow_dispatch triggers from GitHub Actions UI
- Q: Which workflows need testing verification in this feature scope? → A: All four workflows
- Q: Does changing publish schedule require additional acceptance criteria? → A: No (existing workflow verification covers schedule correctness)
- Q: What exact cron expression for Wednesday 09:38 AM EDT? → A: Use EDT year-round (13:38 UTC on Wednesdays)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Security-CI Workflow Verification with Automated Remediation (Priority: P1)

A maintainer verifies that the `security-ci.yml` workflow operates correctly after the Python 3.11+ upgrade and ensures all code smells and vulnerabilities are eliminated from the codebase.

**Why this priority**: Security is the highest priority for project integrity. This workflow must not only run successfully but also actively identify and help eliminate vulnerabilities and code quality issues.

**Independent Test**: Can be fully tested by triggering the workflow via workflow_dispatch on a pull request and verifying that all security scans complete, vulnerabilities are reported, and code quality metrics meet defined standards.

**Acceptance Scenarios**:

1. **Given** the Python 3.11+ environment is configured, **When** the security-ci workflow runs, **Then** pip-audit completes dependency scanning without errors and reports any vulnerabilities found.
2. **Given** code changes are pushed, **When** bandit security scanning runs, **Then** all code is scanned and security issues are reported with severity levels.
3. **Given** the workflow completes, **When** results are reviewed, **Then** zero high-severity vulnerabilities remain unaddressed and code smell metrics show improvement or maintenance of quality standards.
4. **Given** flake8 linting runs, **When** code is analyzed, **Then** all style violations and potential bugs are identified and reported.

---

### User Story 2 - CodeQL Analysis Verification with Quality Gates (Priority: P1)

A maintainer verifies that the `codeql.yml` workflow operates correctly and provides comprehensive code quality analysis that eliminates security vulnerabilities and code smells.

**Why this priority**: CodeQL provides deep semantic analysis beyond basic linting and is critical for identifying complex security vulnerabilities and code quality issues.

**Independent Test**: Can be fully tested by triggering the workflow via workflow_dispatch and confirming CodeQL analysis completes with results uploaded to GitHub Security tab, showing actionable findings.

**Acceptance Scenarios**:

1. **Given** the Python 3.11+ environment is configured, **When** CodeQL analysis runs, **Then** all Python code is analyzed and results are uploaded to GitHub Security.
2. **Given** security queries are configured, **When** analysis completes, **Then** vulnerabilities are identified with severity ratings and remediation guidance is provided.
3. **Given** code quality queries run, **When** results are available, **Then** code smells and anti-patterns are identified and reported for developer action.

---

### User Story 3 - Publish Workflow Verification with Schedule Update (Priority: P2)

A maintainer verifies that the `publish.yaml` workflow operates correctly after the Python 3.11+ upgrade and successfully publishes the generated site without errors. The schedule is updated from daily to weekly (Wednesday 09:38 AM EDT) to reduce GitHub Actions costs.

**Why this priority**: Publishing is essential for site updates and must be reliable, but is slightly lower priority than security verification. Cost optimization is important for sustainability.

**Independent Test**: Can be fully tested by triggering the workflow via workflow_dispatch and confirming the site is generated and deployed to gh-pages branch without errors. Schedule change can be validated by inspecting cron syntax.

**Acceptance Scenarios**:

1. **Given** the Python 3.11+ environment and uv package manager are configured, **When** the publish workflow runs, **Then** dependencies are installed successfully via uv.
2. **Given** dependencies are installed, **When** site generation executes, **Then** all posts and pages are generated and committed to gh-pages without errors.
3. **Given** the workflow completes, **When** the gh-pages branch is checked, **Then** all generated files are present and the site is accessible.
4. **Given** the schedule is set to Wednesday 09:38 AM EDT, **When** the workflow file is inspected, **Then** the cron expression is "38 13 * * 3" (13:38 UTC on Wednesdays).

---

### User Story 4 - Refresh Workflow Verification (Priority: P2)

A maintainer verifies that the `refresh.yaml` workflow operates correctly after the Python 3.11+ upgrade and successfully refreshes all posts and comments with proper backup procedures.

**Why this priority**: Refresh functionality is important for data accuracy but can be manually triggered if issues arise, making it slightly lower priority.

**Independent Test**: Can be fully tested by manually triggering the workflow via workflow_dispatch and confirming posts/comments are refreshed and backup branches are created successfully.

**Acceptance Scenarios**:

1. **Given** the workflow is manually triggered, **When** the refresh process starts, **Then** a backup branch is created with the current gh-pages state.
2. **Given** the backup is created, **When** the last run timestamp is reset, **Then** the full regeneration is forced for all content.
3. **Given** the reset completes, **When** the publish workflow is triggered, **Then** all posts and comments are regenerated successfully.

---

### Edge Cases

- What happens if a workflow fails due to Python version incompatibility or missing dependencies?
- How does the system handle security vulnerabilities that cannot be auto-fixed?
- What happens if a workflow is triggered on a non-main branch?
- How are critical security findings prioritized and escalated to maintainers?
- What happens if automated fix PRs conflict with existing changes?
- What if CodeQL analysis times out or encounters unsupported code patterns?
- How does the system handle dependency conflicts between security tools and project dependencies?
- What if a workflow is configured with excessive GITHUB_TOKEN permissions beyond what's needed?
- What happens if Dependabot creates an action update PR that breaks workflow functionality?
- How does the system handle cache misses or corrupted cache entries?
- What if ubuntu-latest introduces breaking changes that require runner version pinning?
- What happens when concurrent workflow runs are cancelled mid-execution?
- What if the scheduled publish workflow runs but there are no new posts since the last run?
- How does the system handle workflow_dispatch testing on non-main branches without affecting production?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each workflow (security-ci, codeql, publish, refresh) MUST be individually verified to operate correctly with Python 3.11+ and uv package manager
- **FR-002**: Security-ci workflow MUST execute pip-audit, bandit, and flake8 scans and report all findings
- **FR-003**: Security-ci workflow MUST identify and report code smells and vulnerabilities with severity levels
- **FR-003a**: When vulnerabilities are detected, workflows MUST fail and block PR merge
- **FR-003b**: When auto-fixable vulnerabilities are detected, GitHub Actions bot MUST create automated fix PRs using built-in tool suggestions
- **FR-004**: CodeQL workflow MUST perform comprehensive semantic analysis and upload results to GitHub Security
- **FR-005**: CodeQL workflow MUST detect vulnerabilities and code quality issues beyond basic linting
- **FR-006**: Publish workflow MUST successfully install dependencies via uv and generate the complete site
- **FR-006a**: Publish workflow schedule MUST be changed from daily to weekly (Wednesday 09:38 AM EDT, cron: "38 13 * * 3")
- **FR-007**: Refresh workflow MUST create backup branches before forcing full content regeneration
- **FR-008**: All workflows MUST report errors and failures with actionable diagnostic information
- **FR-009**: Security findings MUST be categorized by severity (critical, high, medium, low) for prioritization
- **FR-010**: All workflows MUST complete within reasonable time limits (security-ci: 10 min, codeql: 15 min, publish: 15 min, refresh: 20 min)
- **FR-011**: Workflows MUST support concurrent execution without conflicts (simple utility repo approach)
- **FR-012**: Workflow files MUST be updated manually to preserve control and ensure intentional changes
- **FR-013**: Observability MUST rely on standard GitHub Actions logs and built-in status checks
- **FR-014**: All workflows MUST explicitly declare minimum required permissions for GITHUB_TOKEN following least privilege principle (no more than necessary)
- **FR-015**: GitHub Actions dependencies SHOULD be kept current via automated tooling (for example, Dependabot) where maintainers want automation; manual update processes or CI-driven update workflows are acceptable alternatives.
- **FR-016**: Workflows MUST use dependency caching via actions/setup-python@v6 native uv cache support to optimize CI performance
- **FR-017**: Workflows MUST use ubuntu-latest runners with documented fallback procedure for breaking changes
- **FR-018**: Workflows MUST implement concurrency controls to cancel in-progress runs when new commits are pushed to the same PR
- **FR-019**: All four workflows MUST support manual testing via workflow_dispatch trigger for validation

### Key Entities

- **Workflow File**: YAML configuration defining each GitHub Actions workflow with job definitions and dependencies
- **Security Finding**: A vulnerability, code smell, or quality issue identified by security tools with severity level and location
- **Workflow Run**: An execution instance of a workflow with status, logs, and results
- **Backup Branch**: A git branch created to preserve the current state before destructive operations
- **Quality Metric**: A measurable indicator of code quality (vulnerability count, code smell count, lint violations)
- **Schedule Expression**: Cron syntax defining when automated workflows execute

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four workflows execute successfully on Python 3.11+ environment without configuration errors when tested via workflow_dispatch
- **SC-002**: Security-ci workflow identifies and reports 100% of known vulnerabilities in dependencies within 10 minutes
- **SC-003**: CodeQL analysis completes and uploads findings to GitHub Security for 100% of Python code
- **SC-004**: Zero high-severity or critical vulnerabilities remain unaddressed after workflow execution and automated fix PRs are created
- **SC-005**: Code quality metrics (flake8 violations, code smells) are tracked and show zero increase in technical debt
- **SC-006**: Publish workflow successfully deploys updated site to gh-pages within 15 minutes of trigger
- **SC-006a**: Publish workflow schedule is verified as "38 13 * * 3" (Wednesday 09:38 AM EDT year-round)
- **SC-007**: Refresh workflow creates backup branches and regenerates all content within 20 minutes
- **SC-008**: Workflow failure rate is less than 5% over 30-day period excluding external dependency failures
- **SC-009**: Security findings are categorized and prioritized automatically with 100% accuracy
- **SC-010**: Maintainers receive actionable error reports within 5 minutes of workflow failure

## Assumptions

- Python 3.11+ is available and properly configured in GitHub Actions runners
- The uv package manager is installable and functional in the CI environment
- All project dependencies are compatible with Python 3.11+ and available via uv
- Security scanning tools (pip-audit, bandit, flake8, CodeQL) support Python 3.11+
- GitHub Actions GITHUB_TOKEN is scoped to minimum required permissions per workflow (least privilege)
- Security-ci workflow requires: contents: read, pull-requests: write (for automated fix PRs)
- CodeQL workflow requires: contents: read, security-events: write (for Security tab uploads)
- Publish workflow requires: contents: write (for gh-pages branch updates)
- Refresh workflow requires: contents: write, actions: write (for triggering publish workflow)
- Maintainers have access to GitHub Security tab for CodeQL findings
- Standard GitHub Actions notification mechanisms are sufficient for error reporting
- The project follows standard Python project structure recognizable by security tools
- Workflow execution time limits are reasonable for the project size and complexity
- This is a simple utility repository that doesn't require complex orchestration or external services
- Security tools provide built-in auto-fix capabilities that can be leveraged by GitHub Actions
- Concurrent workflow runs are acceptable and won't cause data corruption or conflicts
 - Repository maintainers are responsible for keeping actions and dependencies up to date; automation (for example, Dependabot) may be enabled at their discretion and must be validated against CI and installer choices before use.
- Auto-merge is acceptable for action updates that pass CI validation
- actions/setup-python@v6 supports native uv caching without additional configuration
- ubuntu-latest (currently 24.04) is stable enough for production use with documented fallback strategy
- Security findings in workflow logs provide sufficient visibility without SARIF upload complexity
- Cancelling in-progress workflow runs for the same PR is safe and won't corrupt state
- User posts content no later than 9:30 AM Wednesday, so 09:38 AM EDT schedule ensures fresh content is captured
- Using EDT year-round (13:38 UTC) is acceptable for simplicity despite not following DST transitions
- workflow_dispatch testing on feature branches is safe and won't interfere with production deployments

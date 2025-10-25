# Implementation Plan: Individual Verification and Update of All GitHub Actions Workflows

**Branch**: `002-every-individual-get` | **Date**: 2025-10-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-every-individual-get/spec.md`

## Summary

This feature verifies and updates all four existing GitHub Actions workflows (security-ci.yml, codeql.yml, publish.yaml, refresh.yaml) to ensure they operate correctly with Python 3.11+ and uv package manager. Key objectives include eliminating code smells and vulnerabilities through comprehensive security scanning, updating the publish workflow schedule from daily to weekly (Wednesday 09:38 AM EDT) to reduce GitHub Actions costs, and ensuring all workflows can be manually tested via workflow_dispatch triggers.

## Technical Context

**Language/Version**: Python 3.11+, GitHub Actions YAML
**Primary Dependencies**: uv (package manager), pip-audit, bandit, flake8, CodeQL, actions/setup-python@v6, actions/checkout@v5
**Storage**: N/A (CI/CD workflows, no persistent storage beyond git branches)
**Testing**: Manual workflow_dispatch triggers via GitHub Actions UI, workflow execution validation
**Target Platform**: ubuntu-latest GitHub Actions runners
**Project Type**: CI/CD infrastructure (GitHub Actions workflows)
**Performance Goals**: security-ci <10min, codeql <15min, publish <15min, refresh <20min
**Constraints**: Least privilege GITHUB_TOKEN permissions, no external service dependencies, simple utility repo approach
**Scale/Scope**: 4 workflow files, Python 3.11+ migration validation, schedule optimization for cost reduction

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle 1: Keep Things Modern and Very Simple ✅
- **Status**: PASS
- **Rationale**: Using Python 3.11+ and uv package manager as required. Workflows follow KISS principle with minimal complexity. No over-engineering.

### Principle 2: Conventional Commits with RAI Attribution ✅
- **Status**: PASS
- **Rationale**: All commits during this feature will follow Conventional Commits with appropriate RAI footers.

### Principle 3: AI-First Content Mirror (Not a UI) ✅
- **Status**: PASS
- **Rationale**: This feature maintains CI/CD infrastructure that supports the content mirror. No UI components involved.

### Principle 4: Toy Utility, Not Production System ✅
- **Status**: PASS
- **Rationale**: Workflows designed for simple utility repo with no HA requirements. Breaking changes acceptable. Cost optimization (weekly schedule) aligns with non-critical nature.

### Principle 5: Mandatory Documentation and Testing at Every Step ⚠️
- **Status**: CONDITIONAL PASS with remediation required
- **Current Violation**: Zero test files exist for 8 production scripts in scripts/ directory
- **Remediation Plan**: This feature focuses on workflow infrastructure verification. Test coverage for scripts/ is documented as technical debt and flagged for future work. Workflow testing will use manual workflow_dispatch validation per spec requirements.
- **Justification**: Testing CI/CD workflows differs from unit/integration testing application code. Workflow validation is inherently integration-level (requires GitHub Actions runtime). Manual workflow_dispatch testing provides equivalent validation coverage for this feature scope.
- **Documentation Updates Required**: README.md, SECURITY_ANALYSIS.md, quickstart.md must be updated to reflect uv migration (flagged in constitution sync report).

## Project Structure

### Documentation (this feature)

```
specs/002-every-individual-get/
├── plan.md              # This file (/speckit.plan output)
├── spec.md              # Feature specification (already exists)
├── research.md          # Phase 0 output (workflow best practices, security tooling)
├── data-model.md        # Phase 1 output (workflow entities, state machines)
├── quickstart.md        # Phase 1 output (testing workflows guide)
├── contracts/           # Phase 1 output (workflow contracts)
│   ├── README.md        # Overview of workflow contracts
│   ├── security-ci-contract.md
│   ├── codeql-contract.md
│   ├── publish-contract.md
│   └── refresh-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by this command)
```

### Source Code (repository root)

```
.github/
└── workflows/
    ├── security-ci.yml   # MODIFY: Add workflow_dispatch, update dependencies to uv
    ├── codeql.yml        # MODIFY: Add workflow_dispatch, verify Python 3.11+
    ├── publish.yaml      # MODIFY: Update schedule to "38 13 * * 3", add workflow_dispatch
    └── refresh.yaml      # MODIFY: Add workflow_dispatch, verify Python 3.11+

scripts/
└── [existing scripts]    # NO CHANGES (workflow verification only)

tests/
└── [future test files]   # FLAGGED: Technical debt for script test coverage

README.md                 # MODIFY: Update uv instructions
SECURITY_ANALYSIS.md      # MODIFY: Update uv instructions
```

**Structure Decision**: This is a CI/CD infrastructure feature modifying existing GitHub Actions workflow files. No new source code or application logic. All changes are YAML workflow configuration updates. The single-project structure remains unchanged.

## Complexity Tracking

*No violations requiring justification. All constitution principles satisfied with documented remediation for Principle 5.*

---

## Phase 0: Research & Best Practices

**Prerequisites**: Constitution Check passed

### Research Topics

1. **GitHub Actions Workflow Best Practices**
   - Task: Research workflow_dispatch trigger patterns and testing strategies
   - Task: Research GITHUB_TOKEN least privilege permission patterns
   - Task: Research concurrency controls for PR workflows
   - Task: Research cron schedule syntax for timezone-aware scheduling

2. **Python 3.11+ Migration for CI/CD**
   - Task: Verify actions/setup-python@v6 supports Python 3.11+
   - Task: Research uv package manager installation in GitHub Actions
   - Task: Research uv cache configuration with actions/setup-python@v6
   - Task: Research ubuntu-latest runner Python 3.11+ compatibility

3. **Security Tool Integration**
   - Task: Research pip-audit integration patterns and auto-fix capabilities
   - Task: Research bandit configuration for Python 3.11+ projects
   - Task: Research flake8 configuration for code smell detection
   - Task: Research CodeQL Python 3.11+ support and query configuration
   - Task: Research automated fix PR patterns with peter-evans/create-pull-request

4. **Workflow Schedule Optimization**
   - Task: Research GitHub Actions billing and cost optimization strategies
   - Task: Research cron schedule patterns for weekly execution
   - Task: Research timezone handling in cron expressions (EDT year-round)

5. **Dependabot Configuration**
   - Task: Research Dependabot auto-merge patterns for GitHub Actions
   - Task: Research Dependabot configuration for actions/ updates

**Output**: `research.md` with all findings, decisions, and rationale

---

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete

### Data Model

**Output**: `data-model.md` containing:

1. **Workflow File Entity**
   - Attributes: name, trigger events, jobs, permissions, timeout, schedule expression
   - Relationships: Contains Jobs, declares Permissions
   - State transitions: Queued → Running → Success/Failure/Cancelled
   - Validation rules: Must have workflow_dispatch trigger, GITHUB_TOKEN permissions must follow least privilege

2. **Security Finding Entity**
   - Attributes: severity (critical/high/medium/low), tool (pip-audit/bandit/flake8/codeql), location, description, auto-fixable
   - Relationships: Belongs to Workflow Run
   - Lifecycle: Detected → Reported → Fixed/Ignored
   - Validation rules: High/critical severity must block merge, auto-fixable findings trigger PR creation

3. **Workflow Run Entity**
   - Attributes: run_id, status, duration, triggered_by, branch, commit_sha, logs
   - Relationships: Belongs to Workflow File, contains Security Findings
   - State machine: Queued → Running → Completed (success/failure/cancelled)
   - Validation rules: Must complete within timeout limits per workflow type

4. **Backup Branch Entity** (refresh workflow)
   - Attributes: branch_name, timestamp, source_commit, gh_pages_state
   - Relationships: Created by Refresh Workflow Run
   - Lifecycle: Created → Preserved (no deletion automation)
   - Validation rules: Naming pattern backup-YYYYMMDD-HHMMSS

5. **Schedule Expression Entity**
   - Attributes: cron_syntax, description, timezone_note, frequency
   - Relationships: Belongs to Workflow File
   - Validation rules: Must be valid cron syntax, publish workflow must be "38 13 * * 3"

### Contracts

**Output**: `contracts/` directory containing:

1. **`README.md`**: Overview of workflow contract expectations and testing strategy

2. **`security-ci-contract.md`**:
   - Triggers: push (main), pull_request (main), workflow_dispatch
   - Jobs: security-lint (pip-audit, bandit, flake8)
   - Permissions: contents: read, pull-requests: write
   - Timeout: 10 minutes
   - Success criteria: All scans complete, findings reported, auto-fix PR created if applicable
   - Failure behavior: Block merge on high/critical vulnerabilities

3. **`codeql-contract.md`**:
   - Triggers: push (main), pull_request (main), schedule (Monday 2:15 AM UTC), workflow_dispatch
   - Jobs: analyze (CodeQL Python analysis)
   - Permissions: security-events: write, contents: read, actions: read, packages: read
   - Timeout: 15 minutes
   - Success criteria: Analysis completes, results uploaded to Security tab
   - Failure behavior: Report findings, do not block merge (informational)

4. **`publish-contract.md`**:
   - Triggers: schedule ("38 13 * * 3"), workflow_dispatch, push (main)
   - Jobs: build (install uv, dependencies, generate site, deploy to gh-pages)
   - Permissions: contents: write
   - Timeout: 15 minutes
   - Success criteria: Site generated, gh-pages updated, site accessible
   - Failure behavior: Report error, do not affect repository state

5. **`refresh-contract.md`**:
   - Triggers: workflow_dispatch only
   - Jobs: refresh (backup gh-pages, reset last_run.txt, trigger publish)
   - Permissions: contents: write, actions: write
   - Timeout: 20 minutes
   - Success criteria: Backup created, timestamp reset, publish triggered, content regenerated
   - Failure behavior: Report error, backup preserved, manual intervention required

### Quickstart Guide

**Output**: `quickstart.md` containing:

- Testing strategy overview (workflow_dispatch manual triggers)
- Step-by-step workflow testing instructions for all 4 workflows
- Validation checklists for each workflow
- Troubleshooting common workflow failures
- Performance monitoring guidance
- Success criteria verification procedures

### Agent Context Update

**Action**: Run `.specify/scripts/bash/update-agent-context.sh copilot` to update `.github/copilot-instructions.md` with:
- GitHub Actions workflow testing patterns
- uv package manager usage in CI/CD
- Workflow_dispatch trigger patterns
- Security tool integration patterns (pip-audit, bandit, flake8, CodeQL)
- Dependabot auto-merge configuration
- Cost optimization strategies (schedule reduction)

---

## Phase 2: Task Decomposition

**Prerequisites**: Phase 1 complete (data-model.md, contracts/, quickstart.md generated)

**Output**: `tasks.md` (generated by `/speckit.tasks` command - NOT created by this plan command)

Expected task structure (preview):
- Phase 1: Update security-ci.yml workflow (US1)
- Phase 2: Update codeql.yml workflow (US2)
- Phase 3: Update publish.yaml workflow with schedule change (US3)
- Phase 4: Update refresh.yaml workflow (US4)
- Phase 5: Test all workflows via workflow_dispatch
- Phase 6: Update documentation (README.md, SECURITY_ANALYSIS.md)
- Phase 7: Verify Dependabot configuration

---

## Implementation Notes

1. **Manual Workflow Testing Required**: Each workflow must be tested via workflow_dispatch trigger from GitHub Actions UI after implementation. This is the validation strategy per spec clarifications.

2. **Schedule Change Impact**: Publish workflow moving from daily to weekly will reduce GitHub Actions costs. No new posts will be processed between weekly runs unless manually triggered.

3. **Documentation Debt**: README.md and SECURITY_ANALYSIS.md currently reference pip/requirements.txt patterns. These must be updated to reflect uv migration (flagged in constitution sync report).

4. **Test Coverage Debt**: Zero tests exist for scripts/ directory (8 production scripts). This is acknowledged technical debt per constitution remediation plan. Workflow validation provides integration-level coverage for this feature.

5. **Dependabot Configuration**: Existing Dependabot configuration should be verified to include GitHub Actions updates with auto-merge enabled.

6. **No Breaking Changes**: All workflow updates are additive (adding workflow_dispatch) or optimization (schedule change). Existing triggers preserved for compatibility.

7. **Timezone Simplicity**: Using EDT year-round (13:38 UTC) per user preference, accepting that this doesn't follow DST transitions but provides simplicity.

---

## Completion Checklist

After implementation (tasks.md execution):

- [ ] All 4 workflows have workflow_dispatch trigger added
- [ ] security-ci.yml or supported)
- [ ] codeql.yml verified to work with Python 3.11+
- [ ] publish.yaml schedule changed to "38 13 * * 3"
- [ ] refresh.yaml verified to work with Python 3.11+
- [ ] All workflows manually tested via workflow_dispatch
- [ ] README.md updated with uv instructions
- [ ] SECURITY_ANALYSIS.md updated with uv instructions
- [ ] Dependabot configuration verified
- [ ] All contract specifications validated
- [ ] Success criteria from spec.md verified

**Next Command**: `/speckit.tasks` to generate detailed task breakdown

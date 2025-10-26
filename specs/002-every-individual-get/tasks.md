# Implementation Tasks: Individual Verification and Update of All GitHub Actions Workflows

**Feature Branch**: `002-every-individual-get`
**Created**: 2025-10-18
**Source**: Generated from [spec.md](./spec.md), [plan.md](./plan.md), and planning documents

## Overview

This document provides sequenced, executable tasks for updating and verifying all four GitHub Actions workflows to support Python 3.11+, uv package manager, automated security remediation, and modern CI/CD best practices. Tasks are organized by user story for independent implementation and testing.

**Total Tasks**: 27
**Estimated Completion**: 2-3 days (with parallelization)
**MVP Scope**: User Story 1 (Security-CI Workflow) - Tasks T001-T011

## Tech Stack

- **Language**: Python 3.11+
- **Package Manager**: uv
- **CI/CD**: GitHub Actions
- **Security Tools**: pip-audit, bandit, flake8, CodeQL
- **Actions**: actions/checkout@v5, actions/setup-python@v6, github/codeql-action@v3, peter-evans/create-pull-request@v5

## Implementation Strategy

1. **Setup First**: Configure Dependabot and create documentation (Phase 1)
2. **Security Workflows First**: User Story 1 (Security-CI) and User Story 2 (CodeQL) are P1 priority - implement before publishing workflows
3. **Independent Stories**: Each user story can be tested independently before moving to the next
4. **MVP Delivery**: User Story 1 provides immediate value - can ship after T011
5. **Incremental Rollout**: Test each workflow thoroughly before proceeding to next

## Phase 1: Setup and Infrastructure

**Goal**: Establish foundation for workflow modernization

### T001 [P] - Configure Dependabot for GitHub Actions

**File**: `.github/dependabot.yml`

**Description**: Create or update Dependabot configuration to automatically update GitHub Actions versions with auto-merge enabled for passing CI.

**Requirements**:
- Enable `github-actions` ecosystem
- Set update interval to daily or weekly
- Configure auto-merge for minor/patch updates
- Set target branch to `main`

**Acceptance**:
- Dependabot configuration file created/updated
- Auto-merge labels configured
- First Dependabot PR appears within 24 hours

**Reference**: FR-015, Session 2025-10-18 clarification

---

### T002 [P] - Document Runner Fallback Procedure

**File**: `.github/RUNNER_FALLBACK.md`

**Description**: Create documentation for pinning ubuntu runner versions when breaking changes occur.

**Content**:
- Current runner strategy (ubuntu-latest)
- Steps to pin to specific version (e.g., ubuntu-24.04)
- Rollback procedure
- Testing checklist for new runner versions

**Acceptance**:
- Documentation file created
- Clear instructions for version pinning
- Referenced in copilot-instructions.md

**Reference**: FR-017, Session 2025-10-18 clarification

---

### T003 [P] - Update Agent Context Documentation

**File**: `.github/copilot-instructions.md`

**Description**: Add workflow guidance to agent context file with information about all four workflows, modernization decisions, and testing procedures.

**Content**:
- Workflow purposes and triggers
- Python 3.11+ and uv requirements
- Security scanning tools
- Least privilege permissions requirements
- Modernization decisions (Dependabot, caching, concurrency)

**Acceptance**:
- Copilot instructions updated
- All workflows documented
- Modernization decisions captured

**Reference**: Plan.md project structure

---

## Phase 2: User Story 1 - Security-CI Workflow Verification (Priority: P1)

**Story Goal**: Verify that the `security-ci.yml` workflow operates correctly with Python 3.11+ and actively eliminates code smells and vulnerabilities.

**Independent Test**: Trigger workflow on PR and verify all security scans complete with automated fix PR creation for vulnerabilities.

### T004 - Update Security-CI: Python and uv Setup

**File**: `.github/workflows/security-ci.yml`

**Description**: Update Python setup to use Python 3.11 with actions/setup-python@v6 and add native uv caching support.

**Changes**:
```yaml
- name: Set up Python
  uses: actions/setup-python@v6
  with:
    python-version: '3.11'
    cache: 'pip'  # Enable native pip/uv caching
```

**Acceptance**:
- Python version changed to 3.11
- setup-python action updated to v6
- Native caching enabled

**Reference**: FR-001, FR-016, security-ci-contract.md

---

### T005 - Update Security-CI: Add Explicit Permissions

**File**: `.github/workflows/security-ci.yml`

**Description**: Add explicit least privilege permissions block at workflow level.

**Changes**:
```yaml
permissions:
  contents: read           # For actions/checkout
  pull-requests: write     # For creating automated fix PRs
```

**Acceptance**:
- Permissions block added before jobs section
- Only required permissions declared
- No excessive permissions granted

**Reference**: FR-014, Session 2025-10-18 clarification, security-ci-contract.md

---

### T006 - Update Security-CI: Add Concurrency Controls

**File**: `.github/workflows/security-ci.yml`

**Description**: Add concurrency configuration to cancel in-progress runs when new commits pushed to same PR.

**Changes**:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Acceptance**:
- Concurrency block added after permissions
- Group uses workflow and ref
- Cancel-in-progress enabled

**Reference**: FR-018, Session 2025-10-18 clarification

---

### T007 - Update Security-CI: Migrate to uv Package Manager

**File**: `.github/workflows/security-ci.yml`

**Description**: Replace pip-based dependency installation with uv.

**Changes**:
- Remove pip install steps
- Add uv installer step
- Update dependency installation to use `uv pip install -e '.[dev]'`

**Before**:
```yaml
- name: Install dependencies for analysis
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
```

**After**:
```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: uv pip install -e '.[dev]'
```

**Acceptance**:
- uv installer step added
- All pip commands replaced with uv
- Dependencies install successfully

**Reference**: FR-001, FR-006, research.md area 3

---

### T008 - Update Security-CI: Add Timeout Limits

**File**: `.github/workflows/security-ci.yml`

**Description**: Add job-level timeout to ensure workflow completes within 10 minutes.

**Changes**:
```yaml
jobs:
  security-lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
```

**Acceptance**:
- Timeout added to security-lint job
- Set to 10 minutes per spec

**Reference**: FR-010, security-ci-contract.md

---

### T009 - Update Security-CI: Enhance Error Reporting

**File**: `.github/workflows/security-ci.yml`

**Description**: Add continue-on-error flags and result aggregation for complete security reporting before workflow failure.

**Changes**:
```yaml
- name: Run pip-audit
  run: pip-audit --progress=none
  continue-on-error: true
  id: pip_audit

- name: Run bandit
  run: bandit -r scripts -ll -iii
  continue-on-error: true
  id: bandit

- name: Run flake8
  run: flake8
  continue-on-error: true
  id: flake8

- name: Check security results
  if: steps.pip_audit.outcome == 'failure' || steps.bandit.outcome == 'failure' || steps.flake8.outcome == 'failure'
  run: |
    echo "::error::Security scans detected issues"
    exit 1
```

**Acceptance**:
- All security tools use continue-on-error
- Step IDs added for result tracking
- Final check step aggregates results
- Workflow fails if any security issue found

**Reference**: FR-002, FR-003, FR-008, research.md area 3

---

### T010 - Update Security-CI: Add Automated Fix PR Creation

**File**: `.github/workflows/security-ci.yml`

**Description**: Add step to create automated fix PRs when security vulnerabilities are detected and auto-fixable.

**Changes**:
```yaml
- name: Create automated fix PR
  if: failure() && (steps.pip_audit.outcome == 'failure' || steps.bandit.outcome == 'failure')
  uses: peter-evans/create-pull-request@v5
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    commit-message: 'fix: auto-remediate security vulnerabilities'
    title: 'Security: Automated vulnerability fixes'
    body: |
      Auto-generated fixes from security scans.

      **Tools**: pip-audit, bandit
      **Run**: ${{ github.run_id }}

      ⚠️ **Review Required**: This PR is blocked from auto-merge and requires manual review.
    branch: auto-fix/security-${{ github.run_id }}
    delete-branch: true
```

**Acceptance**:
- peter-evans/create-pull-request action added
- Runs only on security failure
- Creates PR with descriptive title and body
- Branch name follows pattern auto-fix/security-{run_id}
- PR requires manual review (no auto-merge)

**Reference**: FR-003a, FR-003b, research.md area 2

---

### T011 - Test Security-CI Workflow End-to-End

**Command**: Manual testing via PR

**Description**: Create test PR to validate all security-ci.yml changes work correctly.

**Test Steps**:
1. Create test branch from main
2. Push changes to trigger workflow
3. Verify Python 3.11 and uv install correctly
4. Verify all security scans execute
5. Check permissions are applied correctly
6. Verify timeout enforcement
7. Test automated fix PR creation (if vulnerabilities exist)

**Acceptance Criteria**:
- All acceptance scenarios from spec.md User Story 1 pass
- Workflow completes within 10 minutes
- Security scans report findings correctly
- Automated fix PR created when applicable
- No permission errors

**Reference**: spec.md User Story 1, quickstart.md scenario 1

---

**✓ CHECKPOINT**: Security-CI workflow fully operational. MVP complete at this point - can deliver value before proceeding.

---

## Phase 3: User Story 2 - CodeQL Analysis Verification (Priority: P1)

**Story Goal**: Verify that the `codeql.yml` workflow operates correctly with comprehensive code quality analysis.

**Independent Test**: Run workflow and confirm CodeQL analysis completes with results in GitHub Security tab.

### T012 - Update CodeQL: Add Explicit Permissions

**File**: `.github/workflows/codeql.yml`

**Description**: Verify and update permissions block follows least privilege principle.

**Current State**: Permissions already exist in workflow

**Changes**: Ensure permissions exactly match contract requirements:
```yaml
permissions:
  contents: read
  security-events: write
  packages: read
  actions: read
```

**Acceptance**:
- Permissions match codeql-contract.md
- No excessive permissions
- All required permissions present

**Reference**: FR-014, codeql-contract.md

---

### T013 - Update CodeQL: Add Concurrency Controls

**File**: `.github/workflows/codeql.yml`

**Description**: Add concurrency configuration to cancel in-progress runs.

**Changes**:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Acceptance**:
- Concurrency block added
- Matches security-ci pattern

**Reference**: FR-018

---

### T014 - Update CodeQL: Verify Python 3.11 Configuration

**File**: `.github/workflows/codeql.yml`

**Description**: Verify CodeQL workflow analyzes Python 3.11+ code correctly. Update if setup-python step exists.

**Current State**: CodeQL uses "none" build mode for Python (no explicit setup needed)

**Changes**: Ensure matrix specifies python language and build-mode: none is set:
```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - language: python
        build-mode: none
```

**Acceptance**:
- Matrix configuration correct
- Python language specified
- Build mode set to none (no compilation)

**Reference**: FR-001, codeql-contract.md, research.md area 4

---

### T015 - Update CodeQL: Verify Timeout Configuration

**File**: `.github/workflows/codeql.yml`

**Description**: Ensure timeout is set appropriately for CodeQL analysis (can be longer than other workflows).

**Current State**: timeout-minutes: 360 (6 hours)

**Validation**: Confirm this is acceptable per FR-010 guidance (15 min recommended but CodeQL can legitimately take longer for initial runs)

**Acceptance**:
- Timeout documented and justified
- Within reasonable bounds for CodeQL

**Reference**: FR-010, codeql-contract.md

---

### T016 - Update CodeQL: Verify Security Queries Configuration

**File**: `.github/workflows/codeql.yml`

**Description**: Ensure security-extended and security-and-quality query packs are enabled.

**Current State**: Check existing queries configuration

**Changes**: Verify or add:
```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: ${{ matrix.language }}
    build-mode: ${{ matrix.build-mode }}
    queries: +security-extended,security-and-quality
```

**Acceptance**:
- Query packs include security-extended
- Query packs include security-and-quality
- Prefix with + to combine with default queries

**Reference**: FR-004, FR-005, research.md area 4, codeql-contract.md

---

### T017 - Update CodeQL: Verify Action Versions

**File**: `.github/workflows/codeql.yml`

**Description**: Ensure github/codeql-action uses @v3 (latest stable).

**Current State**: Check current version

**Changes**: Update to v3 if not already:
```yaml
- uses: github/codeql-action/init@v3
- uses: github/codeql-action/analyze@v3
```

**Acceptance**:
- Both init and analyze use @v3
- No deprecated versions

**Reference**: FR-015, research.md area 4

---

### T018 - Test CodeQL Workflow End-to-End

**Command**: Manual testing via PR or workflow_dispatch

**Description**: Trigger CodeQL workflow and validate all functionality.

**Test Steps**:
1. Trigger workflow via push or manual dispatch
2. Monitor workflow execution (may take 10-15 minutes)
3. Verify analysis completes successfully
4. Check GitHub Security tab for uploaded results
5. Verify findings are categorized by severity
6. Check workflow logs for any errors

**Acceptance Criteria**:
- All acceptance scenarios from spec.md User Story 2 pass
- CodeQL analysis completes without errors
- Results uploaded to Security tab
- Findings categorized correctly
- Permissions work correctly

**Reference**: spec.md User Story 2, quickstart.md scenario 2

---

**✓ CHECKPOINT**: Both P1 security workflows operational. Core security capabilities complete.

---

## Phase 4: User Story 3 - Publish Workflow Verification (Priority: P2)

**Story Goal**: Verify that the `publish.yaml` workflow operates correctly with Python 3.11+ and uv.

**Independent Test**: Trigger workflow and verify site generates and deploys to gh-pages.

### T019 - Update Publish: Add Explicit Permissions

**File**: `.github/workflows/publish.yaml`

**Description**: Add explicit permissions block (currently implicit).

**Changes**:
```yaml
permissions:
  contents: write  # Required for pushing to gh-pages branch
```

**Acceptance**:
- Permissions block added at workflow level
- Only contents: write declared
- Follows least privilege

**Reference**: FR-014, publish-contract.md

---

### T020 - Update Publish: Add Concurrency Controls

**File**: `.github/workflows/publish.yaml`

**Description**: Add concurrency configuration to cancel in-progress runs.

**Changes**:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Acceptance**:
- Concurrency block added
- Consistent with other workflows

**Reference**: FR-018

---

### T021 - Update Publish: Verify Python 3.11 and uv Setup

**File**: `.github/workflows/publish.yaml`

**Description**: Verify Python 3.11 and uv are correctly configured. Enable caching.

**Current State**: Already uses Python 3.11 and uv

**Changes**: Add caching to setup-python step:
```yaml
- name: Setup Python
  uses: actions/setup-python@v6.0.0
  with:
    python-version: "3.11"
    cache: 'pip'  # Enable native pip/uv caching
```

**Acceptance**:
- Python 3.11 confirmed
- setup-python@v6 confirmed
- Caching enabled
- uv installation present

**Reference**: FR-001, FR-006, FR-016, publish-contract.md

---

### T022 - Update Publish: Add Timeout Configuration

**File**: `.github/workflows/publish.yaml`

**Description**: Add job-level timeout to ensure workflow completes within 15 minutes.

**Changes**:
```yaml
jobs:
  build:
    if: ${{ github.ref != 'refs/heads/gh-pages' }}
    runs-on: ubuntu-latest
    timeout-minutes: 15
```

**Acceptance**:
- Timeout set to 15 minutes
- Applied to build job

**Reference**: FR-010, publish-contract.md

---

### T023 - Test Publish Workflow End-to-End

**Command**: Manual trigger or push to main

**Description**: Validate publish workflow generates and deploys site correctly.

**Test Steps**:
1. Trigger workflow via workflow_dispatch or push
2. Monitor workflow execution
3. Verify dependencies install via uv
4. Verify site generation completes
5. Check gh-pages branch for updated content
6. Verify site is accessible

**Acceptance Criteria**:
- All acceptance scenarios from spec.md User Story 3 pass
- Workflow completes within 15 minutes
- Site deploys successfully
- No permission errors
- Content appears correctly

**Reference**: spec.md User Story 3, quickstart.md scenario 3

---

**✓ CHECKPOINT**: Publishing workflow operational. Site deployment working.

---

## Phase 5: User Story 4 - Refresh Workflow Verification (Priority: P2)

**Story Goal**: Verify that the `refresh.yaml` workflow operates correctly with proper backup procedures.

**Independent Test**: Manually trigger workflow and verify backup creation and content refresh.

### T024 - Update Refresh: Verify Explicit Permissions

**File**: `.github/workflows/refresh.yaml`

**Description**: Verify permissions block follows least privilege for triggering other workflows.

**Current State**: Already has permissions block

**Validation**: Ensure permissions match contract:
```yaml
permissions:
  contents: write  # For backup branch creation
  actions: write   # For triggering publish workflow
```

**Acceptance**:
- Permissions match refresh-contract.md
- No excessive permissions

**Reference**: FR-014, refresh-contract.md

---

### T025 - Update Refresh: Add Concurrency Controls

**File**: `.github/workflows/refresh.yaml`

**Description**: Add concurrency configuration (though refresh is typically manual).

**Changes**:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Acceptance**:
- Concurrency block added
- Consistent with other workflows

**Reference**: FR-018

---

### T026 - Update Refresh: Add Timeout Configuration

**File**: `.github/workflows/refresh.yaml`

**Description**: Add job-level timeout to ensure workflow completes quickly (only triggers other workflow).

**Changes**:
```yaml
jobs:
  refresh:
    runs-on: ubuntu-latest
    timeout-minutes: 5
```

**Acceptance**:
- Timeout set to 5 minutes
- Applied to refresh job

**Reference**: FR-010, refresh-contract.md

---

### T027 - Test Refresh Workflow End-to-End

**Command**: Manual workflow_dispatch trigger

**Description**: Validate refresh workflow creates backup and triggers publish workflow.

**Test Steps**:
1. Trigger workflow via workflow_dispatch
2. Monitor workflow execution
3. Verify backup branch created with timestamp
4. Verify last_run.txt reset
5. Verify publish workflow triggered
6. Confirm all content regenerates

**Acceptance Criteria**:
- All acceptance scenarios from spec.md User Story 4 pass
- Backup branch created successfully
- Publish workflow triggered
- Content refreshed completely
- Workflow completes within 20 minutes total (5 min + 15 min publish)

**Reference**: spec.md User Story 4, quickstart.md scenario 4

---

**✓ CHECKPOINT**: All four workflows updated and operational.

---

## Phase 6: Polish and Integration

**Goal**: Finalize documentation and perform comprehensive validation.

### T028 [P] - Create Workflow Validation Script

**File**: `scripts/validate_workflows.py`

**Description**: Create Python script to validate workflow YAML files against contracts.

**Functionality**:
- Load workflow YAML files
- Check required fields present
- Verify Python versions
- Validate permissions blocks
- Check timeout configurations
- Report any deviations from contracts

**Acceptance**:
- Script runs successfully
- All four workflows validated
- Reports clear pass/fail status

**Reference**: contracts/ directory

---

### T029 [P] - Update README with Workflow Information

**File**: `README.md`

**Description**: Add section documenting the four GitHub Actions workflows and their purposes.

**Content**:
- Brief description of each workflow
- When they trigger
- What they do
- Links to workflow files

**Acceptance**:
- README updated
- Clear workflow documentation
- Helpful for maintainers

**Reference**: Plan.md

---

### T030 - Perform Full Integration Testing

**Command**: Manual end-to-end testing

**Description**: Execute comprehensive test suite across all workflows to validate complete feature.

**Test Matrix**:
| Workflow | Trigger | Expected Outcome |
|----------|---------|------------------|
| security-ci | Push to main | All scans pass |
| security-ci | PR with vuln | Fix PR created |
| codeql | Weekly schedule | Results in Security tab |
| publish | Daily schedule | Site updated |
| refresh | Manual trigger | Backup + regeneration |

**Acceptance Criteria**:
- All success criteria from spec.md met (SC-001 through SC-010)
- All workflows execute correctly
- Performance meets targets
- No permission errors
- Documentation complete and accurate

**Reference**: spec.md Success Criteria, quickstart.md

---

## Task Dependencies

```
Phase 1 (Setup):
T001, T002, T003 → Can all run in parallel [P]
↓
Phase 2 (Security-CI):
T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011
(Sequential, same file)
↓
Phase 3 (CodeQL):
T012 → T013 → T014 → T015 → T016 → T017 → T018
(Sequential, same file)
↓
Phase 4 (Publish):
T019 → T020 → T021 → T022 → T023
(Sequential, same file)
↓
Phase 5 (Refresh):
T024 → T025 → T026 → T027
(Sequential, same file)
↓
Phase 6 (Polish):
T028, T029 → Can run in parallel [P]
↓
T030 (Final integration testing)
```

**Parallel Opportunities**:
- Phase 1: All tasks can run in parallel
- Phase 6: Documentation tasks can run in parallel
- Phases 2-5: Each user story is independent and can be implemented by different developers simultaneously

## Story Completion Order

1. **User Story 1** (Security-CI) → T004-T011 → Essential security capability
2. **User Story 2** (CodeQL) → T012-T018 → Completes security verification suite
3. **User Story 3** (Publish) → T019-T023 → Enables site deployment
4. **User Story 4** (Refresh) → T024-T027 → Adds content refresh capability

Each story is independently testable and deliverable.

## Validation Checklist

After completing all tasks:

- [ ] All four workflows use Python 3.11+
- [ ] All workflows use uv package manager
- [ ] All workflows have explicit least privilege permissions
- [ ] All workflows have concurrency controls
- [ ] All workflows have appropriate timeouts
- [ ] All workflows have caching enabled (where applicable)
- [ ] Security-ci creates automated fix PRs
- [ ] CodeQL uploads to GitHub Security tab
- [ ] Publish deploys to gh-pages successfully
- [ ] Refresh creates backup branches
- [ ] Dependabot configured for action updates
- [ ] Documentation complete and accurate
- [ ] All success criteria from spec.md met

## Notes

- **No backwards compatibility**: Per constitution, no need to maintain old pip-based workflows
- **Simple utility repo**: Avoid over-engineering, use GitHub native features
- **Manual workflow updates**: No automated workflow file modifications
- **Concurrent execution allowed**: No complex locking needed
- **Tests not explicitly required**: Feature spec doesn't mandate automated tests beyond workflow validation
- **MVP at T011**: Security-CI workflow alone provides immediate value

## Success Metrics

Track these metrics post-implementation:

1. **Workflow Execution Time**: Ensure all workflows meet timeout targets
2. **Failure Rate**: Monitor <5% failure rate over 30 days (SC-008)
3. **Security Findings**: Track vulnerability count trending toward zero
4. **Code Quality**: Monitor flake8 violations don't increase
5. **Automated Fix PRs**: Track PR creation and merge rates
6. **Dependabot Updates**: Monitor action update PR frequency

## References

- [spec.md](./spec.md) - Feature specification with user stories
- [plan.md](./plan.md) - Implementation plan with technical context
- [research.md](./research.md) - Best practices and decisions
- [data-model.md](./data-model.md) - Entities and relationships
- [quickstart.md](./quickstart.md) - Testing and validation guide
- [contracts/](./contracts/) - Workflow configuration contracts

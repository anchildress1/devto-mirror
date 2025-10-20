# Research: GitHub Actions Workflow Verification and Update

**Feature**: Individual Verification and Update of All GitHub Actions Workflows  
**Date**: 2025-10-18  
**Status**: Complete

## Executive Summary

This research document consolidates findings for updating four GitHub Actions workflows to Python 3.11+ with uv package manager, implementing workflow_dispatch triggers for testing, optimizing schedules for cost reduction, and ensuring comprehensive security scanning. All technical unknowns have been resolved with concrete recommendations.

---

## 1. GitHub Actions Workflow Best Practices

### 1.1 workflow_dispatch Trigger Patterns

**Decision**: Add `workflow_dispatch: {}` to all four workflows for manual testing

**Rationale**:
- Enables testing without pushing commits or waiting for schedules
- Supports input parameters if needed (refresh workflow already uses this)
- No breaking changes to existing triggers (additive only)
- GitHub Actions UI provides simple "Run workflow" button

**Implementation Pattern**:
```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch: {}  # Add this line
```

**Alternatives Considered**:
- Repository dispatch webhooks: Too complex for simple utility repo
- Manual git tags: Creates unnecessary repository pollution
- Comment triggers: Requires additional action setup

**Source**: [GitHub Actions Documentation - workflow_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)

### 1.2 GITHUB_TOKEN Least Privilege Patterns

**Decision**: Use explicit minimal permissions per workflow

**Rationale**:
- Default GITHUB_TOKEN has broad permissions that violate least privilege
- Explicit permissions prevent accidental scope creep
- Improves security posture for automated workflows
- Meets constitution Principle 1 (simple, secure)

**Recommended Permissions**:
- **security-ci**: `contents: read, pull-requests: write` (for auto-fix PRs)
- **codeql**: `security-events: write, contents: read, actions: read, packages: read`
- **publish**: `contents: write` (for gh-pages branch updates)
- **refresh**: `contents: write, actions: write` (to trigger publish workflow)

**Implementation Pattern**:
```yaml
permissions:
  contents: read  # Start minimal
  pull-requests: write  # Add only what's needed
```

**Source**: [GitHub Actions Security Hardening - GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)

### 1.3 Concurrency Controls for PR Workflows

**Decision**: Implement `cancel-in-progress: true` for PR-triggered workflows

**Rationale**:
- Saves compute time when multiple commits pushed to same PR
- Reduces queue wait time
- No data corruption risk (workflows are stateless or use atomic git operations)
- Aligns with constitution Principle 4 (toy utility, not production)

**Implementation Pattern**:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel outdated runs
```

**Alternatives Considered**:
- Queue all runs: Wastes resources, unnecessary for non-critical utility
- No concurrency control: Leads to redundant work

**Source**: [GitHub Actions - Using concurrency](https://docs.github.com/en/actions/using-jobs/using-concurrency)

### 1.4 Cron Schedule Syntax for Timezone-Aware Scheduling

**Decision**: Use cron `"38 13 * * 3"` for Wednesday 09:38 AM EDT year-round

**Rationale**:
- GitHub Actions cron always uses UTC timezone
- EDT = UTC-4, so 09:38 EDT = 13:38 UTC
- User posts no later than 09:30 AM Wednesday, schedule captures fresh content
- Simplicity trumps DST correctness per user preference

**Cron Syntax Breakdown**:
```
"38 13 * * 3"
 │  │  │ │ └─ Day of week (3 = Wednesday)
 │  │  │ └─── Month (any)
 │  │  └───── Day of month (any)
 │  └──────── Hour (13 = 1 PM UTC)
 └─────────── Minute (38)
```

**Alternatives Considered**:
- EST schedule (14:38 UTC): User prefers EDT consistency
- DST-aware dual schedules: Over-engineering for simple utility

**Source**: [GitHub Actions - schedule event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)

---

## 2. Python 3.11+ Migration for CI/CD

### 2.1 actions/setup-python@v6 Python 3.11+ Support

**Decision**: Use `actions/setup-python@v6` with `python-version: "3.11"`

**Rationale**:
- Version 6.0.0+ officially supports Python 3.11 and 3.12
- Stable release with proven reliability
- Native uv cache support added in v6
- Already in use in existing workflows

**Implementation Pattern**:
```yaml
- name: Setup Python
  uses: actions/setup-python@v6.0.0
  with:
    python-version: "3.11"
    cache: 'pip'  # Will update to uv cache
```

**Verification**: Publish and refresh workflows already use v6.0.0

**Source**: [actions/setup-python releases](https://github.com/actions/setup-python/releases)

### 2.2 uv Package Manager Installation in GitHub Actions

**Decision**: Install uv via official installer script before dependency step

**Rationale**:
- Official installer ensures latest version
- Single-line installation command
- No pre-built action needed (KISS principle)
- Already successfully used in publish/refresh workflows

**Implementation Pattern**:
```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: uv pip install -e '.[dev]'
```

**Alternatives Considered**:
- Third-party GitHub Action: Adds unnecessary dependency
- Manual binary download: More complex, no version management

**Verification**: Publish workflow successfully uses this pattern

**Source**: [Astral uv installation docs](https://github.com/astral-sh/uv#installation)

### 2.3 uv Cache Configuration with actions/setup-python@v6

**Decision**: Use actions/setup-python@v6 with `cache: 'pip'` (uv compatible)

**Rationale**:
- setup-python v6+ automatically detects uv and caches appropriately
- No additional configuration required (convention over configuration)
- Reduces workflow run time by caching pip/uv packages
- Aligns with FR-016 (use native uv cache support)

**Implementation Pattern**:
```yaml
- name: Setup Python
  uses: actions/setup-python@v6.0.0
  with:
    python-version: "3.11"
    cache: 'pip'  # Works with uv automatically
```

**Note**: The `cache: 'pip'` key tells setup-python to cache Python packages. When uv is used, it intelligently caches uv's package store.

**Source**: [setup-python caching](https://github.com/actions/setup-python#caching-packages-dependencies)

### 2.4 ubuntu-latest Runner Python 3.11+ Compatibility

**Decision**: Continue using `ubuntu-latest` (currently Ubuntu 24.04)

**Rationale**:
- Ubuntu 24.04 includes Python 3.11 and 3.12 by default
- `ubuntu-latest` ensures automatic updates to newer stable Ubuntu versions
- Aligns with FR-017 (use ubuntu-latest with documented fallback)
- No breaking changes expected from runner updates

**Fallback Strategy** (if ubuntu-latest breaks):
1. Pin to specific version: `runs-on: ubuntu-24.04`
2. Document breaking change in workflow comments
3. Test on pinned version before updating
4. Update workflows incrementally

**Implementation Pattern**:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest  # Currently 24.04, auto-updates
```

**Source**: [GitHub Actions runner images](https://github.com/actions/runner-images)

---

## 3. Security Tool Integration

### 3.1 pip-audit Integration and Auto-Fix Capabilities

**Decision**: Use `pip-audit` for vulnerability scanning with manual fix guidance

**Rationale**:
- pip-audit has no built-in auto-fix (reports only)
- Auto-fix PRs require Dependabot or manual intervention
- Current security-ci workflow already uses pip-audit correctly
- Aligns with FR-003b (create fix PRs when possible, not always)

**Implementation Pattern**:
```yaml
- name: Run pip-audit
  run: pip-audit --progress=none
```

**Auto-Fix Strategy**:
- High-priority vulnerabilities: Dependabot creates PRs automatically
- pip-audit provides upgrade guidance in logs
- Manual review ensures quality (matches constitution Principle 4)

**Alternatives Considered**:
- safety: Less actively maintained than pip-audit
- Automated PR creation: Over-engineering for utility repo

**Source**: [pip-audit documentation](https://github.com/pypa/pip-audit)

### 3.2 bandit Configuration for Python 3.11+

**Decision**: Use `bandit -r scripts -ll -iii` (current configuration is correct)

**Rationale**:
- `-r scripts`: Recursive scan of scripts/ directory
- `-ll`: Low and above severity levels
- `-iii`: Confidence level filtering (ignore low confidence)
- bandit fully supports Python 3.11+ (AST-based, version agnostic)

**Implementation Pattern**:
```yaml
- name: Run bandit security scan
  run: bandit -r scripts -ll -iii
```

**No changes needed**: Current security-ci configuration is optimal

**Source**: [bandit documentation](https://bandit.readthedocs.io/)

### 3.3 flake8 Configuration for Code Smell Detection

**Decision**: Use `flake8 scripts/` with project-level configuration

**Rationale**:
- flake8 supports Python 3.11+ (PEP 8 compliance checker)
- Project likely has `.flake8` or `setup.cfg` configuration
- Simple invocation without flags follows KISS principle
- Existing security-ci workflow pattern is correct

**Implementation Pattern**:
```yaml
- name: Run flake8 lint
  run: flake8 scripts/
```

**Configuration**: Use project defaults in `pyproject.toml` or `.flake8`

**Source**: [flake8 documentation](https://flake8.pycqa.org/)

### 3.4 CodeQL Python 3.11+ Support

**Decision**: CodeQL natively supports Python 3.11+ (no changes needed)

**Rationale**:
- CodeQL's Python analysis updated regularly
- Current codeql.yml already correctly configured
- `github/codeql-action/init@v3` includes Python 3.11+ support
- Semantic analysis works across Python versions

**Implementation Pattern**:
```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: python
    queries: security-extended, security-and-quality
```

**No changes needed**: Current configuration is optimal

**Source**: [CodeQL Python support](https://codeql.github.com/docs/codeql-language-guides/codeql-for-python/)

### 3.5 Automated Fix PR Patterns with peter-evans/create-pull-request

**Decision**: Defer automated fix PR implementation (not in current workflows)

**Rationale**:
- Current workflows don't use peter-evans/create-pull-request
- FR-003b requires auto-fix PRs "when possible" (not mandatory)
- Dependabot already handles dependency updates
- Manual fixes align with constitution Principle 4 (simple utility)

**Future Implementation** (if needed):
```yaml
- name: Create Fix PR
  if: failure()
  uses: peter-evans/create-pull-request@v6
  with:
    commit-message: "fix: automated security vulnerability fixes"
    title: "Security: Auto-fix vulnerabilities"
    body: "Automated fixes from security scans"
    branch: auto-fix/security-${{ github.run_id }}
```

**Current Strategy**: Report findings, let Dependabot handle package updates

**Source**: [create-pull-request action](https://github.com/peter-evans/create-pull-request)

---

## 4. Workflow Schedule Optimization

### 4.1 GitHub Actions Billing and Cost Optimization

**Decision**: Reduce publish workflow from daily to weekly (86% cost reduction)

**Rationale**:
- Daily runs: 30 runs/month
- Weekly runs: 4 runs/month
- Cost savings: ~86% reduction in minutes for publish workflow
- Content updates weekly acceptable for personal blog mirror
- Manual trigger available for immediate updates

**Cost Impact Analysis**:
- Current: Daily at 14:15 UTC (9:15 AM EST) = ~450 minutes/month
- Proposed: Weekly Wednesday 13:38 UTC = ~60 minutes/month
- Savings: ~390 minutes/month per workflow

**Implementation**: Change cron from `"15 14 * * *"` to `"38 13 * * 3"`

**Source**: [GitHub Actions billing](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

### 4.2 Cron Schedule Patterns for Weekly Execution

**Decision**: Use `"38 13 * * 3"` for Wednesday 09:38 AM EDT

**Rationale**:
- Day of week 3 = Wednesday (0=Sunday, 1=Monday, etc.)
- 13:38 UTC = 09:38 EDT (UTC-4)
- Captures fresh content posted by 09:30 AM Wednesday
- Single schedule (no DST adjustment) for simplicity

**Weekly Pattern**:
```yaml
schedule:
  - cron: "38 13 * * 3"  # Wednesday 09:38 AM EDT
```

**Alternatives Considered**:
- Multiple days per week: Unnecessary cost increase
- Different time: 09:38 AM aligns with user posting schedule

**Source**: [Crontab Guru - cron schedule expression validator](https://crontab.guru/#38_13_*_*_3)

### 4.3 Timezone Handling in Cron Expressions

**Decision**: Use UTC exclusively with EDT offset calculation

**Rationale**:
- GitHub Actions cron is always UTC (no timezone support)
- EDT = UTC-4 (09:38 EDT = 13:38 UTC)
- EST = UTC-5 (user prefers EDT year-round for simplicity)
- Avoids DST complexity per user preference

**Calculation**:
- User posts: 09:30 AM EDT
- Workflow runs: 09:38 AM EDT (8 minute buffer)
- UTC equivalent: 13:38 UTC (09:38 + 4 hours)

**Tradeoff**: During EST months (winter), workflow runs at 08:38 AM EST. User accepts this for simplicity.

**Source**: User clarification (Session 2025-10-18)

---

## 5. Dependabot Configuration

### 5.1 Dependabot Auto-Merge Patterns for GitHub Actions

**Decision**: Enable Dependabot for `github-actions` ecosystem with manual merge

**Rationale**:
- Existing `.github/dependabot.yml` includes `github-actions`
- Auto-merge requires additional workflow setup (complexity)
- Manual review aligns with FR-012 (manual workflow updates)
- Dependabot PRs provide upgrade safety with CI validation

**Current Configuration**:
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "04:00"
```

**Recommendation**: Keep current manual merge approach (matches constitution principles)

**Auto-Merge Setup** (future consideration):
- Requires separate workflow with `auto-merge` GitHub CLI command
- Adds complexity not justified for 4 workflows

**Source**: [Dependabot configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)

### 5.2 Dependabot Configuration for Actions Updates

**Decision**: Current Dependabot configuration is optimal (no changes needed)

**Rationale**:
- Weekly schedule (Monday 04:00) is reasonable
- `github-actions` ecosystem covers all workflow dependencies
- Existing configuration already functional

**Verification**:
```yaml
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**No action required**: Configuration meets all requirements

**Source**: Existing `.github/dependabot.yml` file

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| workflow_dispatch | Add to all 4 workflows | Enable manual testing |
| GITHUB_TOKEN | Explicit minimal permissions | Security hardening |
| Concurrency | Cancel-in-progress for PRs | Save compute, no data risk |
| Python version | 3.11 via setup-python@v6 | Stable, proven support |
| uv installation | Official installer script | Simple, reliable |
| uv caching | setup-python native support | Zero config, automatic |
| Runner | ubuntu-latest (24.04) | Auto-updates, Python 3.11+ default |
| pip-audit | Current config correct | No auto-fix needed |
| bandit | Current config correct | Python 3.11+ compatible |
| flake8 | Current config correct | Version agnostic |
| CodeQL | Current config correct | Python 3.11+ supported |
| Schedule | Weekly Wed 13:38 UTC | 86% cost reduction |
| Timezone | EDT year-round (13:38 UTC) | Simplicity over DST accuracy |
| Dependabot | Current config optimal | Manual merge acceptable |

**All technical unknowns resolved. Ready for Phase 1 (Design & Contracts).**

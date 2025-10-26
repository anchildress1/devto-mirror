# Quickstart: Testing and Validating Workflow Updates

**Feature**: Individual Verification and Update of All GitHub Actions Workflows
**Date**: 2025-10-17
**Audience**: Maintainers implementing workflow changes

## Overview

This guide provides step-by-step instructions for testing and validating workflow updates for the four GitHub Actions workflows: security-ci.yml, codeql.yml, publish.yaml, and refresh.yaml.

## Prerequisites

- GitHub repository access with Actions enabled
- Git command-line tools installed
- Python 3.11+ installed locally (for local testing)
- uv package manager installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Quick Validation Checklist

Before pushing workflow changes:

- [ ] All workflow files use Python 3.11+
- [ ] All workflows use uv package manager (not pip)
- [ ] Security workflows include automated fix PR logic
- [ ] Timeout limits match spec (security-ci: 10min, codeql: 15min, publish: 15min, refresh: 20min)
- [ ] No backwards compatibility considerations needed (per constitution)

## Testing Strategy

### 1. Local Pre-Flight Checks

Before pushing workflow changes, validate locally:

```bash
# Validate YAML syntax
for file in .github/workflows/*.{yml,yaml}; do
  python -c "import yaml; yaml.safe_load(open('$file'))"
done

# Check Python version specifications
grep -r "python-version" .github/workflows/
# Should show '3.11' or higher

# Check for uv usage
grep -r "uv pip install" .github/workflows/
# Should find instances in publish and updated security workflows

# Verify no pip usage remains
grep -r "pip install -r" .github/workflows/
# Should return empty (no old pip patterns)
```

### 2. Testing Security-CI Workflow

**Test Scenario 1: Clean Build (No Vulnerabilities)**

```bash
# Create test branch
git checkout -b test/security-ci-clean

# Trigger workflow via push
git push origin test/security-ci-clean

# Monitor workflow
gh run watch

# Expected: All checks pass, no fix PR created
```

**Test Scenario 2: Vulnerable Dependency (Auto-Fix)**

```bash
# Create test branch with intentional vulnerability
git checkout -b test/security-ci-vuln

# Add vulnerable dependency to pyproject.toml (for testing only)
# Then push
git push origin test/security-ci-vuln

# Expected:
# - Workflow fails
# - Automated fix PR created with branch name auto-fix/security-{run_id}
# - PR blocks merge until reviewed
```

**Test Scenario 3: Code Quality Issues (flake8)**

```bash
# Create test branch with style violations
git checkout -b test/security-ci-lint

# Add intentional flake8 violations to a Python file
# Then push
git push origin test/security-ci-lint

# Expected:
# - Workflow fails
# - flake8 violations reported in logs
# - Merge blocked until fixed
```

### 3. Testing CodeQL Workflow

**Test Scenario: Full Analysis**

```bash
# Create test branch
git checkout -b test/codeql-analysis

# Trigger workflow via push or PR
git push origin test/codeql-analysis

# Monitor workflow (this may take 10-15 minutes)
gh run watch

# Verify results in GitHub Security tab
open "https://github.com/$GITHUB_REPOSITORY/security/code-scanning"

# Expected:
# - Analysis completes within 15 minutes
# - Results uploaded to Security tab
# - Vulnerabilities (if any) categorized by severity
```

### 4. Testing Publish Workflow

**Test Scenario: Site Generation and Deployment**

```bash
# Ensure DEVTO_USERNAME and PAGES_REPO are set
export DEVTO_USERNAME="your-username"
export PAGES_REPO="owner/repo"

# Manually trigger workflow (or push to main)
gh workflow run publish.yaml

# Monitor workflow
gh run watch

# Verify gh-pages branch updated
git fetch origin gh-pages
git log origin/gh-pages --oneline -5

# Check deployed site
open "https://$GITHUB_REPOSITORY.github.io"

# Expected:
# - Dependencies installed via uv
# - Site generated successfully
# - gh-pages branch updated
# - Site accessible within 15 minutes
```

### 5. Testing Refresh Workflow

**Test Scenario: Full Refresh with Backup**

```bash
# Manually trigger refresh workflow
gh workflow run refresh.yaml

# Monitor workflow
gh run watch

# Verify backup branch created
git fetch --all
git branch -r | grep backup-

# Expected:
# - Backup branch created with timestamp name
# - last_run.txt reset
# - Publish workflow triggered
# - All content regenerated within 20 minutes
```

## Validation Checklist

After each workflow test:

### Security-CI Workflow
- [ ] Workflow triggers on push and pull_request
- [ ] Python 3.11 installed correctly
- [ ] uv package manager used for dependencies
- [ ] pip-audit executes and reports
- [ ] bandit executes and reports
- [ ] flake8 executes and reports
- [ ] High-severity findings block merge
- [ ] Automated fix PR created when applicable
- [ ] Completes within 10 minutes

### CodeQL Workflow
- [ ] Workflow triggers on push, pull_request, and schedule
- [ ] CodeQL analysis completes for all Python code
- [ ] Results uploaded to GitHub Security tab
- [ ] Vulnerabilities categorized by severity
- [ ] Code quality issues reported
- [ ] Completes within 15 minutes

### Publish Workflow
- [ ] Workflow triggers on schedule, push, and manual dispatch
- [ ] Python 3.11 and uv configured correctly
- [ ] Dependencies install successfully
- [ ] Site generation completes without errors
- [ ] gh-pages branch updated
- [ ] Site accessible and displays correctly
- [ ] Completes within 15 minutes

### Refresh Workflow
- [ ] Workflow triggers on manual dispatch only
- [ ] Backup branch created with timestamp
- [ ] last_run.txt reset successfully
- [ ] Publish workflow triggered
- [ ] All content regenerated
- [ ] Completes within 20 minutes

## Troubleshooting

### Common Issues

**Issue**: Workflow fails with "uv: command not found"
```bash
Solution: Ensure uv installer script is included:
run: curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Issue**: Python version mismatch
```bash
Solution: Verify python-version is set to '3.11' in setup-python step
```

**Issue**: Automated fix PR not created
```bash
Solution: Check that:
1. peter-evans/create-pull-request action is properly configured
2. GITHUB_TOKEN has write permissions
3. Workflow has if: failure() condition
```

**Issue**: Workflow timeout
```bash
Solution: Verify timeout-minutes is set per spec requirements
jobs:
  job-name:
    timeout-minutes: 10  # Adjust per workflow
```

**Issue**: Concurrent runs causing conflicts
```bash
Solution: This is expected and acceptable per spec. No action needed.
Conflicts in gh-pages will be resolved by git's automatic merge handling.
```

## Performance Monitoring

Track workflow execution times:

```bash
# List recent workflow runs with durations
gh run list --workflow=security-ci.yml --limit=10 --json conclusion,startedAt,completedAt

# Check if any runs exceed timeout limits
# Security-CI should be <10min
# CodeQL should be <15min
# Publish should be <15min
# Refresh should be <20min
```

## Success Criteria Verification

After all workflows are updated and tested:

- [ ] SC-001: All four workflows execute on Python 3.11+ without errors ✅
- [ ] SC-002: Security-ci identifies vulnerabilities within 10 minutes ✅
- [ ] SC-003: CodeQL uploads findings to GitHub Security ✅
- [ ] SC-004: Zero high-severity vulnerabilities remain unaddressed ✅
- [ ] SC-005: Code quality metrics tracked, no increase in technical debt ✅
- [ ] SC-006: Publish deploys site within 15 minutes ✅
- [ ] SC-007: Refresh creates backups and regenerates within 20 minutes ✅
- [ ] SC-008: Workflow failure rate <5% over 30 days ⏳ (monitor ongoing)
- [ ] SC-009: Security findings categorized automatically ✅
- [ ] SC-010: Error reports delivered within 5 minutes ✅

## Next Steps

After successful validation:

1. Merge workflow updates to main branch
2. Monitor workflow performance over 30 days
3. Review automated fix PRs promptly
4. Track code quality metrics for trends
5. Update copilot-instructions.md with workflow guidance (if needed)

## Support

For issues or questions:
- Review workflow logs in GitHub Actions UI
- Check GitHub Security tab for CodeQL findings
- Consult contracts/ directory for expected configurations
- Refer to research.md for decision rationale

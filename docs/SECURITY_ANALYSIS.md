# Security Analysis Setup

This repository now includes comprehensive security analysis through GitHub's built-in security features.

## Enabled Security Features

### 1. CodeQL Analysis

- **File**: `.github/workflows/codeql.yml`
- **Frequency**: Weekly (Mondays at 2:15 AM UTC) + on pushes/PRs to main
- **Coverage**: Python code security scanning with extended security and quality queries
- **Manual Trigger**: Available via GitHub Actions

### 2. Dependabot

- **File**: `.github/dependabot.yml`
- **Frequency**: Weekly (Mondays at 4:00 AM UTC)
- **Coverage**:
  - Python package dependencies (`pip`)
  - GitHub Actions versions
- **Auto-assignment**: PRs are auto-assigned to repository owner

### 3. Dependencies

- **File**: `requirements.txt`
- **Purpose**: Explicit dependency tracking for security scanning
- **Contents**: Core dependencies used in GitHub Actions workflows

## Additional Recommended Security Settings

To fully enable GitHub's security features, consider enabling these in repository settings:

1. **Security updates** and automated scanning (Settings → Security & analysis)
2. **Security alerts** (Settings → Security & analysis)
3. **Secret scanning** (Settings → Security & analysis)
4. **Private vulnerability reporting** (Settings → Security & analysis)

## Local & CI security checks

This repository now includes an extra CI workflow (`.github/workflows/security-ci.yml`) that runs a few lightweight, fast checks on pushes and PRs:

- Bandit — looks for common Python security anti-patterns in `scripts/`
- pip-audit — checks installed packages for known vulnerabilities
- flake8 — a linter to catch a range of potential issues, including style problems that can hide bugs

To run these locally during development:

1. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
2. Install the dev requirements: `pip install -r dev-requirements.txt`
3. Run `pip-audit`, `bandit -r scripts`, and `flake8` as needed

These checks are intentionally lightweight — they won't find everything, but they reduce noise in automated scans and catch common mistakes that lead to security flags.

## How It Works

- **CodeQL** scans all Python code for security vulnerabilities and code quality issues
- The repository uses CI and manual review to monitor dependencies for known vulnerabilities and to create PRs or advisories for updates when needed
- **Security alerts** notify maintainers of potential issues
- **Regular scanning** ensures ongoing security posture

## Viewing Results

- **CodeQL results**: Go to Security → Code scanning alerts
- **Dependency alerts & updates**: Check Security → Dependabot alerts or your configured dependency monitoring tools in repository settings

---

Generated as part of automated security setup.

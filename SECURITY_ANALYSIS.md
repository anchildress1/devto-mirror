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

1. **Dependabot security updates** (Settings → Security & analysis)
2. **Dependabot alerts** (Settings → Security & analysis)
3. **Secret scanning** (Settings → Security & analysis)
4. **Private vulnerability reporting** (Settings → Security & analysis)

## How It Works

- **CodeQL** scans all Python code for security vulnerabilities and code quality issues
- **Dependabot** monitors dependencies for known vulnerabilities and creates PRs for updates
- **Security alerts** notify maintainers of potential issues
- **Regular scanning** ensures ongoing security posture

## Viewing Results

- **CodeQL results**: Go to Security → Code scanning alerts
- **Dependabot alerts**: Go to Security → Dependabot alerts
- **Dependency updates**: Dependabot will create PRs automatically

---

Generated as part of automated security setup.
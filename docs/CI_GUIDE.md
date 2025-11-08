# CI/CD Technical Guide

This guide provides an in-depth technical explanation of the GitHub Actions workflows that power the Dev.to Mirror project. It covers the architecture, implementation details, and design decisions behind the CI/CD pipeline.

## Workflow Architecture Overview

The project uses a multi-workflow architecture designed for separation of concerns, security, and reliability:

- **`publish.yaml`**: Core site generation and deployment
- **`security-ci.yml`**: Quality assurance and security scanning
- **`codeql.yml`**: Advanced security analysis
- **`refresh.yaml`**: Emergency full regeneration

This separation allows for independent execution, targeted permissions, and easier maintenance.

## Core Workflows Deep Dive

### `publish.yaml` - Site Generation Pipeline

**Technical Implementation**:

```yaml
# Scheduled: Weekly Wednesday 9:38 AM EDT (cron: '38 13 * * 3')
# Manual: workflow_dispatch with optional inputs
```

**Execution Flow**:

1. **Environment Setup**: Python 3.12 with uv caching for faster builds
2. **Dependency Installation**: Uses `uv sync --locked --group dev` for reproducible builds
3. **API Integration**: Fetches posts from Dev.to API using incremental updates via `last_run.txt`
4. **Content Processing**:
   - Generates HTML with Jinja2 templates
   - Creates canonical links back to Dev.to
   - Processes AI-enhanced metadata and cross-references
   - Sanitizes HTML content with bleach
5. **Static Asset Generation**:
   - `sitemap.xml` for search engines
   - `robots.txt` with crawler-specific rules
   - `index.html` with post listings
6. **Deployment**: Uses `actions/deploy-pages@v4` to deploy to `gh-pages` branch

**Key Technical Features**:

- **Incremental Updates**: Only processes new posts since last run using timestamp tracking
- **Rate Limiting**: Built-in delays to respect Dev.to API limits
- **Error Handling**: Graceful failure with detailed logging
- **Caching**: Pip dependency caching reduces build times

**Environment Variables**:

- `DEVTO_USERNAME`: Repository variable (required)
- `PAGES_REPO`: Auto-derived from `github.repository`
- `GITHUB_TOKEN`: Auto-provided for Pages deployment

### `security-ci.yml` - Quality Assurance Pipeline

**Purpose**: Comprehensive security and quality checks on every code change.

**CRITICAL: uv and Makefile Integration**

This workflow uses `uv` for dependency management and runs `make check` for validation. A common mistake is calling `uv run make check`, which causes failures.

❌ **WRONG** (causes "No such file or directory" errors):
```yaml
- name: Run validation
  run: uv run make check
```

✅ **CORRECT**:
```yaml
- name: Install dependencies
  run: uv sync --locked --group dev

- name: Run validation
  run: make check
```

**Why this matters**: The Makefile targets already use `uv run` internally for all tools (black, flake8, bandit, etc.). Calling `uv run make` creates a nested `uv run` context where the inner commands fail to find executables.

**Rule**: After `uv sync`, call Makefile targets directly. Never wrap them in `uv run`.

**Multi-Tool Security Stack**:

1. **bandit** - Python Security Linter
   - Scans for common security issues (SQL injection, hardcoded passwords, etc.)
   - Configured with medium-low severity threshold
   - Supports `# nosec` comments for false positives

2. **flake8** - Style and Logic Linting
   - Enforces PEP 8 style guidelines
   - Custom configuration: 120 char line length, specific ignore rules
   - Catches logical errors and code smells

3. **pip-audit** - Dependency Vulnerability Scanner
   - Scans installed packages against known vulnerability databases
   - Configured to ignore specific vulnerabilities when justified
   - Prevents supply chain attacks

4. **detect-secrets** - Secret Detection
   - Prevents accidental commit of API keys, passwords, tokens
   - Uses baseline file (`.secrets.baseline`) for approved exceptions
   - Scans all file types with intelligent heuristics

5. **Site Generation Validation** - Custom Build Testing
   - Dry-run of site generation with mock data
   - Catches template errors, import issues, syntax problems
   - Runs in isolated environment to prevent side effects

**Execution Strategy**:

- Runs on every push and pull request
- Fails fast on security issues
- Provides detailed error reporting
- Uses least-privilege permissions

### `codeql.yml` - Advanced Security Analysis

**GitHub CodeQL Integration**:

- Static analysis security testing (SAST)
- Language: Python with full semantic analysis
- Detects complex security vulnerabilities that simple linters miss

**Analysis Scope**:

- Control flow analysis
- Data flow tracking
- Taint analysis for injection vulnerabilities
- Memory safety issues
- Authentication and authorization flaws

**Scheduling**:

- Triggered on pushes and PRs for immediate feedback
- Weekly scheduled deep scans
- Results integrated with GitHub Security tab

**Technical Implementation**:

```yaml
strategy:
  matrix:
    language: ['python']
# Uses github/codeql-action@v3 for latest analysis capabilities
```

### `refresh.yaml` - Emergency Recovery Workflow

**Use Case**: When incremental updates fail or complete regeneration is needed.

**Technical Process**:

1. **Backup Creation**: Creates timestamped backup branch
2. **State Reset**: Removes `last_run.txt` to force full regeneration
3. **Workflow Trigger**: Programmatically triggers `publish.yaml`
4. **Safety Measures**: Manual-only trigger to prevent accidental execution

**Implementation Details**:

```yaml
# Manual dispatch only - no automatic triggers
# Optional input: force_full_regen (boolean)
# Uses GitHub API to trigger dependent workflow
```

## Security Architecture

### Permissions Model

Each workflow uses **least-privilege permissions**:

```yaml
permissions:
  contents: read          # Read repository code
  pages: write           # Deploy to GitHub Pages (publish only)
  id-token: write        # OIDC authentication (publish only)
  security-events: write # CodeQL results (codeql only)
```

### Secret Management

**No secrets required**: The project is designed to work with only public information:
- Dev.to username (public)
- Repository name (public)
- GitHub token (auto-provided)

This eliminates secret management complexity and reduces attack surface.

### Dependency Security

**Multi-layered approach**:

- `pip-audit` for known vulnerabilities
- Dependabot for automated updates
- CodeQL for supply chain analysis
- Regular security baseline updates

## Performance Optimizations

### Build Speed Optimizations

1. **Dependency Caching**:

   ```yaml
   - uses: actions/cache@v4
     with:
       path: ~/.cache/uv
       key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
   ```

2. **Incremental Processing**: Only processes new posts since last run

3. **Parallel Execution**: Security checks run independently of site generation

4. **Efficient API Usage**: Respects rate limits while minimizing requests

### Resource Management

- **Timeout Protection**: All workflows have reasonable timeout limits
- **Memory Efficiency**: Streaming processing for large post collections
- **Network Optimization**: Minimal external dependencies

## Error Handling and Monitoring

### Failure Modes

1. **API Failures**: Graceful degradation with retry logic
2. **Build Failures**: Detailed error reporting with context
3. **Deployment Failures**: Rollback capabilities via git history
4. **Security Failures**: Fail-fast with clear remediation guidance

### Monitoring and Observability

- **Workflow Status**: Visible in Actions tab with detailed logs
- **Security Alerts**: Integrated with GitHub Security tab
- **Performance Metrics**: Build time tracking and optimization
- **Error Tracking**: Structured logging for debugging

## Design Decisions and Trade-offs

### Weekly Scheduling Choice

**Decision**: Wednesday 9:38 AM EDT scheduling
**Rationale**:

- Mid-week timing avoids weekend/Monday issues
- EDT timing serves primary user base
- Unusual minute (38) reduces GitHub Actions load balancing conflicts

### Incremental vs Full Regeneration

**Default**: Incremental updates for efficiency
**Override**: Full regeneration available via refresh workflow
**Trade-off**: Speed vs completeness - incremental is faster but may miss template changes

### Security Tool Selection

**Comprehensive coverage**: Multiple tools catch different issue types
**Performance impact**: Parallel execution minimizes build time impact
**False positive management**: Baseline files and ignore patterns for maintainability

### Deployment Strategy

**GitHub Pages**: Simple, reliable, integrated with repository
**Alternative considered**: External hosting (rejected for complexity)
**Trade-off**: Simplicity vs advanced hosting features

## Common CI Issues and Solutions

### Issue: "Failed to spawn: No such file or directory" in CI

**Symptom**:
```
error: Failed to spawn: `black`
  Caused by: No such file or directory (os error 2)
make[1]: *** [Makefile:30: format] Error 2
```

**Root Cause**: Using `uv run make <target>` instead of just `make <target>`.

**Solution**: Remove `uv run` prefix when calling Makefile targets:
```yaml
# Before (broken)
- run: uv run make check

# After (fixed)
- run: make check
```

**Explanation**: The Makefile already wraps tool invocations with `uv run`. The workflow only needs to:
1. Run `uv sync --locked --group dev` to install dependencies
2. Call Makefile targets directly (e.g., `make check`, `make test`)

Double-wrapping with `uv run make` breaks the execution context.

### Issue: Dependencies not found in CI

**Symptom**: Tools like `black`, `flake8`, or `bandit` not found.

**Solution**: Ensure `uv sync --locked --group dev` runs before any Makefile commands:
```yaml
- name: Install dependencies
  run: uv sync --locked --group dev

- name: Run checks
  run: make validate
```

### Issue: Workflow output too verbose

**Solution**: Let tools write to stdout normally; avoid capturing in GITHUB_STEP_SUMMARY:
```yaml
# Keep it simple
- name: Run validation
  run: |
    echo "## 🔍 Validation Results" >> $GITHUB_STEP_SUMMARY
    make check
    echo "✅ All checks passed" >> $GITHUB_STEP_SUMMARY
```

## Workflow Command Patterns Reference

### Correct Patterns for All Workflows

**Installing dependencies:**
```yaml
- name: Install dependencies
  run: uv sync --locked --group dev
```

**Running Makefile targets:**
```yaml
# ✅ CORRECT - Call make directly
- name: Run validation
  run: make check

# ❌ WRONG - Do NOT wrap in uv run
- name: Run validation
  run: uv run make check  # This will fail!
```

**Running Python scripts directly:**
```yaml
# ✅ CORRECT - Use uv run for scripts
- name: Generate site
  run: uv run python scripts/generate_site.py

# ✅ CORRECT - Or use make targets that wrap them
- name: Generate site
  run: make generate-site
```

**Summary:**
- After `uv sync --locked`, the environment is ready
- Makefile targets = call directly (e.g., `make test`, `make check`)
- Python scripts = use `uv run python script.py` OR use make targets
- Never nest: `uv run make` is always wrong

For setup instructions and development workflow, see [`DEV_GUIDE.md`](DEV_GUIDE.md).

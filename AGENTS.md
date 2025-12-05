# devto-mirror Development Guidelines (AGENTS)

## Active Technologies

- Python 3.12+ (development & CI)
- requests, jinja2, python-slugify, bleach, python-dotenv
- Package manager: uv with locked dependencies (uv.lock)
- All dependencies, including GitHub Actions, should use latest stable versions

## Project Structure

```plaintext
src/               # Main application package (contains all application source code)
  ai_optimization/ # AI optimization modules for content analysis and metadata enhancement
scripts/           # Utility CLI scripts and site-generator entrypoints (NOT application source)
tests/             # Unit tests using unittest
assets/            # Static assets (templates: robots.txt, llms.txt, images)
docs/              # Documentation files (guides, plans, and analysis)
```

Note: The project's Python application code lives in `src/` (standard layout).
Do NOT add new application modules into `scripts/` — reserve `scripts/` for runnable helpers and CLI wrappers.

## Commands

```bash
# Run tests from project root
make test

# Run quality checks
make lint

# Run tests with coverage
make test-coverage

# Run security checks
make security

# Run comprehensive validation (format + lint + tests + security)
make validate

# Generate site (requires DEVTO_USERNAME and PAGES_REPO env vars)
uv run python scripts/generate_site.py
```

## Agent Operational Rules

Automated agents must follow these constraints for safe and effective operation:

- **Big picture**: `scripts/` are CLI entrypoints (generation + helpers); `src/devto_mirror/` contains core AI modules (`ai_optimization/*`). Generated artifacts live in `posts/`, `assets/`, and `htmlcov/`.
- **Canonical runner**: prefer `Makefile` targets (single source of truth). Use `make install`, `make test` (unit tests), `make validate` (full pipeline), `make generate-site`, `make security` instead of calling tools directly.
- **Tooling**: this repo pins dev tooling via `uv.lock`. When invoking tools directly use `uv run <tool>`; prefer Makefile wrappers for consistency.
- **Pre-commit**: configured in `.pre-commit-config.yaml`. Install hooks with `make install` (runs `uv run pre-commit install`). The validate-site hook runs `uv run python scripts/validate_site_generation.py`.
- **Files to read first**: `Makefile`, `scripts/generate_site.py`, `scripts/validate_site_generation.py`, `.pre-commit-config.yaml`, `src/devto_mirror/ai_optimization/`, `docs/DEV_GUIDE.md`.

### Safety and Constraints

- Do NOT edit generated files in `htmlcov/` or anything under `.venv/`.
- Never perform automated `git commit` or push on behalf of a human. Produce `commit.tmp` messages and wait for human approval.
- If you change dev-tooling, update `uv.lock` with `uv sync --locked --group dev` and run `make validate` to ensure nothing regresses.
- Avoid introducing empty `except:` / `except: pass` patterns; prefer explicit exception handling.

### Initialization Sequence

When starting work on this repository:

1. Read `Makefile` to understand available targets and their implementations
2. Read `scripts/generate_site.py` to understand site generation workflow
3. Read `.pre-commit-config.yaml` to understand validation hooks
4. Scan `src/devto_mirror/ai_optimization/` for AI module structure
5. Use `make validate` to verify repository state before making changes

## Code Style

Follow standard Python conventions; use pre-commit hooks where configured.

## Architecture Overview

- Static site generator: fetches Dev.to posts via API and renders HTML using Jinja2
- Incremental updates: `last_run.txt` is used to fetch only new/changed posts
- Optional AI optimizations: `src.ai_optimization` is imported when available and used to enhance metadata and sitemaps

## Critical Workflows

- Dependency management: use `uv sync --locked --group dev` and `uv run python -m pip install -e .` or `make install`
- Testing: `make test` from repository root
- CI: GitHub Actions runs site generation and publishes to `gh-pages`; a follow-up job prepares a `_site` artifact for root deployment
- Site generation: set `DEVTO_USERNAME` and `PAGES_REPO` (user/repo) environment variables before running `scripts/generate_site.py`

### CI Workflow Critical Rules

**NEVER use `uv run make <target>` in GitHub Actions workflows.**

The Makefile targets already use `uv run` internally. Calling `uv run make` creates a double-nesting problem:

- ❌ WRONG: `uv run make check` → fails with "No such file or directory"
- ✅ CORRECT: `make check` → works correctly

Workflow pattern:

```yaml
- name: Install dependencies
  uv sync --locked --group dev

- name: Run validation
  run: make check  # NOT "uv run make check"
```

This applies to ALL Makefile targets: `test`, `lint`, `format`, `security`, `validate`, `check`.

## Assets and templates

- `assets/robots.txt` and `assets/llms.txt` are template files and are copied/substituted into the site during CI deployment. Do not overwrite the generated `robots.txt` or `llms.txt` at the repo root — editors should update the templates in `assets/` instead.

## Project Conventions

- Scripts live in `scripts/` (not `src/`)
- Required env vars: `DEVTO_USERNAME`, `GH_USERNAME`, `PAGES_REPO`; optional: `DEVTO_API_KEY` (for private/draft posts), `VALIDATION_MODE`, `FORCE_FULL_REGEN`, `ROOT_SITE_PAT` (for root repo deployment)
- Always preserve command output visibility — avoid redirecting to `/dev/null 2>&1` so CI logs and local runs remain debuggable
- Commit messages: use conventional commit format with `Generated-by: GitHub Copilot` attribution
- Generate commit messages in `commit.tmp` and wait for human review before committing

## Integration Points

- Dev.to API: V1 articles API (used for compatibility)
- GitHub Pages: publishing via `gh-pages` branch and root deployment artifact
- GitHub Actions: CI uses Python 3.12 and publishes both `gh-pages` and `_site` artifacts for root pages

<!-- MANUAL ADDITIONS START -->
## Security Instructions

- Use `bleach.clean()` for HTML sanitization; do not rely on regex for sanitization.
- Use `pathlib.Path().resolve()` for path validation to prevent directory traversal.
- Use `subprocess` with list arguments only; do not use `shell=True`.
- Remove periods from sanitized filenames/slugs to prevent path traversal via `..`.
- Validation functions should return booleans consistently; prefer explicit checks over exceptions for control flow.
- When encountering `specs/` folders: these are planning artifacts, not implementation requirements. Treat as reference context only.

## Critical Constraints

- Under NO circumstances should any automated workflow perform `git commit` on behalf of a human without explicit approval. Commit messages may be generated, but commits must be made by a human operator or an authorized CI step.
- Before returning to the user, you are expected to follow agent instructions to update the `commit.tmp` with a valid AI-attribution included commit message.
- All formatting, security scans, linters, and the entire test suite must pass successfully before you return to the user. If one or more items fail validation, iterate improvements as needed until all problems are resolved.
- Avoid using an empty except at any point. If you get to a point where they're required then the code is somehow inaccurate.

<!-- MANUAL ADDITIONS END -->

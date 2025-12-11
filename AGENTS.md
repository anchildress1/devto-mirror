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
Do NOT add new application modules into `scripts/`—reserve `scripts/` for runnable helpers and CLI wrappers.

## Commands

Use Makefile targets exclusively (do not invoke tools directly):

- `make test` - unit tests
- `make lint` - pre-commit checks (format, lint, security)
- `make security` - bandit + pip-audit scans
- `make validate` - full pipeline (format → lint → security → complexity → test → site validation)
- `make generate-site` - site generation (requires DEVTO_USERNAME and GH_USERNAME env vars)

## Agent Operational Rules

Automated agents must follow these constraints for safe and effective operation:

- **Big picture**: `scripts/` are CLI entrypoints (generation + helpers); `src/devto_mirror/` is the Python package; `src/devto_mirror/ai_optimization/` contains AI modules. Generated artifacts: `posts/` (HTML), `htmlcov/` (coverage reports).
- **Canonical runner**: prefer `Makefile` targets (single source of truth). Use `make install`, `make test` (unit tests), `make validate` (full pipeline), `make generate-site`, `make security` instead of calling tools directly.
- **Tooling**: this repo pins dev tooling via `uv.lock`. When invoking tools directly use `uv run <tool>`; prefer Makefile wrappers for consistency.
- **Pre-commit**: configured in `.pre-commit-config.yaml`. Install hooks with `make install` (runs `uv run pre-commit install`). The validate-site hook runs `uv run python scripts/validate_site_generation.py`.
- **Files to read first**: `Makefile`, `scripts/generate_site.py`, `scripts/validate_site_generation.py`, `.pre-commit-config.yaml`, `src/devto_mirror/ai_optimization/`, `docs/DEV_GUIDE.md`.

### Safety and Constraints

- Do NOT edit generated files in `htmlcov/` or anything under `.venv/`.
- Never perform automated `git commit` or push on behalf of a human. Produce `commit.tmp` messages and wait for human approval.
- If you change dev-tooling, update `uv.lock` with `uv sync --locked --group dev` and run `make validate` to ensure nothing regresses.
- Avoid introducing empty `except:` / `except: pass` patterns; prefer explicit exception handling.



## Code Style

Follow standard Python conventions; use pre-commit hooks where configured.

## Architecture Overview

- Static site generator: fetches Dev.to posts via API and renders HTML using Jinja2
- Incremental updates: `last_run.txt` is used to fetch only new/changed posts
- Optional AI optimizations: `devto_mirror.ai_optimization` is imported when available and used to enhance metadata and sitemaps

## Critical Workflows

- Dependency management: use `uv sync --locked --group dev` and `uv run python -m pip install -e .` or `make install`
- Testing: `make test` from repository root
- CI: GitHub Actions runs site generation and publishes to `gh-pages`; a follow-up job prepares a `_site` artifact for root deployment
- Site generation: set `DEVTO_USERNAME` and `GH_USERNAME` environment variables before running `scripts/generate_site.py`

### CI Workflow Critical Rules

NEVER use `uv run make <target>` in GitHub Actions workflows. Makefile targets already use `uv run` internally; double-nesting causes failures. Always invoke: `make <target>` not `uv run make <target>`.

## Assets and templates

- `assets/robots.txt` and `assets/llms.txt` are template files and are copied/substituted into the site during CI deployment. Do not overwrite the generated `robots.txt` or `llms.txt` at the repo root—editors should update the templates in `assets/` instead.

## Project Conventions

- Scripts live in `scripts/` (not `src/`)
- Required env vars: `DEVTO_USERNAME`, `GH_USERNAME`; optional: `DEVTO_API_KEY`, `VALIDATION_MODE`, `FORCE_FULL_REGEN`, `ROOT_SITE_PAT`
- Always preserve command output visibility—avoid redirecting to `/dev/null 2>&1`
- Generate commit messages in `commit.tmp` with `Generated-by: GitHub Copilot` attribution and wait for human approval before committing

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

- NEVER perform `git commit` on behalf of a human without explicit approval. Generate commit messages in `commit.tmp` with `Generated-by: GitHub Copilot` attribution for human review.
- Before returning to the user: run `make validate` to ensure all checks pass (format, lint, security, tests). If validation fails, iterate until resolved.
- Never use empty `except:` or `except: pass` patterns; prefer explicit exception handling.

<!-- MANUAL ADDITIONS END -->

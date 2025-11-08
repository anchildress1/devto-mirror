# devto-mirror Development Guidelines (AGENTS)

## Active Technologies
- Python 3.12+ (development & CI)
- requests, jinja2, python-slugify, bleach, python-dotenv
- Package manager: uv with locked dependencies (uv.lock)
- All dependencies, including GitHub Actions, should use latest stable versions

## Project Structure
```
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

## AI Agent Quick Start

If you're an automated agent working on this repo, follow these rules to be immediately productive and safe.

- **Big picture**: `scripts/` are CLI entrypoints (generation + helpers); `src/devto_mirror/` contains core AI modules (`ai_optimization/*`). Generated artifacts live in `posts/`, `assets/`, and `htmlcov/`.
- **Canonical runner**: prefer `Makefile` targets (single source of truth). Use `make install`, `make test` (unit tests), `make validate` (full pipeline), `make generate-site`, `make security` instead of calling tools directly.
- **Tooling**: this repo pins dev tooling via `uv.lock`. When invoking tools directly use `uv run <tool>`; prefer Makefile wrappers for consistency.
- **Pre-commit**: configured in `.pre-commit-config.yaml`. Install hooks with `make install` (runs `uv run pre-commit install`). The validate-site hook runs `uv run python scripts/validate_site_generation.py`.
- **Files to read first**: `Makefile`, `scripts/generate_site.py`, `scripts/validate_site_generation.py`, `.pre-commit-config.yaml`, `src/devto_mirror/ai_optimization/`, `docs/DEV_GUIDE.md`.

### Safety and Constraints

- Do NOT edit generated files in `htmlcov/` or anything under `.venv/`.
- Never perform automated `git commit` or push on behalf of a human. Produce `commit.tmp` messages and wait for human approval.
- If you change dev-tooling, update `uv.lock` with `uv sync --locked` and run `make validate` to ensure nothing regresses.
- Avoid introducing empty `except:` / `except: pass` patterns; prefer explicit exception handling.

### Quick Examples
  - Local setup: `python -m venv .venv && source .venv/bin/activate && make install`
  - Run unit tests: `make test`
  - Run full validation (format, lint, security, tests, site): `make validate`
  - Generate site locally: `make generate-site`


## Code Style
Follow standard Python conventions; use pre-commit hooks where configured.

## Architecture Overview
- Static site generator: fetches Dev.to posts via API and renders HTML using Jinja2
- Incremental updates: `last_run.txt` is used to fetch only new/changed posts
- Optional AI optimizations: `src.ai_optimization` is imported when available and used to enhance metadata and sitemaps

## Critical Workflows
- Dependency management: use `uv sync --locked` and `uv run python -m pip install -e .` or `make install`
- Testing: `make test` from repository root
- CI: GitHub Actions runs site generation and publishes to `gh-pages`; a follow-up job prepares a `_site` artifact for root deployment
- Site generation: set `DEVTO_USERNAME` and `PAGES_REPO` (user/repo) environment variables before running `scripts/generate_site.py`

## Assets and templates
- `assets/robots.txt` and `assets/llms.txt` are template files and are copied/substituted into the site during CI deployment. Do not overwrite the generated `robots.txt` or `llms.txt` at the repo root — editors should update the templates in `assets/` instead.

## Project Conventions

- Scripts live in `scripts/` (not `src/`)
- Required env vars: `DEVTO_USERNAME`, `PAGES_REPO`; optional: `DEVTO_API_KEY`, `VALIDATION_MODE`, `FORCE_FULL_REGEN`
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

## Notes about Specs

- Spec Kit is a planning tool and not a hard requirement; treat `spec` folders as guides, not strict rules.

## Critical Constraints

- Under NO circumstances should any automated workflow perform `git commit` on behalf of a human without explicit approval. Commit messages may be generated, but commits must be made by a human operator or an authorized CI step.
- Before returning to the user, you are expected to follow agent instructions to update the `commit.tmp` with a valid AI-attribution included commit message.
- All formatting, security scans, linters, and the entire test suite must pass successfully before you return to the user. If one or more items fail validation, iterate improvements as needed until all problems are resolved.
- Avoid using an empty except at any point. If you get to a point where they're required then the code is somehow inaccurate.

<!-- MANUAL ADDITIONS END -->

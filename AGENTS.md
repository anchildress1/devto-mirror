# devto-mirror Development Guidelines (AGENTS)

## Active Technologies
- Python 3.12+ (development & CI)
- requests, jinja2, python-slugify, bleach, python-dotenv
- Packaging: poetry / pip + editable installs for development
- All dependencies, including GHA MUST use the latest available version

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
python scripts/generate_site.py
```

## Code Style
Follow standard Python conventions; use pre-commit hooks where configured.

## Architecture Overview
- Static site generator: fetches Dev.to posts via API and renders HTML using Jinja2
- Incremental updates: `last_run.txt` is used to fetch only new/changed posts
- Optional AI optimizations: `src.ai_optimization` is imported when available and used to enhance metadata and sitemaps

## Critical Workflows
- Dependency management: `pip install -e .` or `make install`
- Testing: `make test` from repository root
- CI: GitHub Actions runs site generation and publishes to `gh-pages`; a follow-up job prepares a `_site` artifact for root deployment
- Site generation: set `DEVTO_USERNAME` and `PAGES_REPO` (user/repo) environment variables before running `scripts/generate_site.py`

## Assets and templates
- `assets/robots.txt` and `assets/llms.txt` are template files and are copied/substituted into the site during CI deployment. Do not overwrite the generated `robots.txt` or `llms.txt` at the repo root — editors should update the templates in `assets/` instead.

## Project Conventions
- Scripts live in `scripts/` (not `src/`)
- Required env vars: `DEVTO_USERNAME`, `PAGES_REPO`; optional: `DEVTO_API_KEY`, `VALIDATION_MODE`, `FORCE_FULL_REGEN`
- Generated files (posts/, `index.html`, `sitemap.xml`, `robots.txt`, `llms.txt`) are intentionally gitignored in the repository root
- Commit messages: use the conventional commit format. See the project prompt for generating messages.
- NEVER execute `git commit` automatically — generate a message and wait for user confirmation.

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

<!-- MANUAL ADDITIONS END -->

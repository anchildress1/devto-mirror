# devto-mirror Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-12

## Active Technologies
- Python 3.11+ + requests, jinja2, python-slugify, bleach (001-upgrade-the-python)
- Python 3.11+ + uv (package manager), pip-audit, bandit, flake8, GitHub Actions, CodeQL
- Git branches (backup branches), GitHub Security tab (CodeQL findings)

## Project Structure
```
scripts/          # Main application code (not src/)
tests/            # Unit tests using unittest
assets/           # Static assets (excluded from package)
```

## Commands
```bash
# Run tests from project root
python -m unittest

# Run quality checks
pre-commit run --all-files

# Generate site (requires DEVTO_USERNAME and PAGES_REPO env vars)
python scripts/generate_site.py
```

## Code Style
Python 3.11+: Follow standard conventions

## Architecture Overview
- **Static Site Generator**: Fetches Dev.to posts via API, generates SEO-optimized HTML
- **Incremental Updates**: Uses `last_run.txt` timestamp to process only new/changed posts
- **Template System**: Jinja2 templates in `scripts/utils.py` for HTML generation
- **Data Flow**: Dev.to API → JSON processing → HTML files in `posts/` directory

## Critical Workflows
- **Dependency Management**: Use `uv` (not pip) - requires quotes: `uv pip install -e '.[dev]'`
- **Testing**: `python -m unittest` from project root (not scripts/)
- **Code Quality**: `pre-commit run --all-files` (flake8, bandit, detect-secrets)
- **Site Generation**: Set `DEVTO_USERNAME` and `PAGES_REPO` env vars, run `python scripts/generate_site.py`

## Project Conventions
- **Scripts Directory**: All executable code in `scripts/` (not `src/`)
- **Environment Variables**: `DEVTO_USERNAME` (required), `PAGES_REPO` (user/repo format)
- **Generated Files**: HTML output in root directory but gitignored (posts/, index.html, etc.)
- **Package Exclusions**: `specs/`, `assets/`, `tests/`, `.github/` excluded from distribution
- **Commit Messages**: Conventional commits validated by `scripts/validate_commit_msg.py`

## Integration Points
- **Dev.to API**: RESTful article fetching with pagination
- **GitHub Pages**: Static hosting from `gh-pages` branch
- **GitHub Actions**: Daily automated builds using uv
- **SEO Optimization**: Canonical links, meta tags, sitemaps, AI-crawler friendly robots.txt

## Project Nature & Clarification Guidance
- **Simple Utility Repository**: This is a straightforward utility project - avoid over-engineering, complex orchestration, or overly verbose documentation
- **Clarifications**: If you ever have multiple independent questions to interrogate the user with, then always display them in a single prompt to get a single answer aimed to save extraneous/unnecessary interactions. You should make informed decisions based on simplicity principles rather than asking excessive questions. Present all clarification choices at the end when all other parts of the task are complete, for review.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

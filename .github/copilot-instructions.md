# devto-mirror Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-12

## Active Technologies
- Python 3.11+ + requests, jinja2, python-slugify, bleach (001-upgrade-the-python)

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
- **Dependency Management**: Use `pip` with pyproject.toml: `pip install -e '.[dev]'`
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
- **GitHub Actions**: Daily automated builds using pip
- **SEO Optimization**: Canonical links, meta tags, sitemaps, AI-crawler friendly robots.txt

<!-- MANUAL ADDITIONS START -->
## Security Instructions

- Use `bleach.clean()` for HTML sanitization; NEVER use regex or string replacements.
- Use `pathlib.Path().resolve()` to validate file paths and prevent directory traversal.
- Use `subprocess` with list arguments only; NEVER use `shell=True`.
- Exclude periods from slug sanitization characters to prevent path traversal.
- Ensure validation functions return boolean values consistently; avoid mixing exceptions and returns.

<!-- MANUAL ADDITIONS END -->

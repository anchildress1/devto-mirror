# devto-mirror Development Guidelines

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
make test

# Run quality checks
make lint

# Run tests with coverage
make test-coverage

# Run security checks
make security

# Run comprehensive validation
make validate

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
- **Dependency Management**: Use `make install` or `pip install -e '.[dev]'`
- **Testing**: `make test` from project root (not scripts/)
- **Code Quality**: `make lint` (flake8, bandit, detect-secrets)
- **Security**: `make security` (bandit, pip-audit)
- **Validation**: `make validate` (comprehensive validation: format + lint + test + security + site generation)
- **Site Generation**: Set `DEVTO_USERNAME` and `PAGES_REPO` env vars, run `python scripts/generate_site.py`

## Project Conventions
- **Scripts Directory**: All executable code in `scripts/` (not `src/`)
- **Environment Variables**: `DEVTO_USERNAME` (required), `PAGES_REPO` (user/repo format)
- **Generated Files**: HTML output in root directory but gitignored (posts/, index.html, etc.)
- **Package Exclusions**: `specs/`, `assets/`, `tests/`, `.github/` excluded from distribution
- **Commit Messages**: Conventional commits generated using `../awesome-github-copilot/.github/prompts/generate-commit-message.prompt.md`
  - NEVER execute a git commit command unless the user explicitly asks for it.

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
- Do not add useless lambdas anywhere in this codebase. They add no value and confuse readers.

## Notes about Specs

- Spec Kit is a test run for this project and dev. It is not intended to be a bible of any kind. The specs may change or be removed at any time. Depend on instructions above all else.
- Anything living inside of a `spec` folder or related should be assumed to be a planning tool and not a hard requirement.

## Critical Constraints

- Under NO circumstances should you ever attempt to perform a `git commit` command of any kind unless the user explicitly requests it. You may generate commit messages, but you must not execute git commands.

<!-- MANUAL ADDITIONS END -->

# Dev.to Mirror Development Commands

# Prefer the project's venv python if present, otherwise fall back to system `python`.
PYTHON := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python)

.PHONY: help test test-coverage lint format install clean check validate security
.PHONY: test-crawler analyze-crawlers

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install development dependencies
	uv sync --locked --group dev
	# Ensure pre-commit is executed via uv so we use the pinned dev toolchain
	uv run pre-commit install

test:  ## Run unit tests
	uv run python -m unittest discover -s tests -p 'test_*.py'

test-coverage:  ## Run tests with coverage report
	uv run coverage run -m unittest discover -s tests -p 'test_*.py'
	uv run coverage report
	uv run coverage html

lint:  ## Run pre-commit checks (formatting, linting, security)
	pre-commit run --all-files

format:  ## Format code with Black
	uv run black src/ tests/ scripts/ --line-length 120

prechecks:  ## Run prechecks on staged files (applies formatting to staged files only)
	@./scripts/prechecks.sh $$(git diff --name-only --cached)

prechecks-full:  ## Run full prechecks across the repo (force full run)
	@./scripts/prechecks.sh $$(git ls-files)

security:  ## Run security checks
	uv run bandit -r scripts src/ -ll -iii
	uv run pip-audit --progress-spinner=off --skip-editable --ignore-vuln GHSA-4xh5-x5gv-qwph --ignore-vuln GHSA-wj6h-64fc-37mp --ignore-vuln GHSA-7f5h-v6xp-fcq8

validate-site:  ## Validate site generation script
	uv run python scripts/validate_site_generation.py

generate-site:  ## Generate the site locally (creates HTML files in posts/)
	uv run python scripts/generate_site.py

# Crawler testing helpers
test-crawler:  ## Run crawler access test script. Provide BASE_URL as environment variable if needed.
	uv run python scripts/test_crawler_access.py $(BASE_URL)

analyze-crawlers:  ## Run GitHub Pages crawler analysis. Provide BASE_URL as an environment variable if needed.
	uv run python scripts/analyze_github_pages_crawlers.py $(BASE_URL)

check-imports:  ## Check for missing dependencies by running a dry-run of the site generator
	VALIDATION_MODE=true uv run python scripts/generate_site.py

validate:  ## Single command: format → lint → security → test + site (POC ready)
	@set -e; \
	echo "🔍 format → lint → security → test..."; \
	$(MAKE) format && echo "  ✓ format" || (echo "  ✗ format"; exit 1); \
	$(MAKE) lint && echo "  ✓ lint" || (echo "  ✗ lint"; exit 1); \
	$(MAKE) security && echo "  ✓ security" || (echo "  ✗ security"; exit 1); \
	$(MAKE) test && echo "  ✓ test" || (echo "  ✗ test"; exit 1); \
	$(MAKE) check-imports && echo "  ✓ imports" || (echo "  ✗ imports"; exit 1); \
	$(MAKE) validate-site && echo "  ✓ site" || (echo "  ✗ site"; exit 1); \
	echo "✅ Ready to commit."

check: validate  ## Alias for validate

clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Quick aliases
coverage: test-coverage  ## Alias for test-coverage

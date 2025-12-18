# Dev.to Mirror Development Commands

# Prefer the project's venv python if present, otherwise fall back to system `python`.
PYTHON := $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python)

.PHONY: help test lint format install clean check ai-checks security
.PHONY: check-complexity

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install development dependencies
	uv sync --locked --group dev
	# Ensure pre-commit is executed via uv so we use the pinned dev toolchain
	uv run pre-commit install

test:  ## Run unit tests
	uv run coverage run --source src,scripts -m unittest discover -s tests -p 'test_*.py'
	uv run coverage report --fail-under=80
	uv run coverage html

lint:  ## Run pre-commit checks (formatting, linting, security)
	uv run pre-commit run --all-files

format:  ## Format code with Black
	uv run black src/ tests/ scripts/ --line-length 120

prechecks:  ## Run prechecks on staged files (applies formatting to staged files only)
	@./scripts/prechecks.sh $$(git diff --name-only --cached)

prechecks-full:  ## Run full prechecks across the repo (force full run)
	@./scripts/prechecks.sh $$(git ls-files)

security:  ## Run security checks
	uv run bandit -r scripts src/ -ll -iii
	uv run pip-audit --progress-spinner=off --skip-editable --ignore-vuln GHSA-4xh5-x5gv-qwph --ignore-vuln GHSA-wj6h-64fc-37mp --ignore-vuln GHSA-7f5h-v6xp-fcq8

check-complexity:  ## Check cognitive complexity (max 15)
	@echo "🔍 Checking cognitive complexity (max 15)..."
	@uv run radon cc scripts/ src/ -s 2>/dev/null | grep -E "\([1-9][6-9]\)|([2-9][0-9]\)|([1-9][0-9]{2,}\))" && \
		echo "❌ Functions with complexity >15 found. See docs/COMPLEXITY_REFACTORING.md" && exit 1 || \
		echo "✅ All functions within complexity limits"

ai-checks:  ## Single command: format → lint → security → complexity → test + site (POC ready)
	@set -e; \
	echo "🔍 format → lint → security → complexity → test"; \
	$(MAKE) format && echo "  ✓ format" || (echo "  ✗ format"; exit 1); \
	$(MAKE) lint && echo "  ✓ lint" || (echo "  ✗ lint"; exit 1); \
	$(MAKE) security && echo "  ✓ security" || (echo "  ✗ security"; exit 1); \
	$(MAKE) check-complexity && echo "  ✓ complexity" || (echo "  ⚠ complexity (see docs/COMPLEXITY_REFACTORING.md)"; exit 0); \
	$(MAKE) test && echo "  ✓ test" || (echo "  ✗ test"; exit 1); \
	echo "✅ Ready to commit."

clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Dev.to Mirror Development Commands

.PHONY: help test test-coverage lint format install clean check validate security

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install development dependencies
	pip install -e '.[dev]'
	pre-commit install

test:  ## Run unit tests
	python -m unittest discover -s tests -p 'test_*.py'

test-coverage:  ## Run tests with coverage report
	coverage run -m unittest discover -s tests -p 'test_*.py'
	coverage report
	coverage html

lint:  ## Run pre-commit checks (formatting, linting, security)
	pre-commit run --all-files

format:  ## Format code with Black
	black devto_mirror/ tests/ scripts/ --line-length 120

security:  ## Run security checks
	bandit -r scripts devto_mirror/ -ll -iii
	pip-audit --progress-spinner=off --skip-editable --ignore-vuln GHSA-4xh5-x5gv-qwph

validate-site:  ## Validate site generation script
	python scripts/validate_site_generation.py

validate:  ## Comprehensive validation (format + lint + test + security + site generation)
	@echo "🔍 Running comprehensive validation..."
	@echo "📝 Formatting code..."
	@$(MAKE) format
	@echo "🧹 Running linting and pre-commit checks..."
	@$(MAKE) lint
	@echo "🧪 Running tests..."
	@$(MAKE) test
	@echo "🔒 Running security checks..."
	@$(MAKE) security
	@echo "🏗️  Validating site generation..."
	@$(MAKE) validate-site
	@echo "✅ All validation checks passed!"

check: validate  ## Comprehensive validation (format + lint + test + security)

clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Quick aliases
coverage: test-coverage  ## Alias for test-coverage
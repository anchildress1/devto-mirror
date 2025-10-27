# Dev.to Mirror Development Commands

.PHONY: help test test-coverage lint format install clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install development dependencies
	pip install -e '.[dev]'
	pre-commit install

test:  ## Run unit tests
	python -m unittest discover -s tests -p 'test_*.py' -v

test-coverage:  ## Run tests with coverage report
	python scripts/run_tests_with_coverage.py

lint:  ## Run linting and security checks
	pre-commit run --all-files

format:  ## Format code with Black and isort
	black devto_mirror/ tests/ scripts/ --line-length 120
	isort devto_mirror/ tests/ scripts/ --profile black --line-length 120

clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Quick aliases
coverage: test-coverage  ## Alias for test-coverage
check: lint  ## Alias for lint
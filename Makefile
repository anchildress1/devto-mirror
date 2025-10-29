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
	coverage run -m unittest discover -s tests -p 'test_*.py'
	coverage report
	coverage html

lint:  ## Run pre-commit checks (formatting, linting, security)
	pre-commit run --all-files

format:  ## Format code with Black
	black devto_mirror/ tests/ scripts/ --line-length 120


clean:  ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Quick aliases
coverage: test-coverage  ## Alias for test-coverage
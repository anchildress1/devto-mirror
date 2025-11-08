# Quickstart: Upgrade Python Implementation to Astral uv

**Date**: October 12, 2025
**Feature**: Upgrade to Astral uv

## Prerequisites

- Python 3.11+
- Astral uv installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git

## Setup

1. **Clone and navigate**:
   ```bash
   git clone https://github.com/anchildress1/devto-mirror.git
   cd devto-mirror
   git checkout 001-upgrade-the-python
   ```

2. **Create virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -e .
   ```

4. **Run basic test**:
   ```bash
   python -m unittest tests.test_basic
   ```

## Development Workflow

1. **Activate environment**: `source .venv/bin/activate`
2. **Install new dependencies**: `uv add <package>`
3. **Run scripts**: `uv run python scripts/generate_site.py`
4. **Run tests**: `python -m unittest`

## Key Changes from Previous Setup

- **Dependency management**: `uv pip install` instead of `pip install`
- **Virtual environment**: `uv venv` instead of `python -m venv`
- **Configuration**: `pyproject.toml` instead of `requirements.txt`
- **Testing**: New `tests/` directory with basic test suite

## Verification

- All existing scripts run without modification
- Test suite passes: `python -m unittest tests/`
- Dependencies installed via uv
- CI/CD uses uv commands

## Troubleshooting

- **uv not found**: Install uv from https://astral.sh/uv
- **Python version**: Ensure Python 3.11+ is used
- **Activation fails**: Check shell and path to .venv/bin/activate

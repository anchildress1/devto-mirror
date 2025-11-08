#!/usr/bin/env python3
"""Safely install this project in editable mode.

This helper ensures the install is invoked from the project root and gives a
clear error message if `pyproject.toml` or `setup.py` are missing. Use this in
CI or local shells instead of calling `pip install -e .` directly.
"""
import subprocess  # nosec: B404
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    has_pyproject = (project_root / "pyproject.toml").exists()
    has_setup = (project_root / "setup.py").exists()

    if not (has_pyproject or has_setup):
        print(
            f"Error: {project_root} does not appear to be a Python project; missing pyproject.toml or setup.py",
            file=sys.stderr,
        )
        return 2

    python = sys.executable
    cmd = [python, "-m", "pip", "install", "-e", str(project_root)]
    print("Running:", " ".join(cmd))
    try:
        # Running pip via the current Python executable. This uses a list
        # of arguments (no shell) and is intentionally narrow in scope.
        # Mark with nosec to acknowledge and silence bandit warnings for
        # this controlled subprocess usage.
        res = subprocess.run(cmd, check=False)  # nosec: B603
        return res.returncode
    except Exception as e:
        print(f"Failed to run pip: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

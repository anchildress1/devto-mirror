"""Path and filename sanitization utilities."""

import string
from pathlib import Path

SAFE_CHARS = set(string.ascii_letters + string.digits + "_-")


def sanitize_filename(filename: str, replacement: str = "-") -> str:
    """
    Sanitize a filename by replacing unsafe characters.

    Args:
        filename: The filename to sanitize
        replacement: Character to use as replacement (default: "-")

    Returns:
        Sanitized filename with only safe characters
    """
    return "".join(c if c in SAFE_CHARS else replacement for c in filename)


def sanitize_slug(slug: str, max_length: int = 120) -> str:
    """
    Sanitize a slug for use in URLs and filenames.

    Args:
        slug: The slug to sanitize
        max_length: Maximum length of the slug (default: 120)

    Returns:
        Sanitized slug truncated to max_length
    """
    sanitized = sanitize_filename(slug)
    return sanitized[:max_length] if max_length > 0 else sanitized


def validate_safe_path(base_dir: Path, target_path: str) -> Path:
    """
    Validate that a path is safe and within the base directory.

    Args:
        base_dir: Base directory that should contain the target
        target_path: Path to validate

    Returns:
        Resolved safe path

    Raises:
        ValueError: If path traversal is detected
    """
    base = base_dir.resolve()
    target = (base / target_path).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal detected: {target_path}")

    return target

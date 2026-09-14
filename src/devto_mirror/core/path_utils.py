"""Path and filename sanitization utilities."""

import string

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

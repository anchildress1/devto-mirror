"""Base URL for the mirror: a custom domain root (SITE_DOMAIN) or https://<user>.github.io/devto-mirror/."""

from __future__ import annotations

from urllib.parse import urlparse


def normalize_site_domain_input(site_domain: str) -> str:
    """Normalize SITE_DOMAIN (``example.com``, ``example.com/`` or a full URL) into ``https://example.com/``.

    Raises:
        ValueError: if the input cannot be normalized into a host.
    """
    raw = (site_domain or "").strip()
    if not raw:
        raise ValueError("SITE_DOMAIN is empty")

    if "://" in raw:
        parsed = urlparse(raw)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid SITE_DOMAIN URL: {site_domain!r}")
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return base if base.endswith("/") else f"{base}/"

    # A bare "example.com/foo" is ambiguous (path or typo?) and yields surprising URLs.
    if "/" in raw.rstrip("/"):
        raise ValueError(f"SITE_DOMAIN must be a domain, not a path: {site_domain!r}")
    return f"https://{raw.rstrip('/')}/"


def resolve_home(*, site_domain: str = "", gh_username: str = "", project: str = "devto-mirror") -> str:
    """Return the absolute mirror root URL, always ending in ``/``.

    Raises:
        ValueError: if neither site_domain nor gh_username is provided.
    """
    if site_domain.strip():
        return normalize_site_domain_input(site_domain)
    if gh_username.strip():
        return f"https://{gh_username.strip()}.github.io/{project}/"
    raise ValueError("Missing SITE_DOMAIN or GH_USERNAME")

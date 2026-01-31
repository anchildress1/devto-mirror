"""URL utilities for site generation.

This project generates a static site that can be hosted either:
- on a custom domain (SITE_DOMAIN) at the domain root, or
- on GitHub Pages under https://<user>.github.io/devto-mirror/

We centralize URL construction here to avoid subtle bugs like duplicated
"posts" path segments (e.g. /posts/posts/foo.html).
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse


@dataclass(frozen=True)
class SiteUrls:
    """Computed base URLs for the generated site."""

    home: str
    root_home: str


def _ensure_trailing_slash(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    return url if url.endswith("/") else f"{url}/"


def normalize_site_domain_input(site_domain: str) -> str:
    """Normalize SITE_DOMAIN input into a URL origin.

    Accepts:
    - "example.com"
    - "example.com/"
    - "https://example.com" (keeps scheme)

    Returns a string like "https://example.com/".

    Raises:
        ValueError: if the input cannot be normalized into a host.
    """

    raw = (site_domain or "").strip()
    if not raw:
        raise ValueError("SITE_DOMAIN is empty")

    # If a scheme is present, parse as a URL.
    if "://" in raw:
        parsed = urlparse(raw)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid SITE_DOMAIN URL: {site_domain!r}")
        # Keep any path component, but ensure it ends with a slash so urljoin works.
        base = f"{parsed.scheme}://{parsed.netloc}{parsed.path or ''}"
        return _ensure_trailing_slash(base)

    # No scheme provided: treat as a bare domain.
    # We intentionally do not accept paths here ("example.com/foo") because that
    # is ambiguous and tends to create surprising output URLs.
    if "/" in raw:
        raise ValueError(f"SITE_DOMAIN must be a domain, not a path: {site_domain!r}")

    return f"https://{raw}/"


def build_site_urls(
    *,
    site_domain: str = "",
    gh_username: str = "",
    project: str = "devto-mirror",
    fallback_gh_username: str | None = None,
) -> SiteUrls:
    """Compute base URLs for the generated site.

    Args:
        site_domain: Domain or URL for custom-domain hosting.
        gh_username: GitHub username for GitHub Pages hosting.
        project: GitHub Pages project name/path.
        fallback_gh_username: Optional fallback username (used in validation mode).

    Raises:
        ValueError: if neither site_domain nor gh_username (nor fallback) is provided.

    Returns:
        SiteUrls(home=..., root_home=...)
    """

    sd = (site_domain or "").strip()
    gh = (gh_username or "").strip()

    if sd:
        home = normalize_site_domain_input(sd)
        return SiteUrls(home=home, root_home=home)

    username = gh or (fallback_gh_username or "").strip()
    if username:
        home = f"https://{username}.github.io/{project}/"
        root_home = f"https://{username}.github.io/"
        return SiteUrls(home=home, root_home=root_home)

    raise ValueError("Missing SITE_DOMAIN or GH_USERNAME")


def post_page_href(slug: str) -> str:
    """Return an href from one post page to another.

    Post pages live in the same output directory ("posts/"). When a browser is
    currently at ".../posts/current.html", using "posts/other.html" results in
    ".../posts/posts/other.html".

    This function returns a *relative* href suitable for the post template.

    Examples:
        slug="hello" -> "hello.html"
        slug="posts/hello" -> "hello.html"
        slug="posts/hello.html" -> "hello.html"

    Raises:
        ValueError: if slug is empty or contains path traversal.
    """

    raw = (slug or "").strip()
    if not raw:
        raise ValueError("slug is empty")

    # Defensive: reject path traversal. Slugs should be simple filenames.
    if ".." in raw.split("/"):
        raise ValueError("slug contains path traversal")

    # Strip any leading path and extension.
    filename = raw.split("/")[-1]
    if filename.endswith(".html"):
        filename = filename[: -len(".html")]

    if not filename:
        raise ValueError("slug did not contain a filename")

    return f"{filename}.html"


def build_post_url(home: str, slug: str) -> str:
    """Build an absolute URL to a post page.

    Uses urljoin so it works correctly for both custom domains and GitHub Pages.

    The slug may be either "hello" or "posts/hello.html"; duplicate "posts"
    segments will not be introduced.
    """

    base = _ensure_trailing_slash(home)
    if not base:
        raise ValueError("home is empty")

    href = post_page_href(slug)
    # href is like "hello.html"; add posts/ explicitly.
    return urljoin(base, f"posts/{href}")

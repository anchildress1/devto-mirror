"""A mirrored Dev.to article, normalized from the API's full-article payload."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from devto_mirror.core.html_sanitization import sanitize_html_content
from devto_mirror.core.path_utils import sanitize_slug

_IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_HAS_SIZE = re.compile(r"\b(width|height)\s*=", re.IGNORECASE)


def _sized(match: re.Match[str]) -> str:
    tag = match[0]
    # tag[:4] is "<img" in whatever case the source used.
    return tag if _HAS_SIZE.search(tag) else f'{tag[:4]} width="800" height="450"{tag[4:]}'


def ensure_img_dimensions(html: str) -> str:
    """Give ``<img>`` tags without explicit sizes a default width/height so browsers reserve space (CLS)."""
    return _IMG_TAG.sub(_sized, html)


def _devto_canonical(article: dict) -> str:
    # AGENTS.md requires every canonical to point at Dev.to; a repost's own canonical
    # still qualifies since Dev.to hosts the original too, but an external URL does not.
    declared = article.get("canonical_url") or ""
    if declared and urlparse(declared).netloc.lower() == "dev.to":
        return declared
    return article["url"]


def _tags(article: dict) -> tuple[str, ...]:
    # Dev.to intentionally swaps which of tag_list/tags is the array vs. the
    # comma-separated string between the listing and single-article endpoints
    # (forem/forem#4206), so normalize either shape from either key.
    raw = article.get("tag_list") or article.get("tags") or ()
    if isinstance(raw, str):
        raw = raw.split(",")
    return tuple(tag.strip() for tag in raw if tag and tag.strip())


@dataclass(frozen=True, slots=True)
class Post:
    slug: str
    title: str
    url: str
    canonical: str
    description: str
    content_html: str
    cover_image: str
    tags: tuple[str, ...]
    author: str
    username: str
    published: str
    modified: str
    reading_minutes: int

    @classmethod
    def from_article(cls, article: dict) -> Post:
        """Build a Post from a Dev.to full-article dict. Raises KeyError/ValueError on unusable input."""
        slug = sanitize_slug(article["slug"])
        if not slug:
            raise ValueError(f"Article {article.get('id')} has no usable slug")
        user = article.get("user") or {}
        published = article["published_at"]
        return cls(
            slug=slug,
            title=article["title"],
            url=article["url"],
            canonical=_devto_canonical(article),
            description=(article.get("description") or "").strip(),
            content_html=sanitize_html_content(ensure_img_dimensions(article.get("body_html") or "")),
            cover_image=article.get("cover_image") or "",
            tags=_tags(article),
            author=user.get("name") or user.get("username") or "",
            username=user.get("username") or "",
            published=published,
            modified=max(published, article.get("edited_at") or ""),
            reading_minutes=int(article.get("reading_time_minutes") or 0),
        )

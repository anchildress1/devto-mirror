"""Structured data and internal linking for mirrored posts."""

from __future__ import annotations

from devto_mirror.site_generation.post import Post


def article_schema(post: Post) -> dict:
    """Return schema.org BlogPosting JSON-LD attributing the post to its Dev.to original."""
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "url": post.canonical,
        "mainEntityOfPage": post.canonical,
        "datePublished": post.published,
        "dateModified": post.modified,
        "author": {"@type": "Person", "name": post.author, "url": f"https://dev.to/{post.username}"},
        "publisher": {"@type": "Organization", "name": "DEV Community", "url": "https://dev.to"},
    }
    optional = {
        "description": post.description,
        "image": post.cover_image,
        "keywords": list(post.tags),
        "timeRequired": f"PT{post.reading_minutes}M" if post.reading_minutes else "",
    }
    schema.update({key: value for key, value in optional.items() if value})
    return schema


def related_posts(post: Post, posts: list[Post], limit: int = 5) -> list[Post]:
    """Return up to ``limit`` other posts ranked by case-insensitive shared tags (ties keep input order)."""
    tags = {tag.lower() for tag in post.tags}
    scored = [
        (len(tags & {tag.lower() for tag in other.tags}), index, other)
        for index, other in enumerate(posts)
        if other.slug != post.slug
    ]
    ranked = sorted((s for s in scored if s[0]), key=lambda s: (-s[0], s[1]))
    return [other for _, _, other in ranked[:limit]]

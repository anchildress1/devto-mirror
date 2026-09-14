"""Builders for Dev.to API payloads used across tests."""


def make_article(article_id: int = 1, **overrides) -> dict:
    """Return a Dev.to full-article dict (the /api/articles/{id} shape) with sensible defaults."""
    slug = f"post-{article_id}"
    article = {
        "id": article_id,
        "slug": slug,
        "title": f"Post {article_id}",
        "url": f"https://dev.to/ash/{slug}",
        "canonical_url": f"https://dev.to/ash/{slug}",
        "description": f"About post {article_id}",
        "body_html": f"<p>Body {article_id}</p>",
        "cover_image": "",
        "tags": ["python"],
        "user": {"name": "Ash", "username": "ash"},
        "published_at": f"2026-01-{article_id:02d}T00:00:00Z",
        "edited_at": None,
        "reading_time_minutes": 4,
    }
    article.update(overrides)
    return article


def make_summary(article_id: int = 1, **overrides) -> dict:
    """Return a listing entry (the /api/articles?username= shape): no body_html."""
    summary = {key: value for key, value in make_article(article_id).items() if key != "body_html"}
    summary.update(overrides)
    return summary

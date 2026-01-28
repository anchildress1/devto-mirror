"""Fetch DEV/Forem articles for a username.

This pulls the API interaction (paging, retries, delta filtering, cache fallback)
into `src/` so `scripts/generate_site.py` can stay a thin entrypoint.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from devto_mirror.core.api_client import create_devto_session, fetch_page_with_retry, filter_new_articles


@dataclass(frozen=True, slots=True)
class FetchArticlesResult:
    articles: list[dict]
    success: bool
    no_new_posts: bool
    source: str


def _get_first_val(sources: list[dict], keys: list[str], default: Any = "") -> Any:
    for source in sources:
        for key in keys:
            if val := source.get(key):
                return val
    return default


def _convert_cached_post_to_devto_article(*, item: dict, username: str) -> dict | None:
    if not isinstance(item, dict):
        return None

    api_data = item.get("api_data")
    if not isinstance(api_data, dict):
        api_data = {}

    sources = [item, api_data]

    url = (item.get("url") or item.get("link") or "").strip()

    return {
        "id": _get_first_val(sources, ["id"], 0),
        "title": _get_first_val(sources, ["title"], "Untitled"),
        "url": url,
        "published_at": _get_first_val(sources, ["published_at", "date"]),
        "edited_at": _get_first_val(sources, ["edited_at"]),
        "updated_at": _get_first_val(sources, ["updated_at"]),
        "body_html": _get_first_val(sources, ["body_html", "content_html"]),
        "description": (item.get("description") or "").strip(),
        "cover_image": item.get("cover_image") or "",
        "tag_list": _get_first_val(sources, ["tag_list", "tags"], []),
        "slug": item.get("slug") or "",
        "user": {
            "name": item.get("author") or "",
            "username": username,
        },
    }


def _try_load_cached_articles(*, posts_data_path: str | os.PathLike, username: str) -> list[dict]:
    try:
        p = Path(posts_data_path)
        if not p.exists():
            return []

        cached_data = json.loads(p.read_text(encoding="utf-8"))
        if not cached_data:
            return []

        converted: list[dict] = []
        for item in cached_data:
            converted_item = _convert_cached_post_to_devto_article(item=item, username=username)
            if converted_item is not None:
                converted.append(converted_item)
        return converted
    except Exception:
        return []


def _fetch_article_pages(*, username: str, last_run_iso: str | None) -> list[dict]:
    articles: list[dict] = []
    page = 1
    api_base = "https://dev.to/api/articles"

    session = create_devto_session()

    per_page = 100
    while True:
        params = {"username": username, "page": page, "per_page": per_page}
        if page == 1:
            params["_cb"] = time.time() // 60

        data = fetch_page_with_retry(session, api_base, params, page)
        if not data:
            break

        new_or_updated_articles = filter_new_articles(data, last_run_iso)
        articles.extend(new_or_updated_articles)

        # DEV.to orders this list by publish time, not edit time. Page until exhaustion.
        if len(data) < per_page:
            break

        page += 1
        time.sleep(0.5)

    session.close()
    return articles


def _fetch_full_article_json(
    session: requests.Session,
    *,
    article_id: int,
    max_retries: int = 3,
    timeout: int = 30,
    initial_retry_delay: int = 2,
) -> dict | None:
    if max_retries < 1:
        return None

    retry_delay = initial_retry_delay
    for attempt in range(max_retries):
        try:
            full_response = session.get(f"https://dev.to/api/articles/{article_id}", timeout=timeout)
            full_response.raise_for_status()
            return full_response.json()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return None
        except requests.exceptions.RequestException:
            return None

    return None


def _fetch_full_articles(*, article_summaries: list[dict]) -> tuple[list[dict], list[dict]]:
    session = create_devto_session()

    full_articles: list[dict] = []
    failed_articles: list[dict] = []

    for i, article in enumerate(article_summaries):
        article_id = int(article.get("id") or 0)
        full = _fetch_full_article_json(session, article_id=article_id)
        if full is None:
            failed_articles.append(article)
        else:
            full_articles.append(full)

        if i < len(article_summaries) - 1:
            time.sleep(0.8)

    session.close()
    return full_articles, failed_articles


def fetch_all_articles_from_api(
    *,
    username: str,
    last_run_iso: str | None,
    posts_data_path: str | os.PathLike,
    validation_mode: bool,
) -> FetchArticlesResult:
    """Fetch full-article objects plus fetch metadata.

    Distinguishes between:
    - no new posts (successful incremental check yields nothing)
    - API failure (fallback to cached posts_data.json)

    Environment hooks:
    - DEVTO_MIRROR_FORCE_EMPTY_FEED: force empty feed (tests)
    - VALIDATION_NO_POSTS: validation mode, simulate no posts
    """

    if os.getenv("DEVTO_MIRROR_FORCE_EMPTY_FEED", "").lower() in ("true", "1", "yes"):
        return FetchArticlesResult(articles=[], success=True, no_new_posts=bool(last_run_iso), source="forced-empty")

    if validation_mode:
        if os.getenv("VALIDATION_NO_POSTS", "").lower() in ("true", "1", "yes"):
            return FetchArticlesResult(articles=[], success=True, no_new_posts=False, source="validation")

        return FetchArticlesResult(
            articles=[
                {
                    "id": 1,
                    "title": "Test Article",
                    "url": f"https://dev.to/{username}/test-article",
                    "published_at": "2024-01-01T00:00:00Z",
                    "body_html": "<p>Test content</p>",
                    "description": "Test description",
                    "cover_image": "",
                    "tag_list": ["test", "validation"],
                    "slug": "test-article",
                }
            ],
            success=True,
            no_new_posts=False,
            source="mock",
        )

    summaries = _fetch_article_pages(username=username, last_run_iso=last_run_iso)
    if not summaries:
        if last_run_iso:
            return FetchArticlesResult(articles=[], success=True, no_new_posts=True, source="api")
        return FetchArticlesResult(articles=[], success=True, no_new_posts=False, source="api")

    try:
        full_articles, _failed = _fetch_full_articles(article_summaries=summaries)
    except Exception:
        full_articles = []

    if not full_articles:
        cached = _try_load_cached_articles(posts_data_path=posts_data_path, username=username)
        return FetchArticlesResult(articles=cached, success=False, no_new_posts=False, source="cache")

    return FetchArticlesResult(articles=full_articles, success=True, no_new_posts=False, source="api")

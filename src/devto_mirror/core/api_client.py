"""Dev.to (Forem) API client: list a user's articles and sync their full bodies."""

from __future__ import annotations

import logging
import os
import time

import requests

API_URL = "https://dev.to/api/articles"
PER_PAGE = 100
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
MAX_RETRY_WAIT = 60.0

logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """Return a session with the Forem v1 Accept header and DEVTO_KEY (if set) applied."""
    session = requests.Session()
    session.headers.update({"User-Agent": "DevTo-Mirror-Bot/1.0", "Accept": "application/vnd.forem.api-v1+json"})
    if api_key := os.getenv("DEVTO_KEY"):
        session.headers["api-key"] = api_key
    return session


def _retry_after(response: requests.Response, default: float) -> float:
    try:
        wait = float(response.headers.get("Retry-After", default))
    except ValueError:  # HTTP-date form
        wait = default
    # A huge Retry-After would outlive the job timeout and hide the real 429.
    return min(max(wait, 0.0), MAX_RETRY_WAIT)


def get_json(session: requests.Session, url: str, params: dict | None = None, *, attempts: int = 4):
    """GET and decode JSON, retrying timeouts, connection errors, 429 and 5xx with backoff.

    Raises the last ``requests.RequestException`` once attempts are exhausted, or immediately
    for non-retryable HTTP errors.
    """
    delay = 1.0
    for attempt in range(1, attempts + 1):
        try:
            response = session.get(url, params=params, timeout=30)
        except (requests.Timeout, requests.ConnectionError, requests.exceptions.ChunkedEncodingError) as exc:
            error, wait = exc, delay
        else:
            if response.status_code not in RETRYABLE_STATUS:
                response.raise_for_status()
                return response.json()
            error = requests.HTTPError(f"{response.status_code} from {response.url}", response=response)
            wait = _retry_after(response, delay)
        if attempt == attempts:
            raise error
        logger.warning("Attempt %d/%d for %s failed (%s); retrying in %.1fs", attempt, attempts, url, error, wait)
        time.sleep(wait)
        delay *= 2
    raise AssertionError("unreachable")


def list_articles(session: requests.Session, username: str) -> list[dict]:
    """Return summaries of every published article for ``username``, across all pages."""
    articles: list[dict] = []
    page = 1
    while True:
        batch = get_json(session, API_URL, {"username": username, "page": page, "per_page": PER_PAGE})
        if not isinstance(batch, list):
            raise ValueError(f"Unexpected listing payload for page {page}: {batch!r:.200}")
        articles.extend(batch)
        if len(batch) < PER_PAGE:
            return articles
        page += 1
        time.sleep(0.5)


def _last_activity(article: dict) -> str:
    # The API emits uniform ISO-8601 UTC strings, so text comparison orders them correctly.
    return max(article.get("published_at") or "", article.get("edited_at") or "")


def sync_articles(username: str, stored: list[dict]) -> list[dict]:
    """Return the full article for every published post, in listing order.

    Stored articles are reused unless the listing shows a newer edit; posts no longer listed
    are dropped. Any API failure raises, so a partial fetch can never replace the store.

    Raises:
        RuntimeError: if more than half of the stored articles disappear from the listing,
            which is likelier an API glitch than a mass deletion. Pass an empty store to override.
    """
    # Only full articles carry body_html; anything else in the store is refetched.
    known = {a["id"]: a for a in stored if "id" in a and "body_html" in a}
    articles: dict[int, dict] = {}
    with create_session() as session:
        for summary in list_articles(session, username):
            # A post published mid-pagination shifts the pages and can be listed twice.
            if summary["id"] in articles:
                continue
            cached = known.get(summary["id"])
            if cached and _last_activity(cached) == _last_activity(summary):
                articles[summary["id"]] = cached
                continue
            full = get_json(session, f"{API_URL}/{summary['id']}")
            full.pop("body_markdown", None)
            articles[summary["id"]] = full
            time.sleep(0.5)

    dropped = known.keys() - articles.keys()
    for article_id in sorted(dropped):
        logger.warning("Dropping article %s (%s): no longer listed on Dev.to", article_id, known[article_id].get("url"))
    if len(dropped) * 2 > len(known):
        raise RuntimeError(
            f"{len(dropped)} of {len(known)} stored articles vanished from the listing; refusing to sync."
        )
    return list(articles.values())

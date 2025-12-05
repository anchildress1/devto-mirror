import os
import time
from datetime import datetime
from typing import Optional

import requests


def create_devto_session() -> requests.Session:
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"
    if is_ci:
        print("🤖 Running in CI environment - using conservative timeouts and delays")

    session = requests.Session()
    headers = {
        "User-Agent": "DevTo-Mirror-Bot/1.0 (GitHub-Actions)" if is_ci else "DevTo-Mirror-Bot/1.0",
        "Accept": "application/vnd.forem.api-v1+json",
    }

    api_key = os.getenv("DEVTO_API_KEY")
    if api_key:
        headers["api-key"] = api_key

    session.headers.update(headers)
    return session


def fetch_page_with_retry(
    session: requests.Session,
    url: str,
    params: dict,
    page: int,
    max_retries: int = 3,
    timeout: int = 30,
) -> Optional[list]:
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            response = session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  Timeout on page {page}, attempt {attempt + 1}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"  ❌ Failed to fetch page {page} after {max_retries} attempts: {e}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error for page {page}: {e}")
            return None

    return None


def filter_new_articles(data: list, last_run_iso: Optional[str]) -> list:
    if not last_run_iso:
        return data

    last_run_dt = datetime.fromisoformat(last_run_iso)
    return [
        article
        for article in data
        if datetime.fromisoformat(article["published_at"].replace("Z", "+00:00")) > last_run_dt
    ]


def should_continue_pagination(data: list, last_run_iso: Optional[str], new_articles: list) -> bool:
    if not data:
        return False

    if last_run_iso:
        return len(data) >= 100 and len(new_articles) >= len(data)

    return True

import html
import json
import logging
import os
import pathlib
import re
import sys
import time
from datetime import datetime, timezone
from typing import NamedTuple

# Add parent directory to path for imports BEFORE other local imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import bleach
import requests
from dotenv import load_dotenv
from jinja2 import Environment, select_autoescape
from slugify import slugify

from devto_mirror.html_sanitization import sanitize_html_content
from scripts.constants import POSTS_DATA_FILE
from scripts.path_utils import sanitize_filename, sanitize_slug, validate_safe_path
from scripts.utils import INDEX_TMPL, SITEMAP_TMPL, dedupe_posts_by_link, get_post_template

# Import AI optimization components
try:
    from devto_mirror.ai_optimization import create_default_ai_optimization_manager, enhance_post_with_cross_references

    AI_OPTIMIZATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI optimization not available: {e}")
    AI_OPTIMIZATION_AVAILABLE = False

# Load environment variables from .env file if it exists
load_dotenv()

DEVTO_USERNAME = os.getenv("DEVTO_USERNAME", "").strip()
GH_USERNAME = os.getenv("GH_USERNAME", "").strip()
LAST_RUN_FILE = "last_run.txt"
NO_NEW_POSTS_FILE = "no_new_posts.flag"
VALIDATION_MODE = os.getenv("VALIDATION_MODE", "").lower() in ("true", "1", "yes")

if not VALIDATION_MODE:
    if not DEVTO_USERNAME:
        raise ValueError("Missing DEVTO_USERNAME (your Dev.to username)")
    if not GH_USERNAME:
        raise ValueError("Missing GH_USERNAME (your GitHub username)")

username = GH_USERNAME or "user"
HOME = f"https://{username}.github.io/devto-mirror/"
ROOT_HOME = f"https://{username}.github.io/"

ROOT = pathlib.Path(".")
POSTS_DIR = ROOT / "posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize AI optimization manager
ai_manager = None
if AI_OPTIMIZATION_AVAILABLE:
    try:
        site_name = f"{DEVTO_USERNAME}—Dev.to Mirror"
        ai_manager = create_default_ai_optimization_manager(site_name, HOME)
        logging.info("AI optimization manager initialized successfully")
    except Exception as e:
        logging.warning(f"Failed to initialize AI optimization manager: {e}")
        ai_manager = None


class FetchArticlesResult(NamedTuple):
    articles: list[dict]
    success: bool
    no_new_posts: bool
    source: str


def get_last_run_timestamp():
    """Reads the timestamp from the last successful run."""
    p = pathlib.Path(LAST_RUN_FILE)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip()


def set_last_run_timestamp():
    """Writes the current UTC timestamp to the run file."""
    p = pathlib.Path(LAST_RUN_FILE)
    p.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")


def mark_no_new_posts():
    """Create marker file and emit GitHub Actions output for no-op runs."""
    marker_path = pathlib.Path(NO_NEW_POSTS_FILE)
    marker_path.write_text("true", encoding="utf-8")

    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write("no_new_posts=true\n")

    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as summary:
            summary.write("⚠️ No new posts found since last run. Skipping generation.\n")


def _fetch_article_pages(last_run_iso=None):
    from devto_mirror.api_client import create_devto_session, fetch_page_with_retry, filter_new_articles

    articles = []
    page = 1
    api_base = "https://dev.to/api/articles"

    session = create_devto_session()

    while True:
        print(f"Fetching page {page} of articles...")

        params = {"username": DEVTO_USERNAME, "page": page}
        if page > 1:
            params["per_page"] = 100
        if page == 1:
            params["_cb"] = time.time() // 60

        data = fetch_page_with_retry(session, api_base, params, page)

        if not data:
            break

        new_articles = filter_new_articles(data, last_run_iso)
        articles.extend(new_articles)

        if last_run_iso and (len(data) < 100 or len(new_articles) < len(data)):
            break

        page += 1
        time.sleep(0.5)

    session.close()
    return articles


def _is_ci_environment() -> bool:
    return os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"


def _create_devto_v1_session(*, is_ci: bool) -> requests.Session:
    session = requests.Session()
    headers = {
        "User-Agent": "DevTo-Mirror-Bot/1.0 (GitHub-Actions)" if is_ci else "DevTo-Mirror-Bot/1.0",
        "Accept": "application/vnd.forem.api-v1+json",  # Use V1 API for better compatibility
    }

    # Add API key if available for higher rate limits
    api_key = os.getenv("DEVTO_KEY")
    if api_key:
        headers["api-key"] = api_key

    session.headers.update(headers)
    return session


def _fetch_full_article_json(
    session: requests.Session,
    *,
    article_id: int,
    max_retries: int = 3,
    timeout: int = 30,
    initial_retry_delay: int = 2,
) -> dict | None:
    retry_delay = initial_retry_delay
    for attempt in range(max_retries):
        try:
            full_response = session.get(f"https://dev.to/api/articles/{article_id}", timeout=timeout)
            full_response.raise_for_status()
            return full_response.json()
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                print(f"  ⚠️  Timeout/connection error on attempt {attempt + 1}, " f"retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            print(f"  ❌ Failed to fetch article {article_id} after {max_retries} attempts: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error for article {article_id}: {e}")
            return None


def _fetch_full_articles(articles):
    """Fetch full article content for each article (needed for body_html).
    Kept separate so the pagination implementation remains easy to reason about.
    """
    print(f"Found {len(articles)} articles, fetching full content...")
    full_articles = []
    failed_articles = []

    # Detect CI environment and adjust settings
    is_ci = _is_ci_environment()

    # Create a session for connection reuse with V1 API
    session = _create_devto_v1_session(is_ci=is_ci)

    for i, article in enumerate(articles):
        print(f"Fetching full content for article {i + 1}/{len(articles)}: {article.get('title')}")

        article_id = int(article.get("id") or 0)
        full = _fetch_full_article_json(session, article_id=article_id)
        if full is None:
            failed_articles.append(article)
        else:
            full_articles.append(full)

        # Rate limiting between requests
        if i < len(articles) - 1:
            time.sleep(0.8)  # Rate limiting between requests

    session.close()
    print(f"Found {len(full_articles)} articles with full content.")
    if failed_articles:
        print(f"⚠️  Failed to fetch {len(failed_articles)} articles due to timeouts/errors")
        for failed in failed_articles:
            print(f"  - {failed.get('title', 'Unknown')} (ID: {failed['id']})")

    return full_articles


def _convert_cached_post_to_devto_article(item: dict) -> dict | None:
    if not isinstance(item, dict):
        return None

    url = (item.get("url") or item.get("link") or "").strip()
    return {
        "id": item.get("id") or 0,
        "title": item.get("title") or "Untitled",
        "url": url,
        "published_at": item.get("published_at") or item.get("date") or "",
        "body_html": item.get("body_html") or item.get("content_html") or "",
        "description": (item.get("description") or "").strip(),
        "cover_image": item.get("cover_image") or "",
        "tag_list": item.get("tag_list") or item.get("tags") or [],
        "slug": item.get("slug") or "",
        "user": {
            "name": item.get("author") or "",
            "username": DEVTO_USERNAME,
        },
    }


def _try_load_cached_articles():
    """Try to load articles from cached posts_data.json as fallback."""
    try:
        if os.path.exists(POSTS_DATA_FILE):
            print(f"📁 Loading cached articles from {POSTS_DATA_FILE}")
            with open(POSTS_DATA_FILE, "r", encoding="utf-8") as f:
                cached_data = json.load(f)

            if cached_data:
                print(f"✅ Found {len(cached_data)} cached articles")
                # posts_data.json stores mirror-specific keys (link/date/content_html/etc).
                # Convert to Dev.to API-like objects so Post() can consume them safely.
                converted: list[dict] = []
                for item in cached_data:
                    converted_item = _convert_cached_post_to_devto_article(item)
                    if converted_item is not None:
                        converted.append(converted_item)
                return converted
        print("❌ No cached articles available")
        return []
    except Exception as e:
        print(f"❌ Error loading cached articles: {e}")
        return []


def fetch_all_articles_from_api(last_run_iso=None) -> FetchArticlesResult:
    """Return full-article objects plus fetch metadata.

    We distinguish between:
    - *no new posts* (a successful incremental check that yields nothing)
    - *API failure* (where we may fall back to cached posts_data.json)

    That distinction matters because advancing last_run.txt on API failure can
    permanently skip content.
    """
    # Testing hook (test suites/local development only): force empty feed without network calls.
    if os.getenv("DEVTO_MIRROR_FORCE_EMPTY_FEED", "").lower() in ("true", "1", "yes"):
        return FetchArticlesResult(
            articles=[],
            success=True,
            no_new_posts=bool(last_run_iso),
            source="forced-empty",
        )

    if VALIDATION_MODE:
        # Allow tests/validation to simulate an account with zero posts.
        # This must still generate required artifacts without attempting network calls.
        if os.getenv("VALIDATION_NO_POSTS", "").lower() in ("true", "1", "yes"):
            return FetchArticlesResult(articles=[], success=True, no_new_posts=False, source="validation")

        # Return mock data for validation
        # Uncomment the next line to test validation failure detection:
        # raise RuntimeError("Test validation failure")
        return FetchArticlesResult(
            articles=[
                {
                    "id": 1,
                    "title": "Test Article",
                    "url": f"https://dev.to/{DEVTO_USERNAME}/test-article",
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

    try:
        summaries = _fetch_article_pages(last_run_iso=last_run_iso)
        if not summaries:
            # If we're doing incremental updates, this means a successful no-op run.
            if last_run_iso:
                return FetchArticlesResult(articles=[], success=True, no_new_posts=True, source="api")
            # Otherwise: the user has no posts (or none are accessible).
            return FetchArticlesResult(articles=[], success=True, no_new_posts=False, source="api")

        full_articles = _fetch_full_articles(summaries)
        if not full_articles:
            print("⚠️  No full articles fetched, checking for cached data...")
            cached = _try_load_cached_articles()
            return FetchArticlesResult(articles=cached, success=False, no_new_posts=False, source="cache")

        return FetchArticlesResult(articles=full_articles, success=True, no_new_posts=False, source="api")

    except Exception as e:
        print(f"❌ Error fetching articles from API: {e}")
        print("⚠️  Trying to use cached data as fallback...")
        cached = _try_load_cached_articles()
        return FetchArticlesResult(articles=cached, success=False, no_new_posts=False, source="cache")


# ----------------------------
# Templates (posts + index)
# ----------------------------
env = Environment(autoescape=select_autoescape(["html", "xml"]))

# Get the post template (from file or inline fallback)
PAGE_TMPL = get_post_template()

COMMENT_NOTE_TMPL = env.from_string(
    """<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<title>{{ title }}</title>
<link rel="canonical" href="{{ canonical }}">
<meta name="description" content="{{ description }}">
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="article">
<meta property="og:url" content="{{ canonical }}">
<meta property="og:title" content="{{ title }}">
<meta property="og:description" content="{{ description }}">
<meta property="og:image" content="{{ social_image }}">
<meta property="og:site_name" content="{{ site_name }}">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="{{ canonical }}">
<meta name="twitter:title" content="{{ title }}">
<meta name="twitter:description" content="{{ description }}">
<meta name="twitter:image" content="{{ social_image }}">

<!-- LinkedIn -->
<meta property="linkedin:title" content="{{ title }}">
<meta property="linkedin:description" content="{{ description }}">
<meta property="linkedin:image" content="{{ social_image }}">

<!-- Additional Social Meta -->
<meta name="image" content="{{ social_image }}">
<meta name="author" content="{{ author }}">

<!-- AI-Specific Enhanced Metadata -->
{% if enhanced_metadata %}
{% for name, content in enhanced_metadata.items() %}
<meta name="{{ name }}" content="{{ content }}">
{% endfor %}
{% endif %}

<!-- JSON-LD Structured Data -->
{% if json_ld_schemas %}
{% for schema in json_ld_schemas %}
<script type="application/ld+json">
{{ schema | tojson }}
</script>
{% endfor %}
{% endif %}
</head><body>
<main>
  <h1>{{ title }}</h1>
  {% if context %}<p>{{ context }}</p>{% endif %}
  <p><a href="{{ url }}">Open on Dev.to →</a></p>
</main>
</body></html>
"""
)


# ----------------------------
# robots + sitemap
# ----------------------------
# Helpers
# ----------------------------
def strip_html(text):
    """Remove HTML tags and normalize whitespace using bleach."""
    if not text:
        return ""
    cleaned = bleach.clean(text, tags=[], strip=True)
    return " ".join(cleaned.split()).strip()


def _img_tag_has_dimensions(tag: str) -> bool:
    # Accept either single or double quotes, and arbitrary whitespace.
    has_width = re.search(r"\bwidth\s*=\s*(['\"])\d+\1", tag, flags=re.IGNORECASE)
    has_height = re.search(r"\bheight\s*=\s*(['\"])\d+\1", tag, flags=re.IGNORECASE)
    return bool(has_width and has_height)


def _choose_img_size_for_src(*, src_val: str, cover_src: str | None) -> tuple[int, int]:
    if cover_src and src_val and cover_src in src_val:
        return 1000, 420
    if "/cover" in src_val or "cover_image" in src_val:
        return 1000, 420
    return 800, 450


def _add_img_dimensions_to_tag(*, tag: str, width: int, height: int) -> str:
    updated = tag
    if "width=" not in updated:
        updated = updated.replace("<img", f'<img width="{width}"', 1)
    if "height=" not in updated:
        updated = updated.replace("<img", f'<img height="{height}"', 1)
    return updated


def ensure_img_dimensions(content: str, cover_src: str | None = None) -> str:
    """
    Add width/height attributes to <img> tags when missing. This helps browsers reserve
    layout space and reduces cumulative layout shift (CLS) reported by Lighthouse.

    Rules:
    - If an img tag already has width and height attributes, leave it.
    - If the image matches the cover image src (or contains '/cover'), add width=1000 height=420.
    - Otherwise add a conservative default width=800 height=450.
    """
    if not content:
        return content

    def _replacer(match: re.Match[str]) -> str:
        tag = match.group(0)
        if _img_tag_has_dimensions(tag):
            return tag

        src_match = re.search(r"\bsrc\s*=\s*(['\"])(.*?)\1", tag, flags=re.IGNORECASE)
        src_val = src_match.group(2) if src_match else ""
        width, height = _choose_img_size_for_src(src_val=src_val, cover_src=cover_src)
        return _add_img_dimensions_to_tag(tag=tag, width=width, height=height)

    return re.sub(r"<img\b[^>]*>", _replacer, content, flags=re.IGNORECASE)


class Post:
    def __init__(self, api_data):
        # Store the original API data for AI optimization
        self.api_data = api_data

        self.title = api_data.get("title", "Untitled")
        self.link = api_data.get("url", HOME)
        self.date = api_data.get("published_at", "")
        self.content_html = api_data.get("body_html", "")

        # Use the API's description as-is
        self.description = (api_data.get("description", "") or "").strip()

        # Capture cover image for banner display
        self.cover_image = api_data.get("cover_image", "")

        # Extract author from user data in API response
        user_data = api_data.get("user", {})
        self.author = user_data.get("name") or user_data.get("username") or DEVTO_USERNAME

        # Capture tags from Dev.to API and normalize to array
        # Try tag_list first (Dev.to standard), fallback to tags field
        tags_raw = api_data.get("tag_list") or api_data.get("tags", [])
        self.tags = self._normalize_tags(tags_raw)

        # Extract the full slug from the URL instead of using the API's slug field
        # Dev.to URLs have format: https://dev.to/username/full-slug-with-id
        if self.link and "//" in self.link:
            try:
                # Extract the path part after the username
                url_path = self.link.split("//")[1]  # Remove protocol
                path_parts = url_path.split("/")
                if len(path_parts) >= 3:  # domain, username, slug
                    raw_slug = path_parts[2]  # The full slug with ID
                    sanitized = sanitize_slug(raw_slug, max_length=120)
                    self.slug = sanitized or slugify(self.title) or "post"
                else:
                    self.slug = sanitize_filename(api_data.get("slug", slugify(self.title) or "post"))
            except Exception:
                self.slug = sanitize_filename(api_data.get("slug", slugify(self.title) or "post"))
        else:
            self.slug = sanitize_filename(api_data.get("slug", slugify(self.title) or "post"))

    def _normalize_tags(self, tags):
        """
        Normalize tags to always be a list of strings.
        Handles various input formats from Dev.to API or JSON data.
        """
        if not tags:
            return []

        # Already a list - clean and return
        if isinstance(tags, list):
            return [str(tag).strip() for tag in tags if tag and str(tag).strip()]

        # String format - try different separators
        if isinstance(tags, str):
            tags = tags.strip()
            if not tags:
                return []

            # Try comma separation first (most common)
            if "," in tags:
                return [tag.strip() for tag in tags.split(",") if tag.strip()]

            # Try space separation
            if " " in tags:
                return [tag.strip() for tag in tags.split() if tag.strip()]

            # Single tag
            return [tags]

        # Fallback - convert to string and try again
        return self._normalize_tags(str(tags))

    def to_dict(self):
        """Convert Post to dictionary for JSON serialization"""
        # Ensure date is a string (ISO if possible)
        date_val = self.date
        if isinstance(self.date, datetime):
            date_val = self.date.isoformat()
        return {
            "title": self.title,
            "link": self.link,
            "date": date_val,
            "content_html": self.content_html,
            "description": self.description,
            "slug": self.slug,
            "cover_image": self.cover_image,
            "tags": self.tags,
            "author": getattr(self, "author", DEVTO_USERNAME),
            "api_data": getattr(self, "api_data", {}),  # Store original API data
        }

    @classmethod
    def from_dict(cls, data):
        """Create Post from dictionary loaded from JSON"""
        post = cls.__new__(cls)
        post.title = data["title"]
        post.link = data["link"]
        post.date = data["date"]
        post.content_html = data["content_html"]
        post.description = data["description"]
        post.slug = data["slug"]
        post.cover_image = data.get("cover_image", "")  # Handle legacy data without cover_image
        post.tags = post._normalize_tags(data.get("tags", []))  # Handle legacy data without tags and normalize
        post.author = data.get("author", DEVTO_USERNAME)  # Handle legacy data without author
        post.api_data = data.get("api_data", {})  # Restore original API data
        return post


def load_comment_manifest(path="comments.txt"):
    """Read lines of: URL | optional context (one line)."""
    items = []
    p = pathlib.Path(path)
    if not p.exists():
        return items
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        url, *ctx = [s.strip() for s in line.split("|", 1)]
        context = ctx[0] if ctx else ""
        # get a stable id from /comment/<id> or #comment-<id>, else slug of URL
        m = re.search(r"/comment/([A-Za-z0-9]+)", url) or re.search(r"#comment-([A-Za-z0-9_-]+)", url)
        cid = m.group(1) if m else slugify(url)[:48]
        # Sanitize only the filename component (cid) to prevent path traversal
        sanitized_cid = sanitize_filename(cid)
        local = f"comments/{sanitized_cid}.html"
        # short label for index
        label = context or url
        if len(label) > 80:
            label = label[:77] + "..."
        items.append({"url": url, "context": context, "local": local, "text": label})
    return items


def load_existing_posts(path=POSTS_DATA_FILE):
    """Load existing posts from JSON file"""
    p = pathlib.Path(path)
    if not p.exists():
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            posts_data = json.load(f)
            # Convert dicts to Post instances (avoid re-parsing RSS entries)
            return [Post.from_dict(post_dict) for post_dict in posts_data]
    except (json.JSONDecodeError, KeyError):
        return []


def save_posts_data(posts, path=POSTS_DATA_FILE):
    """Save posts to JSON file"""
    posts_data = [post.to_dict() if hasattr(post, "to_dict") else post for post in posts]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)


def is_first_run():
    """Check if this is the first run by looking for posts_data.json"""
    return not pathlib.Path(POSTS_DATA_FILE).exists()


def find_new_posts(api_articles, existing_posts):
    """Find new posts from the API that aren't in existing posts."""
    existing_links = {post["link"] for post in existing_posts}
    new_posts = [Post(article) for article in api_articles if article["url"] not in existing_links]
    return new_posts


# ----------------------------
# Build posts (incremental updates)
# ----------------------------
# Check if we should force a full regeneration
force_full_regen = os.getenv("FORCE_FULL_REGEN", "").lower() in ("true", "1", "yes")

if force_full_regen:
    print("FORCE_FULL_REGEN is set - performing full regeneration...")
    last_run_timestamp = None
else:
    last_run_timestamp = get_last_run_timestamp()

# Load existing posts from previous runs (in CI this may be restored from gh-pages)
existing_posts_data = load_existing_posts()
existing_links = {getattr(p, "link", "") for p in existing_posts_data}

fetch_result = fetch_all_articles_from_api(last_run_timestamp)

if fetch_result.no_new_posts:
    print("No new posts to process. Exiting.")
    # Still update the timestamp to avoid re-checking the same period
    set_last_run_timestamp()
    mark_no_new_posts()
    sys.exit(0)

candidate_posts = [Post(article) for article in fetch_result.articles]

if force_full_regen and fetch_result.success and fetch_result.source == "api":
    truly_new_posts = candidate_posts
    all_posts_data = [p.to_dict() for p in candidate_posts]
else:
    # Filter out posts that already exist
    truly_new_posts = [p for p in candidate_posts if getattr(p, "link", "") not in existing_links]

    # Combine all posts: existing + truly new (as dicts)
    all_posts_data = [p.to_dict() for p in existing_posts_data]
    all_posts_data.extend([p.to_dict() for p in truly_new_posts])

# Deduplicate and sort all posts by date, newest first
all_posts_data = dedupe_posts_by_link(all_posts_data)

# Convert dicts back to Post objects for rendering
all_posts = [Post.from_dict(p) for p in all_posts_data]

if truly_new_posts:
    print(f"Found {len(truly_new_posts)} new posts. Total posts: {len(all_posts)}")
else:
    if all_posts:
        print(f"No new posts found. Using {len(all_posts)} existing posts.")
    else:
        print("No posts found (new or existing). Generating an empty site.")

site_author = all_posts[0].author if all_posts else DEVTO_USERNAME


# Generate (or regenerate) HTML files for all posts and ensure the
# page <link rel="canonical"> matches the feed-provided URL saved in
# posts_data.json (RSS is source-of-truth).
for p in all_posts:
    # Use the feed-provided link as canonical. Fall back to a Dev.to
    # constructed URL only if link is falsy for some reason.
    canonical = getattr(p, "link", None) or f"https://dev.to/{DEVTO_USERNAME}/{p.slug}"

    # Use cover image as social image, fallback to default banner
    social_image = p.cover_image or f"{HOME}assets/devto-mirror.jpg"

    # Apply AI optimizations if available
    optimization_data = {}
    cross_references = {}

    if ai_manager:
        try:
            # Get AI optimization data for this post
            optimization_data = ai_manager.optimize_post(p, all_posts=all_posts)

            # Get cross-reference data using the cross-reference functions
            cross_references = enhance_post_with_cross_references(p, all_posts)

            print(f"Applied AI optimizations to: {p.slug}")
        except Exception as e:
            logging.warning(f"AI optimization failed for post {p.slug}: {e}")
            # Continue with graceful fallback - no optimization data

    # Ensure images have dimensions and improve color contrast in inline styles in content
    content_html = p.content_html or ""
    content_html = ensure_img_dimensions(content_html or "", p.cover_image or "")
    # Replace low-contrast color used in some Dev.to content (heuristic)
    content_html = content_html.replace("color: #868e96", "color: #495057")

    html_out = PAGE_TMPL.render(
        title=p.title,
        canonical=canonical,
        description=html.escape(p.description or ""),
        date=p.date,
        content=sanitize_html_content(content_html or ""),
        cover_image=p.cover_image,
        tags=getattr(p, "tags", []),
        social_image=social_image,
        site_name=f"{DEVTO_USERNAME}—Dev.to Mirror",
        author=p.author,
        enhanced_metadata=optimization_data.get("enhanced_metadata", {}),
        json_ld_schemas=optimization_data.get("json_ld_schemas", []),
        cross_references=cross_references,
    )
    safe_slug = sanitize_slug(p.slug, max_length=120)
    (POSTS_DIR / f"{safe_slug}.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote: {p.slug}.html (canonical: {canonical})")

# Save the updated posts data for next run
save_posts_data(all_posts_data)

# Update the timestamp for the next run only if we successfully checked the API.
if fetch_result.success:
    set_last_run_timestamp()

# ----------------------------
# Build minimal comment pages (optional)
# ----------------------------
comment_items = load_comment_manifest()
if comment_items:
    pathlib.Path("comments").mkdir(exist_ok=True)
    for c in comment_items:
        title = "Comment note"
        desc = (c["context"] or "Comment note").strip()[:300]

        # Default social image
        social_image = f"{HOME}assets/devto-mirror.jpg"

        # For comment notes, canonical should point back to the original Dev.to URL
        html_page = COMMENT_NOTE_TMPL.render(
            title=html.escape(title),
            canonical=c["url"],
            description=html.escape(desc),
            context=html.escape(c["context"]) if c["context"] else "",
            url=c["url"],
            social_image=social_image,
            site_name=f"{DEVTO_USERNAME}—Dev.to Mirror",
            author=site_author,
            enhanced_metadata={},  # Comments don't have enhanced metadata yet
        )
        # Ensure local path is safe. Re-sanitize the filename component to be defensive
        # (load_comment_manifest already attempts sanitization, but double-check here).
        orig_filename = os.path.basename(c["local"])
        name, ext = os.path.splitext(orig_filename)
        sanitized_local = sanitize_filename(name) + ext
        local_path = validate_safe_path(pathlib.Path("comments"), sanitized_local)
        resolved_path = local_path.resolve()
        comments_dir = pathlib.Path("comments").resolve()
        if not str(resolved_path).startswith(str(comments_dir) + os.sep):
            raise ValueError(f"Path traversal detected in comment local path: {c['local']}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(html_page, encoding="utf-8")


devto_profile = f"https://dev.to/{DEVTO_USERNAME}"
site_description = (
    f"Mirror of {DEVTO_USERNAME}'s Dev.to blog posts. "
    "Canonical lives on Dev.to. This is just a crawler-friendly mirror."
)
social_image = f"{HOME}assets/devto-mirror.jpg"

index_html = INDEX_TMPL.render(
    username=DEVTO_USERNAME,
    posts=all_posts,
    comments=comment_items,
    home=HOME,
    canonical=devto_profile,
    site_description=site_description,
    social_image=social_image,
)
pathlib.Path("index.html").write_text(index_html, encoding="utf-8")

# Generate sitemap - use AI-optimized version if available
sitemap_content = None
if ai_manager:
    try:
        sitemap_content = ai_manager.generate_optimized_sitemap(all_posts, comment_items)
        if sitemap_content:
            print("Generated AI-optimized sitemap")
    except Exception as e:
        logging.warning(f"AI sitemap generation failed: {e}")

# Fallback to standard sitemap if AI optimization failed or unavailable
if not sitemap_content:
    sitemap_content = SITEMAP_TMPL.render(home=HOME, posts=all_posts, comments=comment_items)
    print("Generated standard sitemap")

pathlib.Path("sitemap.xml").write_text(sitemap_content, encoding="utf-8")

# Generated with the help of ChatGPT

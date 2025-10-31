import html
import json
import logging
import os
import pathlib
import re
import time
from datetime import datetime, timezone

import bleach
import requests
from dotenv import load_dotenv
from jinja2 import Environment, select_autoescape
from slugify import slugify
from utils import INDEX_TMPL, SITEMAP_TMPL, dedupe_posts_by_link, get_post_template

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
PAGES_REPO = os.getenv("PAGES_REPO", "").strip()  # "user/repo"
LAST_RUN_FILE = "last_run.txt"
POSTS_DATA_FILE = "posts_data.json"
VALIDATION_MODE = os.getenv("VALIDATION_MODE", "").lower() in ("true", "1", "yes")

# Filename sanitization pattern - prevents path traversal and unsafe characters
SAFE_FILENAME_PATTERN = r"[^A-Za-z0-9_-]"

if not DEVTO_USERNAME:
    raise ValueError("Missing DEVTO_USERNAME (your Dev.to username)")
if "/" not in PAGES_REPO:
    raise ValueError("Invalid PAGES_REPO (expected 'user/repo')")

username, repo = PAGES_REPO.split("/")
HOME = f"https://{username}.github.io/{repo}/"

ROOT = pathlib.Path(".")
POSTS_DIR = ROOT / "posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize AI optimization manager
ai_manager = None
if AI_OPTIMIZATION_AVAILABLE:
    try:
        site_name = f"{DEVTO_USERNAME} — Dev.to Mirror"
        ai_manager = create_default_ai_optimization_manager(site_name, HOME)
        logging.info("AI optimization manager initialized successfully")
    except Exception as e:
        logging.warning(f"Failed to initialize AI optimization manager: {e}")
        ai_manager = None


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


def _fetch_article_pages(last_run_iso=None):
    """Return a list of article summary objects from the paginated API.
    This helper keeps the pagination logic isolated to reduce cognitive
    complexity in the public function.
    """
    articles = []
    page = 1
    api_base = "https://dev.to/api/articles"
    while True:
        print(f"Fetching page {page} of articles...")

        params = {"username": DEVTO_USERNAME, "page": page}
        if page > 1:
            params["per_page"] = 100
        if page == 1:
            params["_cb"] = time.time() // 60

        response = requests.get(api_base, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data:
            break

        if last_run_iso:
            last_run_dt = datetime.fromisoformat(last_run_iso)
            new_articles = [
                article
                for article in data
                if datetime.fromisoformat(article["published_at"].replace("Z", "+00:00")) > last_run_dt
            ]
            articles.extend(new_articles)
            if len(data) < 100 or len(new_articles) < len(data):
                break
        else:
            articles.extend(data)

        page += 1

    return articles


def _fetch_full_articles(articles):
    """Fetch full article content for each article (needed for body_html).
    Kept separate so the pagination implementation remains easy to reason about.
    """
    print(f"Found {len(articles)} articles, fetching full content...")
    full_articles = []
    for i, article in enumerate(articles):
        print(f"Fetching full content for article {i + 1}/{len(articles)}: {article.get('title')}")
        full_response = requests.get(f"https://dev.to/api/articles/{article['id']}", timeout=30)
        full_response.raise_for_status()
        full_articles.append(full_response.json())
        if i < len(articles) - 1:
            time.sleep(0.5)

    print(f"Found {len(full_articles)} articles with full content.")
    return full_articles


def fetch_all_articles_from_api(last_run_iso=None):
    """Public API that returns full-article objects after pagination.
    Delegates to smaller helpers to keep complexity low.
    """
    if VALIDATION_MODE:
        # Return mock data for validation
        # Uncomment the next line to test validation failure detection:
        # raise RuntimeError("Test validation failure")
        return [
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
        ]

    summaries = _fetch_article_pages(last_run_iso=last_run_iso)
    return _fetch_full_articles(summaries)


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
ROBOTS_TMPL = """# TEST robots.txt generated by scripts/generate_site.py
# This version BLOCKS half the crawlers to test if GitHub Pages respects robots.txt
# Generated at: {timestamp}

# ALLOWED CRAWLERS (should have access)
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: CCBot
Allow: /

User-agent: facebookexternalhit
Allow: /

# BLOCKED CRAWLERS (should be denied access)
User-agent: Google-Extended
Disallow: /

User-agent: Claude-Web
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: Twitterbot
Disallow: /

User-agent: LinkedInBot
Disallow: /

# All other crawlers - BLOCKED by default
User-agent: *
Disallow: /

Sitemap: {home}sitemap.xml
"""


# ----------------------------
# Helpers
# ----------------------------
def strip_html(text):
    # Remove HTML tags, collapse internal whitespace (newlines/tabs/extra spaces)
    # into single spaces, then trim leading/trailing whitespace.
    if not text:
        return ""
    no_tags = re.sub(r"<[^>]+>", "", text)
    collapsed = re.sub(r"\s+", " ", no_tags)
    return collapsed.strip()


def sanitize_html_content(content):
    """
    Basic HTML sanitization to allow common formatting tags while removing potentially harmful content.
    Uses bleach for robust sanitization.
    """
    if not content:
        return ""

    allowed_tags = [
        "p",
        "br",
        "strong",
        "em",
        "a",
        "code",
        "pre",
        "blockquote",
        "ul",
        "ol",
        "li",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "img",
    ]
    allowed_attributes = {"a": ["href"], "img": ["src", "alt"]}
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes)


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
                    self.slug = path_parts[2]  # The full slug with ID
                else:
                    self.slug = api_data.get("slug", slugify(self.title) or "post")
            except Exception:
                self.slug = api_data.get("slug", slugify(self.title) or "post")
        else:
            self.slug = api_data.get("slug", slugify(self.title) or "post")

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
        sanitized_cid = re.sub(SAFE_FILENAME_PATTERN, "-", cid)
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

api_articles = fetch_all_articles_from_api(last_run_timestamp)

# Convert API articles to Post objects
new_posts = [Post(article) for article in api_articles]

if not new_posts:
    print("No new posts to process. Exiting.")
    # Still update the timestamp to avoid re-checking the same period
    set_last_run_timestamp()
    exit()

# Load existing posts from previous runs
existing_posts_data = load_existing_posts()

# Create a set of existing post URLs for faster lookup
existing_links = {getattr(p, "link", "") for p in existing_posts_data}

# Filter out new posts that already exist
truly_new_posts = []
for post in new_posts:
    if post.link not in existing_links:
        truly_new_posts.append(post)

# Combine all posts: existing + truly new
all_posts_data = existing_posts_data.copy()
for post in truly_new_posts:
    all_posts_data.append(post.to_dict())

# Deduplicate and sort all posts by date, newest first
all_posts_data = dedupe_posts_by_link(all_posts_data)

# Convert dicts back to Post objects for rendering
all_posts = [Post.from_dict(p) for p in all_posts_data]

print(f"Found {len(truly_new_posts)} new posts. Total posts: {len(all_posts)}")


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

    html_out = PAGE_TMPL.render(
        title=p.title,
        canonical=canonical,
        description=html.escape(p.description or ""),
        date=p.date,
        content=sanitize_html_content(p.content_html or ""),
        cover_image=p.cover_image,
        tags=getattr(p, "tags", []),
        social_image=social_image,
        site_name=f"{DEVTO_USERNAME} — Dev.to Mirror",
        author=DEVTO_USERNAME,
        enhanced_metadata=optimization_data.get("enhanced_metadata", {}),
        json_ld_schemas=optimization_data.get("json_ld_schemas", []),
        cross_references=cross_references,
    )
    # Prevent path traversal or unsafe filenames in slugs
    safe_slug = re.sub(SAFE_FILENAME_PATTERN, "-", p.slug)[:120]
    # Periods are not allowed; this prevents path traversal via '..' or similar.
    # No further sanitization needed.
    (POSTS_DIR / f"{safe_slug}.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote: {p.slug}.html (canonical: {canonical})")

# Save the updated posts data for next run
save_posts_data(all_posts_data)

# Update the timestamp for the next run
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
            site_name=f"{DEVTO_USERNAME} — Dev.to Mirror",
            author=DEVTO_USERNAME,
            enhanced_metadata={},  # Comments don't have enhanced metadata yet
        )
        # Ensure local path is safe. Re-sanitize the filename component to be defensive
        # (load_comment_manifest already attempts sanitization, but double-check here).
        orig_filename = os.path.basename(c["local"])
        name, ext = os.path.splitext(orig_filename)
        sanitized_name = re.sub(SAFE_FILENAME_PATTERN, "-", name)
        sanitized_local = sanitized_name + ext
        local_path = pathlib.Path("comments") / sanitized_local
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
pathlib.Path("robots.txt").write_text(
    ROBOTS_TMPL.format(home=HOME, timestamp=datetime.now(timezone.utc).isoformat()), encoding="utf-8"
)

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

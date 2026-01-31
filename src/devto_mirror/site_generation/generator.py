import html
import json
import logging
import os
import pathlib
import re
import sys
from datetime import datetime

import bleach
from dotenv import load_dotenv
from jinja2 import Environment, select_autoescape
from slugify import slugify

from devto_mirror.core.article_fetcher import fetch_all_articles_from_api
from devto_mirror.core.constants import POSTS_DATA_FILE
from devto_mirror.core.html_sanitization import sanitize_html_content
from devto_mirror.core.path_utils import sanitize_filename, sanitize_slug, validate_safe_path
from devto_mirror.core.run_state import get_last_run_timestamp, mark_no_new_posts, set_last_run_timestamp
from devto_mirror.core.utils import INDEX_TMPL, SITEMAP_TMPL, dedupe_posts_by_link, get_post_template

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
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "").strip()
LAST_RUN_FILE = "last_run.txt"
NO_NEW_POSTS_FILE = "no_new_posts.flag"
VALIDATION_MODE = os.getenv("VALIDATION_MODE", "").lower() in ("true", "1", "yes")

if not VALIDATION_MODE:
    if not DEVTO_USERNAME:
        raise ValueError("Missing DEVTO_USERNAME (your Dev.to username)")

    # When not running in validation mode require either SITE_DOMAIN or GH_USERNAME
    if not SITE_DOMAIN and not GH_USERNAME:
        raise ValueError("Missing SITE_DOMAIN or GH_USERNAME")

if SITE_DOMAIN:
    HOME = f"https://{SITE_DOMAIN}/"
    ROOT_HOME = HOME
else:
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


"""(fetching logic moved to src/devto_mirror/article_fetcher.py)"""


# ----------------------------
# Templates (posts + index)
# ----------------------------
env = Environment(autoescape=select_autoescape(["html", "xml"]))

# Get the post template (from file or inline fallback)
PAGE_TMPL = get_post_template()

COMMENT_NOTE_TMPL = env.from_string("""<!doctype html><html lang="en"><head>
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
""")


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
            "id": (getattr(self, "api_data", {}) or {}).get("id") or 0,
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


def _should_force_full_regen() -> bool:
    return os.getenv("FORCE_FULL_REGEN", "").lower() in ("true", "1", "yes")


def _determine_last_run_timestamp(*, force_full_regen: bool) -> str | None:
    if force_full_regen:
        print("FORCE_FULL_REGEN is set - performing full regeneration...")
        return None
    return get_last_run_timestamp(LAST_RUN_FILE)


def _existing_slug_by_id(existing_posts_data: list["Post"]) -> dict[int, str]:
    slug_by_id: dict[int, str] = {}
    for _p in existing_posts_data:
        post_id = _post_id(_p)
        if post_id:
            slug_by_id[post_id] = getattr(_p, "slug", "")
    return slug_by_id


def _post_id(post: "Post") -> int:
    api_data = getattr(post, "api_data", {}) or {}
    try:
        return int(api_data.get("id") or 0)
    except (TypeError, ValueError):
        return 0


def _handle_no_new_posts_exit() -> None:
    print("No new posts to process. Exiting.")
    # Still update the timestamp to avoid re-checking the same period
    set_last_run_timestamp(LAST_RUN_FILE)
    mark_no_new_posts(marker_path=NO_NEW_POSTS_FILE)
    sys.exit(0)


def _merge_posts(
    *,
    existing_posts_data: list["Post"],
    candidate_posts: list["Post"],
    force_full_regen: bool,
    fetch_success: bool,
    fetch_source: str,
) -> tuple[list["Post"], list[dict]]:
    if force_full_regen and fetch_success and fetch_source == "api":
        delta_posts = candidate_posts
        all_posts_data = [p.to_dict() for p in candidate_posts]
    else:
        # Incremental mode: candidate_posts are "new or updated since last run".
        # Merge them into the existing store and let the deduper pick the latest version.
        delta_posts = candidate_posts
        all_posts_data = [p.to_dict() for p in existing_posts_data]
        all_posts_data.extend([p.to_dict() for p in delta_posts])
    return delta_posts, all_posts_data


def _log_post_summary(*, delta_posts: list["Post"], all_posts: list["Post"]) -> None:
    if delta_posts:
        print(f"Found {len(delta_posts)} new/updated posts. Total posts: {len(all_posts)}")
        return

    if all_posts:
        print(f"No new posts found. Using {len(all_posts)} existing posts.")
        return

    print("No posts found (new or existing). Generating an empty site.")


def _canonical_for_post(post: "Post") -> str:
    # Use the feed-provided link as canonical. Fall back to a Dev.to constructed
    # URL only if link is falsy for some reason.
    return getattr(post, "link", None) or f"https://dev.to/{DEVTO_USERNAME}/{post.slug}"


def _social_image_for_post(post: "Post") -> str:
    # Use cover image as social image, fallback to default banner
    return post.cover_image or f"{HOME}assets/devto-mirror.jpg"


def _try_ai_enhancements(post: "Post", all_posts: list["Post"]) -> tuple[dict, dict]:
    if not ai_manager:
        return {}, {}
    try:
        optimization_data = ai_manager.optimize_post(post, all_posts=all_posts)
        cross_references = enhance_post_with_cross_references(post, all_posts)
        print(f"Applied AI optimizations to: {post.slug}")
        return optimization_data, cross_references
    except Exception as e:
        logging.warning(f"AI optimization failed for post {post.slug}: {e}")
        return {}, {}


def _renderable_content_html(post: "Post") -> str:
    # Ensure images have dimensions and improve color contrast in inline styles in content
    content_html = post.content_html or ""
    content_html = ensure_img_dimensions(content_html or "", post.cover_image or "")
    # Replace low-contrast color used in some Dev.to content (heuristic)
    return content_html.replace("color: #868e96", "color: #495057")


def _maybe_remove_old_slug_file(*, post: "Post", new_safe_slug: str, existing_slug_by_id: dict[int, str]) -> None:
    post_id = _post_id(post)
    if not post_id:
        return

    old_slug = existing_slug_by_id.get(post_id) or ""
    if not old_slug:
        return

    old_safe_slug = sanitize_slug(old_slug, max_length=120)
    if old_safe_slug == new_safe_slug:
        return

    old_path = POSTS_DIR / f"{old_safe_slug}.html"
    if old_path.exists():
        old_path.unlink()
        print(f"Removed old slug file for {post_id}: {old_safe_slug}.html")


def _write_post_html(
    *,
    post: "Post",
    canonical: str,
    social_image: str,
    optimization_data: dict,
    cross_references: dict,
) -> None:
    html_out = PAGE_TMPL.render(
        title=post.title,
        canonical=canonical,
        description=html.escape(post.description or ""),
        date=post.date,
        content=sanitize_html_content(_renderable_content_html(post) or ""),
        cover_image=post.cover_image,
        tags=getattr(post, "tags", []),
        social_image=social_image,
        site_name=f"{DEVTO_USERNAME}—Dev.to Mirror",
        author=post.author,
        enhanced_metadata=optimization_data.get("enhanced_metadata", {}),
        json_ld_schemas=optimization_data.get("json_ld_schemas", []),
        cross_references=cross_references,
    )
    safe_slug = sanitize_slug(post.slug, max_length=120)
    (POSTS_DIR / f"{safe_slug}.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote: {post.slug}.html (canonical: {canonical})")


def _write_comment_notes(*, comment_items: list[dict], site_author: str) -> None:
    if not comment_items:
        return

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


def _write_index_page(*, all_posts: list["Post"], comment_items: list[dict]) -> None:
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


def _write_sitemap(*, all_posts: list["Post"], comment_items: list[dict]) -> None:
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


# ----------------------------
# Build posts (incremental updates)
# ----------------------------
def main():
    force_full_regen = _should_force_full_regen()
    last_run_timestamp = _determine_last_run_timestamp(force_full_regen=force_full_regen)

    # Load existing posts from previous runs (in CI this may be restored from gh-pages)
    existing_posts_data = load_existing_posts()
    existing_slug_by_id = _existing_slug_by_id(existing_posts_data)

    fetch_result = fetch_all_articles_from_api(
        username=DEVTO_USERNAME,
        last_run_iso=last_run_timestamp,
        posts_data_path=POSTS_DATA_FILE,
        validation_mode=VALIDATION_MODE,
    )

    if fetch_result.no_new_posts:
        _handle_no_new_posts_exit()

    candidate_posts = [Post(article) for article in fetch_result.articles]

    delta_posts, all_posts_data = _merge_posts(
        existing_posts_data=existing_posts_data,
        candidate_posts=candidate_posts,
        force_full_regen=force_full_regen,
        fetch_success=fetch_result.success,
        fetch_source=fetch_result.source,
    )

    # Deduplicate and sort all posts by date, newest first
    all_posts_data = dedupe_posts_by_link(all_posts_data)

    # Convert dicts back to Post objects for rendering
    all_posts = [Post.from_dict(p) for p in all_posts_data]

    _log_post_summary(delta_posts=delta_posts, all_posts=all_posts)

    site_author = all_posts[0].author if all_posts else DEVTO_USERNAME

    # Generate (or regenerate) HTML files for all posts and ensure the
    # page <link rel="canonical"> matches the feed-provided URL saved in
    # posts_data.json (RSS is source-of-truth).
    for p in all_posts:
        canonical = _canonical_for_post(p)
        social_image = _social_image_for_post(p)
        optimization_data, cross_references = _try_ai_enhancements(p, all_posts)
        safe_slug = sanitize_slug(p.slug, max_length=120)

        # If a post's slug changes on DEV (URL change), avoid leaving a stale orphan file behind.
        _maybe_remove_old_slug_file(post=p, new_safe_slug=safe_slug, existing_slug_by_id=existing_slug_by_id)
        _write_post_html(
            post=p,
            canonical=canonical,
            social_image=social_image,
            optimization_data=optimization_data,
            cross_references=cross_references,
        )

    # Save the updated posts data for next run
    save_posts_data(all_posts_data)

    # Update the timestamp for the next run only if we successfully checked the API.
    if fetch_result.success:
        set_last_run_timestamp(LAST_RUN_FILE)

    # ----------------------------
    # Build minimal comment pages (optional)
    # ----------------------------
    comment_items = load_comment_manifest()
    _write_comment_notes(comment_items=comment_items, site_author=site_author)
    _write_index_page(all_posts=all_posts, comment_items=comment_items)
    _write_sitemap(all_posts=all_posts, comment_items=comment_items)


if __name__ == "__main__":
    main()

# Generated with the help of ChatGPT

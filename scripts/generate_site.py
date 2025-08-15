import os, pathlib, re, html, json
import feedparser
from slugify import slugify
from jinja2 import Template
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

DEVTO_USERNAME = os.getenv("DEVTO_USERNAME", "").strip()
PAGES_REPO = os.getenv("PAGES_REPO", "").strip()  # "user/repo"

assert DEVTO_USERNAME, "Missing DEVTO_USERNAME (your Dev.to username)"
assert "/" in PAGES_REPO, "Invalid PAGES_REPO (expected 'user/repo')"

username, repo = PAGES_REPO.split("/")
HOME = f"https://{username}.github.io/{repo}/"

ROOT = pathlib.Path(".")
POSTS_DIR = ROOT / "posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

FEED_URL = f"https://dev.to/feed/{DEVTO_USERNAME}"
try:
    feed = feedparser.parse(FEED_URL)
    if hasattr(feed, 'bozo') and feed.bozo:
        print(f"Warning: RSS feed parsing issue: {getattr(feed, 'bozo_exception', 'Unknown error')}")
        # For testing purposes, continue with empty feed
    if not hasattr(feed, 'entries') or not feed.entries:
        print("No entries found in RSS feed")
except Exception as e:
    print(f"Error fetching RSS feed: {e}")
    # Create an empty feed for testing
    class MockFeed:
        def __init__(self):
            self.entries = []
    feed = MockFeed()

# ----------------------------
# Templates (posts + index)
# ----------------------------
PAGE_TMPL = Template("""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<title>{{ title }}</title>
<link rel="canonical" href="{{ canonical }}">
<meta name="description" content="{{ description }}">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body>
<main>
  <h1><a href="{{ canonical }}">{{ title }}</a></h1>
  {% if date %}<p><em>Published: {{ date }}</em></p>{% endif %}
  <article>{{ content }}</article>
  <p><a href="{{ canonical }}">Read on Dev.to →</a></p>
</main>
</body></html>
""")

INDEX_TMPL = Template("""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<title>{{ username }} — Dev.to Mirror</title>
<link rel="canonical" href="{{ canonical }}">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body>
<main>
  <h1>{{ username }} — Dev.to Mirror</h1>
  <ul>
  {% for p in posts %}
    <li><a href="posts/{{ p.slug }}.html">{{ p.title }}</a> — <small>{{ p.date }}</small></li>
  {% endfor %}
  </ul>
  {% if comments %}<h2>Comment Notes</h2>
  <ul>
  {% for c in comments %}
    <li><a href="{{ c.local }}">{{ c.text }}</a></li>
  {% endfor %}
  </ul>{% endif %}
  <p>Canonical lives on Dev.to. This is just a crawler-friendly mirror.</p>
</main>
</body></html>
""")

# ----------------------------
# Minimal comment notes (no scraping)
# ----------------------------
COMMENT_NOTE_TMPL = Template("""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<title>{{ title }}</title>
<link rel="canonical" href="{{ canonical }}">
<meta name="description" content="{{ description }}">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
ROBOTS_TMPL = """User-agent: *
Allow: /

# AI crawlers (toggle as needed)
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

Sitemap: {home}sitemap.xml
"""

SITEMAP_TMPL = Template("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{{ home }}</loc></url>
  {% for p in posts %}
    {# Prefer canonical Dev.to link if available #}
    <url><loc>{{ p.link or (home + 'posts/' + p.slug + '.html') }}</loc></url>
  {% endfor %}
  {% for c in comments %}
    <url><loc>{{ c.url or (home + c.local) }}</loc></url>
  {% endfor %}
</urlset>
""")

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

class Post:
    def __init__(self, entry):
        self.title = getattr(entry, "title", "Untitled")
        self.link = getattr(entry, "link", HOME)
        # Normalize date to ISO 8601 if possible; fall back to raw string
        raw_date = getattr(entry, "published", "") or getattr(entry, "updated", "") or ""
        iso_date = ""
        try:
            # feedparser may provide a parsed time tuple
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                iso_date = datetime(*entry.published_parsed[:6]).isoformat() + "Z"
            elif raw_date:
                # Try RFC-style parsing first, then ISO
                try:
                    dt = parsedate_to_datetime(raw_date)
                    iso_date = dt.isoformat()
                except Exception:
                    try:
                        iso_date = datetime.fromisoformat(raw_date).isoformat()
                    except Exception:
                        iso_date = raw_date
        except Exception:
            iso_date = raw_date
        self.date = iso_date
        # Prefer full content, then summary, then empty
        if getattr(entry, "content", None):
            content_html = entry.content[0].value
        elif getattr(entry, "summary", None):
            content_html = entry.summary
        else:
            content_html = ""
        self.content_html = content_html

        # Attempt to extract a special HTML comment description from the content
        # Format: <!-- description: Your description here -->
        desc_match = re.search(r"<!--\s*description:\s*(.*?)-->", content_html, re.IGNORECASE | re.DOTALL)
        if desc_match:
            desc_text = strip_html(desc_match.group(1))
        else:
            # Prefer entry.description if present, otherwise fall back to stripped content_html
            raw_desc = getattr(entry, "description", "") or content_html
            desc_text = strip_html(raw_desc)

        # Ensure description is trimmed and then truncated to 300 chars
        desc_text = (desc_text or "").strip()
        self.description = desc_text[:300]
        self.slug = (slugify(self.title)[:80] or slugify(self.link)) or "post"

    def to_dict(self):
        """Convert Post to dictionary for JSON serialization"""
        # Ensure date is a string (ISO if possible)
        date_val = self.date
        if isinstance(self.date, datetime):
            date_val = self.date.isoformat()
        return {
            'title': self.title,
            'link': self.link,
            'date': date_val,
            'content_html': self.content_html,
            'description': self.description,
            'slug': self.slug
        }

    @classmethod
    def from_dict(cls, data):
        """Create Post from dictionary loaded from JSON"""
        post = cls.__new__(cls)
        post.title = data['title']
        post.link = data['link']
        post.date = data['date']
        post.content_html = data['content_html']
        post.description = data['description']
        post.slug = data['slug']
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
        local = f"comments/{cid}.html"
        # short label for index
        label = (context or url)
        if len(label) > 80:
            label = label[:77] + "..."
        items.append({"url": url, "context": context, "local": local, "text": label})
    return items

def load_existing_posts(path="posts_data.json"):
    """Load existing posts from JSON file"""
    p = pathlib.Path(path)
    if not p.exists():
        return []
    try:
        with open(p, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
            # Convert dicts to Post instances (avoid re-parsing RSS entries)
            return [Post.from_dict(post_dict) for post_dict in posts_data]
    except (json.JSONDecodeError, KeyError):
        return []


def _parse_date_str(datestr):
    """Try to parse a date string from RFC or ISO formats. Returns a timezone-aware
    datetime when possible, otherwise None."""
    if not datestr:
        return None
    # If it's already a datetime, return
    if isinstance(datestr, datetime):
        return datestr
    s = str(datestr).strip()
    try:
        # handle trailing Z
        if s.endswith('Z'):
            s2 = s.replace('Z', '+00:00')
            return datetime.fromisoformat(s2)
    except Exception:
        pass
    try:
        return parsedate_to_datetime(s)
    except Exception:
        pass
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def save_posts_data(posts, path="posts_data.json"):
    """Save posts to JSON file"""
    posts_data = [post.to_dict() for post in posts]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)

def is_first_run():
    """Check if this is the first run by looking for posts_data.json"""
    return not pathlib.Path("posts_data.json").exists()

def find_new_posts(rss_posts, existing_posts):
    """Find new posts from RSS that aren't in existing posts.
    Since RSS posts are ordered by date (newest first), we can stop
    when we find a post that already exists.
    """
    # If no existing posts, everything is new
    if not existing_posts:
        return rss_posts

    # Build a map of existing links for fast lookup
    existing_links = {post.link: post for post in existing_posts}

    new_posts = []
    for post in rss_posts:
        # If this link exists, compare dates and keep the newest in existing_posts
        if post.link in existing_links:
            # We encountered a post already present; treat remaining RSS items as older
            break
        new_posts.append(post)

    return new_posts

# ----------------------------
# Build posts (incremental updates)
# ----------------------------
entries = feed.entries or []
rss_posts = [Post(e) for e in entries]

# Load existing posts from previous runs
existing_posts = load_existing_posts()

def _key_for_post_obj(post):
    # Prefer slug, otherwise last path segment of the link
    slug = getattr(post, 'slug', None)
    if slug:
        return slug.lower()
    link = getattr(post, 'link', '')
    path = urlparse(link).path
    last = path.rstrip('/').split('/')[-1]
    return (last or link).lower()

if is_first_run():
    print("First run: generating all posts from RSS feed")
    new_posts = rss_posts
    all_posts = rss_posts
else:
    print("Subsequent run: checking for new posts")
    new_posts = find_new_posts(rss_posts, existing_posts)

    # Merge by normalized key (slug or last path segment). Prefer the newest
    # post when duplicates exist. existing_posts are treated as older unless
    # their parsed date is newer.
    merged = {}

    def _add_candidate(p):
        key = _key_for_post_obj(p)
        cand_date = _parse_date_str(getattr(p, 'date', None))
        existing = merged.get(key)
        if not existing:
            merged[key] = {'post': p, 'date': cand_date}
            return
        # if existing has no date, prefer candidate if it has one
        if existing['date'] is None and cand_date is not None:
            merged[key] = {'post': p, 'date': cand_date}
            return
        if cand_date is None:
            return
        # prefer newer
        if existing['date'] is None or cand_date > existing['date']:
            merged[key] = {'post': p, 'date': cand_date}

    # Add new posts first (RSS newest), then existing posts to fill gaps
    for p in new_posts:
        _add_candidate(p)
    for p in existing_posts:
        _add_candidate(p)

    # Flatten merged mapping and sort newest-first
    all_posts = [v['post'] for k, v in sorted(merged.items(), key=lambda kv: kv[1]['date'] or datetime.min, reverse=True)]
    print(f"Found {len(new_posts)} new posts")

# Generate (or regenerate) HTML files for all posts and ensure the
# page <link rel="canonical"> matches the feed-provided URL saved in
# posts_data.json (RSS is source-of-truth).
for p in all_posts:
    # Use the feed-provided link as canonical. Fall back to a Dev.to
    # constructed URL only if link is falsy for some reason.
    canonical = getattr(p, 'link', None) or f"https://dev.to/{DEVTO_USERNAME}/{p.slug}"
    html_out = PAGE_TMPL.render(
        title=p.title,
        canonical=canonical,
        description=p.description,
        date=p.date,
        content=p.content_html
    )
    (POSTS_DIR / f"{p.slug}.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote: {p.slug}.html (canonical: {canonical})")

# Save the updated posts data for next run
# Do not overwrite feed-provided links. However, preserve existing descriptions
# when the new feed entry lacks a meaningful description.
    # Use normalized key mapping to prefer existing descriptions when present
existing_key_map = { _key_for_post_obj(ep): ep for ep in existing_posts }
for i, post in enumerate(all_posts):
    try:
        key = _key_for_post_obj(post)
        existing = existing_key_map.get(key)
        if existing:
            new_desc = (post.description or "").strip()
            if (not new_desc) or (new_desc == post.title):
                post.description = existing.description
    except Exception:
        pass

save_posts_data(all_posts)

# ----------------------------
# Build minimal comment pages (optional)
# ----------------------------
comment_items = load_comment_manifest()
if comment_items:
    pathlib.Path("comments").mkdir(exist_ok=True)
    for c in comment_items:
        title = "Comment note"
        desc = (c["context"] or "Comment note").strip()[:300]
        # For comment notes, canonical should point back to the original Dev.to URL
        html_page = COMMENT_NOTE_TMPL.render(
            title=title,
            canonical=c["url"],
            description=desc,
            context=html.escape(c["context"]) if c["context"] else "",
            url=c["url"]
        )
        pathlib.Path(c["local"]).write_text(html_page, encoding="utf-8")

# Use Dev.to profile as canonical for the index page
devto_profile = f"https://dev.to/{DEVTO_USERNAME}"
index_html = INDEX_TMPL.render(username=DEVTO_USERNAME, posts=all_posts, comments=comment_items, home=HOME, canonical=devto_profile)
pathlib.Path("index.html").write_text(index_html, encoding="utf-8")
pathlib.Path("robots.txt").write_text(ROBOTS_TMPL.format(home=HOME), encoding="utf-8")

smap = SITEMAP_TMPL.render(home=HOME, posts=all_posts, comments=comment_items)
pathlib.Path("sitemap.xml").write_text(smap, encoding="utf-8")

# Generated with the help of ChatGPT

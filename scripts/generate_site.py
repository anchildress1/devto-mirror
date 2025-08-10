import os, pathlib, re, html
import feedparser
from slugify import slugify
from jinja2 import Template

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
feed = feedparser.parse(FEED_URL)

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
<link rel="canonical" href="{{ home }}">
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
  <url><loc>{{ home }}posts/{{ p.slug }}.html</loc></url>
  {% endfor %}
  {% for c in comments %}
  <url><loc>{{ home }}{{ c.local }}</loc></url>
  {% endfor %}
</urlset>
""")

# ----------------------------
# Helpers
# ----------------------------
def strip_html(text):
    return re.sub("<[^>]+>", "", text or "").strip()

class Post:
    def __init__(self, entry):
        self.title = getattr(entry, "title", "Untitled")
        self.link = getattr(entry, "link", HOME)
        self.date = getattr(entry, "published", "")
        if getattr(entry, "content", None):
            content_html = entry.content[0].value
        elif getattr(entry, "summary", None):
            content_html = entry.summary
        else:
            content_html = ""
        self.content_html = content_html
        self.description = (getattr(entry, "subtitle", "") or strip_html(content_html))[:300]
        self.slug = (slugify(self.title)[:80] or slugify(self.link)) or "post"

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

# ----------------------------
# Build posts
# ----------------------------
entries = feed.entries or []
posts = [Post(e) for e in entries]

for p in posts:
    html_out = PAGE_TMPL.render(
        title=p.title,
        canonical=p.link,          # Canonical → Dev.to
        description=p.description,
        date=p.date,
        content=p.content_html
    )
    (POSTS_DIR / f"{p.slug}.html").write_text(html_out, encoding="utf-8")

# ----------------------------
# Build minimal comment pages (optional)
# ----------------------------
comment_items = load_comment_manifest()
if comment_items:
    pathlib.Path("comments").mkdir(exist_ok=True)
    for c in comment_items:
        title = "Comment note"
        desc = (c["context"] or "Comment note").strip()[:300]
        html_page = COMMENT_NOTE_TMPL.render(
            title=title,
            canonical=HOME + c["local"],  # self-canonical (this is your context page)
            description=desc,
            context=html.escape(c["context"]) if c["context"] else "",
            url=c["url"]
        )
        pathlib.Path(c["local"]).write_text(html_page, encoding="utf-8")

index_html = INDEX_TMPL.render(username=DEVTO_USERNAME, posts=posts, comments=comment_items, home=HOME)
pathlib.Path("index.html").write_text(index_html, encoding="utf-8")
pathlib.Path("robots.txt").write_text(ROBOTS_TMPL.format(home=HOME), encoding="utf-8")

smap = SITEMAP_TMPL.render(home=HOME, posts=posts, comments=comment_items)
pathlib.Path("sitemap.xml").write_text(smap, encoding="utf-8")

# Generated with the help of ChatGPT

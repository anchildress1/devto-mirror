import os, pathlib, re
import feedparser
from slugify import slugify
from jinja2 import Template

DEVTO_USERNAME = os.getenv("DEVTO_USERNAME", "").strip()
PAGES_REPO = os.getenv("PAGES_REPO", "").strip()  # "user/repo"

assert DEVTO_USERNAME, "Missing DEVTO_USERNAME (your Dev.to username)"
assert "/" in PAGES_REPO, "Invalid PAGES_REPO (expected 'user/repo')"

# Derive GitHub Pages home URL
username, repo = PAGES_REPO.split("/")
HOME = f"https://{username}.github.io/{repo}/"

ROOT = pathlib.Path(".")
POSTS_DIR = ROOT / "posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

FEED_URL = f"https://dev.to/feed/{DEVTO_USERNAME}"
feed = feedparser.parse(FEED_URL)

PAGE_TMPL = Template("""<!doctype html><html lang=\"en\"><head>
<meta charset=\"utf-8\">
<title>{{ title }}</title>
<link rel=\"canonical\" href=\"{{ canonical }}\">
<meta name=\"description\" content=\"{{ description }}\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
</head><body>
<main>
  <h1><a href=\"{{ canonical }}\">{{ title }}</a></h1>
  {% if date %}<p><em>Published: {{ date }}</em></p>{% endif %}
  <article>{{ content }}</article>
  <p><a href=\"{{ canonical }}\">Read on Dev.to →</a></p>
</main>
</body></html>
""")

INDEX_TMPL = Template("""<!doctype html><html lang=\"en\"><head>
<meta charset=\"utf-8\">
<title>{{ username }} — Dev.to Mirror</title>
<link rel=\"canonical\" href=\"{{ home }}\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
</head><body>
<main>
  <h1>{{ username }} — Dev.to Mirror</h1>
  <ul>
  {% for p in posts %}
    <li><a href=\"posts/{{ p.slug }}.html\">{{ p.title }}</a> — <small>{{ p.date }}</small></li>
  {% endfor %}
  </ul>
  <p>Canonical lives on Dev.to. This is just a no-frills crawler-friendly mirror.</p>
</main>
</body></html>
""")

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

SITEMAP_TMPL = Template("""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
  <url><loc>{{ home }}</loc></url>
  {% for p in posts %}
  <url><loc>{{ home }}posts/{{ p.slug }}.html</loc></url>
  {% endfor %}
</urlset>
""")

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

entries = feed.entries or []
posts = [Post(e) for e in entries]

# write posts
for p in posts:
    html_out = PAGE_TMPL.render(
        title=p.title,
        canonical=p.link,          # Canonical → Dev.to
        description=p.description,
        date=p.date,
        content=p.content_html
    )
    (POSTS_DIR / f"{p.slug}.html").write_text(html_out, encoding="utf-8")

# index
index_html = INDEX_TMPL.render(username=DEVTO_USERNAME, posts=posts, home=HOME)
pathlib.Path("index.html").write_text(index_html, encoding="utf-8")

# robots.txt
pathlib.Path("robots.txt").write_text(ROBOTS_TMPL.format(home=HOME), encoding="utf-8")

# sitemap.xml
smap = SITEMAP_TMPL.render(home=HOME, posts=posts)
pathlib.Path("sitemap.xml").write_text(smap, encoding="utf-8")

# Generated with the help of ChatGPT

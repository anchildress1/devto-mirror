import os
import json
import pathlib
import re
from jinja2 import Template

ROOT = pathlib.Path('.')

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

SITEMAP_TMPL = Template("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{{ home }}</loc></url>
  {% for p in posts %}
  <url><loc>{{ p.link or (home + 'posts/' + p.slug + '.html') }}</loc></url>
  {% endfor %}
  {% for c in comments %}
  <url><loc>{{ c.url or (home + c.local) }}</loc></url>
  {% endfor %}
</urlset>
""")


def load_posts_data(path='posts_data.json'):
    p = ROOT / path
    if not p.exists():
        return []
    try:
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def load_comment_manifest(path='comments.txt'):
    items = []
    p = ROOT / path
    if not p.exists():
        return items
    for raw in p.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        url, *ctx = [s.strip() for s in line.split('|', 1)]
        context = ctx[0] if ctx else ''
        m = re.search(r"/comment/([A-Za-z0-9]+)", url) or re.search(r"#comment-([A-Za-z0-9_-]+)", url)
        cid = m.group(1) if m else (re.sub(r'[^A-Za-z0-9]+','-', url)[:48])
        local = f"comments/{cid}.html"
        label = (context or url)
        if len(label) > 80:
            label = label[:77] + '...'
        items.append({'url': url, 'context': context, 'local': local, 'text': label})
    return items


def main():
    posts = load_posts_data()
    comments = load_comment_manifest()

    # Build HOME from env PAGES_REPO if available
    home_env = os.environ.get('PAGES_REPO','')
    if '/' in home_env:
        user, repo = home_env.split('/',1)
        HOME = f"https://{user}.github.io/{repo}/"
    else:
        HOME = os.environ.get('HOME','')

    devto_username = os.environ.get('DEVTO_USERNAME','')
    canonical_index = f"https://dev.to/{devto_username}" if devto_username else HOME

    index_html = INDEX_TMPL.render(username=devto_username, posts=posts, comments=comments, canonical=canonical_index, home=HOME)
    (ROOT / 'index.html').write_text(index_html, encoding='utf-8')

    smap = SITEMAP_TMPL.render(home=HOME, posts=posts, comments=comments)
    (ROOT / 'sitemap.xml').write_text(smap, encoding='utf-8')

if __name__ == '__main__':
    main()

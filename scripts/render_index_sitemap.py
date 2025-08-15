import os
import json
import pathlib
import re
import urllib.parse
from jinja2 import Template
from datetime import datetime
from email.utils import parsedate_to_datetime

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
    {% if home %}<url><loc>{{ home }}</loc></url>{% endif %}
    {% for p in posts %}
    <url><loc>{{ p.link or (home + 'posts/' + p.slug + '.html') }}</loc></url>
    {% endfor %}
    {% for c in comments %}
    <url><loc>{{ c.loc }}</loc></url>
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


def save_posts_data(posts, path='posts_data.json'):
    p = ROOT / path
    try:
        with p.open('w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def merge_posts(existing, new):
    """Merge two lists of post dicts, preferring items from `new` and
    preserving order: new posts first, then existing posts that aren't
    present in `new` (dedupe by 'link')."""
    # Build a map from a normalized key (slug preferred, else last path segment)
    # -> post dict, preferring the newest item.
    merged_map = {}

    def _normalize_slug(slug):
        if not slug:
            return None
        return slug.strip().lower()

    def _normalize_link_for_key(link):
        if not link:
            return None
        try:
            u = urllib.parse.urlparse(link)
            # remove query and fragment, normalize path
            path = u.path.rstrip('/')
            last = path.split('/')[-1] if path else ''
            if last:
                return last.lower()
            # fallback to full path
            return path.lower() or f"{u.netloc}{u.path}".lower()
        except Exception:
            return (link or '').lower()

    def _key_for_post(p):
        if not p:
            return None
        slug = _normalize_slug(p.get('slug'))
        if slug:
            return slug
        link = p.get('link') or ''
        if link:
            return _normalize_link_for_key(link)
        return None

    def _parse_date(d):
        if not d:
            return None
        # Try ISO first (handle trailing Z -> +00:00)
        try:
            ds = d.strip()
            if ds.endswith('Z'):
                # fromisoformat doesn't accept 'Z' for UTC; replace with +00:00
                ds = ds[:-1] + '+00:00'
            dt = datetime.fromisoformat(ds)
            return dt
        except Exception:
            try:
                # RFC 2822 / email-style dates
                return parsedate_to_datetime(d)
            except Exception:
                # last-resort: try to parse common formats without timezone
                try:
                    return datetime.strptime(d, '%Y-%m-%dT%H:%M:%S')
                except Exception:
                    return None

    # Add existing posts into map first keyed by normalized key
    for p in (existing or []):
        k = _key_for_post(p)
        if k:
            merged_map[k] = p

    # Merge/override with new posts (new posts are expected to be newer)
    for p in (new or []):
        k = _key_for_post(p)
        if not k:
            # If we can't form a key, skip
            continue
        existing_p = merged_map.get(k)
        if existing_p:
            d_existing = _parse_date(existing_p.get('date'))
            d_new = _parse_date(p.get('date'))
            if d_new and (not d_existing or d_new >= d_existing):
                merged_map[k] = p
        else:
            merged_map[k] = p

    # Produce a list sorted by date (newest first). If date missing, treat as older.
    def _date_key(item):
        d = _parse_date(item.get('date'))
        return d or datetime.min

    merged_list = sorted(list(merged_map.values()), key=_date_key, reverse=True)
    return merged_list


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
        # normalize comment id from URL fragment or path
        m = re.search(r"/comment/([A-Za-z0-9]+)", url) or re.search(r"#comment-([A-Za-z0-9_-]+)", url)
        cid = m.group(1) if m else (re.sub(r'[^A-Za-z0-9]+','-', url)[:48])
        local = f"comments/{cid}.html"
        label = (context or url)
        if len(label) > 80:
            label = label[:77] + '...'
        items.append({'url': url, 'context': context, 'local': local, 'text': label})
    return items


def main():
    # Load existing posts data from the gh-pages working tree (if present)
    posts = load_posts_data()
    # If a freshly-generated posts_data.json was provided (posts_data_new.json), merge it
    new_path = ROOT / 'posts_data_new.json'
    if new_path.exists():
        try:
            with new_path.open('r', encoding='utf-8') as f:
                new_posts = json.load(f)
        except Exception:
            new_posts = []
        if new_posts:
            print(f"Merging {len(new_posts)} new posts into existing {len(posts)} posts")
            merged = merge_posts(posts, new_posts)
            if save_posts_data(merged):
                print(f"Wrote merged posts_data.json ({len(merged)} posts)")
                posts = merged
            else:
                print("Warning: Failed to write merged posts_data.json")
        else:
            print("No new posts found in posts_data_new.json to merge")
    comments = load_comment_manifest()
    # Deduplicate comments by url/local and compute a final 'loc' for sitemap entries.
    comments_seen = {}
    comments_final = []
    for c in comments:
        key = c.get('url') or c.get('local')
        if not key:
            continue
        if key in comments_seen:
            continue
        comments_seen[key] = True
        if c.get('url'):
            loc = c['url']
        elif HOME:
            loc = HOME + c['local']
        else:
            loc = c['local']
        entry = dict(c)
        entry['loc'] = loc
        # For template compatibility use 'loc' field as 'loc' but template expects 'loc' key
        comments_final.append({'loc': loc, 'url': c.get('url'), 'local': c.get('local'), 'text': c.get('text')})
    # replace comments with final normalized comment list for rendering
    comments = comments_final

    # Build HOME from env PAGES_REPO if available
    home_env = os.environ.get('PAGES_REPO','')
    if '/' in home_env:
        user, repo = home_env.split('/',1)
        HOME = f"https://{user}.github.io/{repo}/"
    else:
        # If PAGES_REPO isn't set, don't use the local filesystem HOME as the site URL.
        # Leave HOME blank so templates fall back to relative paths.
        HOME = ''

    devto_username = os.environ.get('DEVTO_USERNAME','')
    canonical_index = f"https://dev.to/{devto_username}" if devto_username else HOME

    # Deduplicate posts by link (or slug) preferring the newest by date, then sort newest first
    # unified date parser used in dedupe and sorting
    def _parse_date_str(d):
        if not d:
            return None
        ds = d.strip()
        try:
            if ds.endswith('Z'):
                ds = ds[:-1] + '+00:00'
            return datetime.fromisoformat(ds)
        except Exception:
            try:
                return parsedate_to_datetime(d)
            except Exception:
                try:
                    return datetime.strptime(ds, '%Y-%m-%dT%H:%M:%S')
                except Exception:
                    return None

    def dedupe_posts(posts_list):
        """Return a deduped list of posts preferring the newest by date.
        Key by link when available, else slug. """
        def _normalize_key(p):
            if not p:
                return None
            slug = p.get('slug')
            if slug:
                return slug.strip().lower()
            link = p.get('link') or ''
            if link:
                try:
                    u = urllib.parse.urlparse(link)
                    # strip query and fragment
                    path = u.path.rstrip('/')
                    last = path.split('/')[-1] if path else ''
                    if last:
                        return last.lower()
                    return (u.netloc + u.path).lower()
                except Exception:
                    return link.lower()
            return None

        seen = {}
        for p in (posts_list or []):
            key = _normalize_key(p)
            if not key:
                continue
            existing = seen.get(key)
            if not existing:
                seen[key] = p
                continue
            # Compare dates and prefer newest
            d_existing = _parse_date_str(existing.get('date'))
            d_new = _parse_date_str(p.get('date'))
            if d_new and (not d_existing or d_new >= d_existing):
                seen[key] = p

        # Produce list and sort by date
        merged = list(seen.values())
        merged_sorted = sorted(merged, key=lambda x: _parse_date_str(x.get('date')) or datetime.min, reverse=True)
        return merged_sorted

    # Clean posts in-memory for rendering only. Do NOT overwrite posts_data.json
    # here; posts_data.json is authoritative unless an explicit merge is requested
    posts_clean = dedupe_posts(posts)
    posts = posts_clean

    # Ensure posts are sorted newest first by date (use unified parser defined above)
    posts_sorted = sorted(posts, key=lambda x: _parse_date_str(x.get('date')) or datetime.min, reverse=True)

    # When rendering, prefer the dev.to canonical link if present for canonical index
    # and ensure templates use post.link when available.
    # Title should always keep the username (fallback to DEVTO_USERNAME or
    # derive from first post link if not present).
    title_user = devto_username
    if not title_user and posts_sorted:
        # attempt to extract user from first post link
        try:
            first_link = posts_sorted[0].get('link') if isinstance(posts_sorted[0], dict) else getattr(posts_sorted[0], 'link', '')
            if first_link:
                parsed = urllib.parse.urlparse(first_link)
                parts = parsed.path.strip('/').split('/')
                if parts:
                    title_user = parts[0]
        except Exception:
            title_user = ''

    index_html = INDEX_TMPL.render(username=title_user or devto_username, posts=posts_sorted, comments=comments, canonical=canonical_index, home=HOME)
    (ROOT / 'index.html').write_text(index_html, encoding='utf-8')

    # For sitemap, prefer the explicit 'link' field (canonical dev.to URL) when present.
    smap = SITEMAP_TMPL.render(home=HOME, posts=posts_sorted, comments=comments)
    (ROOT / 'sitemap.xml').write_text(smap, encoding='utf-8')

if __name__ == '__main__':
    main()

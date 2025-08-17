import os
import json
import pathlib
import re
import urllib.parse
from jinja2 import Template
from datetime import datetime
from email.utils import parsedate_to_datetime
from utils import INDEX_TMPL, SITEMAP_TMPL, parse_date, dedupe_posts_by_link
from slugify import slugify

ROOT = pathlib.Path('.')


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
        cid = m.group(1) if m else slugify(url)[:48]
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
            # Combine all posts and deduplicate by link
            combined = posts + new_posts
            merged = dedupe_posts_by_link(combined)
            if save_posts_data(merged):
                print(f"Wrote merged posts_data.json ({len(merged)} posts)")
                posts = merged
            else:
                print("Warning: Failed to write merged posts_data.json")
        else:
            print("No new posts found in posts_data_new.json to merge")
    # Build HOME from env PAGES_REPO if available (needed when normalizing comment locs)
    home_env = os.environ.get('PAGES_REPO', '')
    if '/' in home_env:
        user, repo = home_env.split('/', 1)
        HOME = f"https://{user}.github.io/{repo}/"
    else:
        # If PAGES_REPO isn't set, don't use the local filesystem HOME as the site URL.
        # Leave HOME blank so templates fall back to relative paths.
        HOME = ''

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

    devto_username = os.environ.get('DEVTO_USERNAME','')
    canonical_index = f"https://dev.to/{devto_username}" if devto_username else HOME

    # Deduplicate posts by link (or slug) preferring the newest by date, then sort newest first
    # Clean posts in-memory for rendering only. Do NOT overwrite posts_data.json
    # here; posts_data.json is authoritative unless an explicit merge is requested
    posts = dedupe_posts_by_link(posts)

    # Ensure posts are sorted newest first by date (already sorted by dedupe_posts_by_link)
    posts_sorted = posts

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

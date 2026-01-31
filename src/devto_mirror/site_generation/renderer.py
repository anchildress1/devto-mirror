import json
import os
import pathlib
import re
import sys
import urllib.parse

from slugify import slugify

from devto_mirror.core.url_utils import build_site_urls
from devto_mirror.core.utils import INDEX_TMPL, SITEMAP_TMPL, dedupe_posts_by_link

ROOT = pathlib.Path(".")


def load_posts_data(path="posts_data.json"):
    p = ROOT / path
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_posts_data(posts, path="posts_data.json"):
    p = ROOT / path
    try:
        with p.open("w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_comment_manifest(path="comments.txt"):
    items = []
    p = ROOT / path
    if not p.exists():
        return items
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        url, *ctx = [s.strip() for s in line.split("|", 1)]
        context = ctx[0] if ctx else ""
        # normalize comment id from URL fragment or path
        m = re.search(r"/comment/([A-Za-z0-9]+)", url) or re.search(r"#comment-([A-Za-z0-9_-]+)", url)
        cid = m.group(1) if m else slugify(url)[:48]
        local = f"comments/{cid}.html"
        label = context or url
        if len(label) > 80:
            label = label[:77] + "..."
        items.append({"url": url, "context": context, "local": local, "text": label})
    return items


def load_and_merge_posts():
    posts = load_posts_data()
    new_path = ROOT / "posts_data_new.json"
    if new_path.exists():
        try:
            with new_path.open("r", encoding="utf-8") as f:
                new_posts = json.load(f)
        except Exception:
            new_posts = []
        if new_posts:
            print(f"Merging {len(new_posts)} new posts into existing {len(posts)} posts")
            combined = posts + new_posts
            merged = dedupe_posts_by_link(combined)
            if save_posts_data(merged):
                print(f"Wrote merged posts_data.json ({len(merged)} posts)")
                posts = merged
            else:
                print("Warning: Failed to write merged posts_data.json")
        else:
            print("No new posts found in posts_data_new.json to merge")
    return posts


def get_home_url():
    site_domain = os.environ.get("SITE_DOMAIN", "").strip()
    gh_username = os.environ.get("GH_USERNAME", "").strip()
    try:
        return build_site_urls(site_domain=site_domain, gh_username=gh_username).home
    except ValueError:
        return ""


def process_comments(home):
    comments = load_comment_manifest()
    comments_seen = {}
    comments_final = []
    for c in comments:
        key = c.get("url") or c.get("local")
        if not key or key in comments_seen:
            continue
        comments_seen[key] = True
        loc = c.get("url") or (home + c["local"] if home else c["local"])
        entry = dict(c)
        entry["loc"] = loc
        comments_final.append({"loc": loc, "url": c.get("url"), "local": c.get("local"), "text": c.get("text")})
    return comments_final


def get_title_user(posts_sorted, devto_username):
    if devto_username:
        return devto_username
    if not posts_sorted:
        return ""
    try:
        first_post = posts_sorted[0]
        first_link = first_post.get("link") if isinstance(first_post, dict) else getattr(first_post, "link", "")
        if first_link:
            parsed = urllib.parse.urlparse(first_link)
            parts = parsed.path.strip("/").split("/")
            return parts[0] if parts else ""
    except Exception as e:
        # Log the parsing error for visibility (avoids swallowing exceptions silently)
        # and return an empty username as a safe fallback.
        print(f"Warning: failed to extract username from first post link: {e}", file=sys.stderr)
        return ""
    return ""


def render_templates(posts, comments, home, devto_username):
    posts_sorted = dedupe_posts_by_link(posts)
    title_user = get_title_user(posts_sorted, devto_username)
    canonical_index = f"https://dev.to/{devto_username}" if devto_username else home

    index_html = INDEX_TMPL.render(
        username=title_user or devto_username,
        posts=posts_sorted,
        comments=comments,
        canonical=canonical_index,
        home=home,
    )
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")

    smap = SITEMAP_TMPL.render(home=home, posts=posts_sorted, comments=comments)
    (ROOT / "sitemap.xml").write_text(smap, encoding="utf-8")


def main():
    posts = load_and_merge_posts()
    home = get_home_url()
    comments = process_comments(home)
    devto_username = os.environ.get("DEVTO_USERNAME", "")
    render_templates(posts, comments, home, devto_username)


if __name__ == "__main__":
    main()

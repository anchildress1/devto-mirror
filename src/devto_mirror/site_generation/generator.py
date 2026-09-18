"""Build the Dev.to mirror: post pages, comment notes, index, sitemap, robots.txt and llms.txt."""

from __future__ import annotations

import json
import logging
import os
import pathlib
import re
import shutil
from dataclasses import dataclass

from dotenv import load_dotenv
from slugify import slugify

from devto_mirror.core.api_client import sync_articles
from devto_mirror.core.path_utils import sanitize_filename
from devto_mirror.core.url_utils import resolve_home
from devto_mirror.core.utils import env
from devto_mirror.site_generation import seo
from devto_mirror.site_generation.post import Post

STORE_FILE = pathlib.Path("posts_data.json")
COMMENTS_FILE = pathlib.Path("comments.txt")
OUTPUT_DIR = pathlib.Path("_deploy")

_COMMENT_ID = re.compile(r"/comment/([A-Za-z0-9]+)|#comment-([A-Za-z0-9_-]+)")


@dataclass(frozen=True, slots=True)
class CommentNote:
    url: str
    context: str
    path: str

    @property
    def label(self) -> str:
        text = self.context or self.url
        return text if len(text) <= 80 else f"{text[:77]}..."


def load_comment_notes(path: pathlib.Path) -> list[CommentNote]:
    """Parse ``URL | optional context`` lines; blank lines and ``#`` comments are skipped.

    Later lines that resolve to the same output path replace earlier ones, matching which
    note's content actually ends up on disk.
    """
    if not path.exists():
        return []
    notes: dict[str, CommentNote] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        url, _, context = (part.strip() for part in line.partition("|"))
        match = _COMMENT_ID.search(url)
        comment_id = (match[1] or match[2]) if match else slugify(url)[:48]
        note = CommentNote(url=url, context=context, path=f"comments/{sanitize_filename(comment_id)}.html")
        notes[note.path] = note
    return list(notes.values())


def _to_post(article: dict) -> Post:
    try:
        return Post.from_article(article)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Unusable article {article.get('id')} ({article.get('url')}): {exc!r}") from exc


def build_site(posts: list[Post], comments: list[CommentNote], *, home: str, username: str, out: pathlib.Path) -> None:
    """Render every page of the mirror into ``out``. Raises ValueError if two posts share a slug."""
    slugs = [post.slug for post in posts]
    if duplicates := sorted({slug for slug in slugs if slugs.count(slug) > 1}):
        raise ValueError(f"Posts share a slug and would overwrite each other: {duplicates}")
    context = {
        "home": home,
        "username": username,
        "site_name": f"{username}—Dev.to Mirror",
        "default_image": f"{home}assets/devto-mirror.jpg",
    }

    def write(relative: str, template: str, **values) -> None:
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(env.get_template(template).render(**context, **values), encoding="utf-8")

    for post in posts:
        write(
            f"posts/{post.slug}.html",
            "post.html",
            post=post,
            schema=seo.article_schema(post),
            related=seo.related_posts(post, posts),
        )
    for note in comments:
        write(note.path, "comment.html", note=note)
    write("index.html", "index.html", posts=posts, comments=comments)
    write("sitemap.xml", "sitemap.xml", posts=posts, comments=comments)
    write("robots.txt", "robots.txt")
    write("llms.txt", "llms.txt")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    load_dotenv()

    username = os.getenv("DEVTO_USERNAME", "").strip()
    if not username:
        raise SystemExit("Missing DEVTO_USERNAME (your Dev.to username)")
    home = resolve_home(site_domain=os.getenv("SITE_DOMAIN", ""), gh_username=os.getenv("GH_USERNAME", ""))
    force = os.getenv("FORCE_FULL_REGEN", "").strip().lower() in {"1", "true", "yes"}

    # Forcing ignores the store entirely, which is also the way out of a corrupt one.
    stored = json.loads(STORE_FILE.read_text(encoding="utf-8")) if STORE_FILE.exists() and not force else []
    if not isinstance(stored, list) or not all(isinstance(item, dict) for item in stored):
        raise SystemExit(f"{STORE_FILE} is not a list of article objects; corrupt store, aborting.")
    articles = sync_articles(username, stored)
    if not articles:
        raise SystemExit(f"Dev.to lists no published articles for {username!r}; refusing to publish an empty site.")

    posts = sorted((_to_post(a) for a in articles), key=lambda p: p.published, reverse=True)
    # Start clean so posts deleted or renamed on Dev.to never linger in a local build.
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    build_site(posts, load_comment_notes(COMMENTS_FILE), home=home, username=username, out=OUTPUT_DIR)
    # Only commit the store once validation and rendering have both succeeded.
    STORE_FILE.write_text(json.dumps(articles, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info("Rendered %d posts into %s", len(posts), OUTPUT_DIR)


if __name__ == "__main__":
    main()

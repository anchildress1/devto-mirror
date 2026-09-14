"""Tests for devto_mirror.site_generation.generator."""

import json
import os
import pathlib
import re
import tempfile
import unittest
import urllib.robotparser
import xml.etree.ElementTree as ET
from unittest.mock import patch

from devto_mirror.site_generation import generator
from devto_mirror.site_generation.generator import CommentNote, build_site, load_comment_notes
from devto_mirror.site_generation.post import Post
from tests.factories import make_article

HOME = "https://mirror.example/"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def _canonicals(html: str) -> list[str]:
    return re.findall(r'<link rel="canonical" href="([^"]*)">', html)


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory()))


class TestLoadCommentNotes(TempDirTestCase):
    def test_returns_empty_list_when_manifest_is_missing(self):
        self.assertEqual(load_comment_notes(self.tmp / "missing.txt"), [])

    def test_parses_ids_contexts_and_skips_blank_and_comment_lines(self):
        manifest = self.tmp / "comments.txt"
        manifest.write_text(
            "# header\n\n"
            "https://dev.to/ash/comment/2abc | Why I said this\n"
            "https://dev.to/ash/post#comment-x_y-1\n"
            "https://dev.to/ash/some-post\n",
            encoding="utf-8",
        )

        notes = load_comment_notes(manifest)

        self.assertEqual(
            notes,
            [
                CommentNote("https://dev.to/ash/comment/2abc", "Why I said this", "comments/2abc.html"),
                CommentNote("https://dev.to/ash/post#comment-x_y-1", "", "comments/x_y-1.html"),
                CommentNote("https://dev.to/ash/some-post", "", "comments/https-dev-to-ash-some-post.html"),
            ],
        )

    def test_dedupes_notes_that_resolve_to_the_same_path(self):
        manifest = self.tmp / "comments.txt"
        manifest.write_text(
            "https://dev.to/ash/comment/306a2 | first\nhttps://dev.to/ash/comment/306a2 | second\n",
            encoding="utf-8",
        )

        notes = load_comment_notes(manifest)

        self.assertEqual(notes, [CommentNote("https://dev.to/ash/comment/306a2", "second", "comments/306a2.html")])

    def test_label_prefers_context_and_truncates_to_80_chars(self):
        cases = {
            CommentNote("https://u", "", "p"): "https://u",
            CommentNote("https://u", "short", "p"): "short",
            CommentNote("https://u", "x" * 100, "p"): "x" * 77 + "...",
        }
        for note, label in cases.items():
            with self.subTest(context=note.context):
                self.assertEqual(note.label, label)


class TestBuildSite(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        self.posts = [
            Post.from_article(make_article(2, tags=["ai"], description='It\'s "quoted" & <b>')),
            Post.from_article(make_article(1, tags=["ai"], canonical_url="https://dev.to/ash/original")),
        ]
        self.note = CommentNote("https://dev.to/ash/comment/9", "ctx", "comments/9.html")
        build_site(self.posts, [self.note], home=HOME, username="ash", out=self.tmp)

    def _read(self, relative: str) -> str:
        return (self.tmp / relative).read_text(encoding="utf-8")

    def test_every_page_has_exactly_one_canonical_on_devto(self):
        pages = {f"posts/{p.slug}.html": p.canonical for p in self.posts}
        pages |= {"index.html": "https://dev.to/ash", self.note.path: self.note.url}
        for page, expected in pages.items():
            with self.subTest(page=page):
                self.assertEqual(_canonicals(self._read(page)), [expected])
                self.assertTrue(expected.startswith("https://dev.to/"))

    def test_repost_canonicalizes_to_original_but_links_to_itself(self):
        html = self._read("posts/post-1.html")

        self.assertEqual(_canonicals(html), ["https://dev.to/ash/original"])
        self.assertIn('<h1><a href="https://dev.to/ash/post-1">', html)
        self.assertIn('<a href="https://dev.to/ash/post-1">Read on Dev.to →</a>', html)

    def test_sitemap_lists_absolute_same_host_urls_for_every_page(self):
        root = ET.fromstring(self._read("sitemap.xml"))

        locs = [loc.text for loc in root.findall("sm:url/sm:loc", SITEMAP_NS)]

        self.assertEqual(
            locs,
            [HOME, f"{HOME}posts/post-2.html", f"{HOME}posts/post-1.html", f"{HOME}comments/9.html"],
        )

    def test_escapes_description_exactly_once(self):
        html = self._read("posts/post-2.html")

        self.assertIn('content="It&#39;s &#34;quoted&#34; &amp; &lt;b&gt;"', html)
        self.assertNotIn("&amp;#", html)

    def test_embeds_json_ld_and_links_related_posts(self):
        html = self._read("posts/post-2.html")
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)[1])

        self.assertEqual(schema["mainEntityOfPage"], "https://dev.to/ash/post-2")
        self.assertIn('<a href="post-1.html">Post 1</a>', html)

    def test_index_links_every_post_and_comment(self):
        html = self._read("index.html")

        for href in ("posts/post-2.html", "posts/post-1.html", "comments/9.html"):
            self.assertIn(f'href="{href}"', html)

    def test_refuses_to_render_without_posts(self):
        with self.assertRaisesRegex(ValueError, "no posts"):
            build_site([], [], home=HOME, username="ash", out=self.tmp / "empty")

    def test_llms_txt_keeps_markdown_links_intact_for_awkward_titles(self):
        post = Post.from_article(make_article(4, title="[WIP] Map[K]", description="line one\n\n## not a heading"))
        build_site([post], [], home=HOME, username="ash", out=self.tmp / "md")

        llms = (self.tmp / "md/llms.txt").read_text(encoding="utf-8")

        self.assertIn(f"- [\\[WIP\\] Map\\[K\\]]({HOME}posts/post-4.html): line one ## not a heading (canonical:", llms)

    def test_refuses_to_render_posts_that_share_a_slug(self):
        clash = [Post.from_article(make_article(1)), Post.from_article(make_article(2, slug="post-1"))]

        with self.assertRaisesRegex(ValueError, r"share a slug.*\['post-1'\]"):
            build_site(clash, [], home=HOME, username="ash", out=self.tmp / "clash")

    def test_every_page_reserves_training_rights(self):
        for page in ("index.html", "posts/post-1.html", self.note.path):
            with self.subTest(page=page):
                html = self._read(page)
                self.assertIn('<meta name="tdm-reservation" content="1">', html)
                self.assertIn("max-snippet:-1, noai, noimageai", html)

    def test_robots_blocks_training_crawlers_but_admits_search_and_live_retrieval(self):
        robots = self._read("robots.txt")
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(robots.splitlines())
        url = f"{HOME}posts/post-1.html"

        for agent in (
            "GPTBot",
            "ClaudeBot",
            "anthropic-ai",
            "Google-Extended",
            "Applebot-Extended",
            "CCBot",
            "Bytespider",
        ):
            with self.subTest(blocked=agent):
                self.assertFalse(parser.can_fetch(agent, url))
        for agent in (
            "Googlebot",
            "Bingbot",
            "OAI-SearchBot",
            "ChatGPT-User",
            "Claude-SearchBot",
            "Claude-User",
            "PerplexityBot",
        ):
            with self.subTest(allowed=agent):
                self.assertTrue(parser.can_fetch(agent, url))
        self.assertIn("Content-Signal: search=yes, ai-input=yes, ai-train=no", robots)
        self.assertIn(f"Sitemap: {HOME}sitemap.xml", robots)

    def test_llms_txt_indexes_mirror_pages_with_their_devto_canonicals(self):
        llms = self._read("llms.txt")

        self.assertTrue(llms.startswith("# ash—Dev.to Mirror\n"))
        self.assertIn("ai-train=no", llms)
        self.assertIn(
            f"- [Post 1]({HOME}posts/post-1.html): About post 1 (canonical: https://dev.to/ash/original)", llms
        )
        self.assertIn("Content © Ash, all rights reserved.", llms)


class TestMain(TempDirTestCase):
    ENV = {"DEVTO_USERNAME": "ash", "SITE_DOMAIN": "mirror.example"}

    def setUp(self):
        super().setUp()
        self.store = self.tmp / "posts_data.json"
        self.enterContext(patch.object(generator, "load_dotenv"))
        self.enterContext(patch.object(generator, "STORE_FILE", self.store))
        self.enterContext(patch.object(generator, "COMMENTS_FILE", self.tmp / "comments.txt"))
        self.enterContext(patch.object(generator, "OUTPUT_DIR", self.tmp / "out"))
        self.sync = self.enterContext(patch.object(generator, "sync_articles"))
        self.build = self.enterContext(patch.object(generator, "build_site"))

    def _run(self, **env):
        with patch.dict(os.environ, {**self.ENV, **env}, clear=True):
            generator.main()

    def test_syncs_saves_store_and_renders_posts_newest_first(self):
        stored = [make_article(1)]
        self.store.write_text(json.dumps(stored), encoding="utf-8")
        self.sync.return_value = [make_article(1), make_article(3), make_article(2)]

        self._run()

        self.sync.assert_called_once_with("ash", stored)
        self.assertEqual([a["id"] for a in json.loads(self.store.read_text(encoding="utf-8"))], [1, 3, 2])
        posts, comments = self.build.call_args.args
        self.assertEqual([p.slug for p in posts], ["post-3", "post-2", "post-1"])
        self.assertEqual(comments, [])
        self.assertEqual(
            self.build.call_args.kwargs, {"home": "https://mirror.example/", "username": "ash", "out": self.tmp / "out"}
        )

    def test_clears_stale_output_before_rendering(self):
        stale = self.tmp / "out" / "posts" / "deleted-post.html"
        stale.parent.mkdir(parents=True)
        stale.write_text("old", encoding="utf-8")
        self.sync.return_value = [make_article(1)]

        self._run()

        self.assertFalse(stale.exists())

    def test_starts_from_empty_store_when_none_exists(self):
        self.sync.return_value = [make_article(1)]

        self._run()

        self.sync.assert_called_once_with("ash", [])

    def test_force_flag_ignores_the_store_even_when_corrupt(self):
        self.sync.return_value = [make_article(1)]
        for value, forced in (("true", True), ("1", True), ("YES", True), ("no", False)):
            with self.subTest(FORCE_FULL_REGEN=value):
                self.store.write_text(json.dumps([make_article(7)]), encoding="utf-8")
                self._run(FORCE_FULL_REGEN=value)
                self.assertEqual(self.sync.call_args.args[1], [] if forced else [make_article(7)])
        self.store.write_text("{corrupt", encoding="utf-8")
        self._run(FORCE_FULL_REGEN="true")

    def test_names_the_article_when_one_is_unusable(self):
        broken = make_article(5)
        del broken["published_at"]
        self.sync.return_value = [make_article(1), broken]

        with self.assertRaisesRegex(ValueError, r"Unusable article 5 \(https://dev.to/ash/post-5\).*published_at"):
            self._run()
        self.build.assert_not_called()

    def test_falls_back_to_github_pages_home(self):
        self.sync.return_value = [make_article(1)]

        self._run(SITE_DOMAIN="", GH_USERNAME="octo")

        self.assertEqual(self.build.call_args.kwargs["home"], "https://octo.github.io/devto-mirror/")

    def test_refuses_to_publish_when_devto_lists_no_articles(self):
        self.sync.return_value = []

        with self.assertRaisesRegex(SystemExit, "refusing to publish an empty site"):
            self._run()
        self.assertFalse(self.store.exists())
        self.build.assert_not_called()

    def test_requires_devto_username(self):
        with self.assertRaisesRegex(SystemExit, "DEVTO_USERNAME"):
            self._run(DEVTO_USERNAME="  ")
        self.sync.assert_not_called()

    def test_requires_a_site_url(self):
        with self.assertRaisesRegex(ValueError, "SITE_DOMAIN or GH_USERNAME"):
            self._run(SITE_DOMAIN="")
        self.sync.assert_not_called()

    def test_fails_loudly_on_a_corrupt_store(self):
        self.store.write_text("{not json", encoding="utf-8")

        with self.assertRaises(json.JSONDecodeError):
            self._run()
        self.sync.assert_not_called()

    def test_fails_loudly_on_a_structurally_invalid_store(self):
        for payload in ("{}", '["not-a-dict"]', '"just a string"'):
            with self.subTest(payload=payload):
                self.store.write_text(payload, encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "not a list of article objects"):
                    self._run()
                self.sync.assert_not_called()

    def test_defers_writing_the_store_until_the_site_renders(self):
        self.sync.return_value = [make_article(1)]
        self.build.side_effect = RuntimeError("boom")

        with self.assertRaisesRegex(RuntimeError, "boom"):
            self._run()
        self.assertFalse(self.store.exists())


if __name__ == "__main__":
    unittest.main()

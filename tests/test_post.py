"""Tests for devto_mirror.site_generation.post."""

import unittest

from devto_mirror.site_generation.post import Post, ensure_img_dimensions
from tests.factories import make_article


class TestPostFromArticle(unittest.TestCase):
    def test_maps_every_field_from_a_full_article(self):
        article = make_article(
            3,
            cover_image="https://img/c.png",
            tags=["ai", "python"],
            edited_at="2026-02-01T00:00:00Z",
            reading_time_minutes=7,
        )

        post = Post.from_article(article)

        self.assertEqual(post.slug, "post-3")
        self.assertEqual(post.title, "Post 3")
        self.assertEqual(post.url, "https://dev.to/ash/post-3")
        self.assertEqual(post.canonical, "https://dev.to/ash/post-3")
        self.assertEqual(post.description, "About post 3")
        self.assertEqual(post.content_html, "<p>Body 3</p>")
        self.assertEqual(post.cover_image, "https://img/c.png")
        self.assertEqual(post.tags, ("ai", "python"))
        self.assertEqual((post.author, post.username), ("Ash", "ash"))
        self.assertEqual(post.published, "2026-01-03T00:00:00Z")
        self.assertEqual(post.modified, "2026-02-01T00:00:00Z")
        self.assertEqual(post.reading_minutes, 7)

    def test_prefers_devto_canonical_url_for_reposts(self):
        post = Post.from_article(make_article(1, canonical_url="https://dev.to/ash/original"))
        self.assertEqual((post.canonical, post.url), ("https://dev.to/ash/original", "https://dev.to/ash/post-1"))

    def test_falls_back_to_url_when_canonical_url_is_missing_or_empty(self):
        for canonical in (None, ""):
            with self.subTest(canonical_url=canonical):
                post = Post.from_article(make_article(1, canonical_url=canonical))
                self.assertEqual(post.canonical, "https://dev.to/ash/post-1")

    def test_uses_published_as_modified_when_never_edited(self):
        post = Post.from_article(make_article(1, edited_at=None))
        self.assertEqual(post.modified, post.published)

    def test_defaults_optional_fields_when_absent(self):
        article = make_article(1)
        for key in ("description", "body_html", "cover_image", "tags", "user", "reading_time_minutes"):
            article.pop(key)

        post = Post.from_article(article)

        self.assertEqual((post.description, post.content_html, post.cover_image), ("", "", ""))
        self.assertEqual((post.tags, post.author, post.username, post.reading_minutes), ((), "", "", 0))

    def test_falls_back_to_username_when_author_has_no_name(self):
        post = Post.from_article(make_article(1, user={"name": "", "username": "ash"}))
        self.assertEqual(post.author, "ash")

    def test_sanitizes_slug_into_a_safe_filename(self):
        post = Post.from_article(make_article(1, slug="../etc/passwd"))
        self.assertEqual(post.slug, "---etc-passwd")

    def test_rejects_article_with_empty_slug(self):
        article = make_article(1, slug="")

        with self.assertRaisesRegex(ValueError, "no usable slug"):
            Post.from_article(article)

    def test_rejects_article_missing_a_required_field(self):
        for keys in (("slug",), ("title",), ("published_at",), ("url", "canonical_url")):
            with self.subTest(missing=keys):
                article = make_article(1)
                for key in keys:
                    del article[key]
                with self.assertRaises(KeyError):
                    Post.from_article(article)

    def test_sanitizes_body_and_sizes_images(self):
        body = '<p>hi</p><script>alert(1)</script><img src="a.png">'

        post = Post.from_article(make_article(1, body_html=body))

        self.assertEqual(post.content_html, '<p>hi</p><img width="800" height="450" src="a.png">')


class TestEnsureImgDimensions(unittest.TestCase):
    def test_adds_default_size_to_unsized_images_in_any_case(self):
        cases = {
            '<img src="a.png">': '<img width="800" height="450" src="a.png">',
            '<IMG src="a.png">': '<IMG width="800" height="450" src="a.png">',
            "<img>": '<img width="800" height="450">',
        }
        for tag, expected in cases.items():
            with self.subTest(tag=tag):
                self.assertEqual(ensure_img_dimensions(tag), expected)

    def test_leaves_images_that_declare_a_size(self):
        for tag in ('<img width="10" src="a">', "<img height='5' src='a'>", '<img src="a" WIDTH = "3">'):
            with self.subTest(tag=tag):
                self.assertEqual(ensure_img_dimensions(tag), tag)

    def test_leaves_html_without_images_untouched(self):
        self.assertEqual(ensure_img_dimensions("<p>no images</p>"), "<p>no images</p>")


if __name__ == "__main__":
    unittest.main()

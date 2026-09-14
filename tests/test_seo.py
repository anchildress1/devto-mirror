"""Tests for devto_mirror.site_generation.seo."""

import unittest

from devto_mirror.site_generation.post import Post
from devto_mirror.site_generation.seo import article_schema, related_posts
from tests.factories import make_article


def _post(article_id: int, tags: list[str], **overrides) -> Post:
    return Post.from_article(make_article(article_id, tags=tags, **overrides))


class TestArticleSchema(unittest.TestCase):
    def test_builds_blog_posting_attributed_to_the_devto_original(self):
        post = _post(1, ["ai"], cover_image="https://img/c.png", edited_at="2026-03-01T00:00:00Z")

        schema = article_schema(post)

        self.assertEqual(
            schema,
            {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": "Post 1",
                "url": "https://dev.to/ash/post-1",
                "mainEntityOfPage": "https://dev.to/ash/post-1",
                "datePublished": "2026-01-01T00:00:00Z",
                "dateModified": "2026-03-01T00:00:00Z",
                "author": {"@type": "Person", "name": "Ash", "url": "https://dev.to/ash"},
                "publisher": {"@type": "Organization", "name": "DEV Community", "url": "https://dev.to"},
                "description": "About post 1",
                "image": "https://img/c.png",
                "keywords": ["ai"],
                "timeRequired": "PT4M",
            },
        )

    def test_omits_optional_fields_that_are_empty(self):
        post = _post(1, [], description="", cover_image="", reading_time_minutes=0)

        schema = article_schema(post)

        for key in ("description", "image", "keywords", "timeRequired"):
            self.assertNotIn(key, schema)


class TestRelatedPosts(unittest.TestCase):
    def test_ranks_by_shared_tag_count_ignoring_case(self):
        current = _post(1, ["AI", "python", "testing"])
        one_shared = _post(2, ["ai"])
        two_shared = _post(3, ["Python", "TESTING"])

        self.assertEqual(related_posts(current, [current, one_shared, two_shared]), [two_shared, one_shared])

    def test_excludes_self_and_posts_without_shared_tags(self):
        current = _post(1, ["ai"])

        self.assertEqual(related_posts(current, [current, _post(2, ["rust"]), _post(3, [])]), [])

    def test_keeps_input_order_for_ties_and_honors_limit(self):
        current = _post(1, ["ai"])
        others = [_post(i, ["ai"]) for i in range(2, 9)]

        self.assertEqual(related_posts(current, [current, *others], limit=3), others[:3])

    def test_returns_nothing_for_untagged_post(self):
        current = _post(1, [])

        self.assertEqual(related_posts(current, [current, _post(2, ["ai"])]), [])


if __name__ == "__main__":
    unittest.main()

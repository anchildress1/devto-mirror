import unittest

from devto_mirror.core.utils import dedupe_posts_by_link


class TestDedupePostsByLink(unittest.TestCase):
    def test_dedupes_by_id_and_prefers_newer_activity(self):
        older = {
            "id": 123,
            "link": "https://dev.to/me/my-post",
            "date": "2024-01-01T00:00:00Z",
            "api_data": {
                "id": 123,
                "published_at": "2024-01-01T00:00:00Z",
                "edited_at": "2024-01-02T00:00:00Z",
            },
            "title": "Old title",
        }
        newer = {
            "id": 123,
            "link": "https://dev.to/me/my-post-updated",
            "date": "2024-01-01T00:00:00Z",
            "api_data": {
                "id": 123,
                "published_at": "2024-01-01T00:00:00Z",
                "edited_at": "2024-01-03T00:00:00Z",
            },
            "title": "New title",
        }

        result = dedupe_posts_by_link([older, newer])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 123)
        self.assertEqual(result[0]["title"], "New title")
        self.assertEqual(result[0]["link"], "https://dev.to/me/my-post-updated")

    def test_falls_back_to_canonical_link(self):
        a = {"link": "https://example.com/post/", "date": "2024-01-01T00:00:00Z"}
        b = {"link": "https://example.com/post", "date": "2024-01-02T00:00:00Z"}

        result = dedupe_posts_by_link([a, b])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["link"], "https://example.com/post")

    def test_merges_missing_fields_from_older(self):
        # Newer version might be missing fields due to partial caching; we should not drop them.
        older = {
            "id": 1,
            "link": "https://dev.to/me/post",
            "date": "2024-01-01T00:00:00Z",
            "title": "Title",
            "description": "Desc",
            "api_data": {"id": 1, "published_at": "2024-01-01T00:00:00Z"},
        }
        newer_partial = {
            "id": 1,
            "link": "https://dev.to/me/post",
            "date": "2024-01-01T00:00:00Z",
            "api_data": {"id": 1, "edited_at": "2024-01-05T00:00:00Z"},
        }

        result = dedupe_posts_by_link([older, newer_partial])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["description"], "Desc")


if __name__ == "__main__":
    unittest.main()

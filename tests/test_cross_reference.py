"""
Tests for cross-reference functionality.
"""

import unittest
from unittest.mock import Mock

from devto_mirror.ai_optimization.cross_reference import (
    add_source_attribution,
    create_dev_to_backlinks,
    enhance_post_with_cross_references,
    generate_related_links,
)


class TestCrossReference(unittest.TestCase):
    """Test cross-reference functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock post objects
        self.mock_post = Mock()
        self.mock_post.title = "Test Article"
        self.mock_post.link = "https://dev.to/testuser/test-article-123"
        self.mock_post.slug = "test-article-123"
        self.mock_post.author = "Test User"
        self.mock_post.date = "2024-01-01"
        self.mock_post.tags = ["python", "testing", "tutorial"]
        self.mock_post.description = "A test article description"

        # Create related posts for testing
        self.related_post1 = Mock()
        self.related_post1.title = "Related Python Article"
        self.related_post1.link = "https://dev.to/testuser/related-python-456"
        self.related_post1.slug = "related-python-456"
        self.related_post1.tags = ["python", "programming"]
        self.related_post1.description = "Related article about Python"
        self.related_post1.date = "2024-01-02"

        self.related_post2 = Mock()
        self.related_post2.title = "Another Testing Article"
        self.related_post2.link = "https://dev.to/testuser/another-testing-789"
        self.related_post2.slug = "another-testing-789"
        self.related_post2.tags = ["testing", "javascript"]
        self.related_post2.description = "Another article about testing"
        self.related_post2.date = "2024-01-03"

        self.unrelated_post = Mock()
        self.unrelated_post.title = "Unrelated Article"
        self.unrelated_post.link = "https://dev.to/testuser/unrelated-999"
        self.unrelated_post.slug = "unrelated-999"
        self.unrelated_post.tags = ["javascript", "react"]
        self.unrelated_post.description = "Unrelated article"
        self.unrelated_post.date = "2024-01-04"

        self.all_posts = [self.mock_post, self.related_post1, self.related_post2, self.unrelated_post]

    def test_add_source_attribution(self):
        """Test source attribution generation."""
        attribution = add_source_attribution(self.mock_post)

        self.assertIsInstance(attribution, dict)
        self.assertEqual(attribution["source_platform"], "Dev.to")
        self.assertEqual(attribution["source_url"], "https://dev.to/testuser/test-article-123")
        self.assertEqual(attribution["attribution_text"], "Originally published on Dev.to")
        self.assertIn("Test User", attribution["author_attribution"])
        self.assertIn("attribution_html", attribution)
        self.assertIn("meta_tags", attribution)

    def test_add_source_attribution_no_link(self):
        """Test source attribution with missing link."""
        post_no_link = Mock()
        post_no_link.link = ""
        post_no_link.slug = "test-slug"

        attribution = add_source_attribution(post_no_link)
        self.assertIsInstance(attribution, dict)
        # Should return empty dict when no link available

    def test_generate_related_links(self):
        """Test related links generation."""
        related_links = generate_related_links(self.mock_post, self.all_posts)

        self.assertIsInstance(related_links, list)
        self.assertGreater(len(related_links), 0)

        # Should find related posts based on shared tags
        related_titles = [link["title"] for link in related_links]
        self.assertIn("Related Python Article", related_titles)
        self.assertIn("Another Testing Article", related_titles)

        # Should not include the current post
        self.assertNotIn("Test Article", related_titles)

        # Check structure of related link items
        for link in related_links:
            self.assertIn("title", link)
            self.assertIn("link", link)
            self.assertIn("local_link", link)
            self.assertIn("shared_tags", link)
            self.assertIn("relevance_score", link)

    def test_generate_related_links_no_tags(self):
        """Test related links generation with no tags."""
        post_no_tags = Mock()
        post_no_tags.tags = []
        post_no_tags.slug = "no-tags"

        related_links = generate_related_links(post_no_tags, self.all_posts)
        self.assertEqual(len(related_links), 0)

    def test_create_dev_to_backlinks(self):
        """Test Dev.to backlinks creation."""
        backlinks = create_dev_to_backlinks(self.mock_post)

        self.assertIsInstance(backlinks, dict)
        self.assertEqual(backlinks["canonical_url"], "https://dev.to/testuser/test-article-123")
        self.assertEqual(backlinks["source_platform"], "Dev.to")
        self.assertTrue(backlinks["rel_canonical"])
        self.assertIn("structured_data", backlinks)
        self.assertIn("backlink_html", backlinks)

    def test_create_dev_to_backlinks_no_link(self):
        """Test backlinks creation with missing link."""
        post_no_link = Mock()
        post_no_link.link = ""
        post_no_link.slug = "test-slug"

        backlinks = create_dev_to_backlinks(post_no_link)
        self.assertIsInstance(backlinks, dict)
        # Should return empty dict when no link available

    def test_enhance_post_with_cross_references(self):
        """Test comprehensive post enhancement."""
        enhanced = enhance_post_with_cross_references(self.mock_post, self.all_posts)

        self.assertIsInstance(enhanced, dict)
        self.assertIn("attribution", enhanced)
        self.assertIn("related_posts", enhanced)
        self.assertIn("backlinks", enhanced)
        self.assertIn("has_attribution", enhanced)
        self.assertIn("has_related_posts", enhanced)
        self.assertIn("has_backlinks", enhanced)

        # Check that flags are set correctly
        self.assertTrue(enhanced["has_attribution"])
        self.assertTrue(enhanced["has_related_posts"])
        self.assertTrue(enhanced["has_backlinks"])

    def test_related_links_scoring(self):
        """Test that related links are properly scored by tag overlap."""
        related_links = generate_related_links(self.mock_post, self.all_posts, max_related=10)

        # Should be sorted by relevance score (highest first)
        if len(related_links) > 1:
            for i in range(len(related_links) - 1):
                self.assertGreaterEqual(related_links[i]["relevance_score"], related_links[i + 1]["relevance_score"])

    def test_attribution_meta_tags(self):
        """Test that attribution generates proper meta tags."""
        attribution = add_source_attribution(self.mock_post)

        meta_tags = attribution.get("meta_tags", {})
        self.assertIn("article:author", meta_tags)
        self.assertIn("article:publisher", meta_tags)
        self.assertIn("content:source", meta_tags)
        self.assertEqual(meta_tags["article:author"], "Test User")
        self.assertEqual(meta_tags["article:publisher"], "Dev.to")


if __name__ == "__main__":
    unittest.main()

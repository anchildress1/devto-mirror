"""
Tests for the AIOptimizedPost module.
"""

import unittest
from unittest.mock import Mock

from devto_mirror.ai_optimization import AIOptimizedPost, DevToContentAnalyzer


class TestAIOptimizedPost(unittest.TestCase):
    """Test cases for AIOptimizedPost."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock post object
        self.mock_post = Mock()
        self.mock_post.title = "Test Post"
        self.mock_post.content_html = "<p>This is a test post with some content.</p>"
        self.mock_post.slug = "test-post"
        self.mock_post.date = "2024-01-01"
        self.mock_post.tags = ["test", "python"]
        self.mock_post.api_data = {"reading_time_minutes": 3, "public_reactions_count": 5, "tags": ["test", "python"]}

    def test_initialization(self):
        """Test AIOptimizedPost initialization."""
        optimized_post = AIOptimizedPost(self.mock_post)

        # Check that original post attributes are exposed
        self.assertEqual(optimized_post.title, "Test Post")
        self.assertEqual(optimized_post.slug, "test-post")
        self.assertEqual(optimized_post.date, "2024-01-01")

    def test_initialization_with_custom_analyzer(self):
        """Test AIOptimizedPost initialization with custom content analyzer."""
        custom_analyzer = DevToContentAnalyzer()
        optimized_post = AIOptimizedPost(self.mock_post, custom_analyzer)

        self.assertEqual(optimized_post._content_analyzer, custom_analyzer)

    def test_content_analysis_properties(self):
        """Test content analysis properties."""
        optimized_post = AIOptimizedPost(self.mock_post)

        # These should trigger content analysis
        content_type = optimized_post.content_type
        reading_time = optimized_post.reading_time_minutes
        word_count = optimized_post.word_count
        languages = optimized_post.code_languages

        self.assertIsInstance(content_type, str)
        self.assertIsInstance(reading_time, int)
        self.assertIsInstance(word_count, int)
        self.assertIsInstance(languages, list)
        self.assertGreater(reading_time, 0)

    def test_content_fingerprint(self):
        """Test content fingerprint generation."""
        optimized_post = AIOptimizedPost(self.mock_post)
        fingerprint = optimized_post.content_fingerprint

        self.assertIsInstance(fingerprint, str)
        self.assertEqual(len(fingerprint), 16)  # Should be 16 characters

        # Same post should generate same fingerprint
        optimized_post2 = AIOptimizedPost(self.mock_post)
        self.assertEqual(fingerprint, optimized_post2.content_fingerprint)

    def test_ai_metadata(self):
        """Test AI metadata dictionary."""
        optimized_post = AIOptimizedPost(self.mock_post)
        metadata = optimized_post.ai_metadata

        required_keys = [
            "content_type",
            "reading_time_minutes",
            "word_count",
            "code_languages",
            "content_fingerprint",
            "metrics",
            "data_source_flags",
            "analysis_timestamp",
        ]

        for key in required_keys:
            self.assertIn(key, metadata)

    def test_get_content_analysis(self):
        """Test content analysis retrieval."""
        optimized_post = AIOptimizedPost(self.mock_post)
        analysis = optimized_post.get_content_analysis()

        self.assertIsInstance(analysis, dict)
        self.assertIn("metrics", analysis)
        self.assertIn("content_type", analysis)
        self.assertIn("code_languages", analysis)
        self.assertIn("data_source_flags", analysis)

    def test_get_content_analysis_caching(self):
        """Test that content analysis is cached."""
        optimized_post = AIOptimizedPost(self.mock_post)

        # First call should perform analysis
        analysis1 = optimized_post.get_content_analysis()
        self.assertTrue(optimized_post._analysis_performed)

        # Second call should use cache
        analysis2 = optimized_post.get_content_analysis()
        self.assertEqual(analysis1, analysis2)

    def test_get_content_analysis_force_refresh(self):
        """Test forcing content analysis refresh."""
        optimized_post = AIOptimizedPost(self.mock_post)

        # First analysis
        analysis1 = optimized_post.get_content_analysis()

        # Force refresh
        analysis2 = optimized_post.get_content_analysis(force_refresh=True)

        # Should have same structure but timestamps may differ
        self.assertEqual(analysis1["content_type"], analysis2["content_type"])
        self.assertEqual(analysis1["metrics"], analysis2["metrics"])
        self.assertEqual(analysis1["code_languages"], analysis2["code_languages"])

    def test_to_dict(self):
        """Test conversion to dictionary."""
        # Mock the to_dict method on the post
        self.mock_post.to_dict.return_value = {"title": "Test Post", "slug": "test-post", "date": "2024-01-01"}

        optimized_post = AIOptimizedPost(self.mock_post)
        post_dict = optimized_post.to_dict()

        # Should contain original post data
        self.assertIn("title", post_dict)
        self.assertIn("slug", post_dict)

        # Should contain AI optimization data
        self.assertIn("ai_optimization", post_dict)
        ai_data = post_dict["ai_optimization"]
        self.assertIn("content_analysis", ai_data)
        self.assertIn("ai_metadata", ai_data)
        self.assertIn("optimization_applied", ai_data)

    def test_from_post_classmethod(self):
        """Test creating AIOptimizedPost using from_post class method."""
        optimized_post = AIOptimizedPost.from_post(self.mock_post)

        self.assertIsInstance(optimized_post, AIOptimizedPost)
        self.assertEqual(optimized_post.title, "Test Post")

    def test_attribute_delegation(self):
        """Test that unknown attributes are delegated to original post."""
        # Add a custom attribute to the mock post
        self.mock_post.custom_attribute = "custom_value"

        optimized_post = AIOptimizedPost(self.mock_post)

        # Should be able to access the custom attribute
        self.assertEqual(optimized_post.custom_attribute, "custom_value")

    def test_attribute_delegation_error(self):
        """Test that AttributeError is raised for non-existent attributes."""

        # Create a real object instead of Mock to test AttributeError
        class SimplePost:
            def __init__(self):
                self.title = "Test"

        real_post = SimplePost()
        optimized_post = AIOptimizedPost(real_post)

        with self.assertRaises(AttributeError):
            _ = optimized_post.non_existent_attribute

    def test_string_representation(self):
        """Test string representation methods."""
        optimized_post = AIOptimizedPost(self.mock_post)

        str_repr = str(optimized_post)
        self.assertIn("AIOptimizedPost", str_repr)
        self.assertIn("Test Post", str_repr)

        repr_str = repr(optimized_post)
        self.assertEqual(str_repr, repr_str)


if __name__ == "__main__":
    unittest.main()

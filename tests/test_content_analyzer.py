"""
Tests for the DevToContentAnalyzer module.
"""

import unittest
from unittest.mock import Mock

from devto_mirror.ai_optimization import DevToContentAnalyzer


class TestDevToContentAnalyzer(unittest.TestCase):
    """Test cases for DevToContentAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = DevToContentAnalyzer()

    def test_extract_api_metrics_with_valid_data(self):
        """Test extracting metrics from valid API data."""
        api_data = {
            "reading_time_minutes": 5,
            "public_reactions_count": 10,
            "comments_count": 3,
            "word_count": 1000,
        }

        metrics = self.analyzer.extract_api_metrics(api_data)

        self.assertEqual(metrics["reading_time_minutes"], 5)
        self.assertEqual(metrics["public_reactions_count"], 10)
        self.assertEqual(metrics["comments_count"], 3)
        self.assertEqual(metrics["word_count"], 1000)

    def test_extract_api_metrics_with_empty_data(self):
        """Test extracting metrics from empty API data."""
        metrics = self.analyzer.extract_api_metrics({})
        self.assertEqual(metrics, {})

        metrics = self.analyzer.extract_api_metrics(None)
        self.assertEqual(metrics, {})

    def test_validate_numeric_metric(self):
        """Test the _validate_numeric_metric helper method (truncates toward zero)."""
        self.assertEqual(self.analyzer._validate_numeric_metric(10, 0), 10)
        self.assertEqual(self.analyzer._validate_numeric_metric(5, 1), 5)
        self.assertEqual(self.analyzer._validate_numeric_metric(5.7, 0), 5)
        self.assertEqual(self.analyzer._validate_numeric_metric(1, 1), 1)
        self.assertEqual(self.analyzer._validate_numeric_metric(0, 0), 0)
        self.assertEqual(self.analyzer._validate_numeric_metric(-5.7, -10), -5)

        self.assertIsNone(self.analyzer._validate_numeric_metric(None, 0))
        self.assertIsNone(self.analyzer._validate_numeric_metric("string", 0))
        self.assertIsNone(self.analyzer._validate_numeric_metric([], 0))
        self.assertIsNone(self.analyzer._validate_numeric_metric({}, 0))
        self.assertIsNone(self.analyzer._validate_numeric_metric(-5, 0))
        self.assertIsNone(self.analyzer._validate_numeric_metric(0, 1))
        self.assertIsNone(self.analyzer._validate_numeric_metric(True, 0))
        self.assertIsNone(self.analyzer._validate_numeric_metric(False, 0))

    def test_calculate_fallback_metrics(self):
        """Test calculating fallback metrics from HTML content."""
        html_content = """
        <h1>Test Article</h1>
        <p>This is a test article with some content.</p>
        <pre><code class="language-python">print("hello world")</code></pre>
        <img src="test.jpg" alt="test">
        <a href="https://example.com">Link</a>
        """

        metrics = self.analyzer.calculate_fallback_metrics(html_content)

        self.assertIn("word_count", metrics)
        self.assertIn("reading_time_minutes", metrics)
        self.assertIn("content_length_chars", metrics)
        self.assertIn("code_blocks_count", metrics)
        self.assertIn("images_count", metrics)
        self.assertIn("links_count", metrics)

        self.assertGreater(metrics["word_count"], 0)
        self.assertGreater(metrics["reading_time_minutes"], 0)
        self.assertEqual(metrics["images_count"], 1)
        self.assertEqual(metrics["links_count"], 1)

    def test_extract_code_languages(self):
        """Test extracting programming languages from HTML content."""
        html_content = """
        <pre><code class="language-python">print("hello")</code></pre>
        <code class="lang-javascript">console.log("test");</code>
        <pre data-lang="typescript">interface Test {}</pre>
        """

        languages = self.analyzer.extract_code_languages(html_content)

        self.assertIn("python", languages)
        self.assertIn("javascript", languages)
        self.assertIn("typescript", languages)

    def test_normalize_language_name(self):
        """Test language name normalization."""
        test_cases = [
            ("js", "javascript"),
            ("py", "python"),
            ("ts", "typescript"),
            ("c++", "cpp"),
            ("c#", "csharp"),
            ("golang", "go"),
            ("yml", "yaml"),
            ("invalid-very-long-language-name-that-should-be-rejected", ""),
            ("", ""),
        ]

        for input_lang, expected in test_cases:
            result = self.analyzer._normalize_language_name(input_lang)
            self.assertEqual(result, expected, f"Failed for input: {input_lang}")

    def test_determine_content_type(self):
        """Test content type determination based on tags and title."""
        # Create mock post objects
        tutorial_post = Mock()
        tutorial_post.title = "How to Build a Web App"
        tutorial_post.tags = ["tutorial", "beginners"]

        discussion_post = Mock()
        discussion_post.title = "What do you think about AI?"
        discussion_post.tags = ["discuss", "opinion"]

        ai_post = Mock()
        ai_post.title = "GitHub Copilot Tips"
        ai_post.tags = ["ai", "githubcopilot"]

        # Test with API data
        api_data_tutorial = {"tags": ["tutorial", "howto"]}
        api_data_discussion = {"tags": ["discuss", "community"]}
        api_data_ai = {"tags": ["ai", "chatgpt"]}

        self.assertEqual(self.analyzer._determine_content_type(tutorial_post, api_data_tutorial), "tutorial")
        self.assertEqual(self.analyzer._determine_content_type(discussion_post, api_data_discussion), "discussion")
        self.assertEqual(self.analyzer._determine_content_type(ai_post, api_data_ai), "ai")

    def test_analyze_post_content_integration(self):
        """Test the main analyze_post_content method integration."""
        # Create mock post
        mock_post = Mock()
        mock_post.content_html = """
        <h1>Test Tutorial</h1>
        <p>This is a tutorial about Python programming.</p>
        <pre><code class="language-python">
        def hello():
            print("Hello, World!")
        </code></pre>
        """
        mock_post.title = "How to Write Python Functions"
        mock_post.tags = ["tutorial", "python"]
        mock_post.slug = "test-tutorial"

        api_data = {"reading_time_minutes": 3, "public_reactions_count": 5, "tags": ["tutorial", "python", "beginners"]}

        result = self.analyzer.analyze_post_content(mock_post, api_data)

        # Check structure
        self.assertIn("metrics", result)
        self.assertIn("content_type", result)
        self.assertIn("code_languages", result)
        self.assertIn("data_source_flags", result)
        self.assertIn("analysis_timestamp", result)

        # Check content
        self.assertEqual(result["content_type"], "tutorial")
        self.assertIn("python", result["code_languages"])
        self.assertEqual(result["metrics"]["reading_time_minutes"], 3)
        self.assertEqual(result["metrics"]["public_reactions_count"], 5)

        # Check data source flags
        self.assertEqual(result["data_source_flags"]["reading_time_source"], "api")
        self.assertTrue(result["data_source_flags"]["api_data_available"])


if __name__ == "__main__":
    unittest.main()

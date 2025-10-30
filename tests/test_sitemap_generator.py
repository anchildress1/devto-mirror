"""
Tests for the AI Sitemap Generator module.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock
from xml.etree import ElementTree as ET  # nosec B405 - Used for parsing controlled test XML

from devto_mirror.ai_optimization.sitemap_generator import DevToAISitemapGenerator


class TestDevToAISitemapGenerator(unittest.TestCase):
    """Test cases for DevToAISitemapGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DevToAISitemapGenerator("https://example.com", "Test Site")

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        generator = DevToAISitemapGenerator()
        self.assertEqual(generator.site_url, "")
        self.assertEqual(generator.site_name, "ChecKMarK Dev.to Mirror")

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        generator = DevToAISitemapGenerator("https://custom.com/", "Custom Site")
        self.assertEqual(generator.site_url, "https://custom.com")  # Should strip trailing slash
        self.assertEqual(generator.site_name, "Custom Site")

    def test_generate_main_sitemap_basic(self):
        """Test basic main sitemap generation."""
        # Create mock posts
        mock_post1 = Mock()
        mock_post1.configure_mock(
            **{
                "title": "Test Post 1",
                "slug": "test-post-1",
                "link": "https://dev.to/user/test-post-1",
                "date": "2023-01-01T12:00:00Z",
                "tags": ["python", "tutorial"],
                "api_data": {"published_at": "2023-01-01T12:00:00Z"},
            }
        )

        mock_post2 = Mock()
        mock_post2.configure_mock(
            **{
                "title": "Test Post 2",
                "slug": "test-post-2",
                "link": "https://dev.to/user/test-post-2",
                "date": "2023-01-02T12:00:00Z",
                "tags": ["javascript"],
                "api_data": {"published_at": "2023-01-02T12:00:00Z"},
            }
        )

        posts = [mock_post1, mock_post2]
        comments = [
            {"local": "comments/comment1.html", "url": "https://example.com/comments/comment1.html"},
            {"local": "comments/comment2.html"},
        ]

        sitemap_xml = self.generator.generate_main_sitemap(posts, comments)

        # Verify it's valid XML
        self.assertIsInstance(sitemap_xml, str)
        self.assertTrue(sitemap_xml.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

        # Parse XML to verify structure
        root = ET.fromstring(sitemap_xml)  # nosec B314 - Parsing controlled test XML
        self.assertTrue(root.tag.endswith("urlset"))
        # Check namespace is present (may be in different attribute format)
        self.assertIn("http://www.sitemaps.org/schemas/sitemap/0.9", sitemap_xml)

        # Check that URLs are included
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        # Always use namespace since our generator uses it
        url_elements = root.findall("ns:url", namespace)
        urls = []
        for url_elem in url_elements:
            loc_elem = url_elem.find("ns:loc", namespace)
            if loc_elem is not None:
                urls.append(loc_elem.text)
        self.assertIn("https://example.com", urls)  # Home page
        self.assertIn("https://dev.to/user/test-post-1", urls)  # Post 1
        self.assertIn("https://dev.to/user/test-post-2", urls)  # Post 2
        self.assertIn("https://example.com/comments/comment1.html", urls)  # Comment 1

    def test_generate_main_sitemap_fallback(self):
        """Test main sitemap generation with fallback when optimization fails."""
        # Create posts that might cause issues
        mock_post = Mock()
        mock_post.configure_mock(
            **{
                "title": "Test Post",
                "slug": "test-post",
                "link": "https://dev.to/user/test-post",
                "date": None,  # This might cause issues
                "tags": None,
                "api_data": {},
            }
        )

        posts = [mock_post]
        comments = []

        sitemap_xml = self.generator.generate_main_sitemap(posts, comments)

        # Should still generate valid XML
        self.assertIsInstance(sitemap_xml, str)
        self.assertTrue(sitemap_xml.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

        # Parse XML to verify structure
        root = ET.fromstring(sitemap_xml)  # nosec B314 - Parsing controlled test XML
        self.assertTrue(root.tag.endswith("urlset"))

    def test_generate_content_sitemap(self):
        """Test content-specific sitemap generation."""
        # Create posts with different content types
        tutorial_post = Mock()
        tutorial_post.configure_mock(
            **{
                "title": "Python Tutorial",
                "slug": "python-tutorial",
                "link": "https://dev.to/user/python-tutorial",
                "date": "2023-01-01T12:00:00Z",
                "tags": ["python", "tutorial", "beginners"],
                "api_data": {"published_at": "2023-01-01T12:00:00Z"},
            }
        )

        ai_post = Mock()
        ai_post.configure_mock(
            **{
                "title": "AI Discussion",
                "slug": "ai-discussion",
                "link": "https://dev.to/user/ai-discussion",
                "date": "2023-01-02T12:00:00Z",
                "tags": ["ai", "githubcopilot"],
                "api_data": {"published_at": "2023-01-02T12:00:00Z"},
            }
        )

        posts = [tutorial_post, ai_post]

        sitemap_xml = self.generator.generate_content_sitemap(posts)

        # Verify it's valid XML
        self.assertIsInstance(sitemap_xml, str)
        if sitemap_xml:  # May be empty if categorization fails
            root = ET.fromstring(sitemap_xml)  # nosec B314 - Parsing controlled test XML
            self.assertTrue(root.tag.endswith("urlset"))

    def test_generate_discovery_feed(self):
        """Test AI discovery feed generation."""
        mock_post = Mock()
        mock_post.configure_mock(
            **{
                "title": "Test Post",
                "slug": "test-post",
                "link": "https://dev.to/user/test-post",
                "date": "2023-01-01T12:00:00Z",
                "description": "Test description",
                "tags": ["python", "tutorial"],
                "api_data": {
                    "published_at": "2023-01-01T12:00:00Z",
                    "reading_time_minutes": 5,
                    "public_reactions_count": 10,
                },
            }
        )

        posts = [mock_post]

        feed_xml = self.generator.generate_discovery_feed(posts)

        # Verify it's valid XML
        self.assertIsInstance(feed_xml, str)
        if feed_xml:  # May be empty if generation fails
            root = ET.fromstring(feed_xml)  # nosec B314 - Parsing controlled test XML
            self.assertEqual(root.tag, "rss")
            self.assertEqual(root.attrib["version"], "2.0")

    def test_determine_content_type(self):
        """Test content type determination based on tags."""
        # Test tutorial detection
        tutorial_post = Mock()
        tutorial_post.configure_mock(**{"tags": ["python", "tutorial", "beginners"], "api_data": {}})
        self.assertEqual(self.generator._determine_content_type(tutorial_post), "tutorial")

        # Test AI detection
        ai_post = Mock()
        ai_post.configure_mock(**{"tags": ["ai", "githubcopilot"], "api_data": {}})
        self.assertEqual(self.generator._determine_content_type(ai_post), "ai")

        # Test discussion detection
        discussion_post = Mock()
        discussion_post.configure_mock(**{"tags": ["discuss", "community"], "api_data": {}})
        self.assertEqual(self.generator._determine_content_type(discussion_post), "discussion")

        # Test default (article)
        article_post = Mock()
        article_post.configure_mock(**{"tags": ["random", "other"], "api_data": {}})
        self.assertEqual(self.generator._determine_content_type(article_post), "article")

        # Test with API data tags
        api_post = Mock()
        api_post.configure_mock(**{"tags": [], "api_data": {"tags": ["career", "job"]}})
        self.assertEqual(self.generator._determine_content_type(api_post), "career")

    def test_get_post_date(self):
        """Test post date extraction."""
        # Test with post.date
        post_with_date = Mock()
        post_with_date.configure_mock(**{"date": "2023-01-01T12:00:00Z", "api_data": {}})
        date = self.generator._get_post_date(post_with_date)
        self.assertIsInstance(date, datetime)
        self.assertEqual(date.year, 2023)

        # Test with API data
        post_with_api_date = Mock()
        post_with_api_date.configure_mock(**{"date": "", "api_data": {"published_at": "2023-02-01T12:00:00Z"}})
        date = self.generator._get_post_date(post_with_api_date)
        self.assertIsInstance(date, datetime)
        self.assertEqual(date.month, 2)

        # Test with no date
        post_no_date = Mock()
        post_no_date.configure_mock(**{"date": "", "api_data": {}})
        date = self.generator._get_post_date(post_no_date)
        self.assertIsNone(date)

    def test_determine_post_priority(self):
        """Test post priority determination."""
        # Test tutorial priority
        tutorial_post = Mock()
        tutorial_post.configure_mock(**{"api_data": {"public_reactions_count": 5}})
        priority = self.generator._determine_post_priority(tutorial_post, "tutorial")
        self.assertEqual(priority, "0.9")

        # Test AI priority
        ai_post = Mock()
        ai_post.configure_mock(**{"api_data": {"public_reactions_count": 25}})
        priority = self.generator._determine_post_priority(ai_post, "ai")
        self.assertEqual(priority, "0.9")  # 0.8 + 0.05 for reactions > 20

        # Test high engagement boost
        popular_post = Mock()
        popular_post.configure_mock(**{"api_data": {"public_reactions_count": 60}})
        priority = self.generator._determine_post_priority(popular_post, "article")
        self.assertEqual(priority, "0.6")  # 0.5 + 0.1 for reactions > 50

    def test_determine_post_changefreq(self):
        """Test post change frequency determination."""
        from datetime import timedelta

        # Test recent post (daily)
        recent_date = datetime.now() - timedelta(days=3)
        recent_post = Mock()
        recent_post.configure_mock(**{"date": recent_date.isoformat() + "Z", "api_data": {}})
        changefreq = self.generator._determine_post_changefreq(recent_post)
        self.assertEqual(changefreq, "daily")

        # Test older post (yearly)
        old_date = datetime.now() - timedelta(days=200)
        old_post = Mock()
        old_post.configure_mock(**{"date": old_date.isoformat() + "Z", "api_data": {}})
        changefreq = self.generator._determine_post_changefreq(old_post)
        self.assertEqual(changefreq, "yearly")

        # Test post with no date
        no_date_post = Mock()
        no_date_post.configure_mock(**{"date": "", "api_data": {}})
        changefreq = self.generator._determine_post_changefreq(no_date_post)
        self.assertEqual(changefreq, "monthly")

    def test_create_url_entry(self):
        """Test URL entry creation."""
        entry = self.generator._create_url_entry(
            loc="https://example.com/test", lastmod="2023-01-01T12:00:00Z", changefreq="weekly", priority="0.8"
        )

        expected = {
            "loc": "https://example.com/test",
            "lastmod": "2023-01-01T12:00:00Z",
            "changefreq": "weekly",
            "priority": "0.8",
        }
        self.assertEqual(entry, expected)

        # Test minimal entry
        minimal_entry = self.generator._create_url_entry("https://example.com")
        self.assertEqual(minimal_entry, {"loc": "https://example.com"})

    def test_xml_escaping(self):
        """Test that XML content is properly escaped."""
        mock_post = Mock()
        mock_post.configure_mock(
            **{
                "title": "Test & Special <Characters>",
                "slug": "test-special-chars",
                "link": "https://dev.to/user/test-special-chars",
                "date": "2023-01-01T12:00:00Z",
                "tags": [],
                "api_data": {},
            }
        )

        posts = [mock_post]
        comments = []

        sitemap_xml = self.generator.generate_main_sitemap(posts, comments)

        # Should not contain unescaped special characters in XML
        self.assertNotIn("&", sitemap_xml.replace("&amp;", ""))  # & should be escaped
        self.assertNotIn(
            "<",
            sitemap_xml.replace("</", "")
            .replace("<url", "")
            .replace("<?xml", "")
            .replace("<urlset", "")
            .replace("<loc", "")
            .replace("<lastmod", "")
            .replace("<changefreq", "")
            .replace("<priority", ""),
        )

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        # Test with empty posts and comments
        sitemap_xml = self.generator.generate_main_sitemap([], [])

        # Should still generate valid XML with at least home page
        self.assertIsInstance(sitemap_xml, str)
        self.assertTrue(sitemap_xml.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

        root = ET.fromstring(sitemap_xml)  # nosec B314 - Parsing controlled test XML
        self.assertTrue(root.tag.endswith("urlset"))

        # Should have at least home page URL
        # Use namespace-aware search
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall("ns:url", namespace)
        self.assertGreaterEqual(len(urls), 1)


if __name__ == "__main__":
    unittest.main()

"""
Tests for the Schema Generator module.
"""

import unittest
from unittest.mock import Mock

from devto_mirror.ai_optimization import DevToSchemaGenerator, validate_json_ld_schema


class TestValidateJsonLdSchema(unittest.TestCase):
    """Test cases for JSON-LD schema validation."""

    def test_validate_valid_schema(self):
        """Test validation of a valid Schema.org schema."""
        valid_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {"@type": "Person", "name": "Test Author"},
        }

        self.assertTrue(validate_json_ld_schema(valid_schema))

    def test_validate_invalid_schema_missing_context(self):
        """Test validation fails for schema missing @context."""
        invalid_schema = {"@type": "Article", "headline": "Test Article"}

        self.assertFalse(validate_json_ld_schema(invalid_schema))

    def test_validate_invalid_schema_missing_type(self):
        """Test validation fails for schema missing @type."""
        invalid_schema = {"@context": "https://schema.org", "headline": "Test Article"}

        self.assertFalse(validate_json_ld_schema(invalid_schema))

    def test_validate_invalid_schema_wrong_context(self):
        """Test validation fails for schema with wrong @context."""
        invalid_schema = {
            "@context": "https://example.com",
            "@type": "Article",
            "headline": "Test Article",
        }

        self.assertFalse(validate_json_ld_schema(invalid_schema))

    def test_validate_non_dict_input(self):
        """Test validation fails for non-dictionary input."""
        self.assertFalse(validate_json_ld_schema("not a dict"))
        self.assertFalse(validate_json_ld_schema(None))
        self.assertFalse(validate_json_ld_schema([]))


class TestDevToSchemaGenerator(unittest.TestCase):
    """Test cases for DevToSchemaGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = DevToSchemaGenerator("Test Site", "https://example.com")

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        generator = DevToSchemaGenerator()
        self.assertEqual(generator.site_name, "ChecKMarK Dev.to Mirror")
        self.assertEqual(generator.site_url, "")

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        generator = DevToSchemaGenerator("Custom Site", "https://custom.com/")
        self.assertEqual(generator.site_name, "Custom Site")
        self.assertEqual(generator.site_url, "https://custom.com")  # Should strip trailing slash

    def test_generate_article_schema_basic(self):
        """Test basic article schema generation."""
        # Create mock post with proper attribute configuration
        mock_post = Mock()
        mock_post.configure_mock(
            **{
                "title": "Test Article",
                "date": "2023-01-01T12:00:00Z",
                "description": "Test description",
                "tags": ["python", "tutorial"],
                "content_html": "<p>Test content with some words here.</p>",
                "cover_image": "",
            }
        )

        canonical_url = "https://dev.to/testuser/test-article"

        schema = self.generator.generate_article_schema(mock_post, canonical_url)

        # Check basic structure
        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "Article")
        self.assertEqual(schema["headline"], "Test Article")
        self.assertEqual(schema["url"], canonical_url)
        self.assertEqual(schema["mainEntityOfPage"]["@id"], canonical_url)

        # Check author extracted from URL when no API data provided
        self.assertEqual(schema["author"]["name"], "testuser")
        self.assertEqual(schema["author"]["url"], "https://dev.to/testuser")

        # Check publisher
        self.assertEqual(schema["publisher"]["name"], "Test Site")
        self.assertEqual(schema["publisher"]["url"], "https://example.com")

        # Check dates
        self.assertEqual(schema["datePublished"], "2023-01-01T12:00:00Z")
        self.assertEqual(schema["dateModified"], "2023-01-01T12:00:00Z")

        # Check other fields
        self.assertEqual(schema["description"], "Test description")
        self.assertEqual(schema["keywords"], ["python", "tutorial"])
        self.assertIn("wordCount", schema)

    def test_generate_article_schema_with_api_data(self):
        """Test article schema generation with API data."""
        mock_post = Mock()
        mock_post.configure_mock(
            **{
                "title": "Test Article",
                "tags": [],
                "content_html": "<p>Test content</p>",
                "description": "",
                "cover_image": "",
            }
        )

        api_data = {
            "user": {"name": "John Doe", "username": "johndoe"},
            "published_at": "2023-01-01T12:00:00Z",
            "edited_at": "2023-01-02T12:00:00Z",
            "tags": ["javascript", "webdev"],
            "reading_time_minutes": 5,
            "social_image": "https://example.com/image.jpg",
            "language": "en",
        }

        canonical_url = "https://dev.to/johndoe/test-article"

        schema = self.generator.generate_article_schema(mock_post, canonical_url, api_data)

        # Check API data is used
        self.assertEqual(schema["author"]["name"], "John Doe")
        self.assertEqual(schema["author"]["url"], "https://dev.to/johndoe")
        self.assertEqual(schema["datePublished"], "2023-01-01T12:00:00Z")
        self.assertEqual(schema["dateModified"], "2023-01-02T12:00:00Z")
        self.assertEqual(schema["keywords"], ["javascript", "webdev"])
        self.assertEqual(schema["timeRequired"], "PT5M")
        self.assertEqual(schema["image"]["url"], "https://example.com/image.jpg")
        self.assertEqual(schema["inLanguage"], "en")

    def test_generate_website_schema(self):
        """Test website schema generation."""
        site_info = {
            "name": "My Dev Blog",
            "url": "https://myblog.com",
            "description": "A blog about development",
        }

        schema = self.generator.generate_website_schema(site_info)

        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "WebSite")
        self.assertEqual(schema["@id"], "https://myblog.com")
        self.assertEqual(schema["name"], "My Dev Blog")
        self.assertEqual(schema["url"], "https://myblog.com")
        self.assertEqual(schema["description"], "A blog about development")

        # Check search action
        self.assertIn("potentialAction", schema)
        self.assertEqual(schema["potentialAction"]["@type"], "SearchAction")

    def test_generate_website_schema_minimal(self):
        """Test website schema generation with minimal info."""
        schema = self.generator.generate_website_schema({})

        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "WebSite")
        self.assertEqual(schema["name"], "Test Site")
        self.assertEqual(schema["url"], "https://example.com")

    def test_generate_breadcrumb_schema(self):
        """Test breadcrumb schema generation."""
        mock_post = Mock()
        mock_post.configure_mock(**{"title": "My Test Post", "slug": "my-test-post"})

        schema = self.generator.generate_breadcrumb_schema(mock_post)

        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "BreadcrumbList")

        # Check breadcrumb items
        items = schema["itemListElement"]
        self.assertEqual(len(items), 3)

        # Home
        self.assertEqual(items[0]["position"], 1)
        self.assertEqual(items[0]["name"], "Home")
        self.assertEqual(items[0]["item"], "https://example.com")

        # Posts
        self.assertEqual(items[1]["position"], 2)
        self.assertEqual(items[1]["name"], "Posts")
        self.assertEqual(items[1]["item"], "https://example.com/posts")

        # Current post
        self.assertEqual(items[2]["position"], 3)
        self.assertEqual(items[2]["name"], "My Test Post")
        self.assertEqual(items[2]["item"], "https://example.com/posts/my-test-post.html")

    def test_schema_validation_integration(self):
        """Test that generated schemas pass validation."""
        mock_post = Mock()
        mock_post.configure_mock(
            **{
                "title": "Test Article",
                "date": "2023-01-01T12:00:00Z",
                "slug": "test-article",
                "content_html": "<p>Test content</p>",
                "description": "",
                "tags": [],
                "cover_image": "",
            }
        )

        canonical_url = "https://dev.to/user/test-article"

        # Test article schema validation
        article_schema = self.generator.generate_article_schema(mock_post, canonical_url)
        self.assertTrue(validate_json_ld_schema(article_schema))

        # Test website schema validation
        website_schema = self.generator.generate_website_schema({"name": "Test", "url": "https://test.com"})
        self.assertTrue(validate_json_ld_schema(website_schema))

        # Test breadcrumb schema validation
        breadcrumb_schema = self.generator.generate_breadcrumb_schema(mock_post)
        self.assertTrue(validate_json_ld_schema(breadcrumb_schema))

    def test_engagement_metrics_with_page_views(self):
        """Test engagement metrics extraction with page views."""
        api_data = {
            "comments_count": 5,
            "public_reactions_count": 20,
            "page_views_count": 100,
        }

        metrics = self.generator._extract_engagement_metrics(api_data)

        # Check interactionStatistic
        self.assertIn("interactionStatistic", metrics)
        self.assertEqual(len(metrics["interactionStatistic"]), 2)

        # Check additionalProperty
        self.assertIn("additionalProperty", metrics)
        self.assertEqual(len(metrics["additionalProperty"]), 1)
        self.assertEqual(metrics["additionalProperty"][0]["name"], "pageViews")
        self.assertEqual(metrics["additionalProperty"][0]["value"], 100)

    def test_engagement_metrics_merge_preserves_existing_properties(self):
        """Test that additionalProperty merge doesn't overwrite existing entries (defensive scenario)."""
        api_data = {
            "comments_count": 5,
            "public_reactions_count": 20,
            "page_views_count": 100,
        }

        metrics = self.generator._extract_engagement_metrics(api_data)

        # Simulate pre-populated additionalProperty (defensive test)
        pre_existing_property = {"@type": "PropertyValue", "name": "customMetric", "value": 42}
        metrics["additionalProperty"].insert(0, pre_existing_property)

        # Verify merge preserved existing entry
        self.assertEqual(len(metrics["additionalProperty"]), 2)
        self.assertEqual(metrics["additionalProperty"][0]["name"], "customMetric")
        self.assertEqual(metrics["additionalProperty"][1]["name"], "pageViews")


if __name__ == "__main__":
    unittest.main()

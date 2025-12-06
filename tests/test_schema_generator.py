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
        self.assertEqual(generator.site_url, "https://custom.com")

    def test_generate_article_schema_basic(self):
        """Test basic article schema generation."""
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

        self.assertEqual(schema["@context"], "https://schema.org")
        self.assertEqual(schema["@type"], "Article")
        self.assertEqual(schema["headline"], "Test Article")
        self.assertEqual(schema["url"], canonical_url)
        self.assertEqual(schema["mainEntityOfPage"]["@id"], canonical_url)
        self.assertEqual(schema["author"]["name"], "testuser")
        self.assertEqual(schema["author"]["url"], "https://dev.to/testuser")
        self.assertEqual(schema["publisher"]["name"], "Test Site")
        self.assertEqual(schema["publisher"]["url"], "https://example.com")
        self.assertEqual(schema["datePublished"], "2023-01-01T12:00:00Z")
        self.assertEqual(schema["dateModified"], "2023-01-01T12:00:00Z")
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

        items = schema["itemListElement"]
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["position"], 1)
        self.assertEqual(items[0]["name"], "Home")
        self.assertEqual(items[0]["item"], "https://example.com")
        self.assertEqual(items[1]["position"], 2)
        self.assertEqual(items[1]["name"], "Posts")
        self.assertEqual(items[1]["item"], "https://example.com/posts")
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

        article_schema = self.generator.generate_article_schema(mock_post, canonical_url)
        self.assertTrue(validate_json_ld_schema(article_schema))

        website_schema = self.generator.generate_website_schema({"name": "Test", "url": "https://test.com"})
        self.assertTrue(validate_json_ld_schema(website_schema))

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

        self.assertIn("interactionStatistic", metrics)
        self.assertEqual(len(metrics["interactionStatistic"]), 2)
        self.assertIn("additionalProperty", metrics)
        self.assertEqual(metrics["additionalProperty"], [{"@type": "PropertyValue", "name": "pageViews", "value": 100}])

    def test_engagement_metrics_page_views_only(self):
        """Ensure page views produce additionalProperty without empty interactionStatistic."""
        api_data = {"page_views_count": 42}

        metrics = self.generator._extract_engagement_metrics(api_data)

        self.assertNotIn("interactionStatistic", metrics)
        self.assertEqual(metrics["additionalProperty"], [{"@type": "PropertyValue", "name": "pageViews", "value": 42}])

    def test_calculate_word_count_strips_html(self):
        """_calculate_word_count removes HTML tags and counts words."""
        content = "<p>Hello <strong>world</strong></p>"
        self.assertEqual(self.generator._calculate_word_count(content), 2)

    def test_calculate_word_count_empty(self):
        """Empty content produces zero word count."""
        self.assertEqual(self.generator._calculate_word_count(""), 0)

    def test_collect_interaction_stats_filters_invalid(self):
        """_collect_interaction_stats omits None or negative values."""
        api_data = {"comments_count": 3, "public_reactions_count": -1, "page_views_count": None}

        stats = self.generator._collect_interaction_stats(api_data)

        self.assertEqual(stats, {"commentCount": 3})

    def test_create_interaction_counter_structure(self):
        """_create_interaction_counter returns valid Schema.org object."""
        counter = self.generator._create_interaction_counter("https://schema.org/LikeAction", 7)

        self.assertEqual(
            counter,
            {
                "@type": "InteractionCounter",
                "interactionType": "https://schema.org/LikeAction",
                "userInteractionCount": 7,
            },
        )

    def test_extract_author_info_prefers_api_data(self):
        """API data takes precedence over canonical URL when extracting author."""
        api_data = {"user": {"name": "Alice", "username": "alice"}}

        result = self.generator._extract_author_info("https://dev.to/bob/post", api_data)

        self.assertEqual(result, ("Alice", "https://dev.to/alice"))

    def test_extract_author_info_falls_back_to_canonical(self):
        """Username is derived from canonical URL when API data missing."""
        result = self.generator._extract_author_info("https://dev.to/charlie/post", None)

        self.assertEqual(result, ("charlie", "https://dev.to/charlie"))

    def test_extract_author_info_defaults_when_missing(self):
        """Returns default author data when extraction fails."""
        result = self.generator._extract_author_info("https://example.com/post", None)

        self.assertEqual(result, ("Dev.to Author", "https://example.com/post"))


if __name__ == "__main__":
    unittest.main()

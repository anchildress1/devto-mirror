"""
Tests for the AI optimization utils module.
"""

import unittest

from devto_mirror.ai_optimization.utils import validate_json_ld_schema


class TestValidateJsonLdSchema(unittest.TestCase):
    """Test cases for validate_json_ld_schema function."""

    def test_valid_article_schema(self):
        """Test validation of a valid Article schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {"@type": "Person", "name": "Test Author"},
        }

        self.assertTrue(validate_json_ld_schema(schema))

    def test_valid_website_schema(self):
        """Test validation of a valid WebSite schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Test Site",
            "url": "https://example.com",
        }

        self.assertTrue(validate_json_ld_schema(schema))

    def test_missing_context(self):
        """Test validation fails when @context is missing."""
        schema = {
            "@type": "Article",
            "headline": "Test Article",
        }

        self.assertFalse(validate_json_ld_schema(schema))

    def test_missing_type(self):
        """Test validation fails when @type is missing."""
        schema = {
            "@context": "https://schema.org",
            "headline": "Test Article",
        }

        self.assertFalse(validate_json_ld_schema(schema))

    def test_invalid_context(self):
        """Test validation fails with invalid @context."""
        schema = {
            "@context": "https://example.com",
            "@type": "Article",
            "headline": "Test Article",
        }

        self.assertFalse(validate_json_ld_schema(schema))

    def test_empty_type(self):
        """Test validation fails with empty @type."""
        schema = {
            "@context": "https://schema.org",
            "@type": "",
            "headline": "Test Article",
        }

        self.assertFalse(validate_json_ld_schema(schema))

    def test_non_dict_input(self):
        """Test validation fails with non-dictionary input."""
        self.assertFalse(validate_json_ld_schema("not a dict"))
        self.assertFalse(validate_json_ld_schema(None))
        self.assertFalse(validate_json_ld_schema([]))
        self.assertFalse(validate_json_ld_schema(123))

    def test_non_string_context(self):
        """Test validation fails with non-string @context."""
        schema = {
            "@context": {"@vocab": "https://schema.org"},
            "@type": "Article",
            "headline": "Test Article",
        }

        self.assertFalse(validate_json_ld_schema(schema))

    def test_non_string_type(self):
        """Test validation fails with non-string @type."""
        schema = {
            "@context": "https://schema.org",
            "@type": ["Article", "BlogPosting"],
            "headline": "Test Article",
        }

        self.assertFalse(validate_json_ld_schema(schema))

    def test_complex_valid_schema(self):
        """Test validation of a complex but valid schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {"@type": "Person", "name": "Test Author", "url": "https://example.com/author"},
            "publisher": {
                "@type": "Organization",
                "name": "Test Publisher",
                "logo": {"@type": "ImageObject", "url": "https://example.com/logo.png"},
            },
            "datePublished": "2023-01-01T00:00:00Z",
            "dateModified": "2023-01-02T00:00:00Z",
            "image": {"@type": "ImageObject", "url": "https://example.com/image.jpg", "width": 800, "height": 600},
            "keywords": ["test", "article", "schema"],
            "wordCount": 500,
        }

        self.assertTrue(validate_json_ld_schema(schema))


if __name__ == "__main__":
    unittest.main()

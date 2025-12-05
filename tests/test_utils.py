"""
Tests for the AI optimization utils module.
"""

import unittest

from devto_mirror.ai_optimization.utils import determine_content_type, validate_json_ld_schema


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


class TestDetermineContentType(unittest.TestCase):
    """Test cases for determine_content_type function."""

    def test_tutorial_tags(self):
        """Test tutorial content type detection."""
        self.assertEqual(determine_content_type(["python", "tutorial", "beginners"]), "tutorial")
        self.assertEqual(determine_content_type(["howto", "guide"]), "tutorial")
        self.assertEqual(determine_content_type(["walkthrough"]), "tutorial")

    def test_discussion_tags(self):
        """Test discussion content type detection."""
        self.assertEqual(determine_content_type(["discuss", "community"]), "discussion")
        self.assertEqual(determine_content_type(["watercooler", "opinion"]), "discussion")
        self.assertEqual(determine_content_type(["thoughts"]), "discussion")

    def test_career_tags(self):
        """Test career content type detection."""
        self.assertEqual(determine_content_type(["career", "job"]), "career")
        self.assertEqual(determine_content_type(["interview", "workplace"]), "career")
        self.assertEqual(determine_content_type(["professional"]), "career")

    def test_writing_tags(self):
        """Test writing content type detection."""
        self.assertEqual(determine_content_type(["writing", "blogging"]), "writing")
        self.assertEqual(determine_content_type(["writers", "content"]), "writing")

    def test_technology_tags(self):
        """Test technology content type detection."""
        self.assertEqual(determine_content_type(["technology", "tools"]), "technology")
        self.assertEqual(determine_content_type(["vscode", "webdev"]), "technology")

    def test_ai_tags(self):
        """Test AI content type detection."""
        self.assertEqual(determine_content_type(["ai", "githubcopilot"]), "ai")
        self.assertEqual(determine_content_type(["chatgpt", "machinelearning"]), "ai")
        self.assertEqual(determine_content_type(["ml"]), "ai")

    def test_productivity_tags(self):
        """Test productivity content type detection."""
        self.assertEqual(determine_content_type(["productivity", "workflow"]), "productivity")
        self.assertEqual(determine_content_type(["automation", "efficiency"]), "productivity")

    def test_challenge_tags(self):
        """Test challenge content type detection."""
        self.assertEqual(determine_content_type(["devchallenge", "challenge"]), "challenge")
        self.assertEqual(determine_content_type(["contest", "hackathon"]), "challenge")

    def test_wellness_tags(self):
        """Test wellness content type detection."""
        self.assertEqual(determine_content_type(["mentalhealth", "wellness"]), "wellness")
        self.assertEqual(determine_content_type(["burnout", "health"]), "wellness")

    def test_default_article_type(self):
        """Test default article type for unmatched tags."""
        self.assertEqual(determine_content_type(["random", "other"]), "article")
        self.assertEqual(determine_content_type(["unknown"]), "article")

    def test_empty_tags(self):
        """Test handling of empty tag list."""
        self.assertEqual(determine_content_type([]), "article")

    def test_non_list_input(self):
        """Test handling of non-list input."""
        self.assertEqual(determine_content_type(None), "article")
        self.assertEqual(determine_content_type("string"), "article")
        self.assertEqual(determine_content_type(123), "article")

    def test_case_insensitivity(self):
        """Test that tag matching is case-insensitive."""
        self.assertEqual(determine_content_type(["TUTORIAL", "Python"]), "tutorial")
        self.assertEqual(determine_content_type(["AI", "MachineLearning"]), "ai")
        self.assertEqual(determine_content_type(["Career", "JOB"]), "career")

    def test_mixed_valid_invalid_tags(self):
        """Test handling of mixed valid and invalid tags."""
        self.assertEqual(determine_content_type(["tutorial", None, "python"]), "tutorial")
        self.assertEqual(determine_content_type([123, "ai", "test"]), "ai")

    def test_priority_order(self):
        """Test that first matching content type is returned."""
        tags_with_multiple_matches = ["tutorial", "ai", "career"]
        self.assertEqual(determine_content_type(tags_with_multiple_matches), "tutorial")


if __name__ == "__main__":
    unittest.main()

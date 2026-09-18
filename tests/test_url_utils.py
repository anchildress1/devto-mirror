"""Tests for devto_mirror.core.url_utils."""

import unittest

from devto_mirror.core.url_utils import normalize_site_domain_input, resolve_home


class TestNormalizeSiteDomainInput(unittest.TestCase):
    def test_normalizes_accepted_forms_to_an_origin_with_trailing_slash(self):
        cases = {
            "example.com": "https://example.com/",
            " example.com/ ": "https://example.com/",
            "https://example.com": "https://example.com/",
            "http://example.com/blog": "http://example.com/blog/",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_site_domain_input(raw), expected)

    def test_rejects_unusable_input(self):
        cases = {"": "empty", "   ": "empty", "example.com/blog": "not a path", "https://": "Invalid"}
        for raw, message in cases.items():
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, message):
                normalize_site_domain_input(raw)


class TestResolveHome(unittest.TestCase):
    def test_prefers_site_domain_over_github_pages(self):
        self.assertEqual(resolve_home(site_domain="x.dev", gh_username="octo"), "https://x.dev/")

    def test_builds_github_pages_project_url(self):
        self.assertEqual(resolve_home(gh_username=" octo "), "https://octo.github.io/devto-mirror/")

    def test_raises_when_neither_is_set(self):
        with self.assertRaisesRegex(ValueError, "Missing SITE_DOMAIN or GH_USERNAME"):
            resolve_home(site_domain=" ", gh_username="")


if __name__ == "__main__":
    unittest.main()

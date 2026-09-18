"""Tests for devto_mirror.core.path_utils."""

import unittest

from devto_mirror.core.path_utils import sanitize_filename, sanitize_slug


class TestSanitizeFilename(unittest.TestCase):
    def test_replaces_every_unsafe_character(self):
        cases = {"ok_name-1": "ok_name-1", "../a/b": "---a-b", "a b.c": "a-b-c", "ünï": "-n-"}
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(sanitize_filename(raw), expected)

    def test_uses_custom_replacement(self):
        self.assertEqual(sanitize_filename("a/b", replacement="_"), "a_b")


class TestSanitizeSlug(unittest.TestCase):
    def test_truncates_to_max_length(self):
        self.assertEqual(sanitize_slug("a" * 200), "a" * 120)
        self.assertEqual(sanitize_slug("abcdef", max_length=3), "abc")

    def test_non_positive_max_length_disables_truncation(self):
        self.assertEqual(sanitize_slug("a" * 200, max_length=0), "a" * 200)


if __name__ == "__main__":
    unittest.main()

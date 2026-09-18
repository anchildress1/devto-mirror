#!/usr/bin/env python3
"""Unit tests for HTML sanitization helpers."""

import unittest

from devto_mirror.core.html_sanitization import sanitize_html_content


class TestHtmlSanitization(unittest.TestCase):
    """Regression tests for Dev.to embed sanitization."""

    def test_github_readme_embed_wrappers_not_escaped(self):
        html_in = (
            '<div class="ltag-github-readme-tag">'
            '<div class="readme-overview">'
            '<a href="https://github.com/anchildress1/devto-mirror">anchildress1 / devto-mirror</a>'
            "<p>My ongoing WIP 🤖 AI prompts, custom agents & instructions.</p>"
            "</div>"
            "</div>"
        )

        out = sanitize_html_content(html_in)

        # The bug: wrappers got escaped, showing raw HTML like "&lt;div class=...&gt;".
        self.assertNotIn("&lt;div", out)

        # Preserve safe wrapper tags/classes so the embed can be styled.
        self.assertIn('class="ltag-github-readme-tag"', out)
        self.assertIn('class="readme-overview"', out)

        # Content should still be present.
        self.assertIn('href="https://github.com/anchildress1/devto-mirror"', out)
        self.assertIn("My ongoing WIP", out)

    def test_script_tags_are_removed(self):
        html_in = '<p>hi</p><script>alert("nope")</script><p>bye</p>'
        out = sanitize_html_content(html_in)

        self.assertNotIn("<script", out.lower())
        self.assertNotIn("alert", out)
        self.assertIn("hi", out)
        self.assertIn("bye", out)

    def test_preserves_tables_and_inline_semantics(self):
        html_in = (
            '<table><thead><tr><th scope="col">k</th></tr></thead>'
            '<tbody><tr><td colspan="2">v</td></tr></tbody></table>'
            "<p>H<sub>2</sub>O <kbd>Ctrl</kbd> <del>old</del></p>"
        )

        self.assertEqual(sanitize_html_content(html_in), html_in)

    def test_drops_inline_styles_from_images(self):
        out = sanitize_html_content('<img src="a.png" style="position:fixed" width="1" height="1">')

        self.assertEqual(out, '<img src="a.png" width="1" height="1">')

    def test_returns_empty_string_for_empty_input(self):
        self.assertEqual(sanitize_html_content(""), "")


if __name__ == "__main__":
    unittest.main()

"""Tests for devto_mirror.core.utils"""

import unittest
from unittest.mock import patch

import devto_mirror.core.utils as utils_module


class TestFirebaseAnalyticsSnippet(unittest.TestCase):
    VALID_CONFIG = '{"apiKey": "abc", "projectId": "demo", "measurementId": "G-TEST123"}'

    def test_empty_when_env_unset(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(str(utils_module.firebase_analytics_snippet()), "")

    def test_raises_when_set_but_unusable(self):
        cases = {"not json": "Expecting value", '{"apiKey": "abc"}': "measurementId", '["G-1"]': "measurementId"}
        for raw, message in cases.items():
            with self.subTest(config=raw), patch.dict("os.environ", {"FIREBASE_WEB_CONFIG": raw}):
                with self.assertRaisesRegex(ValueError, message):
                    utils_module.firebase_analytics_snippet()

    def test_renders_snippet_when_configured(self):
        with patch.dict("os.environ", {"FIREBASE_WEB_CONFIG": self.VALID_CONFIG}):
            snippet = str(utils_module.firebase_analytics_snippet())
        self.assertIn("getAnalytics", snippet)
        self.assertIn("G-TEST123", snippet)
        self.assertIn(utils_module.FIREBASE_SDK_VERSION, snippet)

    def test_injected_into_every_page_through_the_base_template(self):
        context = {"home": "https://x/", "username": "u", "site_name": "u", "default_image": "i"}
        with patch.dict("os.environ", {"FIREBASE_WEB_CONFIG": self.VALID_CONFIG}):
            html = utils_module.env.get_template("index.html").render(posts=[], comments=[], **context)
        self.assertIn("G-TEST123", html)


if __name__ == "__main__":
    unittest.main()

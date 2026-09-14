"""Tests for devto_mirror.core.api_client."""

import os
import unittest
from unittest.mock import MagicMock, patch

import requests

from devto_mirror.core import api_client
from tests.factories import make_article, make_summary


def _response(status: int = 200, payload=None, headers: dict | None = None) -> MagicMock:
    response = MagicMock(status_code=status, headers=headers or {}, url="https://dev.to/api/x")
    response.json.return_value = payload
    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(f"{status} error", response=response)
    return response


class TestCreateSession(unittest.TestCase):
    def test_sets_forem_headers_without_api_key_when_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            session = api_client.create_session()
        self.assertEqual(session.headers["Accept"], "application/vnd.forem.api-v1+json")
        self.assertNotIn("api-key", session.headers)

    def test_adds_api_key_header_when_devto_key_set(self):
        with patch.dict(os.environ, {"DEVTO_KEY": "secret"}, clear=True):
            session = api_client.create_session()
        self.assertEqual(session.headers["api-key"], "secret")


class TestGetJson(unittest.TestCase):
    def setUp(self):
        self.sleep = self.enterContext(patch.object(api_client.time, "sleep"))
        self.session = MagicMock()

    def test_returns_decoded_json_on_success(self):
        self.session.get.return_value = _response(payload=[{"id": 1}])

        result = api_client.get_json(self.session, "https://dev.to/api/articles", {"page": 1})

        self.assertEqual(result, [{"id": 1}])
        self.session.get.assert_called_once_with("https://dev.to/api/articles", params={"page": 1}, timeout=30)
        self.sleep.assert_not_called()

    def test_retries_transient_network_errors_with_backoff(self):
        for error in (
            requests.Timeout("slow"),
            requests.ConnectionError("reset"),
            requests.exceptions.ChunkedEncodingError("dropped mid-body"),
        ):
            with self.subTest(error=type(error).__name__):
                self.sleep.reset_mock()
                self.session.get.side_effect = [error, error, _response(payload={"ok": True})]

                self.assertEqual(api_client.get_json(self.session, "u"), {"ok": True})
                self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [1.0, 2.0])

    def test_honors_numeric_retry_after_on_429(self):
        self.session.get.side_effect = [_response(429, headers={"Retry-After": "7"}), _response(payload=[])]

        self.assertEqual(api_client.get_json(self.session, "u"), [])
        self.sleep.assert_called_once_with(7.0)

    def test_clamps_retry_after_between_zero_and_max_wait(self):
        for header, expected in (("3600", api_client.MAX_RETRY_WAIT), ("-5", 0.0)):
            with self.subTest(retry_after=header):
                self.sleep.reset_mock()
                self.session.get.side_effect = [_response(429, headers={"Retry-After": header}), _response(payload=[])]

                api_client.get_json(self.session, "u")

                self.sleep.assert_called_once_with(expected)

    def test_falls_back_to_backoff_when_retry_after_is_http_date(self):
        headers = {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}
        self.session.get.side_effect = [_response(503, headers=headers), _response(payload=[])]

        api_client.get_json(self.session, "u")

        self.sleep.assert_called_once_with(1.0)

    def test_raises_last_error_after_exhausting_attempts(self):
        self.session.get.side_effect = [_response(502)] * 3

        with self.assertRaisesRegex(requests.HTTPError, "502"):
            api_client.get_json(self.session, "u", attempts=3)
        self.assertEqual(self.session.get.call_count, 3)
        self.assertEqual(self.sleep.call_count, 2)

    def test_raises_timeout_after_exhausting_attempts(self):
        self.session.get.side_effect = requests.Timeout("slow")

        with self.assertRaises(requests.Timeout):
            api_client.get_json(self.session, "u", attempts=2)
        self.assertEqual(self.session.get.call_count, 2)

    def test_raises_immediately_on_non_retryable_status(self):
        self.session.get.return_value = _response(404)

        with self.assertRaisesRegex(requests.HTTPError, "404"):
            api_client.get_json(self.session, "u")
        self.session.get.assert_called_once()
        self.sleep.assert_not_called()


class TestListArticles(unittest.TestCase):
    def test_pages_until_a_short_page(self):
        self.enterContext(patch.object(api_client.time, "sleep"))
        session = MagicMock()
        full_page = [make_summary(i % 28 + 1) for i in range(api_client.PER_PAGE)]
        session.get.side_effect = [_response(payload=full_page), _response(payload=[make_summary(1)])]

        result = api_client.list_articles(session, "ash")

        self.assertEqual(len(result), api_client.PER_PAGE + 1)
        pages = [c.kwargs["params"]["page"] for c in session.get.call_args_list]
        self.assertEqual(pages, [1, 2])
        self.assertEqual(session.get.call_args.kwargs["params"]["username"], "ash")

    def test_rejects_non_list_listing_payload(self):
        session = MagicMock()
        session.get.return_value = _response(payload={"error": "not found", "status": 404})

        with self.assertRaisesRegex(ValueError, "Unexpected listing payload for page 1"):
            api_client.list_articles(session, "ash")

    def test_returns_empty_list_for_user_without_articles(self):
        session = MagicMock()
        session.get.return_value = _response(payload=[])

        self.assertEqual(api_client.list_articles(session, "ash"), [])
        session.get.assert_called_once()


class TestSyncArticles(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(api_client.time, "sleep"))
        self.session = MagicMock()
        self.session.__enter__.return_value = self.session
        self.enterContext(patch.object(api_client, "create_session", return_value=self.session))
        self.listing: list[dict] = []
        self.full: dict[int, dict] = {}
        self.session.get.side_effect = self._route

    def _route(self, url, params=None, timeout=None):
        if url == api_client.API_URL:
            return _response(payload=self.listing)
        article_id = int(url.rsplit("/", 1)[1])
        return _response(payload=dict(self.full[article_id])) if article_id in self.full else _response(500)

    def _fetched_ids(self) -> list[int]:
        return [
            int(c.args[0].rsplit("/", 1)[1]) for c in self.session.get.call_args_list if c.args[0] != api_client.API_URL
        ]

    def test_reuses_stored_article_when_listing_shows_no_new_activity(self):
        stored = make_article(1, body_html="<p>cached</p>")
        self.listing = [make_summary(1)]

        result = api_client.sync_articles("ash", [stored])

        self.assertEqual(result, [stored])
        self.assertEqual(self._fetched_ids(), [])

    def test_refetches_article_edited_since_it_was_stored(self):
        self.listing = [make_summary(1, edited_at="2026-02-01T00:00:00Z")]
        self.full[1] = make_article(1, edited_at="2026-02-01T00:00:00Z", body_html="<p>new</p>")

        result = api_client.sync_articles("ash", [make_article(1, body_html="<p>old</p>")])

        self.assertEqual(result[0]["body_html"], "<p>new</p>")
        self.assertEqual(self._fetched_ids(), [1])

    def test_fetches_new_articles_and_strips_markdown_body(self):
        self.listing = [make_summary(2)]
        self.full[2] = make_article(2, body_markdown="# huge")

        result = api_client.sync_articles("ash", [])

        self.assertEqual([a["id"] for a in result], [2])
        self.assertNotIn("body_markdown", result[0])

    def test_drops_and_logs_stored_articles_no_longer_listed(self):
        self.listing = [make_summary(1), make_summary(2)]

        with self.assertLogs(api_client.logger, "WARNING") as logs:
            result = api_client.sync_articles("ash", [make_article(1), make_article(2), make_article(9)])

        self.assertEqual([a["id"] for a in result], [1, 2])
        self.assertIn("Dropping article 9 (https://dev.to/ash/post-9)", logs.output[0])

    def test_refuses_when_more_than_half_of_the_store_vanishes(self):
        self.listing = [make_summary(1)]
        stored = [make_article(1), make_article(2), make_article(3)]

        with self.assertLogs(api_client.logger, "WARNING"), self.assertRaisesRegex(RuntimeError, "2 of 3 stored"):
            api_client.sync_articles("ash", stored)

    def test_skips_articles_listed_twice_across_pages(self):
        self.listing = [make_summary(1), make_summary(2), make_summary(1)]
        self.full = {1: make_article(1), 2: make_article(2)}

        result = api_client.sync_articles("ash", [])

        self.assertEqual([a["id"] for a in result], [1, 2])
        self.assertEqual(self._fetched_ids(), [1, 2])

    def test_refetches_store_entries_without_a_body(self):
        self.listing = [make_summary(1)]
        self.full[1] = make_article(1)
        legacy = {"id": 1, "title": "Post 1", "content_html": "<p>x</p>"}

        api_client.sync_articles("ash", [legacy])

        self.assertEqual(self._fetched_ids(), [1])

    def test_propagates_full_fetch_failure_instead_of_returning_partial_results(self):
        self.listing = [make_summary(1), make_summary(2)]
        self.full[1] = make_article(1)

        with self.assertRaisesRegex(requests.HTTPError, "500"):
            api_client.sync_articles("ash", [])
        self.assertEqual(self._fetched_ids(), [1] + [2] * 4)

    def test_propagates_listing_failure(self):
        self.session.get.side_effect = requests.ConnectionError("down")
        stored = [make_article(1)]

        with self.assertRaises(requests.ConnectionError):
            api_client.sync_articles("ash", stored)


if __name__ == "__main__":
    unittest.main()

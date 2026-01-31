import unittest
from types import SimpleNamespace

from devto_mirror.ai_optimization.cross_reference import generate_related_links
from devto_mirror.core.url_utils import (
    build_post_url,
    build_site_urls,
    normalize_site_domain_input,
    post_page_href,
)


class TestSiteUrlUtils(unittest.TestCase):
    def test_normalize_site_domain_bare_domain(self):
        self.assertEqual(normalize_site_domain_input("example.com"), "https://example.com/")

    def test_normalize_site_domain_keeps_scheme(self):
        self.assertEqual(normalize_site_domain_input("https://example.com"), "https://example.com/")
        self.assertEqual(normalize_site_domain_input("https://example.com/"), "https://example.com/")

    def test_normalize_site_domain_allows_path_when_scheme_present(self):
        self.assertEqual(normalize_site_domain_input("https://example.com/blog"), "https://example.com/blog/")

    def test_normalize_site_domain_rejects_path_without_scheme(self):
        with self.assertRaises(ValueError):
            normalize_site_domain_input("example.com/blog")

    def test_build_site_urls_prefers_site_domain(self):
        urls = build_site_urls(site_domain="example.com", gh_username="ignored")
        self.assertEqual(urls.home, "https://example.com/")
        self.assertEqual(urls.root_home, "https://example.com/")

    def test_build_site_urls_gh_pages(self):
        urls = build_site_urls(gh_username="octocat")
        self.assertEqual(urls.home, "https://octocat.github.io/devto-mirror/")
        self.assertEqual(urls.root_home, "https://octocat.github.io/")

    def test_build_site_urls_validation_fallback_user(self):
        urls = build_site_urls(fallback_gh_username="user")
        self.assertEqual(urls.home, "https://user.github.io/devto-mirror/")
        self.assertEqual(urls.root_home, "https://user.github.io/")

    def test_build_site_urls_missing_raises(self):
        with self.assertRaises(ValueError):
            build_site_urls()

    def test_post_page_href_basic(self):
        self.assertEqual(post_page_href("hello"), "hello.html")

    def test_post_page_href_strips_posts_prefix_and_html_ext(self):
        self.assertEqual(post_page_href("posts/hello"), "hello.html")
        self.assertEqual(post_page_href("posts/hello.html"), "hello.html")

    def test_post_page_href_rejects_empty(self):
        with self.assertRaises(ValueError):
            post_page_href("")

    def test_post_page_href_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            post_page_href("posts/../pwn")

    def test_build_post_url_works_with_or_without_trailing_slash(self):
        self.assertEqual(
            build_post_url("https://octocat.github.io/devto-mirror", "hello"),
            "https://octocat.github.io/devto-mirror/posts/hello.html",
        )
        self.assertEqual(
            build_post_url("https://octocat.github.io/devto-mirror/", "posts/hello.html"),
            "https://octocat.github.io/devto-mirror/posts/hello.html",
        )


class TestRelatedLinksHref(unittest.TestCase):
    def test_generate_related_links_does_not_duplicate_posts_segment(self):
        current = SimpleNamespace(slug="current", tags=["python"], title="Current")
        other = SimpleNamespace(slug="other-1", tags=["python"], title="Other", link="https://dev.to/u/other-1")

        related = generate_related_links(current, [current, other], max_related=5)
        self.assertEqual(len(related), 1)

        # This is the regression: from a /posts/*.html page, href="posts/x.html" becomes /posts/posts/x.html.
        self.assertEqual(related[0]["local_link"], "other-1.html")


if __name__ == "__main__":
    unittest.main()

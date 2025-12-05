"""
Schema Generator Module for AI Optimization

This module provides JSON-LD structured data generation for Dev.to mirror sites,
implementing Schema.org compliant markup for articles, websites, and breadcrumb
navigation to enhance AI crawler understanding.

Extracted from scripts/ai_optimization.py as part of package migration.
"""

import logging
import re
from typing import Any, Dict, Optional, Tuple

from .utils import validate_json_ld_schema

logger = logging.getLogger(__name__)


class DevToSchemaGenerator:
    """
    Generates Schema.org compliant JSON-LD structured data for Dev.to mirror sites.

    Optimized for AI crawlers while maintaining compatibility with existing templates.
    """

    def __init__(self, site_name: str = "ChecKMarK Dev.to Mirror", site_url: str = ""):
        """
        Initialize schema generator with site information.

        Args:
            site_name: Name of the mirror site for publisher information
            site_url: Base URL of the mirror site
        """
        self.site_name = site_name
        self.site_url = site_url.rstrip("/")

    def _extract_author_info(self, canonical_url: str, api_data: Optional[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Extract author name and URL from API data or canonical URL.

        Args:
            canonical_url: Canonical URL pointing to original Dev.to post
            api_data: Optional original Dev.to API response data

        Returns:
            Tuple of (author_name, author_url)
        """
        if api_data and "user" in api_data:
            user_data = api_data["user"]
            author_name = user_data.get("name", user_data.get("username", "Dev.to Author"))
            username = user_data.get("username")
            if username:
                return author_name, f"https://dev.to/{username}"

        if canonical_url:
            try:
                url_parts = canonical_url.split("/")
                if len(url_parts) >= 4 and "dev.to" in canonical_url:
                    username = url_parts[3]
                    return username, f"https://dev.to/{username}"
            except Exception:
                logger.debug("Failed to extract username from canonical URL")

        return "Dev.to Author", canonical_url

    def _extract_dates(self, post: Any, api_data: Optional[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Extract and format published and modified dates.

        Args:
            post: Post object containing article data
            api_data: Optional original Dev.to API response data

        Returns:
            Tuple of (published_date, modified_date)
        """
        published_date = ""
        if api_data:
            published_date = api_data.get("published_at", "")
        if not published_date:
            published_date = getattr(post, "date", "")

        published_date = self._ensure_iso_format(published_date)

        modified_date = published_date
        if api_data and api_data.get("edited_at"):
            modified_date = self._ensure_iso_format(api_data["edited_at"])

        return published_date, modified_date

    def _ensure_iso_format(self, date_str: str) -> str:
        """
        Ensure date string is in ISO format with timezone.

        Args:
            date_str: Date string to format

        Returns:
            ISO formatted date string with timezone
        """
        if isinstance(date_str, str) and date_str:
            if not date_str.endswith("Z") and "+" not in date_str and "T" in date_str:
                return date_str + "Z"
        return date_str

    def _extract_image(self, post: Any, api_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract image information for the article.

        Args:
            post: Post object containing article data
            api_data: Optional original Dev.to API response data

        Returns:
            Image schema dictionary or None
        """
        image_url = ""
        if api_data:
            image_url = api_data.get("social_image") or api_data.get("cover_image", "")
        if not image_url:
            image_url = getattr(post, "cover_image", "")

        if image_url:
            return {"@type": "ImageObject", "url": image_url, "width": 1000, "height": 500}
        return None

    def _extract_tags(self, post: Any, api_data: Optional[Dict[str, Any]]) -> list:
        """
        Extract tags/keywords from post or API data.

        Args:
            post: Post object containing article data
            api_data: Optional original Dev.to API response data

        Returns:
            List of tags
        """
        tags = []
        if api_data:
            tags = api_data.get("tags", [])
        if not tags:
            tags = getattr(post, "tags", [])
        return tags if isinstance(tags, list) else []

    def _calculate_word_count(self, content_html: str) -> int:
        """
        Calculate word count from HTML content.

        Args:
            content_html: HTML content string

        Returns:
            Word count
        """
        if not content_html:
            return 0
        text_content = re.sub(r"<[^>]+>", "", content_html)
        return len(text_content.split())

    def _extract_engagement_metrics(self, api_data: Optional[Dict[str, Any]], schema: Dict[str, Any]) -> None:
        """
        Extract and add engagement metrics to schema.

        Args:
            api_data: Optional original Dev.to API response data
            schema: Schema dictionary to update
        """
        if not api_data:
            return

        interaction_stats = {}
        comments_count = api_data.get("comments_count")
        if comments_count is not None and comments_count >= 0:
            interaction_stats["commentCount"] = comments_count

        reactions_count = api_data.get("public_reactions_count")
        if reactions_count is not None and reactions_count >= 0:
            interaction_stats["interactionCount"] = reactions_count

        page_views = api_data.get("page_views_count")
        if page_views is not None and page_views >= 0:
            interaction_stats["pageViews"] = page_views

        if not interaction_stats:
            return

        schema["interactionStatistic"] = []

        if "commentCount" in interaction_stats:
            schema["interactionStatistic"].append(
                {
                    "@type": "InteractionCounter",
                    "interactionType": "https://schema.org/CommentAction",
                    "userInteractionCount": interaction_stats["commentCount"],
                }
            )

        if "interactionCount" in interaction_stats:
            schema["interactionStatistic"].append(
                {
                    "@type": "InteractionCounter",
                    "interactionType": "https://schema.org/LikeAction",
                    "userInteractionCount": interaction_stats["interactionCount"],
                }
            )

        if "pageViews" in interaction_stats:
            schema["additionalProperty"] = schema.get("additionalProperty", [])
            schema["additionalProperty"].append(
                {"@type": "PropertyValue", "name": "pageViews", "value": interaction_stats["pageViews"]}
            )

    def generate_article_schema(self, post: Any, canonical_url: str, api_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate Schema.org Article markup for a blog post.

        Args:
            post: Post object containing article data
            canonical_url: Canonical URL pointing to original Dev.to post
            api_data: Optional original Dev.to API response data

        Returns:
            Dictionary containing JSON-LD Article schema
        """
        author_name, author_url = self._extract_author_info(canonical_url, api_data)
        published_date, modified_date = self._extract_dates(post, api_data)

        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": getattr(post, "title", "Untitled"),
            "author": {"@type": "Person", "name": author_name, "url": author_url},
            "publisher": {"@type": "Organization", "name": self.site_name, "url": self.site_url or canonical_url},
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical_url},
            "url": canonical_url,
        }

        if published_date:
            schema["datePublished"] = published_date
            schema["dateModified"] = modified_date

        description = getattr(post, "description", "")
        if description:
            schema["description"] = description

        image = self._extract_image(post, api_data)
        if image:
            schema["image"] = image

        tags = self._extract_tags(post, api_data)
        if tags:
            schema["keywords"] = tags

        if api_data and "reading_time_minutes" in api_data:
            reading_time = api_data["reading_time_minutes"]
            if reading_time and reading_time > 0:
                schema["timeRequired"] = f"PT{reading_time}M"

        word_count = self._calculate_word_count(getattr(post, "content_html", ""))
        if word_count > 0:
            schema["wordCount"] = word_count

        if api_data and "language" in api_data:
            schema["inLanguage"] = api_data["language"]

        self._extract_engagement_metrics(api_data, schema)

        if validate_json_ld_schema(schema):
            return schema

        logger.warning("Generated article schema failed validation")
        return {}

    def generate_website_schema(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Schema.org WebSite markup for site-level structured data.

        Args:
            site_info: Dictionary containing site metadata (name, url, description)

        Returns:
            Dictionary containing JSON-LD WebSite schema
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": site_info.get("url", self.site_url),
            "name": site_info.get("name", self.site_name),
            "url": site_info.get("url", self.site_url),
        }

        # Add description if provided
        description = site_info.get("description")
        if description:
            schema["description"] = description

        # Add search action for the site
        if self.site_url:
            schema["potentialAction"] = {
                "@type": "SearchAction",
                "target": {"@type": "EntryPoint", "urlTemplate": f"{self.site_url}/?q={{search_term_string}}"},
                "query-input": "required name=search_term_string",
            }

        # Validate schema before returning
        if validate_json_ld_schema(schema):
            return schema
        else:
            logger.warning("Generated website schema failed validation")
            return {}

    def generate_breadcrumb_schema(self, post: Any) -> Dict[str, Any]:
        """
        Generate Schema.org BreadcrumbList markup for navigation context.

        Args:
            post: Post object for breadcrumb context

        Returns:
            Dictionary containing JSON-LD BreadcrumbList schema
        """
        breadcrumbs = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": self.site_url or "/"},
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Posts",
                "item": f"{self.site_url}/posts" if self.site_url else "/posts",
            },
        ]

        # Add the current post as the final breadcrumb
        post_title = getattr(post, "title", "Post")
        post_slug = getattr(post, "slug", "post")
        breadcrumbs.append(
            {
                "@type": "ListItem",
                "position": 3,
                "name": post_title,
                "item": f"{self.site_url}/posts/{post_slug}.html" if self.site_url else f"/posts/{post_slug}.html",
            }
        )

        schema = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": breadcrumbs}

        # Validate schema before returning
        if validate_json_ld_schema(schema):
            return schema
        else:
            logger.warning("Generated breadcrumb schema failed validation")
            return {}

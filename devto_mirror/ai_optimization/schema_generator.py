"""
Schema Generator Module for AI Optimization

This module provides JSON-LD structured data generation for Dev.to mirror sites,
implementing Schema.org compliant markup for articles, websites, and breadcrumb
navigation to enhance AI crawler understanding.

Extracted from scripts/ai_optimization.py as part of package migration.
"""

import json
import logging
from typing import Any, Dict

# Configure logging for schema generation
logger = logging.getLogger(__name__)


def validate_json_ld_schema(schema: Dict[str, Any]) -> bool:
    """
    Validate JSON-LD schema for basic Schema.org compliance.

    Args:
        schema: Dictionary containing JSON-LD schema

    Returns:
        True if schema appears valid, False otherwise
    """
    try:
        # Check for required Schema.org fields
        if not isinstance(schema, dict):
            return False

        # Must have @context and @type
        if "@context" not in schema or "@type" not in schema:
            return False

        # @context should be Schema.org
        context = schema.get("@context")
        if not isinstance(context, str) or "schema.org" not in context:
            return False

        # @type should be a valid Schema.org type
        schema_type = schema.get("@type")
        if not isinstance(schema_type, str) or not schema_type:
            return False

        # Try to serialize to JSON to ensure it's valid
        json.dumps(schema)

        return True

    except Exception as e:
        logger.warning(f"JSON-LD schema validation failed: {e}")
        return False


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
        # Extract author information from API data if available
        author_name = "Dev.to Author"
        author_url = canonical_url

        if api_data and "user" in api_data:
            user_data = api_data["user"]
            author_name = user_data.get("name", user_data.get("username", "Dev.to Author"))
            username = user_data.get("username")
            if username:
                author_url = f"https://dev.to/{username}"
        elif canonical_url:
            # Extract username from Dev.to URL pattern: https://dev.to/username/post-slug
            try:
                url_parts = canonical_url.split("/")
                if len(url_parts) >= 4 and "dev.to" in canonical_url:
                    username = url_parts[3]  # Username from URL
                    author_name = username
                    author_url = f"https://dev.to/{username}"
            except Exception:
                logger.debug("Failed to extract username from canonical URL")
        elif canonical_url:
            # Extract username from Dev.to URL pattern: https://dev.to/username/post-slug
            try:
                url_parts = canonical_url.split("/")
                if len(url_parts) >= 4 and "dev.to" in canonical_url:
                    username = url_parts[3]  # Username from URL
                    author_name = username
                    author_url = f"https://dev.to/{username}"
            except Exception:
                logger.debug("Failed to extract username from canonical URL")

        # Get post dates - prefer API data, fallback to Post object
        published_date = ""
        if api_data:
            published_date = api_data.get("published_at", "")
        if not published_date:
            published_date = getattr(post, "date", "")

        # Ensure ISO format with timezone
        if isinstance(published_date, str) and published_date:
            if not published_date.endswith("Z") and "+" not in published_date and "T" in published_date:
                published_date = published_date + "Z"

        # Build the article schema
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": getattr(post, "title", "Untitled"),
            "author": {"@type": "Person", "name": author_name, "url": author_url},
            "publisher": {"@type": "Organization", "name": self.site_name, "url": self.site_url or canonical_url},
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical_url},
            "url": canonical_url,
        }

        # Add dates if available
        if published_date:
            schema["datePublished"] = published_date
            # Use edited_at if available, otherwise use published_at
            edited_date = published_date
            if api_data and api_data.get("edited_at"):
                edited_date = api_data["edited_at"]
                if not edited_date.endswith("Z") and "+" not in edited_date and "T" in edited_date:
                    edited_date = edited_date + "Z"
            schema["dateModified"] = edited_date

        # Add description if available
        description = getattr(post, "description", "")
        if description:
            schema["description"] = description

        # Add images - prefer social_image from API, fallback to cover_image
        image_url = ""
        if api_data:
            image_url = api_data.get("social_image") or api_data.get("cover_image", "")
        if not image_url:
            image_url = getattr(post, "cover_image", "")

        if image_url:
            schema["image"] = {
                "@type": "ImageObject",
                "url": image_url,
                "width": 1000,  # Default dimensions for Dev.to images
                "height": 500,
            }

        # Add tags as keywords - prefer API data
        tags = []
        if api_data:
            # Dev.to API provides tags as array
            tags = api_data.get("tags", [])
        if not tags:
            tags = getattr(post, "tags", [])

        if tags and isinstance(tags, list):
            schema["keywords"] = tags

        # Add reading time if available from API
        if api_data and "reading_time_minutes" in api_data:
            reading_time = api_data["reading_time_minutes"]
            if reading_time and reading_time > 0:
                schema["timeRequired"] = f"PT{reading_time}M"  # ISO 8601 duration format

        # Add word count estimation from content
        content_html = getattr(post, "content_html", "")
        if content_html:
            # Basic word count estimation
            import re

            text_content = re.sub(r"<[^>]+>", "", content_html)
            word_count = len(text_content.split())
            if word_count > 0:
                schema["wordCount"] = word_count

        # Add language if available from API
        if api_data and "language" in api_data:
            schema["inLanguage"] = api_data["language"]

        # Validate schema before returning
        if validate_json_ld_schema(schema):
            return schema
        else:
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

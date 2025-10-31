"""
Metadata Enhancement Module for AI Optimization

This module provides metadata enhancement capabilities for Dev.to mirror sites,
adding AI-specific meta tags while preserving existing OpenGraph, Twitter Card,
and LinkedIn meta tags from current templates.
"""

import hashlib
import logging
import re
from typing import Any, Dict

# Configure logging
logger = logging.getLogger(__name__)


class DevToMetadataEnhancer:
    """
    Metadata enhancer for Dev.to mirror sites.

    Adds AI-specific meta tags while preserving all existing OpenGraph,
    Twitter Card, and LinkedIn meta tags from current templates.
    """

    def __init__(self, site_name: str = "ChecKMarK Dev.to Mirror", site_url: str = ""):
        """
        Initialize metadata enhancer with site information.

        Args:
            site_name: Name of the mirror site
            site_url: Base URL of the mirror site
        """
        self.site_name = site_name
        self.site_url = site_url.rstrip("/")

    def enhance_post_metadata(self, post: Any) -> Dict[str, str]:
        """
        Generate enhanced metadata dictionary for a blog post.

        Args:
            post: Post object containing article data

        Returns:
            Dictionary of meta tag name/content pairs for AI optimization
        """
        metadata = {}

        # Add article-specific meta tags
        metadata.update(self._add_article_meta_tags(post))

        # Add AI-specific meta tags
        metadata = self.add_ai_specific_tags(metadata)

        # Add source attribution metadata
        metadata.update(self.add_source_attribution_metadata(post))

        # Add content fingerprint
        content_fingerprint = self.generate_content_fingerprint(post)
        if content_fingerprint:
            metadata["content-fingerprint"] = content_fingerprint

        return metadata

    def _add_article_meta_tags(self, post: Any) -> Dict[str, str]:
        """
        Add article-specific meta tags (article:author, article:published_time, etc.).

        Args:
            post: Post object containing article data

        Returns:
            Dictionary of article meta tags
        """
        metadata = {}

        # Extract author information
        author_name = getattr(post, "author", "")
        if not author_name:
            # Try to extract from API data if available
            api_data = getattr(post, "api_data", {})
            if api_data and "user" in api_data:
                user_data = api_data["user"]
                author_name = user_data.get("name", user_data.get("username", ""))

        if author_name:
            metadata["article:author"] = author_name

        # Add published time
        published_date = getattr(post, "date", "")
        if not published_date:
            # Try to get from API data
            api_data = getattr(post, "api_data", {})
            if api_data:
                published_date = api_data.get("published_at", "")

        if published_date:
            # Ensure ISO format with timezone
            if isinstance(published_date, str) and published_date:
                if not published_date.endswith("Z") and "+" not in published_date and "T" in published_date:
                    published_date = published_date + "Z"
            metadata["article:published_time"] = published_date

        # Add modified time if available
        api_data = getattr(post, "api_data", {})
        if api_data and api_data.get("edited_at"):
            edited_date = api_data["edited_at"]
            if not edited_date.endswith("Z") and "+" not in edited_date and "T" in edited_date:
                edited_date = edited_date + "Z"
            metadata["article:modified_time"] = edited_date

        # Add content type
        content_type = self._determine_content_type(post)
        if content_type:
            metadata["content-type"] = content_type

        return metadata

    def _determine_content_type(self, post: Any) -> str:
        """
        Determine the content type of the post based on tags and content.

        Args:
            post: Post object to analyze

        Returns:
            String indicating content type (tutorial, article, discussion, etc.)
        """
        # Get tags from post or API data
        tags = getattr(post, "tags", [])
        if not tags:
            api_data = getattr(post, "api_data", {})
            if api_data:
                tags = api_data.get("tags", [])

        if not isinstance(tags, list):
            tags = []

        # Convert tags to lowercase for comparison
        tags_lower = [tag.lower() for tag in tags if isinstance(tag, str)]

        # Determine content type based on actual Dev.to tags
        if any(tag in tags_lower for tag in ["tutorial", "howto", "guide", "walkthrough", "beginners"]):
            return "tutorial"
        elif any(
            tag in tags_lower for tag in ["discuss", "discussion", "watercooler", "community", "opinion", "thoughts"]
        ):
            return "discussion"
        elif any(tag in tags_lower for tag in ["career", "job", "interview", "workplace", "professional"]):
            return "career"
        elif any(tag in tags_lower for tag in ["writing", "writers", "blogging", "content"]):
            return "writing"
        elif any(tag in tags_lower for tag in ["technology", "tooling", "tools", "vscode", "webdev"]):
            return "technology"
        elif any(tag in tags_lower for tag in ["ai", "githubcopilot", "chatgpt", "machinelearning", "ml"]):
            return "ai"
        elif any(tag in tags_lower for tag in ["productivity", "workflow", "automation", "efficiency"]):
            return "productivity"
        elif any(tag in tags_lower for tag in ["devchallenge", "challenge", "contest", "hackathon"]):
            return "challenge"
        elif any(tag in tags_lower for tag in ["mentalhealth", "wellness", "burnout", "health"]):
            return "wellness"
        else:
            return "article"

    def add_ai_specific_tags(self, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Add AI-specific meta tags to existing metadata.

        Args:
            metadata: Existing metadata dictionary

        Returns:
            Enhanced metadata with AI-specific tags added
        """
        # Add robots meta tag with AI-friendly directives
        metadata["robots"] = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"

        # Add content language (default to English)
        if "content-language" not in metadata:
            metadata["content-language"] = "en"

        # Add generator information
        metadata["generator"] = f"{self.site_name} AI-Optimized Mirror"

        # Add referrer policy for better privacy
        metadata["referrer"] = "strict-origin-when-cross-origin"

        # Add theme color if not present
        if "theme-color" not in metadata:
            metadata["theme-color"] = "#000000"

        return metadata

    def generate_content_fingerprint(self, post: Any) -> str:
        """
        Generate unique content identifier for the post.

        Args:
            post: Post object to fingerprint

        Returns:
            Unique string identifier for content tracking
        """
        # Collect identifying information
        fingerprint_data = []

        # Add title
        title = getattr(post, "title", "")
        if title:
            fingerprint_data.append(f"title:{title}")

        # Add publication date
        date = getattr(post, "date", "")
        if not date:
            api_data = getattr(post, "api_data", {})
            if api_data:
                date = api_data.get("published_at", "")
        if date:
            fingerprint_data.append(f"date:{date}")

        # Add Dev.to URL if available
        link = getattr(post, "link", "")
        if link:
            fingerprint_data.append(f"source:{link}")

        # Add content hash (first 100 characters of content)
        content = getattr(post, "content_html", "") or getattr(post, "content", "")
        if content:
            # Remove HTML tags for cleaner hash
            clean_content = re.sub(r"<[^>]+>", "", content)
            content_sample = clean_content[:100].strip()
            if content_sample:
                fingerprint_data.append(f"content:{content_sample}")

        # Add author information for uniqueness
        api_data = getattr(post, "api_data", {})
        if api_data and "user" in api_data:
            username = api_data["user"].get("username", "")
            if username:
                fingerprint_data.append(f"author:{username}")

        # Create hash from combined data
        if fingerprint_data:
            combined_data = "|".join(fingerprint_data)
            hash_object = hashlib.sha256(combined_data.encode("utf-8"))
            return hash_object.hexdigest()[:16]  # Use first 16 characters

        return ""

    def add_source_attribution_metadata(self, post: Any) -> Dict[str, str]:
        """
        Add Dev.to source attribution meta tags and canonical link validation.

        Args:
            post: Post object with Dev.to source information

        Returns:
            Dictionary of source attribution meta tags
        """
        metadata = {}

        # Add canonical link validation
        canonical_url = getattr(post, "link", "")
        if canonical_url:
            metadata["canonical"] = canonical_url

            # Validate that it's a proper Dev.to URL
            if self._validate_devto_canonical_url(canonical_url):
                metadata["source-platform"] = "dev.to"
                metadata["source-url"] = canonical_url

                # Extract username from Dev.to URL for attribution
                username = self._extract_username_from_devto_url(canonical_url)
                if username:
                    metadata["source-author-profile"] = f"https://dev.to/{username}"

        # Add original publication information
        api_data = getattr(post, "api_data", {})
        if api_data:
            # Add original Dev.to post ID if available
            post_id = api_data.get("id")
            if post_id:
                metadata["source-post-id"] = str(post_id)

            # Add original publication date
            published_at = api_data.get("published_at")
            if published_at:
                metadata["original-published-date"] = published_at

            # Add reading time from Dev.to if available
            reading_time = api_data.get("reading_time_minutes")
            if reading_time and reading_time > 0:
                metadata["reading-time"] = f"{reading_time} minutes"

            # Add engagement metrics from Dev.to API
            reactions_count = api_data.get("public_reactions_count")
            if reactions_count is not None and reactions_count >= 0:
                metadata["devto:reactions"] = str(reactions_count)

            comments_count = api_data.get("comments_count")
            if comments_count is not None and comments_count >= 0:
                metadata["devto:comments"] = str(comments_count)

            page_views = api_data.get("page_views_count")
            if page_views is not None and page_views >= 0:
                metadata["devto:page_views"] = str(page_views)

            # Add community engagement score (calculated from reactions and comments)
            if reactions_count is not None and comments_count is not None:
                engagement_score = reactions_count + (comments_count * 2)  # Comments weighted higher
                metadata["devto:engagement_score"] = str(engagement_score)

        return metadata

    def _validate_devto_canonical_url(self, url: str) -> bool:
        """
        Validate that the canonical URL is a proper Dev.to URL.

        Args:
            url: URL to validate

        Returns:
            True if valid Dev.to URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False

        # Check if it's a Dev.to URL
        return "dev.to" in url.lower() and url.startswith(("http://", "https://"))

    def _extract_username_from_devto_url(self, url: str) -> str:
        """
        Extract username from Dev.to URL pattern.

        Args:
            url: Dev.to URL (e.g., https://dev.to/username/post-slug)

        Returns:
            Username string, or empty string if extraction fails
        """
        try:
            if not url or "dev.to" not in url:
                return ""

            # Split URL and extract username
            # Expected format: https://dev.to/username/post-slug
            url_parts = url.split("/")
            if len(url_parts) >= 4 and "dev.to" in url:
                username = url_parts[3]  # Username should be at index 3
                # Basic validation - username shouldn't be empty or contain special chars
                if username and username.replace("-", "").replace("_", "").isalnum():
                    return username

        except Exception as e:
            logger.debug(f"Failed to extract username from URL {url}: {e}")

        return ""

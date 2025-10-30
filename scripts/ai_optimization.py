"""
AI Optimization Module for Dev.to Mirror

This module provides AI-specific enhancements for the Dev.to mirror site,
including structured data generation, metadata enhancement, content analysis,
cross-referencing, and specialized sitemap generation for AI crawlers.

All components are designed to integrate with the existing site generation
workflow while preserving backward compatibility and existing functionality.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Configure logging for AI optimization
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


class SchemaGenerator(ABC):
    """
    Interface for generating JSON-LD structured data markup.

    Generates Schema.org compliant structured data for articles, websites,
    and breadcrumb navigation to enhance AI crawler understanding.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def generate_website_schema(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Schema.org WebSite markup for site-level structured data.

        Args:
            site_info: Dictionary containing site metadata (name, url, description)

        Returns:
            Dictionary containing JSON-LD WebSite schema
        """
        pass

    @abstractmethod
    def generate_breadcrumb_schema(self, post: Any) -> Dict[str, Any]:
        """
        Generate Schema.org BreadcrumbList markup for navigation context.

        Args:
            post: Post object for breadcrumb context

        Returns:
            Dictionary containing JSON-LD BreadcrumbList schema
        """
        pass


class MetadataEnhancer(ABC):
    """
    Interface for enhancing HTML metadata with AI-specific tags.

    Adds comprehensive metadata while preserving existing OpenGraph,
    Twitter Card, and LinkedIn meta tags from current templates.
    """

    @abstractmethod
    def enhance_post_metadata(self, post: Any) -> Dict[str, str]:
        """
        Generate enhanced metadata dictionary for a blog post.

        Args:
            post: Post object containing article data

        Returns:
            Dictionary of meta tag name/content pairs for AI optimization
        """
        pass

    @abstractmethod
    def add_ai_specific_tags(self, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Add AI-specific meta tags to existing metadata.

        Args:
            metadata: Existing metadata dictionary

        Returns:
            Enhanced metadata with AI-specific tags added
        """
        pass

    @abstractmethod
    def generate_content_fingerprint(self, post: Any) -> str:
        """
        Generate unique content identifier for the post.

        Args:
            post: Post object to fingerprint

        Returns:
            Unique string identifier for content tracking
        """
        pass


class CrossReferenceManager(ABC):
    """
    Interface for managing Dev.to source attribution and cross-linking.

    Enhances existing canonical link behavior with prominent source attribution
    and simple content relationship mapping based on shared tags.
    """

    @abstractmethod
    def add_source_attribution(self, post: Any) -> Dict[str, Any]:
        """
        Generate enhanced Dev.to source attribution data.

        Args:
            post: Post object with original Dev.to link

        Returns:
            Dictionary containing attribution metadata and display elements
        """
        pass

    @abstractmethod
    def generate_related_links(self, post: Any, all_posts: List[Any]) -> List[Dict[str, Any]]:
        """
        Generate related post suggestions based on shared tags.

        Args:
            post: Current post object
            all_posts: List of all available posts for comparison

        Returns:
            List of related post dictionaries with relevance scoring
        """
        pass

    @abstractmethod
    def create_dev_to_backlinks(self, post: Any) -> Dict[str, str]:
        """
        Create structured backlink data to original Dev.to post.

        Args:
            post: Post object with Dev.to URL

        Returns:
            Dictionary containing backlink metadata and validation info
        """
        pass


class AISitemapGenerator(ABC):
    """
    Interface for generating AI-optimized sitemaps and discovery feeds.

    Extends existing sitemap functionality with AI-specific metadata
    while maintaining backward compatibility with current sitemap.xml format.
    """

    @abstractmethod
    def generate_main_sitemap(self, posts: List[Any], comments: List[Dict[str, Any]]) -> str:
        """
        Generate main sitemap.xml with AI optimization enhancements.

        Args:
            posts: List of Post objects
            comments: List of comment page dictionaries

        Returns:
            XML string for main sitemap with enhanced metadata
        """
        pass

    @abstractmethod
    def generate_content_sitemap(self, posts: List[Any]) -> str:
        """
        Generate content-type specific sitemap for AI crawlers.

        Args:
            posts: List of Post objects to categorize

        Returns:
            XML string for content-specific sitemap
        """
        pass

    @abstractmethod
    def generate_discovery_feed(self, posts: List[Any]) -> str:
        """
        Generate AI crawler discovery feed with structured metadata.

        Args:
            posts: List of Post objects for discovery feed

        Returns:
            XML or JSON string optimized for AI crawler discovery
        """
        pass


class DevToSchemaGenerator(SchemaGenerator):
    """
    Concrete implementation of SchemaGenerator for Dev.to mirror sites.

    Generates Schema.org compliant JSON-LD structured data optimized for
    AI crawlers while maintaining compatibility with existing templates.
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


class DevToMetadataEnhancer(MetadataEnhancer):
    """
    Concrete implementation of MetadataEnhancer for Dev.to mirror sites.

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
        import hashlib

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
            import re

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

            # Add reaction count if available
            reactions_count = api_data.get("public_reactions_count", 0)
            if reactions_count > 0:
                metadata["original-reactions"] = str(reactions_count)

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


class AIOptimizationManager:
    """
    Coordinator class that manages all AI optimization components.

    This class serves as the main integration point for the existing
    generate_site.py workflow, coordinating all AI optimization components
    while ensuring graceful fallback when optimization fails.
    """

    def __init__(
        self,
        schema_generator: Optional[Any] = None,  # SchemaGenerator from devto_mirror.ai_optimization
        metadata_enhancer: Optional[MetadataEnhancer] = None,
        content_analyzer: Optional[Any] = None,
        cross_reference_manager: Optional[CrossReferenceManager] = None,
        sitemap_generator: Optional[AISitemapGenerator] = None,
    ):
        """
        Initialize AI optimization manager with component implementations.

        Args:
            schema_generator: Implementation of SchemaGenerator interface
            metadata_enhancer: Implementation of MetadataEnhancer interface
            content_analyzer: Implementation of ContentAnalyzer interface
            cross_reference_manager: Implementation of CrossReferenceManager interface
            sitemap_generator: Implementation of AISitemapGenerator interface
        """
        self.schema_generator = schema_generator
        self.metadata_enhancer = metadata_enhancer
        self.content_analyzer = content_analyzer
        self.cross_reference_manager = cross_reference_manager
        self.sitemap_generator = sitemap_generator

        # Track optimization status for error handling
        self.optimization_enabled = True
        self.component_status = {
            "schema": schema_generator is not None,
            "metadata": metadata_enhancer is not None,
            "content": content_analyzer is not None,
            "cross_reference": cross_reference_manager is not None,
            "sitemap": sitemap_generator is not None,
        }

    def optimize_post(self, post: Any, api_data: Dict[str, Any] = None, all_posts: List[Any] = None) -> Dict[str, Any]:
        """
        Apply all AI optimizations to a single post.

        Args:
            post: Post object to optimize
            api_data: Optional original Dev.to API data (will use post.api_data if not provided)
            all_posts: Optional list of all posts for cross-referencing

        Returns:
            Dictionary containing all optimization data for template rendering
        """
        optimization_data = {
            "json_ld_schemas": [],
            "enhanced_metadata": {},
            "content_analysis": {},
            "cross_references": {},
            "optimization_applied": False,
        }

        if not self.optimization_enabled:
            return optimization_data

        # Use provided api_data or fall back to post.api_data
        if api_data is None:
            api_data = getattr(post, "api_data", {})

        try:
            if self.schema_generator:
                try:
                    canonical_url = getattr(post, "link", "")
                    article_schema = self.schema_generator.generate_article_schema(post, canonical_url, api_data)
                    breadcrumb_schema = self.schema_generator.generate_breadcrumb_schema(post)

                    optimization_data["json_ld_schemas"] = [article_schema, breadcrumb_schema]
                except Exception as e:
                    logger.warning(f"Schema generation failed for post {getattr(post, 'slug', 'unknown')}: {e}")

            if self.metadata_enhancer:
                try:
                    enhanced_meta = self.metadata_enhancer.enhance_post_metadata(post)
                    optimization_data["enhanced_metadata"] = enhanced_meta
                except Exception as e:
                    logger.warning(f"Metadata enhancement failed for post {getattr(post, 'slug', 'unknown')}: {e}")

            if self.content_analyzer:
                try:
                    content_analysis = self.content_analyzer.analyze_post_content(post, api_data)
                    optimization_data["content_analysis"] = content_analysis
                except Exception as e:
                    logger.warning(f"Content analysis failed for post {getattr(post, 'slug', 'unknown')}: {e}")

            if self.cross_reference_manager:
                try:
                    source_attribution = self.cross_reference_manager.add_source_attribution(post)
                    related_links = self.cross_reference_manager.generate_related_links(post, all_posts)
                    backlinks = self.cross_reference_manager.create_dev_to_backlinks(post)

                    optimization_data["cross_references"] = {
                        "source_attribution": source_attribution,
                        "related_links": related_links,
                        "backlinks": backlinks,
                    }
                except Exception as e:
                    logger.warning(
                        f"Cross-reference generation failed for post {getattr(post, 'slug', 'unknown')}: {e}"
                    )

            optimization_data["optimization_applied"] = True

        except Exception as e:
            logger.error(f"AI optimization failed for post {getattr(post, 'slug', 'unknown')}: {e}")

        return optimization_data

    def generate_optimized_sitemap(self, posts: List[Any], comments: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate AI-optimized sitemap using the sitemap generator.

        Args:
            posts: List of Post objects
            comments: List of comment dictionaries

        Returns:
            Optimized sitemap XML string, or None if generation fails
        """
        if not self.sitemap_generator:
            return None

        try:
            return self.sitemap_generator.generate_main_sitemap(posts, comments)
        except Exception as e:
            logger.error(f"AI sitemap generation failed: {e}")
            return None

    def create_optimized_post(self, post: Any) -> Any:
        """
        Create an AIOptimizedPost wrapper for the given post.

        Args:
            post: Original Post object to wrap

        Returns:
            AIOptimizedPost instance with content analysis capabilities
        """
        # Import here to avoid circular imports
        from devto_mirror.ai_optimization import AIOptimizedPost

        return AIOptimizedPost.from_post(post, self.content_analyzer)

    def create_optimized_posts(self, posts: List[Any]) -> List[Any]:
        """
        Create AIOptimizedPost wrappers for a list of posts.

        Args:
            posts: List of original Post objects

        Returns:
            List of AIOptimizedPost instances
        """
        optimized_posts = []
        for post in posts:
            try:
                optimized_post = self.create_optimized_post(post)
                optimized_posts.append(optimized_post)
            except Exception as e:
                logger.warning(f"Failed to create optimized post for {getattr(post, 'slug', 'unknown')}: {e}")
                # Fallback: create a basic wrapper without content analyzer
                from devto_mirror.ai_optimization import AIOptimizedPost

                optimized_posts.append(AIOptimizedPost(post, None))

        return optimized_posts

    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get current status of AI optimization components.

        Returns:
            Dictionary containing component status and performance metrics
        """
        return {
            "enabled": self.optimization_enabled,
            "components": self.component_status.copy(),
            "active_components": sum(self.component_status.values()),
        }


def create_default_ai_optimization_manager(
    site_name: str = "ChecKMarK Dev.to Mirror", site_url: str = ""
) -> AIOptimizationManager:
    """
    Create a fully configured AIOptimizationManager with all default implementations.

    Args:
        site_name: Name of the mirror site
        site_url: Base URL of the mirror site

    Returns:
        Configured AIOptimizationManager instance
    """
    # Create all component implementations
    from devto_mirror.ai_optimization import DevToContentAnalyzer, DevToSchemaGenerator

    schema_generator = DevToSchemaGenerator(site_name, site_url)
    metadata_enhancer = DevToMetadataEnhancer(site_name, site_url)
    content_analyzer = DevToContentAnalyzer()

    # Note: CrossReferenceManager and AISitemapGenerator implementations
    # will be added in future tasks
    cross_reference_manager = None
    sitemap_generator = None

    return AIOptimizationManager(
        schema_generator=schema_generator,
        metadata_enhancer=metadata_enhancer,
        content_analyzer=content_analyzer,
        cross_reference_manager=cross_reference_manager,
        sitemap_generator=sitemap_generator,
    )

"""
AI Optimization Module for Dev.to Mirror

This module provides AI-specific enhancements for the Dev.to mirror site,
including structured data generation, metadata enhancement, content analysis,
cross-referencing, and specialized sitemap generation for AI crawlers.

All components are designed to integrate with the existing site generation
workflow while preserving backward compatibility and existing functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import json
import logging

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


class ContentAnalyzer(ABC):
    """
    Interface for analyzing and extracting semantic information from posts.

    Prioritizes Dev.to API data when available, with fallback calculations
    for missing metrics. Focuses on basic content analysis suitable for AI consumption.
    """

    @abstractmethod
    def analyze_post_content(self, post: Any, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze post content and extract semantic information.

        Args:
            post: Post object containing content
            api_data: Original Dev.to API response data

        Returns:
            Dictionary containing content analysis results with data source flags
        """
        pass

    @abstractmethod
    def extract_api_metrics(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metrics directly from Dev.to API data when available.

        Args:
            api_data: Original Dev.to API response

        Returns:
            Dictionary of metrics extracted from API (reading_time, reactions, etc.)
        """
        pass

    @abstractmethod
    def calculate_fallback_metrics(self, content: str) -> Dict[str, Any]:
        """
        Calculate basic metrics when API data is unavailable.

        Args:
            content: HTML content string to analyze

        Returns:
            Dictionary of calculated metrics (word_count, estimated_reading_time)
        """
        pass

    @abstractmethod
    def extract_code_languages(self, content: str) -> List[str]:
        """
        Identify programming languages from code blocks in content.

        Args:
            content: HTML content containing code blocks

        Returns:
            List of detected programming language identifiers
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
        self.site_url = site_url.rstrip('/')

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
                url_parts = canonical_url.split('/')
                if len(url_parts) >= 4 and 'dev.to' in canonical_url:
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
            published_date = getattr(post, 'date', '')

        # Ensure ISO format with timezone
        if isinstance(published_date, str) and published_date:
            if not published_date.endswith('Z') and '+' not in published_date and 'T' in published_date:
                published_date = published_date + 'Z'

        # Build the article schema
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": getattr(post, 'title', 'Untitled'),
            "author": {
                "@type": "Person",
                "name": author_name,
                "url": author_url
            },
            "publisher": {
                "@type": "Organization",
                "name": self.site_name,
                "url": self.site_url or canonical_url
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": canonical_url
            },
            "url": canonical_url
        }

        # Add dates if available
        if published_date:
            schema["datePublished"] = published_date
            # Use edited_at if available, otherwise use published_at
            edited_date = published_date
            if api_data and api_data.get("edited_at"):
                edited_date = api_data["edited_at"]
                if not edited_date.endswith('Z') and '+' not in edited_date and 'T' in edited_date:
                    edited_date = edited_date + 'Z'
            schema["dateModified"] = edited_date

        # Add description if available
        description = getattr(post, 'description', '')
        if description:
            schema["description"] = description

        # Add images - prefer social_image from API, fallback to cover_image
        image_url = ""
        if api_data:
            image_url = api_data.get("social_image") or api_data.get("cover_image", "")
        if not image_url:
            image_url = getattr(post, 'cover_image', '')

        if image_url:
            schema["image"] = {
                "@type": "ImageObject",
                "url": image_url,
                "width": 1000,  # Default dimensions for Dev.to images
                "height": 500
            }

        # Add tags as keywords - prefer API data
        tags = []
        if api_data:
            # Dev.to API provides tags as array
            tags = api_data.get("tags", [])
        if not tags:
            tags = getattr(post, 'tags', [])

        if tags and isinstance(tags, list):
            schema["keywords"] = tags

        # Add reading time if available from API
        if api_data and "reading_time_minutes" in api_data:
            reading_time = api_data["reading_time_minutes"]
            if reading_time and reading_time > 0:
                schema["timeRequired"] = f"PT{reading_time}M"  # ISO 8601 duration format

        # Add word count estimation from content
        content_html = getattr(post, 'content_html', '')
        if content_html:
            # Basic word count estimation
            import re
            text_content = re.sub(r'<[^>]+>', '', content_html)
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
            "@id": site_info.get('url', self.site_url),
            "name": site_info.get('name', self.site_name),
            "url": site_info.get('url', self.site_url)
        }

        # Add description if provided
        description = site_info.get('description')
        if description:
            schema["description"] = description

        # Add search action for the site
        if self.site_url:
            schema["potentialAction"] = {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{self.site_url}/?q={{search_term_string}}"
                },
                "query-input": "required name=search_term_string"
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
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": self.site_url or "/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Posts",
                "item": f"{self.site_url}/posts" if self.site_url else "/posts"
            }
        ]

        # Add the current post as the final breadcrumb
        post_title = getattr(post, 'title', 'Post')
        post_slug = getattr(post, 'slug', 'post')
        breadcrumbs.append({
            "@type": "ListItem",
            "position": 3,
            "name": post_title,
            "item": f"{self.site_url}/posts/{post_slug}.html" if self.site_url else f"/posts/{post_slug}.html"
        })

        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumbs
        }

        # Validate schema before returning
        if validate_json_ld_schema(schema):
            return schema
        else:
            logger.warning("Generated breadcrumb schema failed validation")
            return {}


class AIOptimizationManager:
    """
    Coordinator class that manages all AI optimization components.

    This class serves as the main integration point for the existing
    generate_site.py workflow, coordinating all AI optimization components
    while ensuring graceful fallback when optimization fails.
    """

    def __init__(
        self,
        schema_generator: Optional[SchemaGenerator] = None,
        metadata_enhancer: Optional[MetadataEnhancer] = None,
        content_analyzer: Optional[ContentAnalyzer] = None,
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
            api_data = getattr(post, 'api_data', {})

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

"""
AI Optimization Manager

This module provides the main coordination class for all AI optimization components.
The AIOptimizationManager serves as the integration point for the existing
generate_site.py workflow, coordinating all AI optimization components
while ensuring graceful fallback when optimization fails.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


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
        metadata_enhancer: Optional[Any] = None,  # MetadataEnhancer from devto_mirror.ai_optimization
        content_analyzer: Optional[Any] = None,  # ContentAnalyzer from devto_mirror.ai_optimization
        cross_reference_manager: Optional[Any] = None,  # CrossReferenceManager interface
        sitemap_generator: Optional[Any] = None,  # AISitemapGenerator from devto_mirror.ai_optimization
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
    from devto_mirror.ai_optimization import (
        DevToAISitemapGenerator,
        DevToContentAnalyzer,
        DevToMetadataEnhancer,
        DevToSchemaGenerator,
    )

    schema_generator = DevToSchemaGenerator(site_name, site_url)
    metadata_enhancer = DevToMetadataEnhancer(site_name, site_url)
    content_analyzer = DevToContentAnalyzer()
    sitemap_generator = DevToAISitemapGenerator(site_name, site_url)

    # Note: CrossReferenceManager implementation uses functions from cross_reference module
    # rather than a class-based approach, so we don't instantiate it here
    cross_reference_manager = None

    return AIOptimizationManager(
        schema_generator=schema_generator,
        metadata_enhancer=metadata_enhancer,
        content_analyzer=content_analyzer,
        cross_reference_manager=cross_reference_manager,
        sitemap_generator=sitemap_generator,
    )

"""
AI-Optimized Post Wrapper Module

This module provides a wrapper class that extends existing Post objects
with AI optimization fields and analysis capabilities.
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


class AIOptimizedPost:
    """
    Wrapper class that extends existing Post objects with AI optimization fields.

    This class wraps the existing Post class and adds AI-specific analysis data
    while preserving all original functionality and attributes.
    """

    def __init__(self, post: Any, content_analyzer: Optional[Any] = None):
        """
        Initialize AI-optimized post wrapper.

        Args:
            post: Original Post object to wrap
            content_analyzer: Optional ContentAnalyzer instance for analysis
        """
        self._original_post = post

        # Import here to avoid circular imports
        if content_analyzer is None:
            from .content_analyzer import DevToContentAnalyzer

            content_analyzer = DevToContentAnalyzer()

        self._content_analyzer = content_analyzer
        self._analysis_cache = None
        self._analysis_performed = False

        # Expose all original post attributes
        self._expose_original_attributes()

    def _expose_original_attributes(self):
        """Expose all attributes from the original post object."""
        # Get all attributes from the original post
        for attr_name in dir(self._original_post):
            if not attr_name.startswith("_"):  # Skip private attributes
                try:
                    attr_value = getattr(self._original_post, attr_name)
                    # Only expose non-callable attributes (data, not methods)
                    if not callable(attr_value):
                        setattr(self, attr_name, attr_value)
                except AttributeError:
                    continue

    def get_content_analysis(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get content analysis results, performing analysis if not already done.

        Args:
            force_refresh: If True, force re-analysis even if cached

        Returns:
            Dictionary containing content analysis results
        """
        if not self._analysis_performed or force_refresh or self._analysis_cache is None:
            self._perform_content_analysis()

        return self._analysis_cache or {}

    def _perform_content_analysis(self):
        """Perform content analysis using the content analyzer."""
        try:
            api_data = getattr(self._original_post, "api_data", {})
            self._analysis_cache = self._content_analyzer.analyze_post_content(self._original_post, api_data)
            self._analysis_performed = True
        except Exception as e:
            logger.warning(f"Content analysis failed for post {getattr(self._original_post, 'slug', 'unknown')}: {e}")
            self._analysis_cache = {
                "metrics": {},
                "content_type": "article",
                "code_languages": [],
                "data_source_flags": {"error": str(e)},
                "analysis_timestamp": "",
            }
            self._analysis_performed = True

    @property
    def content_type(self) -> str:
        """Get the determined content type."""
        analysis = self.get_content_analysis()
        return analysis.get("content_type", "article")

    @property
    def reading_time_minutes(self) -> int:
        """Get reading time in minutes (from API or calculated)."""
        analysis = self.get_content_analysis()
        metrics = analysis.get("metrics", {})
        return metrics.get("reading_time_minutes", 1)

    @property
    def word_count(self) -> int:
        """Get word count (from API or calculated)."""
        analysis = self.get_content_analysis()
        metrics = analysis.get("metrics", {})
        return metrics.get("word_count", 0)

    @property
    def code_languages(self) -> List[str]:
        """Get list of detected programming languages."""
        analysis = self.get_content_analysis()
        return analysis.get("code_languages", [])

    @property
    def content_fingerprint(self) -> str:
        """Get unique content fingerprint."""
        # Generate a simple fingerprint based on title and content
        title = getattr(self._original_post, "title", "")
        content = getattr(self._original_post, "content_html", "")
        date = getattr(self._original_post, "date", "")

        fingerprint_data = f"{title}|{date}|{content[:100]}"
        return hashlib.sha256(fingerprint_data.encode("utf-8")).hexdigest()[:16]

    @property
    def ai_metadata(self) -> Dict[str, Any]:
        """Get comprehensive AI metadata dictionary."""
        analysis = self.get_content_analysis()

        return {
            "content_type": self.content_type,
            "reading_time_minutes": self.reading_time_minutes,
            "word_count": self.word_count,
            "code_languages": self.code_languages,
            "content_fingerprint": self.content_fingerprint,
            "metrics": analysis.get("metrics", {}),
            "data_source_flags": analysis.get("data_source_flags", {}),
            "analysis_timestamp": analysis.get("analysis_timestamp", ""),
        }

    @property
    def data_source_flags(self) -> Dict[str, str]:
        """Get data source flags indicating API vs calculated fields."""
        analysis = self.get_content_analysis()
        return analysis.get("data_source_flags", {})

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AIOptimizedPost to dictionary, including AI analysis data.

        Returns:
            Dictionary representation including original post data and AI analysis
        """
        # Start with original post data
        if hasattr(self._original_post, "to_dict"):
            post_dict = self._original_post.to_dict()
        else:
            # Fallback: manually create dict from attributes
            post_dict = {
                "title": getattr(self._original_post, "title", ""),
                "link": getattr(self._original_post, "link", ""),
                "date": getattr(self._original_post, "date", ""),
                "content_html": getattr(self._original_post, "content_html", ""),
                "description": getattr(self._original_post, "description", ""),
                "slug": getattr(self._original_post, "slug", ""),
                "cover_image": getattr(self._original_post, "cover_image", ""),
                "tags": getattr(self._original_post, "tags", []),
                "api_data": getattr(self._original_post, "api_data", {}),
            }

        # Add AI optimization data
        post_dict["ai_optimization"] = {
            "content_analysis": self.get_content_analysis(),
            "ai_metadata": self.ai_metadata,
            "optimization_applied": self._analysis_performed,
        }

        return post_dict

    @classmethod
    def from_post(cls, post: Any, content_analyzer: Optional[Any] = None) -> "AIOptimizedPost":
        """
        Create AIOptimizedPost from existing Post object.

        Args:
            post: Original Post object
            content_analyzer: Optional ContentAnalyzer instance

        Returns:
            AIOptimizedPost wrapper instance
        """
        return cls(post, content_analyzer)

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the original post object if not found in wrapper.

        Args:
            name: Attribute name to access

        Returns:
            Attribute value from original post

        Raises:
            AttributeError: If attribute not found in either wrapper or original post
        """
        try:
            return getattr(self._original_post, name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __str__(self) -> str:
        """String representation of the AI-optimized post."""
        title = getattr(self._original_post, "title", "Untitled")
        content_type = self.content_type
        return f"AIOptimizedPost(title='{title}', content_type='{content_type}')"

    def __repr__(self) -> str:
        """Detailed string representation of the AI-optimized post."""
        return self.__str__()

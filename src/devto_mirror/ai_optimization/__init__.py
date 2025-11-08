"""
AI Optimization Package

This package provides AI-specific enhancements for the Dev.to mirror site,
including structured data generation, metadata enhancement, content analysis,
cross-referencing, and specialized sitemap generation for AI crawlers.

This package is being migrated from the monolithic scripts/ai_optimization.py
to provide better modularity and maintainability.
"""

from .content_analyzer import DevToContentAnalyzer
from .cross_reference import (
    add_source_attribution,
    create_dev_to_backlinks,
    enhance_post_with_cross_references,
    generate_related_links,
)
from .manager import AIOptimizationManager, create_default_ai_optimization_manager
from .metadata_enhancer import DevToMetadataEnhancer
from .optimized_post import AIOptimizedPost
from .schema_generator import DevToSchemaGenerator
from .sitemap_generator import DevToAISitemapGenerator
from .utils import validate_json_ld_schema

__all__ = [
    "DevToContentAnalyzer",
    "AIOptimizedPost",
    "add_source_attribution",
    "generate_related_links",
    "create_dev_to_backlinks",
    "enhance_post_with_cross_references",
    "AIOptimizationManager",
    "create_default_ai_optimization_manager",
    "DevToMetadataEnhancer",
    "DevToSchemaGenerator",
    "validate_json_ld_schema",
    "DevToAISitemapGenerator",
]

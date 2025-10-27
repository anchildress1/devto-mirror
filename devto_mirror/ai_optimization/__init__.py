"""
AI Optimization Package

This package provides AI-specific enhancements for the Dev.to mirror site,
including structured data generation, metadata enhancement, content analysis,
cross-referencing, and specialized sitemap generation for AI crawlers.

This package is being migrated from the monolithic scripts/ai_optimization.py
to provide better modularity and maintainability.
"""

from .content_analyzer import DevToContentAnalyzer
from .optimized_post import AIOptimizedPost

__all__ = [
    "DevToContentAnalyzer",
    "AIOptimizedPost",
]

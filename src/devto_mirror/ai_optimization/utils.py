"""
AI Optimization Utilities

This module provides utility functions for AI optimization components,
including JSON-LD schema validation and other helper functions.
"""

import json
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

CONTENT_TYPE_MAPPINGS: List[Tuple[str, List[str]]] = [
    ("tutorial", ["tutorial", "howto", "guide", "walkthrough", "stepbystep", "beginners"]),
    ("discussion", ["discuss", "discussion", "watercooler", "community", "opinion", "thoughts"]),
    ("career", ["career", "job", "interview", "workplace", "professional"]),
    ("writing", ["writing", "writers", "blogging", "content"]),
    ("technology", ["technology", "tooling", "tools", "vscode", "webdev"]),
    ("ai", ["ai", "githubcopilot", "chatgpt", "machinelearning", "ml"]),
    ("productivity", ["productivity", "workflow", "automation", "efficiency"]),
    ("challenge", ["devchallenge", "challenge", "contest", "hackathon"]),
    ("wellness", ["mentalhealth", "wellness", "burnout", "health"]),
]


def determine_content_type(tags: List[str]) -> str:
    """
    Determine content type based on tag list.

    Args:
        tags: List of tag strings (will be normalized to lowercase)

    Returns:
        Content type string (tutorial, discussion, career, etc.)
    """
    if not isinstance(tags, list):
        return "article"

    tags_lower = [tag.lower() for tag in tags if isinstance(tag, str)]

    for content_type, keywords in CONTENT_TYPE_MAPPINGS:
        if any(keyword in tags_lower for keyword in keywords):
            return content_type

    return "article"


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

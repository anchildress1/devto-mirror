"""
AI Optimization Utilities

This module provides utility functions for AI optimization components,
including JSON-LD schema validation and other helper functions.
"""

import json
import logging
from typing import Any, Dict

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

"""
Cross-Reference Manager Module for Dev.to Mirror

This module provides straightforward functions for enhancing Dev.to source attribution
and generating related content suggestions without complex inheritance hierarchies.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)


def add_source_attribution(post: Any, site_config: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Add enhanced Dev.to source attribution metadata.

    Args:
        post: Post object containing Dev.to information
        site_config: Optional site configuration with attribution settings

    Returns:
        Dictionary of attribution metadata for templates
    """
    attribution_data = {}

    try:
        # Get canonical Dev.to URL
        canonical_url = getattr(post, "link", "")
        if not canonical_url:
            logger.warning(f"No canonical URL found for post: {getattr(post, 'slug', 'unknown')}")
            return attribution_data

        # Validate that it's a Dev.to URL
        parsed_url = urlparse(canonical_url)
        if not parsed_url.netloc.endswith("dev.to"):
            logger.warning(f"Non-Dev.to canonical URL detected: {canonical_url}")

        # Basic attribution text
        attribution_data["source_platform"] = "Dev.to"
        attribution_data["source_url"] = canonical_url
        attribution_data["attribution_text"] = "Originally published on Dev.to"
        attribution_data["attribution_link_text"] = "Read the original article on Dev.to"

        # Enhanced attribution with author information
        author = getattr(post, "author", "")
        if not author:
            # Fallback: try to extract from api_data
            api_data = getattr(post, "api_data", {})
            user_data = api_data.get("user", {})
            author = user_data.get("name") or user_data.get("username") or "Dev.to Author"
        attribution_data["author_attribution"] = f"by {author} on Dev.to"

        # Publication date for attribution
        date = getattr(post, "date", "")
        if date:
            attribution_data["publication_date"] = date
            attribution_data["full_attribution"] = f"Originally published by {author} on Dev.to ({date})"
        else:
            attribution_data["full_attribution"] = f"Originally published by {author} on Dev.to"

        # Structured data for attribution
        attribution_data["structured_attribution"] = {
            "source": "Dev.to",
            "author": author,
            "canonical_url": canonical_url,
            "publication_date": date,
        }

        # Generate prominent attribution HTML
        attribution_data["attribution_html"] = _generate_attribution_html(canonical_url, author, date, site_config)

        # Generate meta tags for source attribution
        attribution_data["meta_tags"] = _generate_attribution_meta_tags(canonical_url, author, date)

        logger.debug(f"Generated source attribution for post: {getattr(post, 'slug', 'unknown')}")

    except Exception as e:
        logger.error(f"Error generating source attribution: {e}")
        # Provide minimal fallback attribution
        attribution_data = {
            "source_platform": "Dev.to",
            "attribution_text": "Originally published on Dev.to",
            "attribution_html": "<p><em>Originally published on Dev.to</em></p>",
        }

    return attribution_data


def generate_related_links(post: Any, all_posts: List[Any], max_related: int = 5) -> List[Dict[str, str]]:
    """
    Generate related content suggestions based on shared tags.

    Args:
        post: Current post object
        all_posts: List of all available posts for comparison
        max_related: Maximum number of related posts to return

    Returns:
        List of related post dictionaries with title, link, and relevance info
    """
    related_posts = []

    try:
        # Get current post tags
        current_tags = getattr(post, "tags", [])
        if not current_tags or not isinstance(current_tags, list):
            logger.debug(f"No tags found for post: {getattr(post, 'slug', 'unknown')}")
            return related_posts

        current_slug = getattr(post, "slug", "")
        current_tags_lower = [tag.lower() for tag in current_tags if isinstance(tag, str)]

        # Score other posts based on tag overlap
        post_scores = []
        for other_post in all_posts:
            other_slug = getattr(other_post, "slug", "")

            # Skip the current post
            if other_slug == current_slug:
                continue

            other_tags = getattr(other_post, "tags", [])
            if not other_tags or not isinstance(other_tags, list):
                continue

            other_tags_lower = [tag.lower() for tag in other_tags if isinstance(tag, str)]

            # Calculate tag overlap score
            shared_tags = set(current_tags_lower) & set(other_tags_lower)
            if shared_tags:
                # Score based on number of shared tags and tag rarity
                score = len(shared_tags)

                # Boost score for exact tag matches (case-sensitive)
                exact_matches = set(current_tags) & set(other_tags)
                score += len(exact_matches) * 0.5

                post_scores.append(
                    {
                        "post": other_post,
                        "score": score,
                        "shared_tags": list(shared_tags),
                        "exact_matches": list(exact_matches),
                    }
                )

        # Sort by score (highest first) and take top results
        post_scores.sort(key=lambda x: x["score"], reverse=True)
        top_posts = post_scores[:max_related]

        # Format related posts for template use
        for item in top_posts:
            related_post = item["post"]
            related_posts.append(
                {
                    "title": getattr(related_post, "title", "Untitled"),
                    "link": getattr(related_post, "link", ""),
                    "local_link": f"posts/{getattr(related_post, 'slug', '')}.html",
                    "description": getattr(related_post, "description", ""),
                    "shared_tags": item["shared_tags"],
                    "relevance_score": item["score"],
                    "date": getattr(related_post, "date", ""),
                }
            )

        if related_posts:
            logger.debug(f"Found {len(related_posts)} related posts for: {getattr(post, 'slug', 'unknown')}")

    except Exception as e:
        logger.error(f"Error generating related links: {e}")

    return related_posts


def create_dev_to_backlinks(post: Any) -> Dict[str, Any]:
    """
    Create structured data for linking back to original Dev.to post.

    Args:
        post: Post object containing Dev.to information

    Returns:
        Dictionary containing backlink metadata and structured data
    """
    backlink_data = {}

    try:
        canonical_url = getattr(post, "link", "")
        if not canonical_url:
            logger.warning(f"No canonical URL for backlink generation: {getattr(post, 'slug', 'unknown')}")
            return backlink_data

        # Basic backlink information
        backlink_data["canonical_url"] = canonical_url
        backlink_data["rel_canonical"] = True
        backlink_data["source_platform"] = "Dev.to"

        # Extract Dev.to username and post slug from URL
        parsed_url = urlparse(canonical_url)
        if parsed_url.netloc.endswith("dev.to") and parsed_url.path:
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) >= 2:
                backlink_data["devto_username"] = path_parts[0]
                backlink_data["devto_slug"] = path_parts[1]

        # Generate structured data for backlinks
        backlink_data["structured_data"] = {
            "@type": "WebPage",
            "url": canonical_url,
            "isPartOf": {
                "@type": "WebSite",
                "@id": "https://dev.to",
                "name": "DEV Community",
            },
            "mainEntity": {
                "@type": "Article",
                "url": canonical_url,
            },
        }

        # Generate HTML for backlink display
        backlink_data["backlink_html"] = _generate_backlink_html(canonical_url, post)

        # Meta tags for canonical linking
        backlink_data["canonical_meta"] = f'<link rel="canonical" href="{canonical_url}">'

        logger.debug(f"Generated Dev.to backlinks for post: {getattr(post, 'slug', 'unknown')}")

    except Exception as e:
        logger.error(f"Error creating Dev.to backlinks: {e}")

    return backlink_data


def _generate_attribution_html(
    canonical_url: str, author: str, date: str, site_config: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate HTML for prominent Dev.to attribution display.

    Args:
        canonical_url: Original Dev.to post URL
        author: Post author name
        date: Publication date
        site_config: Optional site configuration

    Returns:
        HTML string for attribution display
    """
    try:
        # Basic attribution with styling
        attribution_html = f"""
        <div style="border: 1px solid #e0e0e0; padding: 15px; margin: 20px 0;
                    background-color: #f9f9f9; border-radius: 5px;">
            <p style="margin: 0; font-style: italic; color: #666;">
                <strong>📝 Originally published on Dev.to</strong><br>
                by {author}"""

        if date:
            attribution_html += f" on {date}"

        attribution_html += f"""
            </p>
            <p style="margin: 10px 0 0 0;">
                <a href="{canonical_url}"
                   style="color: #3b49df; text-decoration: none; font-weight: bold;"
                   target="_blank" rel="noopener">
                    → Read the original article on Dev.to
                </a>
            </p>
        </div>
        """

        return attribution_html.strip()

    except Exception as e:
        logger.error(f"Error generating attribution HTML: {e}")
        return f'<p><em>Originally published on <a href="{canonical_url}">Dev.to</a></em></p>'


def _generate_attribution_meta_tags(canonical_url: str, author: str, date: str) -> Dict[str, str]:
    """
    Generate meta tags for source attribution.

    Args:
        canonical_url: Original Dev.to post URL
        author: Post author name
        date: Publication date

    Returns:
        Dictionary of meta tag name-content pairs
    """
    meta_tags = {
        "article:author": author,
        "article:publisher": "Dev.to",
        "article:source": "Dev.to",
        "content:source": canonical_url,
        "content:original_publisher": "Dev.to",
    }

    if date:
        meta_tags["article:published_time"] = date

    return meta_tags


def _generate_backlink_html(canonical_url: str, post: Any) -> str:
    """
    Generate HTML for backlink display.

    Args:
        canonical_url: Original Dev.to post URL
        post: Post object

    Returns:
        HTML string for backlink display
    """
    try:
        title = getattr(post, "title", "this article")

        backlink_html = f"""
        <div style="margin: 20px 0; padding: 10px; border-left: 4px solid #3b49df; background-color: #f8f9ff;">
            <p style="margin: 0; font-size: 0.9em; color: #555;">
                💬 Join the discussion about "{title}" on Dev.to:
            </p>
            <p style="margin: 5px 0 0 0;">
                <a href="{canonical_url}"
                   style="color: #3b49df; font-weight: bold; text-decoration: none;"
                   target="_blank" rel="noopener">
                    View comments and reactions →
                </a>
            </p>
        </div>
        """

        return backlink_html.strip()

    except Exception as e:
        logger.error(f"Error generating backlink HTML: {e}")
        return f'<p><a href="{canonical_url}">View on Dev.to</a></p>'


def enhance_post_with_cross_references(
    post: Any, all_posts: List[Any], site_config: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Enhance a post with all cross-reference data (attribution, related links, backlinks).

    Args:
        post: Post object to enhance
        all_posts: List of all posts for related content generation
        site_config: Optional site configuration

    Returns:
        Dictionary containing all cross-reference enhancements
    """
    try:
        cross_ref_data = {
            "attribution": add_source_attribution(post, site_config),
            "related_posts": generate_related_links(post, all_posts),
            "backlinks": create_dev_to_backlinks(post),
        }

        # Add convenience flags
        cross_ref_data["has_attribution"] = bool(cross_ref_data["attribution"])
        cross_ref_data["has_related_posts"] = len(cross_ref_data["related_posts"]) > 0
        cross_ref_data["has_backlinks"] = bool(cross_ref_data["backlinks"])

        logger.debug(f"Enhanced post with cross-references: {getattr(post, 'slug', 'unknown')}")

        return cross_ref_data

    except Exception as e:
        logger.error(f"Error enhancing post with cross-references: {e}")
        return {
            "attribution": {},
            "related_posts": [],
            "backlinks": {},
            "has_attribution": False,
            "has_related_posts": False,
            "has_backlinks": False,
        }

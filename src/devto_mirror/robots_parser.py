"""Robots.txt parsing utilities."""

import re
from typing import Optional


def parse_robots_txt(content: str) -> dict:
    """
    Parse robots.txt content and extract permissions.

    Args:
        content: Raw robots.txt content

    Returns:
        Dictionary containing parsed rules and analysis
    """
    allowed_agents, disallowed_agents, universal_rules = _parse_user_agent_rules(content)
    sitemap_url = _extract_sitemap(content)

    return {
        "content_length": len(content),
        "allowed_agents": list(allowed_agents),
        "disallowed_agents": list(disallowed_agents),
        "universal_rules": universal_rules,
        "sitemap_url": sitemap_url,
        "analysis": {
            "universal_allow": "/" in universal_rules["allow"],
            "has_restrictions": bool(disallowed_agents or universal_rules["disallow"]),
            "total_specific_agents": len(allowed_agents) + len(disallowed_agents),
        },
    }


def _parse_user_agent_rules(content: str) -> tuple[set, set, dict]:
    """
    Parse user agent rules from robots.txt content.

    Args:
        content: Raw robots.txt content

    Returns:
        Tuple of (allowed_agents, disallowed_agents, universal_rules)
    """
    allowed_agents = set()
    disallowed_agents = set()
    universal_rules = {"allow": [], "disallow": []}
    current_agents = []

    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.lower().startswith("user-agent:"):
            current_agents = _parse_user_agent_line(line)
        elif line.lower().startswith("allow:"):
            _process_allow_rule(line, current_agents, allowed_agents, universal_rules)
        elif line.lower().startswith("disallow:"):
            _process_disallow_rule(line, current_agents, disallowed_agents, universal_rules)

    return allowed_agents, disallowed_agents, universal_rules


def _parse_user_agent_line(line: str) -> list:
    """Extract user agent from line."""
    agent = line.split(":", 1)[1].strip()
    return ["*"] if agent == "*" else [agent]


def _process_allow_rule(line: str, current_agents: list, allowed_agents: set, universal_rules: dict) -> None:
    """Process an Allow directive."""
    path = line.split(":", 1)[1].strip()
    if "*" in current_agents:
        universal_rules["allow"].append(path)
    else:
        for agent in current_agents:
            allowed_agents.add(agent)


def _process_disallow_rule(line: str, current_agents: list, disallowed_agents: set, universal_rules: dict) -> None:
    """Process a Disallow directive."""
    path = line.split(":", 1)[1].strip()
    if "*" in current_agents:
        universal_rules["disallow"].append(path)
    else:
        for agent in current_agents:
            if path:
                disallowed_agents.add(agent)


def _extract_sitemap(content: str) -> Optional[str]:
    """Extract sitemap URL from robots.txt content."""
    sitemap_match = re.search(r"Sitemap:\s*(.+)", content, re.IGNORECASE)
    return sitemap_match.group(1).strip() if sitemap_match else None

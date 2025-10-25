"""
Shared utilities for devto-mirror scripts
"""
from datetime import datetime
from email.utils import parsedate_to_datetime
from jinja2 import Environment, select_autoescape

# Use a Jinja environment with autoescape enabled for HTML/XML templates
env = Environment(autoescape=select_autoescape(['html', 'xml']))

# Shared templates
INDEX_TMPL = env.from_string("""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<title>{{ username }} — Dev.to Mirror</title>
<link rel="canonical" href="{{ canonical }}">
<meta name="description" content="{{ site_description }}">
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="{{ home }}">
<meta property="og:title" content="{{ username }} — Dev.to Mirror">
<meta property="og:description" content="{{ site_description }}">
<meta property="og:image" content="{{ social_image }}">
<meta property="og:site_name" content="{{ username }} — Dev.to Mirror">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="{{ home }}">
<meta name="twitter:title" content="{{ username }} — Dev.to Mirror">
<meta name="twitter:description" content="{{ site_description }}">
<meta name="twitter:image" content="{{ social_image }}">

<!-- LinkedIn -->
<meta property="linkedin:title" content="{{ username }} — Dev.to Mirror">
<meta property="linkedin:description" content="{{ site_description }}">
<meta property="linkedin:image" content="{{ social_image }}">

<!-- Additional Social Meta -->
<meta name="image" content="{{ social_image }}">
<meta name="author" content="{{ username }}">
</head><body>
<main>
  <h1>{{ username }} — Dev.to Mirror</h1>
  <ul>
  {% for p in posts %}
        <li>
            <a href="posts/{{ p.slug }}.html">{{ p.title }}</a>
            {% if p.description %} — {{ p.description }}{% endif %}
                        {% if p.tags %}
                                — <small>Tags:
                                    {% for tag in p.tags %}
                                        #{{ tag }}{% if not loop.last %}, {% endif %}
                                    {% endfor %}
                                </small>
                        {% endif %}
            — <small>{{ p.date }}</small>
        </li>
  {% endfor %}
  </ul>
  {% if comments %}<h2>Comment Notes</h2>
  <ul>
  {% for c in comments %}
    <li><a href="{{ c.local }}">{{ c.text }}</a></li>
  {% endfor %}
  </ul>{% endif %}
  <p>Canonical lives on Dev.to. This is just a crawler-friendly mirror.</p>
</main>
</body></html>
""")

SITEMAP_TMPL = env.from_string("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{{ home }}</loc></url>
  {% for p in posts %}
    {# Prefer canonical Dev.to link if available #}
    <url><loc>{{ p.link or (home + 'posts/' + p.slug + '.html') }}</loc></url>
  {% endfor %}
  {% for c in comments %}
    <url><loc>{{ c.url or (home + c.local) }}</loc></url>
  {% endfor %}
</urlset>
""")


def parse_date(date_str):
    """
    Unified date parsing function that handles various formats.
    Returns timezone-aware datetime when possible, otherwise None.
    """
    if not date_str:
        return None

    if isinstance(date_str, datetime):
        return date_str

    if isinstance(date_str, (int, float)):
        try:
            return datetime.fromtimestamp(date_str)
        except Exception:
            return None

    s = str(date_str).strip()

    # Handle trailing Z (ISO format)
    try:
        if s.endswith('Z'):
            s = s.replace('Z', '+00:00')
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        # Failed to parse as ISO format, try RFC format
        pass

    # Try RFC-style parse
    try:
        return parsedate_to_datetime(s)
    except (ValueError, TypeError, OverflowError):
        # Failed to parse as RFC format, try basic ISO format
        pass

    # Try basic ISO without timezone
    try:
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
    except Exception:
        return None


def dedupe_posts_by_link(posts_list):
    """
    Remove duplicate posts based on their 'link' field.
    Keeps the post with the most recent date when duplicates are found.
    Returns a list of posts sorted by date (newest first).
    """
    if not posts_list:
        return []

    posts_map = {}

    for post in posts_list:
        link = post.get('link') if isinstance(post, dict) else getattr(post, 'link', None)
        if not link:
            continue

        post_dict = post.to_dict() if hasattr(post, 'to_dict') else post
        new_date = parse_date(post_dict.get('date'))

        existing = posts_map.get(link)
        if existing is None:
            posts_map[link] = post_dict
            continue

        existing_date = parse_date(existing.get('date'))
        # Keep the newer post when possible
        if new_date and (not existing_date or new_date > existing_date):
            posts_map[link] = post_dict

    deduped = sorted(posts_map.values(), key=lambda p: parse_date(p.get('date')) or datetime.min, reverse=True)
    return deduped

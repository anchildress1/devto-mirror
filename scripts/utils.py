"""
Shared utilities for devto-mirror scripts
"""

import pathlib
from datetime import datetime
from email.utils import parsedate_to_datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Use a Jinja environment with autoescape enabled for HTML/XML templates
# Also add FileSystemLoader to load templates from files
template_dir = pathlib.Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(template_dir) if template_dir.exists() else None,
    autoescape=select_autoescape(["html", "xml"]),
)


# Load post template from file if available, otherwise use inline template
def get_post_template():
    """Get the post template, preferring file-based template if available"""
    try:
        if template_dir.exists():
            return env.get_template("post_template.html")
    except Exception as e:
        # Log the error but continue with fallback
        import logging

        logging.debug(f"Failed to load post template from file: {e}")

    # Fallback to inline template
    return env.from_string(POST_TEMPLATE_INLINE)


# Inline post template as fallback
POST_TEMPLATE_INLINE = """<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<title>{{ title }}</title>
<link rel="canonical" href="{{ canonical }}">
<meta name="description" content="{{ description }}">
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="article">
<meta property="og:url" content="{{ canonical }}">
<meta property="og:title" content="{{ title }}">
<meta property="og:description" content="{{ description }}">
<meta property="og:image" content="{{ social_image }}">
<meta property="og:site_name" content="{{ site_name }}">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="{{ canonical }}">
<meta name="twitter:title" content="{{ title }}">
<meta name="twitter:description" content="{{ description }}">
<meta name="twitter:image" content="{{ social_image }}">

<!-- LinkedIn -->
<meta property="linkedin:title" content="{{ title }}">
<meta property="linkedin:description" content="{{ description }}">
<meta property="linkedin:image" content="{{ social_image }}">

<!-- Additional Social Meta -->
<meta name="image" content="{{ social_image }}">
<meta name="author" content="{{ author }}">
{% if tags %}<meta name="keywords" content="{{ tags|join(', ') }}">{% endif %}

<!-- AI-Specific Enhanced Metadata -->
{% if enhanced_metadata %}
{% for name, content in enhanced_metadata.items() %}
<meta name="{{ name }}" content="{{ content }}">
{% endfor %}
{% endif %}

<!-- Cross-Reference Attribution Meta Tags -->
{% if cross_references and cross_references.attribution and cross_references.attribution.meta_tags %}
{% for name, content in cross_references.attribution.meta_tags.items() %}
<meta name="{{ name }}" content="{{ content }}">
{% endfor %}
{% endif %}

<!-- JSON-LD Structured Data -->
{% if json_ld_schemas %}
{% for schema in json_ld_schemas %}
<script type="application/ld+json">
{{ schema | tojson }}
</script>
{% endfor %}
{% endif %}
</head><body>
<main>
  <h1><a href="{{ canonical }}">{{ title }}</a></h1>
  {% if cover_image %}
  <img src="{{ cover_image }}?v=2"
      alt="Banner image for {{ title }}"
      style="width:100%;max-width:1000px;height:auto;margin:1em 0;">
  {% endif %}
  {% if date %}<p><em>Published: {{ date }}</em></p>{% endif %}
    {% if tags %}
    <p><strong>Tags:</strong>
        {% for tag in tags %}
            <span style="background:#f0f0f0; padding:2px 6px; margin:2px; border-radius:3px; font-size:0.9em;">
                #{{ tag }}
            </span>{% if not loop.last %} {% endif %}
        {% endfor %}
    </p>
    {% endif %}
  {% if description %}<p><em>{{ description }}</em></p>{% endif %}

  <!-- Enhanced Dev.to Attribution -->
  {% if cross_references and cross_references.attribution and cross_references.has_attribution %}
  {{ cross_references.attribution.attribution_html | safe }}
  {% endif %}

  <article>{{ content }}</article>

  <!-- Dev.to Backlinks -->
  {% if cross_references and cross_references.backlinks and cross_references.has_backlinks %}
  {{ cross_references.backlinks.backlink_html | safe }}
  {% endif %}

  <!-- Related Posts Section -->
  {% if cross_references and cross_references.related_posts and cross_references.has_related_posts %}
  <section style="margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px;
                  border: 1px solid #e9ecef;">
    <h3 style="margin-top: 0; color: #495057; font-size: 1.2em;">📚 Related Articles</h3>
    <ul style="list-style: none; padding: 0; margin: 0;">
      {% for related in cross_references.related_posts %}
      <li style="margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px;
                 border-left: 3px solid #007bff;">
        <div>
          <a href="{{ related.local_link }}" style="color: #007bff; text-decoration: none; font-weight: bold;">
            {{ related.title }}
          </a>
          {% if related.description %}
          <p style="margin: 5px 0; color: #6c757d; font-size: 0.9em;">{{ related.description }}</p>
          {% endif %}
          {% if related.shared_tags %}
          <div style="margin: 5px 0;">
            <small style="color: #868e96;">Shared tags:
              {% for tag in related.shared_tags %}
                <span style="background: #e9ecef; padding: 1px 4px; border-radius: 2px;
                             margin: 0 2px;">#{{ tag }}</span>
              {% endfor %}
            </small>
          </div>
          {% endif %}
        </div>
      </li>
      {% endfor %}
    </ul>
  </section>
  {% endif %}

  <p><a href="{{ canonical }}">Read on Dev.to →</a></p>
</main>
</body></html>"""

# Shared templates
INDEX_TMPL = env.from_string(
    """<!doctype html><html lang="en"><head>
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
"""
)

SITEMAP_TMPL = env.from_string(
    """<?xml version="1.0" encoding="UTF-8"?>
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
"""
)


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
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
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
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
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
        link = post.get("link") if isinstance(post, dict) else getattr(post, "link", None)
        if not link:
            continue

        post_dict = post.to_dict() if hasattr(post, "to_dict") else post
        new_date = parse_date(post_dict.get("date"))

        existing = posts_map.get(link)
        if existing is None:
            posts_map[link] = post_dict
            continue

        existing_date = parse_date(existing.get("date"))
        # Keep the newer post when possible
        if new_date and (not existing_date or new_date > existing_date):
            posts_map[link] = post_dict

    def _post_date_key(p):
        return parse_date(p.get("date")) or datetime.min

    deduped = sorted(posts_map.values(), key=_post_date_key, reverse=True)
    return deduped

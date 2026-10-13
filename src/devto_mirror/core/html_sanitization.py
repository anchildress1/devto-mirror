"""Allowlist sanitizer for Dev.to post bodies."""

from __future__ import annotations

import re

import nh3


def sanitize_html_content(content: str) -> str:
    """Sanitize post HTML while preserving basic formatting and safe embed wrappers.

    Notes:
    - Dev.to "ltag" embeds (e.g. GitHub README cards) use wrapper div/span tags with
      class hooks. The allowlist keeps those wrappers so the embed styling survives.
    - nh3 strips disallowed tags but keeps their body as text. That is *not*
      acceptable for <script>/<style> blocks, so we remove those blocks first.
    """

    if not content:
        return ""

    # Remove script/style blocks entirely (tag + content) so their payload doesn't
    # end up as visible text after sanitization.
    content = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", "", content)
    # Dev.to heading anchors are empty self-links: keep them as fragment targets, not unnamed links.
    content = re.sub(r'<a name="([^"]+)" href="#\1">\s*</a>', r'<a id="\1"></a>', content)

    allowed_tags = {
        *("p", "br", "hr", "div", "span", "blockquote", "pre", "code", "kbd"),
        *("strong", "em", "b", "i", "del", "s", "sub", "sup", "a", "img", "figure", "figcaption"),
        *("h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd"),
        *("table", "thead", "tbody", "tfoot", "tr", "th", "td", "details", "summary"),
    }

    allowed_attributes = {
        # Keep links readable and allow embed/card markup to style anchors.
        "a": {"href", "title", "rel", "target", "class", "id"},
        # Dev.to "ltag" embeds use wrapper div/span with class hooks.
        "div": {"class"},
        "span": {"class"},
        # width/height let browsers reserve space (CLS). No style: CSS sanitization isn't enabled.
        "img": {"src", "alt", "width", "height", "class", "title", "loading"},
        "th": {"colspan", "rowspan", "scope"},
        "td": {"colspan", "rowspan"},
    }

    # link_rel=None: "rel" is allowlisted on <a>, which nh3 treats as a conflict, and
    # bleach never injected rel either. url_schemes matches bleach's former default.
    return nh3.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        url_schemes={"http", "https", "mailto"},
        link_rel=None,
    )

"""HTML sanitization helpers.

These live in the application package (src/) so unit tests can import them without
triggering script side-effects.
"""

from __future__ import annotations

import re

import bleach


def sanitize_html_content(content: str) -> str:
    """Sanitize post HTML while preserving basic formatting and safe embed wrappers.

    Notes:
    - Dev.to "ltag" embeds (e.g. GitHub README cards) use wrapper div/span tags with
      class hooks. If we don't allow those wrappers, bleach will escape them into
      visible text ("&lt;div ...&gt;") unless strip=True.
    - With strip=True, bleach removes the tag but keeps its body as text. That is
      *not* acceptable for <script>/<style> blocks, so we remove those blocks first.
    """

    if not content:
        return ""

    # Remove script/style blocks entirely (tag + content) so their payload doesn't
    # end up as visible text after sanitization.
    content = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", "", content)

    allowed_tags = [
        "p",
        "br",
        "strong",
        "em",
        "a",
        "div",
        "span",
        "code",
        "pre",
        "blockquote",
        "ul",
        "ol",
        "li",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "img",
        "hr",
    ]

    allowed_attributes = {
        # Keep links readable and allow embed/card markup to style anchors.
        "a": ["href", "title", "rel", "target", "class"],
        # Dev.to "ltag" embeds use wrapper div/span with class hooks.
        "div": ["class"],
        "span": ["class"],
        # allow width/height/loading so we can avoid CLS and improve Lighthouse scores
        "img": ["src", "alt", "width", "height", "style", "class", "title", "loading"],
    }

    # IMPORTANT: strip disallowed tags rather than escaping them into visible text.
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True,
        strip_comments=True,
    )

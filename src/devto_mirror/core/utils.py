"""Jinja environment shared by every generated page."""

import json
import os
import pathlib

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

TEMPLATE_DIR = pathlib.Path(__file__).parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)

FIREBASE_SDK_VERSION = "12.19.0"

_FIREBASE_ANALYTICS_TMPL = """<!-- Firebase Analytics -->
<script type="module">
  import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/{version}/firebase-app.js";
  import {{ getAnalytics }} from "https://www.gstatic.com/firebasejs/{version}/firebase-analytics.js";
  const app = initializeApp({config});
  getAnalytics(app);
</script>"""


def firebase_analytics_snippet():
    """Build the Firebase Analytics script tag from FIREBASE_WEB_CONFIG.

    Returns safe markup for the snippet, or empty markup when the env var is
    unset/invalid or carries no measurementId. Forks without their own
    configured project therefore ship no analytics.
    """
    raw = os.getenv("FIREBASE_WEB_CONFIG", "").strip()
    if not raw:
        return Markup("")
    try:
        config = json.loads(raw)
    except (ValueError, TypeError):
        return Markup("")
    if not isinstance(config, dict) or not config.get("measurementId"):
        return Markup("")
    # Owner-controlled repo variable, not user input; escaping "<" neutralizes
    # any </script> breakout so the embedded JSON is inert regardless of source.
    config_json = json.dumps(config).replace("<", "\\u003c")
    return Markup(_FIREBASE_ANALYTICS_TMPL.format(version=FIREBASE_SDK_VERSION, config=config_json))  # nosec B704


# Expose to all templates rendered through this env; evaluated at render time.
env.globals["firebase_analytics"] = firebase_analytics_snippet

import os
import sys
import json
import pathlib
import requests
from datetime import datetime
from slugify import slugify
from jinja2 import Template

# --- Configuration ---
DEVTO_USERNAME = os.getenv("DEVTO_USERNAME", "").strip()
PAGES_REPO = os.getenv("PAGES_REPO", "").strip()
assert DEVTO_USERNAME, "Missing DEVTO_USERNAME"
assert "/" in PAGES_REPO, "Invalid PAGES_REPO (expected 'user/repo')"
username, repo = PAGES_REPO.split("/")
HOME = f"https://{username}.github.io/{repo}/"

ROOT = pathlib.Path(".")
POSTS_DIR = ROOT / "posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Templates (copied from generate_site.py) ---
PAGE_TMPL = Template("""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<title>{{ title }}</title>
<link rel="canonical" href="{{ canonical }}">
<meta name="description" content="{{ description }}">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body>
<main>
  <h1><a href="{{ canonical }}">{{ title }}</a></h1>
  {% if date %}<p><em>Published: {{ date }}</em></p>{% endif %}
  <article>{{ content }}</article>
  <p><a href="{{ canonical }}">Read on Dev.to →</a></p>
</main>
</body></html>
""")

# --- Helper Functions ---
def load_existing_posts(path="posts_data.json"):
    p = pathlib.Path(path)
    if not p.exists():
        return []
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return []

def save_posts_data(posts, path="posts_data.json"):
    # Sort posts by date, newest first
    posts.sort(key=lambda p: p.get('date', ''), reverse=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def fetch_article_from_api(slug):
    """Fetch a single article from the Dev.to API."""
    api_url = f"https://dev.to/api/articles/{DEVTO_USERNAME}/{slug}"
    print(f"Fetching article from: {api_url}")
    response = requests.get(api_url)
    response.raise_for_status()  # Will raise an exception for 4xx/5xx errors
    return response.json()

def convert_api_to_post_format(api_data):
    """Converts the API response to the format used in posts_data.json."""
    return {
        'title': api_data.get('title', 'Untitled'),
        'link': api_data.get('url', ''),
        'date': api_data.get('published_at', ''),
        'content_html': api_data.get('body_html', ''),
        'description': api_data.get('description', ''),
        'slug': api_data.get('slug', '')
    }

# --- Main Logic ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_post.py <post_slug>")
        sys.exit(1)

    post_slug = sys.argv[1]

    try:
        # 1. Fetch article from API
        article_data = fetch_article_from_api(post_slug)
        new_post = convert_api_to_post_format(article_data)

        # 2. Load existing posts
        existing_posts = load_existing_posts()
        existing_links = {p.get('link') for p in existing_posts}

        # 3. Add new post if it doesn't exist
        if new_post['link'] in existing_links:
            print(f"Post '{new_post['title']}' already exists. Skipping.")
        else:
            print(f"Adding new post: '{new_post['title']}'")
            existing_posts.append(new_post)
            save_posts_data(existing_posts)

            # 4. Generate HTML file for the new post
            html_out = PAGE_TMPL.render(
                title=new_post['title'],
                canonical=new_post['link'],
                description=new_post['description'],
                date=new_post['date'],
                content=new_post['content_html']
            )
            (POSTS_DIR / f"{new_post['slug']}.html").write_text(html_out, encoding="utf-8")
            print(f"Wrote: {new_post['slug']}.html")

        print("Post processing complete.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching article from API: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

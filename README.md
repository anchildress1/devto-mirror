# Dev\.to Mirror — The Set-and-Forget AI Crawler

![anchildress1/devto-mirror social card: A colorful crawler](https://github.com/anchildress1/devto-mirror/blob/main/assets/devto-mirror.jpg)

> [!NOTE]
>
> I’m slowly accepting that one or two brave souls might actually read my strong (and usually correct) opinions. 😅 I’m also always looking for ways to improve AI results across the board, because... well, _somebody_ has to. 🧠
>
> The internet already changed — blink and you missed it. We don’t Google anymore; we ask ChatGPT (the wise ones even ask for sources). 🤖
>  - **When I searched**: my [Dev.to](https://dev.to/anchildress1) showed up just as expected
>  - **When I asked Gemini the same thing**: crickets. 🦗
>
> So yeah, obvious disconnect... Also, I’m _not_ hosting a blog on my domain (I’m a backend dev; hosting a pretty blog + analytics sounds like a relaxing afternoon with Dante’s DevOps. Hard pass. 🔥🫠), but I still want control of `robots.txt.`
>
> **Enter the five-minute ChatGPT fix:** a tiny static mirror with canonicals back to **Dev.to** — no domain, no analytics — just (practically) instantly crawlable 😉🐜.
>
> P.S. “Five minutes” usually means two hours. Acceptable losses. 😅 And seriously, writing this blurb took longer than the code. 🤨 Alright.... **3 hours** (it took me an hour to get the picture just right, enough anyway). Still worth it! 😅
>
> — Ashley 🦄

---

## Repo Stuff

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-EDC531.svg?logo=apache)](./LICENSE)
![Repo Size](https://img.shields.io/github/repo-size/anchildress1/devto-mirror)
![Last Commit](https://img.shields.io/github/last-commit/anchildress1/devto-mirror)
![Stars](https://img.shields.io/github/stars/anchildress1/devto-mirror)
<br />
 [![BuyMeACoffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/anchildress1)
 [![dev.to Badge](https://img.shields.io/badge/dev.to-0A0A0A?logo=devdotto\&logoColor=fff)](https://dev.to/anchildress1)
 [![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?logo=linkedin\&logoColor=white)](https://www.linkedin.com/in/anchildress1/)

> **DevTO-Mirror** helps make your dev.to blogs more discoverable by search engines by automatically generating and hosting a mirror site with generous `robots.txt` rules. Avoiding Dante’s DevOps and the maintenance headache. This is a simple html, no frills approach with a sitemap and robots.tx — _that's it_. If you're like me and treat some comments as mini-posts, you can selectively pull in the ones that deserve their own page.

---

## How it works 🚀

* Runs ~~hourly~~ daily at **`9:15 AM EST`** so you (almost) never post exactly on the mirror time
* Uses a **single repo variable**: `DEVTO_USERNAME` — your Dev.to username
* Derives everything else (GitHub Pages URL, repository context) automatically
* Generates: `index.html`, `/posts/*.html`, `robots.txt`, `sitemap.xml`
* **Comments:** provides a way to index those special comments that are worthy of mini-post status by pulling your predefined comments into dedicated /comments/ pages with your blurb and context
* `robots.txt` welcomes major AI crawlers (toggle as you like): GPTBot, ClaudeBot, Claude-Web, Google-Extended, PerplexityBot, Bytespider, CCBot (Common Crawl), and more 👍

### First Run

- Fetches all posts from the RSS feed
- Generates HTML files for all posts
- Creates `posts_data.json` to track all posts
- Generates `index.html` and `sitemap.xml`

### Subsequent Runs

- Fetches latest posts from RSS feed
- Compares against existing posts in `posts_data.json`
- Only processes NEW posts (stops when it finds an existing post)
- Generates HTML files only for new posts
- Updates `posts_data.json` with new posts at the top
- Regenerates `index.html` and `sitemap.xml` with complete post list

**Note on Descriptions:** Post descriptions are automatically truncated to 160 characters to align with SEO best practices for search engine result snippets.

---

````markdown
# Dev.to Mirror

![social card](https://github.com/anchildress1/devto-mirror/blob/main/assets/devto-mirror.jpg)

This repository contains a tiny static mirror generator for Dev.to posts. It fetches posts from the Dev.to RSS feed and produces a minimal, crawler-friendly static site with canonical links back to Dev.to.

## What this repository contains

- `scripts/generate_site.py` — generator script that reads Dev.to RSS, produces `posts/` HTML files, `index.html`, `robots.txt`, and `sitemap.xml`, and persists post metadata to `posts_data.json`.
- `posts/` — generated HTML files for individual posts.
- `posts_data.json` — generated metadata tracking the known posts.
- `comments/` — optional generated note pages for comment links.
- `assets/` — images and static assets.

## Usage

Set the required environment variables and run the generator locally:

```bash
export DEVTO_USERNAME="your-username"
# Optionally set PAGES_REPO (e.g. username/repo). If not set, the script derives it from the git remote.
python scripts/generate_site.py
```

The first run generates all posts found in the RSS feed and writes `posts_data.json`. Subsequent runs update the archive incrementally and regenerate `index.html` and `sitemap.xml`.



## Notes

- The generator uses `feedparser`, `jinja2`, and `python-slugify`.
- Environment variables required: `DEVTO_USERNAME` (the Dev.to username). `PAGES_REPO` is optional but can be set to `username/repo`.

## Local test

```bash
python -m venv .venv && source .venv/bin/activate
pip install feedparser jinja2 python-slugify
DEVTO_USERNAME=yourname PAGES_REPO=username/repo python scripts/generate_site.py
open index.html
```

<small>Generated with the help of automation tooling</small>

````
4. **Enable GitHub Pages**

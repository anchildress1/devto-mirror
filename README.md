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
* Generates: `index.html`, `.nojekyll`, `robots.txt`, `sitemap.xml`, `last_run.txt`, `/posts/*.html`
* **Comments:** The `comments.txt` file provides a way to index those special comments that are worthy of mini-post status by pulling your predefined comments into dedicated `/comments/` pages with your blurb and context
* `robots.txt` welcomes major AI crawlers (toggle as you like): GPTBot, ClaudeBot, Claude-Web, Google-Extended, PerplexityBot, Bytespider, CCBot (Common Crawl), and more 👍

### First Run

- Fetches all posts via the Dev.to public API
- Generates HTML files for all posts
- Creates `posts_data.json` to track all posts
- Generates `index.html` and `sitemap.xml`

### Subsequent Runs

- Fetches latest posts via the Dev.to API
- Compares against existing posts in `posts_data.json`
- Only processes NEW posts (stops when it finds an existing post)
- Generates HTML files only for new posts
- Updates `posts_data.json` with new posts at the top
- Regenerates `index.html` and `sitemap.xml` with complete post list

Incremental updates are keyed off `last_run.txt`, which stores the ISO8601 UTC timestamp of the last successful run. The generator only processes articles with `published_at` after that timestamp and then updates the file.

**Note on Descriptions:** Post descriptions are automatically truncated to 160 characters to align with SEO best practices for search engine result snippets.

### Refresh All Posts and Comments 🔄

Need to refresh all your posts and comments? Use the **Refresh** workflow for a complete regeneration:

1. **Go to Actions** → "Refresh All Posts and Comments"
2. **Click "Run workflow"** → "Run workflow"
3. **Monitor progress** - The workflow will:
   - 📦 Create a timestamped backup branch of your current site
   - 🔄 Reset the last run timestamp to force full API data retrieval
   - 🚀 Trigger the main publish workflow for complete regeneration

**When to use refresh:**
- After making significant changes to the codebase
- When you suspect missing or corrupted data
- To force a complete rebuild from scratch

The refresh process safely backs up your current state before wiping and regenerating everything, ensuring you can recover if needed.

---

## Quick Setup (2-Second Version) ⚡

**TL;DR:** Fork this repo → Set your Dev.to username → Enable GitHub Pages → Done. Your site auto-updates daily.

### Step-by-Step Setup

1. **Fork this repository** or use it as a template
2. **Set Repository Variable**
   - Go to Settings → Secrets and variables → Actions → Variables
   - Add `DEVTO_USERNAME` with your Dev.to username
3. **Delete existing gh-pages branch** (if it exists)
   - Go to your repo → Branches
   - Delete the `gh-pages` branch if present
4. **Run the workflow manually** (creates the gh-pages branch)
   - Go to Actions → "Generate and Deploy Site"
   - Click "Run workflow" → "Run workflow"
   - Wait for it to complete (creates `gh-pages` branch with your content)
5. **Enable GitHub Pages** (now that gh-pages exists)
   - Go to Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `gh-pages`

🎉 **Your site is now live!** → `https://anchildress1.github.io/devto-mirror/` 👈 Add your actual URL here so your site stays discoverable!

*Note: All post links now include full Dev.to slugs with post IDs for proper navigation.*

### Local Development

```bash
git clone https://github.com/anchildress1/devto-mirror.git
cd devto-mirror
python -m venv .venv && source .venv/bin/activate
pip install requests jinja2 python-slugify
export DEVTO_USERNAME="your-username"
python scripts/generate_site.py
open index.html
```

## What You Get

- **Auto-generated site** that updates daily at 9:15 AM EST
- **SEO-friendly**: canonical links, sitemap.xml, robots.txt
- **AI crawler-friendly**: welcomes GPTBot, ClaudeBot, Google-Extended, etc.
- **Zero maintenance**: set it and forget it
- **Comment support**: optionally include special comments as standalone pages
# Trigger workflow rebuild Sun Aug 17 18:08:28 EDT 2025

---

## License 📄

Every project has to have a stack of fine print somewhere. _Keep going, keep going, keep going..._ Here's mine, as painless as possible:

You know where [the license](./LICENSE) is, but I'll sum it up: **this is not open source** (even though you can still do just about anything you want with it). As long as you're not turning it into the next big SaaS or selling subscriptions in the cloud, then have fun! Else, **you've gotta ask me first.**

Basically? This project's got boundaries. Be cool, don't try to sneak it into a product launch, and we'll get along just fine. 😘


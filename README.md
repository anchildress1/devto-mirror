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
* **Comments:** pulls your Dev.to comment URLs and content into dedicated /comments/ pages with your blurb and context (perfect for when a “comment” is basically a mini‑post)
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

---

## Key Benefits

1. **Preserves History**: Maintains all historical posts, not just the last 30 days from RSS
2. **Efficient**: Only generates HTML for new posts, skips existing ones
3. **Rolling Updates**: New posts appear at the top, creating a growing archive
4. **Fast**: No need to regenerate existing content

## Files

- `scripts/generate_site.py` - Main script with incremental update logic
- `posts_data.json` - Persistent storage of all posts (auto-generated)
- `.github/workflows/publish.yaml` - GitHub Actions workflow (runs daily)

## Environment Variables

This should be set in the repo settings as an environment variable.

- `DEVTO_USERNAME` - Your Dev.to username

---

## Manual Usage

```bash
export DEVTO_USERNAME="your-username"
# PAGES_REPO is automatically calculated from your repository information
python scripts/generate_site.py
```

The script automatically detects first run vs subsequent runs and behaves accordingly.

---

## Forking and Using This Mirror

### Quick Setup for Your Own Dev.to Mirror

1. **Fork this repository**
   ```bash
   # Click "Fork" on GitHub or use GitHub CLI
   gh repo fork anchildress1/devto-mirror --clone
   ```

2. **Delete existing `gh-pages` branch**
   ```bash
   git push origin --delete gh-pages
   ```

3. **Configure your Dev.to username**
   - Go to your forked repository settings
   - Navigate to Settings → Secrets and variables → Repository variables
   - Add a new variable:
     - Name: `DEVTO_USERNAME`
     - Value: `your-devto-username`

4. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` (or your default branch)
   - Folder: `/ (root)`

5. **Run the initial setup**
   - Go to Actions tab
   - Click on "Dev.to Mirror (Static, Hourly)"
   - Click "Run workflow" → "Run workflow"
   - Wait for completion
   - Optional: You can change the schedule (UTC) in `.github/workflows/publish.yaml` to run at a different time.

6. **Your mirror is ready!**
   - Visit `https://yourusername.github.io/devto-mirror`
   - Posts will auto-update daily at 2:15 PM UTC

### Troubleshooting

- **No posts appearing**: Check that `DEVTO_USERNAME` variable is set correctly
- **Pages not updating**: Verify GitHub Pages is enabled and workflow is running
- **Want to start fresh**: Use the "Reset All" workflow described above

---

## Pro Tip 💡

Add a custom `description:` in your Dev.to post as a comment. It’s not mandatory, but it *can* help bots pull in a better preview — even if it’s extra work up front.

```markdown
<!-- description: One-line summary for crawlers and previews for this post. -->
```

> 🦄 I did do this on a couple, and I’m still waiting to see if it truly makes a difference. It wouldn’t be the first time ChatGPT talked me into something that sounded absolutely insane and ended up 100% working... I guess we'll find out!

---

## Discovery & Timing ⏱️

* GitHub Pages is friendly — usually crawled within **minutes to a few hours**
* AI engines may take **hours to a couple days** to surface your content
* You can speed it up with minimal linking (no big broadcast required)

**Examples:**

* Add a small link to this mirror in **this repo’s README**. That’s enough for discovery.
* Optional: if you have a **profile README** (`<your-username>/<your-username>`), drop a quiet line like: `Mirror for bots → https://<github-username>.github.io/<repo>/`.
* Optional: orgs can use an **org profile README** (`.github/profile/README.md`) with a tiny link.
* You do **not** need to put the Pages link into your Dev.to posts if you want to keep the mirror low‑profile. The **sitemap.xml** and the link from this repo are sufficient.

---

## Local Test 🖥️

```bash
python -m venv .venv && source .venv/bin/activate
pip install feedparser jinja2 python-slugify
DEVTO_USERNAME=yourname PAGES_REPO=username/repo python scripts/generate_site.py
open index.html
```

> 🦄 I’ve never actually tried the local test myself — if it works for you, let me know. 😅

---

<small>Generated with the help of ChatGPT and GitHub Copilot</small>

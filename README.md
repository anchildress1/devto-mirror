# Dev.to Mirror (Static, Hourly, Zero‑Drama)

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
> P.S. “Five minutes” usually means two hours. Acceptable losses. 😅 And seriously, writing this blurb took longer than the code. 🤨
>
> — Ashley 🦄

---

## How it works 🚀

* Runs **hourly at **`:03`** UTC** so you (almost) never post exactly on the mirror time
* Uses a **single repo variable**: `DEVTO_USERNAME` — your Dev.to username
* Derives everything else (GitHub Pages URL, repository context) automatically
* Generates: `index.html`, `/posts/*.html`, `robots.txt`, `sitemap.xml`
* `robots.txt` welcomes major AI crawlers (toggle as you like): GPTBot, ClaudeBot, Claude-Web, Google-Extended, PerplexityBot, Bytespider, CCBot (Common Crawl), and more 👍

---

## Quick Setup 🛠️

1. Go to **Settings → Secrets and variables → Actions → Variables**:

   * Add `DEVTO_USERNAME = your-devto-username`
2. **Enable GitHub Pages**:

   * Go to **Settings → Pages**
   * Under **Build and deployment**, set **Source** to **Deploy from a branch**
   * Set **Branch** to **main** and **Folder** to **/** (root)
   * Click **Save**
3. Manually trigger the workflow once via **Actions → Run workflow**.
4. Visit your auto-generated site at:

   ```
   https://<github-username>.github.io/<repo>/
   ```

   Example: `https://example.github.io/devto-mirror/`

---

## Pro Tip 💡

Add a custom `description:` in your Dev.to post front matter. It’s not mandatory, but it *can* help bots pull in a better preview — even if it’s extra work up front.

```yaml
---
description: "One-line summary for crawlers and previews."
---
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

<small>Generated with the help of ChatGPT</small>

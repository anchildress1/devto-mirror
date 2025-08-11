# Dev\.to Mirror — The Set-and-Forget AI Crawler

![anchildress1/devto-mirror social card: A colorful crawler](https://github.com/anchildress1/devto-mirror/blob/main/assets/devto-mirror-2.jpg)

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

# Repo Stuff

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
5. Add a small link to this mirror in **this repo’s README** for discovery.
  > Like _right here_ 👇

   Example: [https://anchildress1.github.io/devto-mirror/](https://anchildress1.github.io/devto-mirror/)

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

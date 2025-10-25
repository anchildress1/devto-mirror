# Dev.to Mirror — The Set-and-Forget AI Crawler

🔗 **Live Site:** [anchildress1.github.io/devto-mirror](https://anchildress1.github.io/devto-mirror/)

![anchildress1/devto-mirror social card: A colorful crawler](https://github.com/anchildress1/devto-mirror/blob/main/assets/devto-mirror.jpg)

> [!NOTE]
>
> I'm slowly accepting that one or two brave souls might actually read my strong (and usually correct) opinions. 😅 I'm also always looking for ways to improve AI results across the board, because... well, _somebody_ has to. 🧠
>
> The internet already changed — blink and you missed it. We don't Google anymore; we ask ChatGPT (the wise ones even ask for sources). 🤖
>  - **When I searched**: my [Dev.to](https://dev.to/anchildress1) showed up just as expected
>  - **When I asked Gemini the same thing**: crickets. 🦗
>
> So yeah, obvious disconnect... Also, I'm _not_ hosting a blog on my domain (I'm a backend dev; hosting a pretty blog + analytics sounds like a relaxing afternoon with Dante's DevOps. Hard pass. 🔥🫠), but I still want control of `robots.txt.`
>
> **Enter the five-minute ChatGPT fix:** a tiny static mirror with canonicals back to **Dev.to** — no domain, no analytics — just (practically) instantly crawlable 😉🐜.
>
> P.S. "Five minutes" usually means two hours. Acceptable losses. 😅 And seriously, writing this blurb took longer than the code. 🤨 Alright.... **3 hours** (it took me an hour to get the picture just right, enough anyway). Still worth it! 😅
>
> — Ashley 🦄

---

## Repo Stuff

[![GitHub License](https://img.shields.io/badge/license-Polyform_Shield_1.0.0-yellow)](./LICENSE) ![Repo Size](https://img.shields.io/github/repo-size/anchildress1/devto-mirror) ![Last Commit](https://img.shields.io/github/last-commit/anchildress1/devto-mirror) ![Stars](https://img.shields.io/github/stars/anchildress1/devto-mirror)
 [![BuyMeACoffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/anchildress1) [![dev.to Badge](https://img.shields.io/badge/dev.to-0A0A0A?logo=devdotto\&logoColor=fff)](https://dev.to/anchildress1) [![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?logo=linkedin\&logoColor=white)](https://www.linkedin.com/in/anchildress1/)

## What is this?

Auto-generates a static mirror of your Dev.to blog with generous `robots.txt` for AI crawlers. Simple HTML, sitemap, canonical links — zero maintenance.

---

## Quick Setup ⚡

1. Fork this repo
2. Set repository variable: Settings → Actions → Variables → Add `DEVTO_USERNAME`
3. Delete `gh-pages` branch if it exists
4. Run workflow: [Actions → "Generate and Publish Dev.to Mirror Site" → Run workflow](https://github.com/anchildress1/devto-mirror/actions)
5. Enable Pages: Settings → Pages → Deploy from branch → `gh-pages`

Done. Auto-updates weekly (Wednesdays) at 9:40 AM EDT.

---

## How it works

- Fetches posts via Dev.to API (incremental updates via `last_run.txt` timestamp)
- Generates HTML files with canonical links back to Dev.to
- Creates sitemap, robots.txt, index
- Optional: Include special comments as standalone pages via `comments.txt`

**Refresh everything:** Actions → "Generate and Publish Dev.to Mirror Site" and set `force_full_regen` to `true` (creates backup, wipes, regenerates)

---

## Local Development

```bash
git clone https://github.com/anchildress1/devto-mirror.git
cd devto-mirror
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
export DEVTO_USERNAME="your-username"
export PAGES_REPO="your-username/devto-mirror"

# Run tests
python -m unittest

# Run quality checks
pre-commit run --all-files

# Generate site
python scripts/generate_site.py
```

### Local Security & Linting

Install hooks: `pre-commit install`
Run checks: `pre-commit run --all-files`
Manual audit: `pip-audit --progress-spinner=off`

Runs: bandit, flake8, detect-secrets, pip-audit

---

## License 📄

Every project has to have a stack of fine print somewhere. _Keep going, keep going, keep going..._ Here's mine, as painless as possible:

You know where [the license](./LICENSE) is, but I'll sum it up: **this is not open source** (even though you can still do just about anything you want with it). As long as you're not turning it into the next big SaaS or selling subscriptions in the cloud, then have fun! Else, **you've gotta ask me first.**

Basically? This project's got boundaries. Be cool, don't try to sneak it into a product launch, and we'll get along just fine. 😘

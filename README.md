# Dev.to Mirror — The Set-and-Forget AI Crawler

🔗 **Live Site:** [anchildress1.github.io/devto-mirror](https://anchildress1.github.io/devto-mirror/)

![anchildress1/devto-mirror social card: A colorful crawler](https://github.com/anchildress1/devto-mirror/blob/main/assets/devto-mirror.jpg)

This Copilot generated utility helps make your Dev.to blogs more discoverable by search engines by automatically generating and hosting a mirror site with generous `robots.txt` rules. Avoiding Dante’s DevOps and the maintenance headache. This is a simple html, no frills approach with a sitemap and robots.tx — _that's it_ (although I'm slowly working through enhancements). If you're like me and treat some comments as mini-posts, you can selectively pull in the ones that deserve their own page.

> [!NOTE]
>
> I'm slowly accepting that one or two brave souls might actually read my strong (and usually correct) opinions. 😅 I'm also always looking for ways to improve AI results across the board, because... well, _somebody_ has to. 🧠
>
> The internet already changed — blink and you missed it. We don't Google anymore; we ask ChatGPT (the wise ones even ask for sources). 🤖
>
> - **When I searched**: my [Dev.to](https://dev.to/anchildress1) showed up just as expected
> - **When I asked Gemini the same thing**: crickets. 🦗
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

[![GitHub License](https://img.shields.io/badge/license-Polyform_Shield_1.0.0-yellow?style=flat)](./LICENSE) ![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat) ![Repo Size](https://img.shields.io/github/repo-size/anchildress1/devto-mirror?style=flat) ![Last Commit](https://img.shields.io/github/last-commit/anchildress1/devto-mirror?style=flat)

[![Publish Dev.to Mirror Site](https://github.com/anchildress1/devto-mirror/actions/workflows/publish.yaml/badge.svg?branch=main&style=flat)](https://github.com/anchildress1/devto-mirror/actions/workflows/publish.yaml) [![CodeQL Analysis](https://github.com/anchildress1/devto-mirror/actions/workflows/codeql.yml/badge.svg?style=flat)](https://github.com/anchildress1/devto-mirror/actions/workflows/codeql.yml) [![Security and Lint CI](https://github.com/anchildress1/devto-mirror/actions/workflows/security-ci.yml/badge.svg?style=flat)](https://github.com/anchildress1/devto-mirror/actions/workflows/security-ci.yml)

![Python Badge](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fanchildress1%2Fdevto-mirror%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.project.requires-python&style=flat&logo=python&logoColor=fff&label=Python&color=3776AB) ![Jinja Badge](https://img.shields.io/badge/Jinja-7E0C1B?logo=jinja&logoColor=fff&style=flat) ![GitHub Pages Badge](https://img.shields.io/badge/GitHub%20Pages-222?logo=githubpages&logoColor=fff&style=flat) ![GitHub Actions Badge](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=fff&style=flat) ![GitHub Copilot Badge](https://img.shields.io/badge/GitHub%20Copilot-000?logo=githubcopilot&logoColor=fff&style=flat)

 [![BuyMeACoffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?logo=buy-me-a-coffee&logoColor=black&style=flat)](https://www.buymeacoffee.com/anchildress1) [![dev.to Badge](https://img.shields.io/badge/dev.to-0A0A0A?logo=devdotto&logoColor=fff&style=flat)](https://dev.to/anchildress1) [![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin\&logoColor=white&style=flat)](https://www.linkedin.com/in/anchildress1/)

## What is this?

Auto-generates a static mirror of your Dev.to blog with generous `robots.txt` for AI crawlers. Simple HTML, sitemap, canonical links — zero maintenance.

---

## Quick Setup ⚡

1. Fork this repo
2. Set repository variables: Settings → Actions → Variables
   - Add `DEVTO_USERNAME` (your Dev.to username)
   - Add `GH_USERNAME` (GitHub username, since apparently naming this variable "GITHUB" is not allowed)
3. (Optional) Set API key: Settings → Actions → Secrets → Add `DEVTO_API_KEY` (only needed for private/draft posts)
4. (Optional) Set root deploy token: Settings → Actions → Secrets → Add `ROOT_SITE_PAT` (see Root Deployment below)
5. Delete `gh-pages` branch if it exists
6. Run workflow: [Actions → "Generate and Publish Dev.to Mirror Site" → Run workflow](https://github.com/anchildress1/devto-mirror/actions)
7. Enable Pages: Settings → Pages → Deploy from branch → `gh-pages`

> Auto-updates weekly (Wednesdays) at 9:40 AM EST.

### Root Deployment (Optional)

To deploy config files (robots.txt, llms.txt, sitemap.xml) to your root GitHub Pages (`https://<username>.github.io/`):

1. Create a repository named `<username>/<username>` (e.g., `anchildress1/anchildress1`)
2. Create a Personal Access Token:
   - Settings → Developer settings → Personal access tokens → Generate new token
   - Classic: Check `repo` scope
   - Fine-grained: Grant `contents: write` permission to your `<username>/<username>` repo
3. Add token as repository secret: Settings → Actions → Secrets → New secret named `ROOT_SITE_PAT`

Without this token, the workflow will only deploy to the project repository.

> **Note:** The workflow automatically generates robots.txt and llms.txt for your root GitHub Pages site using `GH_USERNAME`. The robots.txt template in `assets/` uses `{root_home}` placeholders that are replaced during deployment to your `<username>/<username>` repo - no manual URL configuration needed!

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

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or update to latest version
uv self --no-python-downloads update

# Create lockfile and sync dependencies
uv lock
uv sync --locked --group dev

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your DEVTO_USERNAME and PAGES_REPO

# Run full validation
make validate

# Generate site locally
uv run python scripts/generate_site.py
```

**For detailed development setup, CI/CD workflows, and troubleshooting**: See [`docs/DEV_GUIDE.md`](docs/DEV_GUIDE.md)

---

## Documentation 📚

Additional documentation is available in the [`docs/`](./docs/) directory:

- [Development Guide](./docs/DEV_GUIDE.md) - Local development setup and commands
- [CI/CD Guide](./docs/CI_GUIDE.md) - GitHub Actions workflows and deployment
- [Security Analysis](./docs/SECURITY_ANALYSIS.md) - Security recommendations and workflows
- [Migration Plan](./docs/MIGRATION_PLAN.md) - AI optimization refactoring progress

## License 📄

Every project has to have a stack of fine print somewhere. _Keep going, keep going, keep going..._ Here's mine, as painless as possible:

You know where [the license](./LICENSE) is, but I'll sum it up: **this is not open source** (even though you can still do just about anything you want with it). As long as you're not turning it into the next big SaaS or selling subscriptions in the cloud, then have fun! Else, **you've gotta ask me first.**

Basically? This project's got boundaries. Be cool, don't try to sneak it into a product launch, and we'll get along just fine. 😘

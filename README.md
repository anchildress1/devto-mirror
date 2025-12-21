# Dev.to Mirror—The Set-and-Forget AI Crawler

🔗 **Live Site:** [anchildress1.github.io/devto-mirror](https://anchildress1.github.io/devto-mirror/)

![anchildress1/devto-mirror social card: A colorful crawler](https://github.com/anchildress1/devto-mirror/blob/main/assets/new-devto-mirror-crawlies-banner.jpg)

This Copilot generated utility helps make your Dev.to blogs more discoverable by search engines by automatically generating and hosting a mirror site with generous `robots.txt` rules. Avoiding Dante’s DevOps and the maintenance headache. This is a simple html, no frills approach with a sitemap and robots.tx—_that's it_ (although I'm slowly working through enhancements). If you're like me and treat some comments as mini-posts, you can selectively pull in the ones that deserve their own page.

> [!NOTE]
>
> I'm slowly accepting that one or two brave souls might actually read my strong (and usually correct) opinions. 😅 I'm also always looking for ways to improve AI results across the board, because... well, _somebody_ has to. 🧠
>
> The internet already changed—blink and you missed it. We don't Google anymore; we ask ChatGPT (the wise ones even ask for sources). 🤖
>
> - **When I searched**: my [Dev.to](https://dev.to/anchildress1) showed up just as expected
> - **When I asked Gemini and ChatGPT the same thing**: crickets. 🦗
>
> So yeah, obvious disconnect... Also, I'm _not_ hosting a blog on my domain (I'm a backend dev; hosting a pretty blog + analytics sounds like a relaxing afternoon with Dante's DevOps. Hard pass. 🔥🫠), but I still want control of `robots.txt.`
>
> **Enter the five-minute ChatGPT fix:** a tiny static mirror with canonicals back to **Dev.to**—no domain, no analytics—just (practically) instantly crawlable 😉🐜.
>
> P.S. "Five minutes" usually means two hours. Acceptable losses. 😅 And seriously, writing this blurb took longer than the code. 🤨 Alright.... **3 hours** (it took me an hour to get the picture just right, enough anyway) and lots of follow up work. Still worth it! 😅
>
>—Ashley 🦄

## Repo Stuff

[![GitHub License](https://img.shields.io/badge/license-Polyform_Shield_1.0.0-yellow?style=for-the-badge)](./LICENSE) ![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge) ![Repo Size](https://img.shields.io/github/repo-size/anchildress1/devto-mirror?style=for-the-badge) ![Last Commit](https://img.shields.io/github/last-commit/anchildress1/devto-mirror?style=for-the-badge)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/anchildress1/devto-mirror/publish.yaml?branch=main&style=for-the-badge&logo=github&logoColor=fff&label=Publish%20Dev.to%20Mirror%20Site)](https://github.com/anchildress1/devto-mirror/actions/workflows/publish.yaml) [![CodeQL Analysis](https://img.shields.io/github/actions/workflow/status/anchildress1/devto-mirror/codeql.yml?branch=main&style=for-the-badge&logo=github&logoColor=fff&label=CodeQL%20Analysis)](https://github.com/anchildress1/devto-mirror/actions/workflows/codeql.yml) [![Security and Lint CI](https://img.shields.io/github/actions/workflow/status/anchildress1/devto-mirror/security-ci.yml?branch=main&style=for-the-badge&logo=github&logoColor=fff&label=Security%20and%20Quality%20CI)](https://github.com/anchildress1/devto-mirror/actions/workflows/security-ci.yml)

![Python Badge](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fanchildress1%2Fdevto-mirror%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.project.requires-python&style=for-the-badge&logo=python&logoColor=fff&label=Python&color=3776AB) ![uv Badge](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=fff&style=for-the-badge) ![Jinja Badge](https://img.shields.io/badge/Jinja-7E0C1B?logo=jinja&logoColor=fff&style=for-the-badge) ![GitHub Actions Badge](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=fff&style=for-the-badge) ![GitHub Pages Badge](https://img.shields.io/badge/GitHub%20Pages-222?logo=githubpages&logoColor=fff&style=for-the-badge)

![Verdent Badge](https://img.shields.io/badge/Verdent-00D486?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAzMiAzMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48dGl0bGU+VmVyZGVudDwvdGl0bGU+CjxwYXRoIGQ9Ik0xNy42IDkuOUMxNy42IDEyLjEgMTYuOCAxNC4yIDE1LjQgMTUuN0wxNS4xIDE2QzEzLjcgMTcuNSAxMi44IDE5LjYgMTIuOCAyMS44QzEyLjggMjIuNSAxMi45IDIzLjIgMTMuMSAyMy45QzEwLjcgMjIuOSA4LjggMjAuOSA4IDE4LjRDNy44IDE3LjYgNy43IDE2LjggNy43IDE2QzcuNyAxMy44IDguNSAxMS44IDkuOCAxMC4zTDE1LjMgNEMxNi4yIDUgMTYuOSA2LjEgMTcuMyA3LjVDMTcuNSA4LjIgMTcuNiA5IDE3LjYgOS45WiIgZmlsbD0iI2ZmZmZmZiIvPgo8cGF0aCBkPSJNMTQuMyAyMi43QzE0LjMgMjAuNSAxNS4xIDE4LjQgMTYuNSAxNi45TDE2LjggMTYuNkMxOC4yIDE1LjEgMTkuMSAxMyAxOS4xIDEwLjhDMTkuMSAxMCAxOSA5LjQgMTguOCA4LjdDMjEuMiA5LjcgMjMuMSAxMS43IDIzLjkgMTQuMkMyNCAxNSAyNC4yIDE1LjggMjQuMiAxNi42QzI0LjIgMTguOCAyMy40IDIwLjggMjIuMSAyMi4zTDE2LjYgMjguNkMxNS43IDI3LjYgMTUgMjYuNSAxNC42IDI1LjFDMTQuNCAyNC4zIDE0LjMgMjMuNSAxNC4zIDIyLjdaIiBmaWxsPSIjZmZmZmZmIi8+Cjwvc3ZnPg==) ![GitHub Copilot Badge](https://img.shields.io/badge/GitHub%20Copilot-000?logo=githubcopilot&logoColor=fff&style=for-the-badge)

![Conventional Commits Badge](https://img.shields.io/badge/Conventional%20Commits-FE5196?logo=conventionalcommits&logoColor=fff&style=for-the-badge) ![Lefthook Badge](https://img.shields.io/badge/Lefthook-FF1E1E?logo=lefthook&logoColor=fff&style=for-the-badge) ![Dependabot Badge](https://img.shields.io/badge/Dependabot-025E8C?logo=dependabot&logoColor=fff&style=for-the-badge)

 [![BuyMeACoffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?logo=buy-me-a-coffee&logoColor=black&style=for-the-badge)](https://www.buymeacoffee.com/anchildress1) [![dev.to Badge](https://img.shields.io/badge/dev.to-0A0A0A?logo=devdotto&logoColor=fff&style=for-the-badge)](https://dev.to/anchildress1) [![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin\&logoColor=white&style=for-the-badge)](https://www.linkedin.com/in/anchildress1/) [![Medium](https://img.shields.io/badge/Medium-000?logo=medium&logoColor=fff&style=for-the-badge)](https://medium.com/@anchildress1) [![Reddit Badge](https://img.shields.io/badge/Reddit-FF4500?logo=reddit&logoColor=fff&style=for-the-badge)](https://www.reddit.com/user/anchildress1/)

## What is this?

Auto-generates a static mirror of your Dev.to blog with generous `robots.txt` for AI crawlers. Simple HTML, sitemap, canonical links—zero maintenance.

## Quick Setup ⚡

1. **Fork** this repo
2. **Set variables** (Settings → Actions → Variables):
  - `DEVTO_USERNAME` – your Dev.to username
  - `GH_USERNAME` – your GitHub username
3. **(Optional) Set API key** (Settings → Actions → Secrets):
  - `DEVTO_KEY` – for private/draft posts
4. **Delete** `gh-pages` branch if it exists
5. **Update** `comments.txt` file (or delete it completely)
6. **Run workflow** Actions → [Generate and Publish Dev.to Mirror Site](https://github.com/1nchildress1/devto-mirror/actions) → Run workflow
7. **Enable Pages** → Settings → Pages → Deploy from branch → `gh-pages`

This will automatically pull new content from Dev every **Wednesday at 9:40 AM EST**.

> [!IMPORTANT]
> Deploying with a `gh-pages` branch is somewhat deprecated, but it was the most straightforward way to keep a running history. This eliminates unnecessary calls to the Dev API every week. If you want to force a complete refresh, you can manually trigger the `publish.yaml` workflow with the `force_full_regen` option.

## How it works

Fetches posts via Dev.to API (incremental updates via `last_run.txt`). Generates **plain HTML** files with canonical links back to Dev.to, AI-specific optimizations, plus sitemap and robots.txt. Optional: include comments as standalone pages via `comments.txt` or delete it entirely.

**Force full regeneration:** Actions → [Generate and Publish Dev.to Mirror Site](https://github.com/1nchildress1/devto-mirror/actions) → Run workflow with `force_full_regen: true`.

> [!WARNING]
> I've tinkered some with moving `robots.txt` and `llms.txt` to the base-level repo, but haven't been able to make it work yet. Research says it's possible, but I'm either doing it all wrong *or* AI lied to me. 🤷‍♀️ So, the [Google Search Console](https://search.google.com/search-console) have a difficult time locating these files currently. Otherwise, there doesn't seem to be any problems with keeping those files here.

## Local Development

```bash
git clone https://github.com/anchildress1/devto-mirror.git
cd devto-mirror

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or update to latest version
uv self --no-python-downloads update

# Install dependencies and lefthook hooks
make install

# Configure environment
cp .env.example .env
# Edit .env with your DEVTO_USERNAME and GH_USERNAME

# Run validation
make ai-checks
```

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

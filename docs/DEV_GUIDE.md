# Development Guide

How to run devto-mirror locally, what the checks do, and how to set up a fork's deploy.

## 🚀 Local Setup

You need Python 3.12+, [`uv`](https://docs.astral.sh/uv/), Git, and a Dev.to account with published posts. The Git hooks also call [`actionlint`](https://github.com/rhysd/actionlint), which isn't a Python package—install it yourself (e.g. `brew install actionlint`).

```bash
git clone https://github.com/anchildress1/devto-mirror.git
cd devto-mirror
make install        # dev dependencies + Lefthook hooks
cp .env.example .env
# edit .env (see Environment Variables below)
make ai-checks      # confirm everything passes before you change anything
uv run python -m devto_mirror.site_generation.generator
```

The generator writes the site into `_deploy/` and the article store into `posts_data.json`, both in the repo root and both gitignored. Open `_deploy/index.html` to browse the result. The next run reuses `posts_data.json` and only fetches articles that are new or edited since.

## ⚙️ Environment Variables

The generator loads `.env` automatically.

| Variable | Required | What it does |
| --- | --- | --- |
| `DEVTO_USERNAME` | yes | Dev.to profile to mirror |
| `SITE_DOMAIN` | one of these two | Custom domain; wins over `GH_USERNAME` |
| `GH_USERNAME` | one of these two | Builds `https://<user>.github.io/devto-mirror/` |
| `DEVTO_KEY` | no | Dev.to API key; only raises rate limits, since the mirror calls public endpoints |
| `FORCE_FULL_REGEN` | no | `true` ignores `posts_data.json` and refetches every article |
| `FIREBASE_WEB_CONFIG` | no | Firebase web config JSON with a `measurementId`; adds Firebase Analytics to every page. A set-but-invalid value fails the build |

`SITE_DOMAIN` accepts `example.com`, `example.com/`, or a full URL like `https://example.com/blog/`. A bare domain with a path (`example.com/blog`) is rejected as ambiguous. For GitHub Pages, use a bare domain—the deploy writes it to `CNAME`.

Custom domain:

```bash
DEVTO_USERNAME=your-username
SITE_DOMAIN=crawly.anchildress1.dev
```

GitHub Pages:

```bash
DEVTO_USERNAME=your-username
GH_USERNAME=your-github-username
```

## 🔁 Development Workflow

| Command | What it runs |
| --- | --- |
| `make install` | `uv sync --locked --group dev`, then installs Lefthook hooks (skipped in CI) |
| `make format` | Black, 120-character lines |
| `make lint` | `black --check`, `isort --check-only`, flake8 |
| `make security` | bandit; pip-audit (CI only, or locally with `PIP_AUDIT=1`); a detect-secrets gate against `.secrets.baseline` |
| `make check-complexity` | radon cyclomatic complexity; fails on any function over 15 |
| `make test` | unittest suite with coverage |
| `make ai-checks` | format → lint → security → complexity → test |
| `make clean` | removes coverage output, caches, and build artifacts |

`make ai-checks` formats in place, and CI fails if it changes any tracked file—so run it (or `make format`) before you push.

## 🪝 Git Hooks

`make install` wires up Lefthook:

- **pre-commit**: `uv lock`, Black, flake8, isort, `make security`, and actionlint on staged workflow files
- **commit-msg**: `gitlint-rai` checks the message format
- **pre-push**: `make test`, `make check-complexity`, actionlint

A failing hook blocks the commit or push. Run `make format`, then `make lint`, to see what's wrong.

## 🧭 Code Tour

- `site_generation/generator.py` — the entry point: loads the store, syncs with Dev.to, renders every page
- `site_generation/post.py` — the `Post` model built from a Dev.to article (sanitized HTML, canonical URL, dates)
- `site_generation/seo.py` — `BlogPosting` JSON-LD and related posts by shared tags
- `core/api_client.py` — lists articles, fetches new or edited ones, retries transient failures
- `core/html_sanitization.py` — bleach allowlist for post bodies, including tables
- `core/url_utils.py` — turns `SITE_DOMAIN`/`GH_USERNAME` into the site's root URL
- `core/utils.py` — the Jinja environment and the optional Firebase Analytics snippet
- `templates/` — `base.html` holds the shared `<head>`; `post.html`, `index.html`, and `comment.html` extend it

## 🧪 Testing

```bash
make test                                     # full suite + coverage report
uv run python -m unittest tests.test_seo      # one module
```

Tests use `unittest` and never touch the network—API calls and sleeps are mocked, and `tests/factories.py` builds Dev.to article payloads. Coverage must stay at or above 85% (it's currently 100%); an HTML report lands in `htmlcov/`.

## 🩺 Troubleshooting

| Error | Fix |
| --- | --- |
| `Missing DEVTO_USERNAME` | Create `.env` from `.env.example` and set the variable |
| `Missing SITE_DOMAIN or GH_USERNAME` | Set one of them |
| `SITE_DOMAIN must be a domain, not a path` | Use a bare domain or a full `https://` URL |
| `Dev.to lists no published articles ... refusing to publish an empty site` | Check the username; the account needs at least one published post |
| `... stored articles vanished from the listing; refusing to sync` | Usually a Dev.to glitch—rerun later. After a real mass deletion, run with `FORCE_FULL_REGEN=true` |
| `FIREBASE_WEB_CONFIG must be a JSON object with a measurementId` | Fix the variable's JSON, or unset it to disable Analytics |
| HTTP errors after retries | Dev.to is down or rate-limiting you; rerun later, or set `DEVTO_KEY` for higher limits |
| `actionlint: command not found` in hooks | Install actionlint (see Local Setup) |
| Import errors | Run `make install` so the package is installed into `.venv` |

## 🚢 GitHub Actions Setup

There are two deploy paths:

- **Upstream (owner `anchildress1`) → Firebase Hosting** via `publish.yaml`. Keyless auth through Workload Identity Federation; only runs for the repo owner. See [CI_GUIDE.md](./CI_GUIDE.md).
- **Forks → GitHub Pages** via `deploy-gh-pages.yml`. This is the path below.

To set up a fork:

1. Add the repository variables (Settings → Secrets and variables → Actions → Variables): `DEVTO_USERNAME`, plus `GH_USERNAME` or `SITE_DOMAIN`. Optionally add a `DEVTO_KEY` secret.
2. Run Actions → **Deploy Dev.to Mirror to GitHub Pages** → Run workflow. It creates the `gh-pages` branch. If your fork inherited upstream's `gh-pages`, the run replaces its contents—upstream's articles aren't in your Dev.to listing, so they drop out of the store.
3. Enable Pages: Settings → Pages → Deploy from a branch → `gh-pages`. The site appears at `https://<username>.github.io/devto-mirror/` (or your custom domain).

After that, the workflow runs every Wednesday at 14:40 UTC. Run it manually any time from the Actions tab—for example right after publishing a post, or with `force_full_regen=true` to refetch every article.

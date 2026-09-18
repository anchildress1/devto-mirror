# CI/CD Guide

How the GitHub Actions workflows build, deploy, and check devto-mirror.

## 🗺️ Workflow Overview

| Workflow | Runs on | Does |
| --- | --- | --- |
| `publish.yaml` | push to `main` touching the workflow or the composite action; manual | Upstream deploy to Firebase Hosting |
| `deploy-gh-pages.yml` | weekly (Wed 14:40 UTC, skipped upstream); manual; `workflow_call` | Fork deploy to GitHub Pages |
| `security-ci.yml` | non-draft PRs; manual | `make ai-checks` |
| `codeql.yml` | non-draft PRs to `main`; weekly (Mon 02:23 UTC); manual | CodeQL analysis for Python |
| `release-please.yml` | push to `main`; manual | Opens release PRs and syncs `uv.lock` to the release version |
| `rai-attribution.yml` | push to `main` | Scores AI-attribution commit footers and opens a PR updating the README badge |

Every job sets its own permissions and a timeout, and every workflow has a concurrency group.

## 🏗️ Shared Site Generation

Both deploy workflows call the composite action `.github/actions/generate-site`, so they produce identical output. It:

1. Restores `posts_data.json` from the state branch. A missing branch or missing file means an empty store, and every article gets fetched.
2. Installs uv (pinned to 0.12.13) and runs `uv sync --locked --no-build`.
3. Runs `python -m devto_mirror.site_generation.generator`, which renders the site into `_deploy/`.
4. Copies static files into `_deploy/`: `.nojekyll`, the Google and Algolia verification pages, and `assets/devto-mirror.jpg`. When the state branch is `gh-pages`, it copies `posts_data.json` too, so the store ships with the site.

Inputs: `devto_username`, `gh_username`, `site_domain`, `devto_key`, `force_full_regen`, `state_branch` (default `gh-pages`), `firebase_web_config`. The action has no outputs; the deploy steps read `_deploy/` and `posts_data.json` from the workspace.

If the Dev.to API still fails after retries, lists zero articles, or a sync would drop more than half the stored articles, the generator exits non-zero. The job stops before any deploy step, so neither the site nor the store changes.

## 🔥 Upstream Deploy: `publish.yaml`

Runs only when the repository owner is `anchildress1`; forks skip it. The weekly schedule is commented out, so upstream deploys on a push that changes the workflow or composite action, or on a manual run with an optional `force_full_regen`.

1. Generates the site with `state_branch: mirror-state`. `site_domain` is `SITE_DOMAIN`, or `<FIREBASE_PROJECT_ID>.web.app` when that's unset.
2. Authenticates to Google Cloud through Workload Identity Federation—no service-account key lives in the repo.
3. Deploys `_deploy/` with `npx --ignore-scripts firebase-tools deploy --only hosting`.
4. Pushes `posts_data.json` to the `mirror-state` branch (`keep_files: false`). That branch holds the store and nothing else.

Repository variables:

- `GCP_WORKLOAD_IDENTITY_PROVIDER` — full WIF provider resource name
- `GCP_DEPLOY_SERVICE_ACCOUNT` — deploy service account email (needs `roles/firebasehosting.admin`)
- `FIREBASE_PROJECT_ID` — optional, defaults to `anchildress1`
- `FIREBASE_WEB_CONFIG` — optional; turns on Firebase Analytics (an invalid value fails the build)

## 📄 Fork Deploy: `deploy-gh-pages.yml`

Runs weekly on forks (the scheduled run is skipped upstream), manually, or as a reusable workflow.

1. Generates the site with `state_branch: gh-pages`.
2. Publishes `_deploy/` to `gh-pages` with `peaceiris/actions-gh-pages`, replacing the branch contents every time (`keep_files: false`). Deleted or renamed posts stop being served.
3. Writes `CNAME` from `SITE_DOMAIN`, so for Pages `SITE_DOMAIN` must be a bare domain.

A fork that inherited upstream's `gh-pages` branch doesn't need cleanup. The first run restores upstream's store, but none of those articles appear in the fork owner's Dev.to listing, so they're dropped and the branch is replaced.

> [!NOTE]
> Root GitHub Pages deployment (username.github.io) is not currently available. If you need crawler access at the root domain, you can manually copy `robots.txt` and `llms.txt` to your root repository.

## 💾 The Article Store

`posts_data.json` is the only state: the full Dev.to article payloads, minus `body_markdown`. Upstream keeps it on `mirror-state`; forks keep it on `gh-pages`. Upstream, a `pages` ruleset blocks deleting either branch.

Both deploy workflows set `cancel-in-progress: false`. A cancelled run could leave the published site and the stored state out of step, so a queued run waits instead.

## 🛡️ Quality Gate: `security-ci.yml`

Installs dependencies with `uv sync --locked --no-build --group dev`, runs `make ai-checks` (format, lint, security, complexity, tests), then runs `git diff --exit-code`. Because `make ai-checks` formats in place, that last step is what fails a PR with unformatted code.

The ruleset on `main` requires the `security-quality`, `CodeQL`, and `semgrep-cloud-platform/scan` checks to pass before merging.

## 🔐 Permissions and Secrets

| Job | Permissions |
| --- | --- |
| `publish.yaml` | `contents: write` (push to `mirror-state`), `id-token: write` (WIF) |
| `deploy-gh-pages.yml` | `contents: write` (push to `gh-pages`) |
| `security-ci.yml` | `contents: read` |
| `codeql.yml` | `security-events: write`, `contents: read`, `actions: read`, `packages: read` |
| `release-please.yml` | `contents: write`, `pull-requests: write` |
| `rai-attribution.yml` | `contents: write`, `pull-requests: write` |

Besides the automatic `GITHUB_TOKEN`, the only secrets are an optional `DEVTO_KEY` (raises Dev.to rate limits) and the release-please token (`MY_RELEASE_PLEASE_TOKEN`). The Firebase web config is public by design and lives in a plain variable.

## 🧯 Common CI Issues

### `Failed to spawn: black` (or flake8, bandit)

```text
error: Failed to spawn: `black`
  Caused by: No such file or directory (os error 2)
```

The workflow wrapped a Makefile target in `uv run`. The Makefile already calls every tool through `uv run`, and nesting breaks tool lookup. Sync first, then call `make` directly:

```yaml
- name: Install dependencies
  run: uv sync --locked --no-build --group dev

- name: Run validation
  run: make ai-checks   # never `uv run make ai-checks`
```

### `security-quality` fails on `git diff --exit-code`

`make ai-checks` reformatted a file you committed. Run `make format` locally, commit the result, and push again.

For local setup and the development workflow, see [DEV_GUIDE.md](./DEV_GUIDE.md).

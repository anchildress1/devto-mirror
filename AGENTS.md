- Single entry point: `uv run python -m devto_mirror.site_generation.generator`. Do not add other runnable modules or scripts.
- Change page output in `src/devto_mirror/templates/`. Never hand-edit `_deploy/` or `posts_data.json` (generated, gitignored).

## Repo map

| Path | Holds |
| --- | --- |
| `src/devto_mirror/core/api_client.py` | Dev.to listing + `sync_articles` (retry/backoff) |
| `src/devto_mirror/core/html_sanitization.py` | bleach allowlist for post bodies |
| `src/devto_mirror/core/path_utils.py` | filename/slug sanitizing |
| `src/devto_mirror/core/url_utils.py` | `resolve_home` (site root URL) |
| `src/devto_mirror/core/utils.py` | Jinja `env` + `firebase_analytics` template global |
| `src/devto_mirror/site_generation/generator.py` | `main`, `build_site`, `comments.txt` parsing |
| `src/devto_mirror/site_generation/post.py` | `Post` model built from a full-article payload |
| `src/devto_mirror/site_generation/seo.py` | `BlogPosting` JSON-LD, tag-overlap related posts |
| `src/devto_mirror/templates/` | `base.html` (shared head), `post.html`, `index.html`, `comment.html`, `sitemap.xml`, `robots.txt`, `llms.txt` |
| `scripts/` | `check_detect_secrets.py`, `run_pip_audit.py` only; both run via `make security` |
| `tests/` | `unittest`; build API payloads with `tests/factories.py` |
| `.github/actions/generate-site/` | composite action shared by both deploy workflows |
| `docs/` | human docs; rules in `docs/AGENTS.md` |

## Invariants

- `posts_data.json` is the only state. Do not add timestamp, cursor, or run-state files.
- An API failure after retries must raise. Never write the store or render from a partial fetch.
- A sync that drops more than half the stored articles raises; `FORCE_FULL_REGEN` (ignores the store) is the only override.
- Every page's canonical URL points at Dev.to.

## Commands

- `make install` — deps + Lefthook hooks.
- `make ai-checks` — format → lint → security → complexity → test. Run before every commit.
- `make test` — coverage gate is 85%; do not lower it.
- No Makefile target for the task → `uv run <tool>`.
- Run `uv lock` only when dependencies change, then `make ai-checks`.

## CI

- In GitHub Actions, run `make <target>`. Never `uv run make <target>`.
- `security-ci.yml` fails when `make ai-checks` rewrites tracked files; run `make format` before pushing.

## Environment

| Var | Rule |
| --- | --- |
| `DEVTO_USERNAME` | required |
| `SITE_DOMAIN` / `GH_USERNAME` | one required; `SITE_DOMAIN` wins |
| `DEVTO_KEY` | optional; raises rate limits only |
| `FORCE_FULL_REGEN` | `true`/`1`/`yes` ignores the store and refetches every article |
| `FIREBASE_WEB_CONFIG` | optional; unset = no Analytics; set = must be a JSON object with `measurementId` or the build fails |

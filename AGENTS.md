# devto-mirror AGENTS (AI-only)

## Repo map (authoritative)

- `src/`: application package only
  - `src/devto_mirror/ai_optimization/`: optional AI modules
- `scripts/`: runnable entrypoints + helpers (legacy, move code out opportunistically)
- `tests/`: `unittest`
- `assets/`: templates/static inputs (edit these, not generated root artifacts)
- `docs/`: documentation (doc-specific rules live in `docs/AGENTS.md`)

## Canonical commands

- Prefer Makefile targets when available:
  - `make install`
  - `make ai-checks`
  - `make test`
  - `make security`

- If there is no Makefile target for a task, use `uv run <tool>`.

## Lefthook

- Lefthook is configured in `lefthook.yml` and may be invoked indirectly by Makefile targets.
- Use `make lint` / `make ai-checks`.

## Dependency workflows

- Install deps:
  - Prefer `make install`.
  - Otherwise use `uv sync --locked --group dev`.

- Update lockfile ONLY when dependencies changed:
  - run `uv lock`
  - then run `make ai-checks`

## CI invariant

- In GitHub Actions, NEVER run `uv run make <target>`.
- Always run `make <target>`.

## Project-required environment

- Required: `DEVTO_USERNAME`
- Site URL (one required): `SITE_DOMAIN` or `GH_USERNAME`
- Optional: `DEVTO_KEY`, `VALIDATION_MODE`, `FORCE_FULL_REGEN`, `ROOT_SITE_PAT`

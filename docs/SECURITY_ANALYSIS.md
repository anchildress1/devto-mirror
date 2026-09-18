# Security Analysis

What scans this repository, when they run, and how to run the same checks locally.

## 🔍 CodeQL

- **File**: `.github/workflows/codeql.yml`
- **Runs**: non-draft PRs to `main`, weekly (Mondays 02:23 UTC), and manually
- **Coverage**: Python, with the `security-extended` and `security-and-quality` query suites
- **Gate**: the `main` ruleset requires the CodeQL check and blocks merging on any code-scanning alert

## 📦 Dependabot

- **File**: `.github/dependabot.yml`
- **Runs**: weekly (Mondays 04:00 UTC), at most one open PR per ecosystem
- **Coverage**: Python dependencies (the `uv` ecosystem, from `pyproject.toml` and `uv.lock`) and GitHub Actions versions
- **Assignment**: PRs are assigned to the repository owner

## 🧰 Local and CI Checks

`make security` runs three tools, and `make ai-checks` includes it. CI runs `make ai-checks` on every non-draft PR through `.github/workflows/security-ci.yml`.

- **bandit** scans `src/` and `scripts/`, reporting medium-or-higher severity issues at high confidence
- **pip-audit** checks installed packages for known vulnerabilities. It always runs in CI; locally it's skipped unless you set `PIP_AUDIT=1`. In CI a failure or timeout fails the build; locally it only warns
- **detect-secrets** scans every git-tracked file and fails on any secret not already recorded in `.secrets.baseline`

flake8 runs separately under `make lint`.

To run them locally:

```bash
make install
make security              # bandit + detect-secrets (+ pip-audit with PIP_AUDIT=1)
make ai-checks             # everything CI runs
```

These checks are lightweight—they won't find everything, but they catch the common mistakes that lead to security flags.

## 🛡️ Built-in Safeguards

- **Untrusted HTML**: post bodies from Dev.to pass through a bleach allowlist; `<script>` and `<style>` blocks are removed outright
- **Templates**: Jinja autoescaping is on for every HTML and XML template
- **Deploy credentials**: the Firebase deploy authenticates through Workload Identity Federation, so no service-account key is stored in the repo
- **Supply chain**: third-party actions are pinned to commit SHAs, and `firebase-tools` runs with `--ignore-scripts`

## ⚙️ Recommended Repository Settings

To get the most from GitHub's security features, enable these under Settings → Security & analysis:

1. Dependabot security updates
2. Dependabot alerts
3. Secret scanning
4. Private vulnerability reporting

## 👀 Viewing Results

- **CodeQL**: Security → Code scanning alerts
- **Dependencies**: Security → Dependabot alerts

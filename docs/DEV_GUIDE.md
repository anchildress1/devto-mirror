# Development Guide

This guide covers setting up the Dev.to Mirror project for local development. The project generates a static mirror of your Dev.to blog posts with AI-enhanced metadata and cross-references.

## Local Development Setup

### Prerequisites

- Python 3.12+ (the project uses modern Python features)
- Git
- A Dev.to account with published posts

### Quick Start

1. **Clone and setup**:

   ```bash
   git clone https://github.com/anchildress1/devto-mirror.git
   cd devto-mirror
   make install   # Installs dev dependencies and lefthook hooks
   ```

2. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your actual values - see Environment Variables section below
   ```

3. **Install lefthook hooks** (recommended):

   ```bash
   make install   # Installs dev deps and lefthook hooks
   ```

4. **Run validation to ensure everything works**:

   ```bash
   make ai-checks  # Comprehensive check: format, lint, test, security, site generation
   ```

5. **Generate your site locally**:

   ```bash
   uv run python scripts/generate_site.py   # Creates HTML files in posts/ directory
   ```

## Environment Variables

The project uses a `.env` file for local development configuration. This keeps sensitive data out of version control and makes local testing easier.

**Required variables:**

- `DEVTO_USERNAME`: Your Dev.to username (e.g., "anchildress1")

**Site URL configuration (one required):**

- `SITE_DOMAIN`: Custom domain (e.g., "crawly.checkmarkdevtools.dev")
- `GH_USERNAME`: GitHub username (e.g., "anchildress1") - used if `SITE_DOMAIN` not set

**Optional variables:**

- `FORCE_FULL_REGEN`: Set to "true" to regenerate all posts instead of incremental updates
- `VALIDATION_MODE`: Set to "true" to use mock data instead of API calls (for testing)

**Example .env file (with custom domain):**

```bash
DEVTO_USERNAME=your-username
SITE_DOMAIN=crawly.checkmarkdevtools.dev
FORCE_FULL_REGEN=false
VALIDATION_MODE=false
```

**Example .env file (with GitHub Pages):**

```bash
DEVTO_USERNAME=your-username
GH_USERNAME=your-github-username
FORCE_FULL_REGEN=false
VALIDATION_MODE=false
```

## Development Workflow

The project includes a comprehensive development workflow with automated quality checks:

**Daily development commands:**

```bash
make format         # Auto-format code with Black (120 char line length)
make lint           # Run all lefthook checks (linting, security, secrets)
make test           # Run unit tests for AI optimization modules
make ai-checks       # Run everything: format + lint + test + security + site validation
```

**Understanding the validation pipeline:**

- **Format**: Uses Black to ensure consistent code style
- **Lint**: Runs lefthook checks (formatting, linting, security)
- **Test**: Unit tests for content analysis and cross-reference features
- **Site validation**: Dry-run of site generation to catch build errors early
- **Security**: Scans for vulnerabilities and security issues

## Git Hooks

Lefthook hooks run automatically when you commit, catching issues before they reach CI:

```bash
lefthook install                    # One-time setup
lefthook run pre-commit            # Manual run on all files
git commit -m "your message"       # Hooks run automatically
```

**What the hooks check:**

- Code formatting (Black)
- Linting and style checks
- Security issues (bandit)
- Secret detection
- Site generation validation

If any hook fails, the commit is blocked until you fix the issues.

## Project Structure

```plaintext
devto-mirror/
├── scripts/                 # Main site generation and utility scripts
│   ├── generate_site.py    # Core site generation logic
│   ├── validate_site_generation.py  # Lefthook validation
│   └── utils.py            # Shared script utilities
├── src/                    # Python package (AI optimization modules)
│   └── ai_optimization/    # Content analysis and cross-references
├── tests/                  # Unit tests
├── docs/                   # Documentation
└── .env.example           # Environment variable template
```

## Testing

The project includes multiple levels of testing:

**Unit tests** (for AI optimization features):

```bash
make test                   # Run all unit tests with coverage
```

**Site generation validation** (catches build errors):

```bash
uv run python scripts/validate_site_generation.py # Test site generation with mock data
```

**Integration testing** (full pipeline):

```bash
make ai-checks              # Complete validation pipeline
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| **ModuleNotFoundError: No module named 'src'** | Ensure you're in the correct virtual environment and the package is installed (`make install` will run the recommended install steps). |
| **Missing DEVTO_USERNAME** | Check your `.env` file exists and has the correct variable names |
| **Lefthook hooks failing** | Run `make format` then `make lint` to see specific issues |
| **Site generation fails locally** | Check that your Dev.to username is correct and you have published posts |
| **Import errors** | Make sure you ran `make install` (or the equivalent `uv` commands) and activated your virtual environment |

## GitHub Actions Setup

### Repository Configuration

After forking the repository, configure it for automatic deployment:

1. **Set repository variables**:
   - Navigate to Settings → Actions → Variables → Repository variables
   - Add `DEVTO_USERNAME` with your Dev.to username
   - This tells the workflows which Dev.to profile to mirror

2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Under "Source", select "Deploy from a branch"
   - Choose `gh-pages` branch (created automatically by first workflow run)
   - Your site will be available at `https://yourusername.github.io/devto-mirror`

3. **Run initial workflow**:
   - Go to Actions → "Generate and Publish Dev.to Mirror Site" → Run workflow
   - This creates the `gh-pages` branch and deploys your first site

### Manual Workflow Triggers

Trigger workflows manually for testing or immediate updates:

1. Go to repository's **Actions** tab
2. Select the workflow you want to run
3. Click **"Run workflow"** button
4. Choose branch (usually `main`) and any options
5. Click **"Run workflow"** to start

**When to use manual triggers**:

- Testing changes before they go live
- Immediate updates after publishing new posts
- Troubleshooting workflow issues
- Full site regeneration (via `publish.yaml` with `force_full_regen=true`)

For detailed explanations of the CI/CD workflows and their technical implementation, see [`CI_GUIDE.md`](CI_GUIDE.md).

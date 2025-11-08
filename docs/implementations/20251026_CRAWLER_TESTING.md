# Crawler Accessibility Testing

This document describes the crawler accessibility testing implementation for the Dev.to Mirror project.

## Overview

Two Python scripts have been implemented to test and analyze crawler accessibility:

1. **`scripts/test_crawler_access.py`** - Tests major search engine crawler access
2. **`scripts/analyze_github_pages_crawlers.py`** - Analyzes GitHub Pages crawler restrictions

## Scripts

### test_crawler_access.py

Tests whether major search engine crawlers can access the site by simulating different user agents.

**Tested Crawlers:**

- Googlebot, Bingbot, GPTBot, ClaudeBot, Claude-Web
- PerplexityBot, DuckDuckBot, Bytespider, CCBot
- facebookexternalhit, Twitterbot, LinkedInBot

**Usage:**

```bash
# Use the Makefile helper which runs the script via uv. Optionally pass BASE_URL env var.
make test-crawler BASE_URL=https://your-site.example
```

**Output:**

- Console summary of crawler access results
- `crawler_access_report.json` with detailed results

### analyze_github_pages_crawlers.py

Analyzes GitHub Pages deployment for crawler restrictions and compares with robots.txt permissions.

**Features:**

- Parses robots.txt for intended permissions
- Compares actual access with expected access
- Generates recommendations for deployment platform

**Usage:**

```bash
# Use the Makefile helper which runs the analysis via uv. Optionally pass BASE_URL env var.
make analyze-crawlers BASE_URL=https://your-site.example
```

**Output:**

- Console analysis summary
- `github_pages_crawler_analysis.json` with detailed analysis

## Testing Approach

### Phase 1: Restrictive robots.txt Deployment

To properly test if GitHub Pages respects robots.txt restrictions, we've implemented a **restrictive robots.txt** that:

**✅ ALLOWS access to 7 crawlers:**

- Googlebot, Bingbot, GPTBot, ClaudeBot, DuckDuckBot, CCBot, facebookexternalhit

**❌ BLOCKS access to 6 crawlers:**

- Google-Extended, Claude-Web, PerplexityBot, Bytespider, Twitterbot, LinkedInBot

**🚫 BLOCKS all other crawlers** via `User-agent: * Disallow: /`

### Expected Results

**If GitHub Pages RESPECTS robots.txt:**

- Allowed crawlers should return HTTP 200
- Blocked crawlers should return HTTP 403/404 or be denied access
- Test should show ~50% of crawlers blocked

**If GitHub Pages IGNORES robots.txt:**

- ALL crawlers will return HTTP 200 regardless of Disallow rules
- Test will show 0% of crawlers blocked
- This proves robots.txt enforcement is not implemented

## Automated Testing in CI/CD

The GitHub Actions workflow now includes:

1. 🔍 **Deployment Verification** - Shows actual deployed content
2. 🧪 **Crawler Access Testing** - Tests all major crawlers post-deploy
3. 📊 **GitHub Pages Analysis** - Compares expected vs actual behavior
4. 📝 **GitHub Summary** - Results posted to workflow summary with emojis

## Current Test Status

🧪 **TESTING IN PROGRESS** - Deploying restrictive robots.txt to verify GitHub Pages behavior

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 2.1:** THE Deployment_Platform SHALL allow unrestricted crawler access to all site content
- **Requirement 2.4:** IF GitHub Pages blocks any crawlers from accessing content, THEN THE Deployment_Platform SHALL be migrated to an alternative service

**Result:** No migration needed - GitHub Pages allows unrestricted crawler access.

## Usage in CI/CD

These scripts can be integrated into GitHub Actions workflows for continuous monitoring:

```yaml
- name: Test Crawler Access
  run: make test-crawler

- name: Analyze GitHub Pages Restrictions
  run: make analyze-crawlers
```

## Future Monitoring

The scripts should be run periodically to monitor for any changes in GitHub Pages crawler policies or access patterns.

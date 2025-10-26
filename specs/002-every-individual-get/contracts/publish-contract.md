# Contract: Publish Workflow

**Workflow File**: `.github/workflows/publish.yaml`  
**Purpose**: Generate static site from Dev.to posts and deploy to gh-pages branch  
**Priority**: P2 (essential but lower than security workflows)

## Triggers

```yaml
on:
  schedule:
    - cron: "38 13 * * 3"  # Wednesday 09:38 AM EDT (13:38 UTC)
  workflow_dispatch: {}
  push:
    branches: [main]
```

**Schedule Change**: Daily → Weekly (86% cost reduction)
- Old: `"15 14 * * *"` (daily 9:15 AM EST)
- New: `"38 13 * * 3"` (weekly Wednesday 9:38 AM EDT year-round)

## Jobs

### build

**Runs-on**: `ubuntu-latest`  
**Timeout**: 15 minutes

**Steps**:
1. Checkout repository (fetch-depth: 0)
2. Setup Python 3.11 (actions/setup-python@v6.0.0)
3. Install uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
4. Install dependencies (`uv pip install -e .`)
5. Generate site (scripts/generate_site.py)
6. Deploy to gh-pages branch

## Permissions

```yaml
permissions:
  contents: write  # Required for gh-pages branch updates
```

**Rationale**: Minimal permissions for deployment. No pull-request or security-events access needed.

## Success Criteria

1. **Dependencies Installed**: uv successfully installs all packages from pyproject.toml
2. **Site Generated**: scripts/generate_site.py completes without errors
3. **Content Created**: index.html, sitemap.xml, robots.txt, posts/*.html generated
4. **gh-pages Updated**: New commit pushed to gh-pages branch
5. **Site Accessible**: GitHub Pages serves updated content within 5 minutes
6. **Duration**: Workflow completes in <15 minutes

## Failure Behavior

**On Failure**:
- Workflow status: ❌ Failed
- Repository state: Unchanged (atomic git operations)
- Notification: GitHub Actions email/notification to maintainer
- gh-pages branch: Previous version remains deployed
- Manual intervention: Review logs, fix issue, re-run via workflow_dispatch

**Common Failure Modes**:
- **uv installation fails**: Check network connectivity, uv installer availability
- **Dependency conflicts**: Review pyproject.toml, check uv resolver logs
- **Script errors**: Check DEVTO_USERNAME variable, API rate limits, Python errors
- **gh-pages push fails**: Check permissions, branch protection rules

## Validation Checklist

After implementation:
- [ ] Schedule updated to `"38 13 * * 3"`
- [ ] workflow_dispatch trigger added
- [ ] Python 3.11 configured
- [ ] uv installation step present
- [ ] Dependencies installed via `uv pip install -e .`
- [ ] Permissions set to `contents: write` only
- [ ] Timeout set to 15 minutes
- [ ] Manual test run successful
- [ ] Site deploys correctly
- [ ] Cron schedule verified with crontab.guru

## Testing Procedure

1. Navigate to Actions → "Dev.to Mirror (Static, Hourly)"
2. Click "Run workflow"
3. Select branch: main
4. Click "Run workflow" button
5. Monitor execution (~5-10 minutes expected)
6. Verify success criteria:
   - ✅ uv installed
   - ✅ Dependencies resolved
   - ✅ Site generated
   - ✅ gh-pages updated
   - ✅ Site accessible at GitHub Pages URL

## Schedule Verification

```bash
# Verify cron expression
echo "38 13 * * 3" | crontab.guru

# Expected output:
# At 13:38 on Wednesday

# Timezone calculation:
# 13:38 UTC = 09:38 EDT (UTC-4)
# 13:38 UTC = 08:38 EST (UTC-5) [winter months]
```

**Acceptance**: User posts by 09:30 AM Wednesday EDT. Workflow at 09:38 AM EDT captures fresh content.

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Duration | <15 min | ~5-10 min typical |
| Frequency | Weekly Wed | Daily (before change) |
| Cost per month | ~60 minutes | ~450 minutes (before) |
| Failure rate | <5% | TBD (monitor 30 days) |

## Dependencies

- Python 3.11+
- uv package manager
- Repository variables: DEVTO_USERNAME, PAGES_REPO (derived from github.repository)
- Dev.to public API (no auth required)
- GitHub Pages enabled on repository

## Related Workflows

- **refresh.yaml**: Can trigger this workflow via `workflow_call` after resetting timestamp
- **security-ci.yml**: Validates code quality before merge (prevents broken publishes)
- **codeql.yml**: Monitors for security issues in generation scripts

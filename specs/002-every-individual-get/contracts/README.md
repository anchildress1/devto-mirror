# Workflow Contracts

This directory contains behavioral contracts for all four GitHub Actions workflows. Each contract defines triggers, permissions, timeouts, success criteria, and failure behaviors.

## Contract Files

1. **security-ci-contract.md** - Security scanning and linting workflow
2. **codeql-contract.md** - CodeQL semantic analysis workflow
3. **publish-contract.md** - Site generation and deployment workflow (with schedule update)
4. **refresh-contract.md** - Full content regeneration workflow with backup

## Testing Strategy

All workflows support manual testing via `workflow_dispatch` trigger:

1. Navigate to Actions tab in GitHub repository
2. Select desired workflow from left sidebar
3. Click "Run workflow" button
4. Select branch (default: main)
5. Click "Run workflow" to trigger
6. Monitor execution and verify contract compliance

## Contract Structure

Each contract includes:
- **Triggers**: Events that start the workflow
- **Jobs**: Execution steps and dependencies
- **Permissions**: GITHUB_TOKEN scope requirements
- **Timeout**: Maximum execution time
- **Success Criteria**: Expected outcomes for passing run
- **Failure Behavior**: Actions taken on workflow failure

## Validation Checklist

After workflow updates:
- [ ] workflow_dispatch trigger added
- [ ] Explicit permissions declared
- [ ] Timeout within specified limits
- [ ] Manual test run successful
- [ ] Contract success criteria met
- [ ] Failure behavior documented

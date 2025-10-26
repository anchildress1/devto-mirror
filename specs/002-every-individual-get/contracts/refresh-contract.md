# Contract: Refresh Workflow

**File**: 
**Triggers**: workflow_dispatch only (manual)
**Permissions**: contents:write, actions:write
**Timeout**: 20 minutes
**Jobs**: refresh (backup gh-pages, reset last_run.txt, trigger publish)
**Success**: Backup created, timestamp reset, publish triggered, content regenerated
**Failure**: Report error, backup preserved, manual intervention required

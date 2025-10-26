# Contract: Security-CI Workflow

**File**: `.github/workflows/security-ci.yml`  
**Triggers**: push (main), pull_request (main), workflow_dispatch  
**Permissions**: contents:read, pull-requests:write  
**Timeout**: 10 minutes  
**Jobs**: security-lint (pip-audit, bandit, flake8)  
**Success**: All scans complete, findings reported, high/critical block merge  
**Failure**: Block PR merge on high/critical vulnerabilities

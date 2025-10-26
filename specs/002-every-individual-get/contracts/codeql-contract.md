# Contract: CodeQL Workflow

**File**: 
**Triggers**: push (main), pull_request (main), schedule (Mon 2:15 AM UTC), workflow_dispatch
**Permissions**: security-events:write, contents:read, actions:read, packages:read
**Timeout**: 15 minutes
**Jobs**: analyze (CodeQL Python semantic analysis)
**Success**: Analysis completes, results uploaded to Security tab
**Failure**: Report findings (informational, no merge block)

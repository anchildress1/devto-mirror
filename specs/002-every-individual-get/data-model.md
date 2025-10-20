# Data Model: GitHub Actions Workflows

**Feature**: Individual Verification and Update of All GitHub Actions Workflows  
**Date**: 2025-10-18

## Entity Definitions

### 1. Workflow File

**Description**: YAML configuration file defining a GitHub Actions workflow

**Attributes**:
- `name` (string): Human-readable workflow name
- `trigger_events` (array): List of events that trigger workflow (push, pull_request, schedule, workflow_dispatch)
- `jobs` (map): Job definitions with steps
- `permissions` (map): GITHUB_TOKEN permission declarations
- `timeout_minutes` (integer): Maximum execution time
- `schedule_expression` (string, optional): Cron syntax for scheduled runs
- `concurrency_group` (string, optional): Concurrency control group identifier

**Relationships**:
- Contains 1+ Jobs
- Declares Permissions
- May have Schedule Expression

**State Transitions**:
```
[Defined] → [Committed] → [Triggered] → [Queued] → [Running] → [Completed]
```

**Validation Rules**:
- MUST include workflow_dispatch trigger (FR-019)
- MUST declare explicit minimal GITHUB_TOKEN permissions (FR-014)
- MUST complete within timeout limits (FR-010)
- Security-ci: contents:read, pull-requests:write
- CodeQL: security-events:write, contents:read, actions:read, packages:read
- Publish: contents:write
- Refresh: contents:write, actions:write

---

### 2. Security Finding

**Description**: A vulnerability, code smell, or quality issue identified by security tools

**Attributes**:
- `severity` (enum): critical | high | medium | low
- `tool` (enum): pip-audit | bandit | flake8 | codeql
- `location` (string): File path and line number
- `description` (string): Finding details
- `auto_fixable` (boolean): Whether automated fix is possible
- `cve_id` (string, optional): CVE identifier if applicable

**Relationships**:
- Belongs to Workflow Run
- May trigger Fix PR creation

**Lifecycle**:
```
[Detected] → [Reported] → [Fixed | Ignored | Deferred]
```

**Validation Rules**:
- High/critical severity MUST block PR merge (FR-003a)
- Auto-fixable findings MAY trigger automated fix PR (FR-003b)
- All findings MUST be categorized by severity (FR-009)

---

### 3. Workflow Run

**Description**: An execution instance of a workflow

**Attributes**:
- `run_id` (integer): Unique GitHub Actions run ID
- `status` (enum): queued | in_progress | completed
- `conclusion` (enum): success | failure | cancelled | skipped
- `duration_seconds` (integer): Execution time
- `triggered_by` (enum): push | pull_request | schedule | workflow_dispatch | workflow_call
- `branch` (string): Git branch name
- `commit_sha` (string): Git commit hash
- `logs_url` (string): GitHub Actions logs URL
- `started_at` (timestamp): ISO8601 UTC timestamp
- `completed_at` (timestamp, optional): ISO8601 UTC timestamp

**Relationships**:
- Belongs to Workflow File
- Contains 0+ Security Findings
- May create Backup Branch (refresh workflow only)

**State Machine**:
```
[Queued] → [In Progress] → [Completed]
                              ├─ Success
                              ├─ Failure
                              └─ Cancelled
```

**Validation Rules**:
- MUST complete within workflow-specific timeout (FR-010)
- Cancelled runs acceptable (FR-018 concurrency controls)
- Failure rate MUST be <5% over 30 days (SC-008)

---

### 4. Backup Branch

**Description**: Git branch preserving gh-pages state before refresh

**Attributes**:
- `branch_name` (string): backup-YYYYMMDD-HHMMSS format
- `timestamp` (timestamp): Creation time ISO8601 UTC
- `source_commit` (string): Original gh-pages commit SHA
- `gh_pages_state` (json): Snapshot metadata

**Relationships**:
- Created by Refresh Workflow Run
- References source gh-pages branch

**Lifecycle**:
```
[Created] → [Preserved] (no automated deletion)
```

**Validation Rules**:
- Naming pattern MUST match `backup-YYYYMMDD-HHMMSS` (FR-007)
- MUST be created BEFORE resetting last_run.txt (FR-007)
- No automated deletion (manual cleanup only)

---

### 5. Schedule Expression

**Description**: Cron syntax defining automated workflow triggers

**Attributes**:
- `cron_syntax` (string): Standard cron format (minute hour day month weekday)
- `description` (string): Human-readable schedule description
- `timezone_note` (string): Timezone clarification (GitHub Actions uses UTC)
- `frequency` (enum): daily | weekly | monthly

**Relationships**:
- Belongs to Workflow File
- Triggers Workflow Runs on schedule

**Validation Rules**:
- MUST be valid cron syntax
- Publish workflow MUST use "38 13 * * 3" (Wednesday 09:38 AM EDT) (FR-006a, SC-006a)
- CodeQL workflow MUST use "15 2 * * 1" (Monday 02:15 AM UTC) (existing, no change)
- All times in UTC (GitHub Actions requirement)

---

## Entity Relationship Diagram

```
┌─────────────────┐
│ Workflow File   │
│ ─────────────── │
│ name            │
│ triggers        │◄──────┐
│ jobs            │       │
│ permissions     │       │ belongs to
│ timeout         │       │
└────────┬────────┘       │
         │                │
         │ contains       │
         ▼                │
┌─────────────────┐       │
│ Workflow Run    │       │
│ ─────────────── │       │
│ run_id          │───────┘
│ status          │
│ conclusion      │
│ duration        │
│ triggered_by    │
└────────┬────────┘
         │
         │ contains
         ▼
┌─────────────────┐
│Security Finding │
│ ─────────────── │
│ severity        │
│ tool            │
│ location        │
│ auto_fixable    │
└─────────────────┘

┌─────────────────┐
│ Schedule Expr   │
│ ─────────────── │ belongs to
│ cron_syntax     ├───────────► Workflow File
│ frequency       │
└─────────────────┘

┌─────────────────┐
│ Backup Branch   │
│ ─────────────── │ created by
│ branch_name     ├───────────► Workflow Run
│ timestamp       │             (refresh only)
└─────────────────┘
```

---

## State Machine Details

### Workflow Run State Machine

```
          ┌─────────┐
          │ Queued  │
          └────┬────┘
               │ workflow triggered
               ▼
        ┌─────────────┐
        │ In Progress │
        └──────┬──────┘
               │
       ┌───────┼────────┐
       │       │        │
       ▼       ▼        ▼
  ┌─────┐ ┌────────┐ ┌──────────┐
  │Success│ │Failure│ │Cancelled │
  └─────┘ └────────┘ └──────────┘
```

### Security Finding Lifecycle

```
┌──────────┐
│ Detected │
└────┬─────┘
     │ tool scan completes
     ▼
┌──────────┐
│ Reported │
└────┬─────┘
     │
 ┌───┴───┬─────────┐
 │       │         │
 ▼       ▼         ▼
┌────┐ ┌────────┐ ┌─────────┐
│Fixed│ │Ignored│ │Deferred │
└────┘ └────────┘ └─────────┘
```

---

## Validation Summary

| Entity | Critical Validations |
|--------|---------------------|
| Workflow File | workflow_dispatch trigger, explicit permissions, timeout limits |
| Security Finding | Severity categorization, merge blocking rules, auto-fix triggers |
| Workflow Run | Timeout enforcement, failure rate tracking, concurrency cancellation |
| Backup Branch | Naming pattern, creation ordering, no auto-deletion |
| Schedule Expression | Valid cron syntax, publish="38 13 * * 3", UTC timezone |

**All entities support the 4 workflow verification user stories (US1-US4).**

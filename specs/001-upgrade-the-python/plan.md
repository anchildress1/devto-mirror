# Implementation Plan: Upgrade Python Implementation to Astral uv

**Branch**: `001-upgrade-the-python` | **Date**: October 12, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-upgrade-the-python/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Upgrade the Python project to use Astral uv for dependency management, replace requirements.txt with pyproject.toml, add basic test infrastructure, and update documentation. Maintain all existing functionality while modernizing the tooling.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: requests, jinja2, python-slugify, bleach
**Storage**: Local files (JSON data files, HTML output)
**Testing**: unittest (built-in Python testing framework)
**Target Platform**: Linux/Mac/Windows (development), GitHub Actions runners (CI/CD)
**Project Type**: Single project (utility scripts)
**Performance Goals**: Fast enough for daily automated runs (< 5 minutes)
**Constraints**: Maintain existing functionality, no breaking changes
**Scale/Scope**: Small personal utility project

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Keep Things Modern and Very Simple**: Using Astral uv aligns with modern Python tooling
- ✅ **Conventional Commits**: Will follow conventional commit standards
- ✅ **This is NOT a UI**: Project generates static HTML mirror, no UI components
- ✅ **This is NOT a Critical Prod System**: Personal utility with low criticality, acceptable to introduce changes

**Gate Status**: PASSED - No violations detected

## Project Structure

### Documentation (this feature)

```
specs/001-upgrade-the-python/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
scripts/
├── generate_site.py
├── clean_posts_data.py
├── fix_slugs.py
├── render_index_sitemap.py
├── reset_repository.py
├── analyze_descriptions.py
├── validate_commit_msg.py
├── utils.py
└── __pycache__/

tests/
├── __init__.py
└── test_basic.py

pyproject.toml          # New: replaces requirements.txt
README.md               # Updated: references uv commands
.github/
└── workflows/          # Updated: use uv in CI
```

**Structure Decision**: Single project structure maintained. Added tests/ directory for basic testing infrastructure. Configuration modernized with pyproject.toml.

## Complexity Tracking

*No violations to justify*

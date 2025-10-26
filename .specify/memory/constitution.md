<!--
Sync Impact Report:
Version: 1.0.0 → 1.1.0
Change Type: MINOR (added mandatory testing/documentation principle)
Ratification Date: 2025-10-18
Last Amended: 2025-10-18

Modified Principles:
- Added "Mandatory Documentation and Testing at Every Step"

Templates Requiring Updates:
✅ .specify/templates/plan-template.md (Constitution Check section verified)
✅ .specify/templates/spec-template.md (User Scenarios & Testing mandatory section verified)
✅ .specify/templates/tasks-template.md (Test tasks structure verified)
⚠ README.md - needs uv migration documentation updates
⚠ SECURITY_ANALYSIS.md - needs uv migration documentation updates
⚠ specs/002-every-individual-get/quickstart.md - needs pip→uv consistency fixes

Follow-up TODOs:
- Update all user-facing documentation to reflect uv package manager migration
- Ensure all specs reference uv, not pip/poetry
-->

# devto-mirror Constitution

**Version**: 1.1.0
**Ratified**: 2025-10-18
**Last Amended**: 2025-10-18
**Project**: devto-mirror - Static HTML mirror generator for Dev.to blog posts

## Preamble

This constitution establishes the immutable principles governing the devto-mirror project. These principles guide all development decisions, feature specifications, and implementation work. Violations require explicit justification and project maintainer approval.

## Core Principles

### Principle 1: Keep Things Modern and Very Simple

**Declaration**: This is a modern Python 3.11+ project using Astral uv package manager. KISS (Keep It Simple, Stupid) and YAGNI (You Aren't Gonna Need It) principles are paramount.

**Rules**:
- MUST use Python 3.11 or higher
- MUST use uv for dependency management (NOT pip, NOT poetry)
- MUST define dependencies in `pyproject.toml`
- MUST NOT add features until they are explicitly needed
- MUST NOT over-engineer solutions
- Inline code comments are ONLY allowed for complex or non-obvious "why" explanations
- MUST use docstrings (Pydocs) throughout to document the codebase concisely with only necessary details

**Rationale**: Simplicity reduces maintenance burden and cognitive load. Modern tooling (uv) provides faster, more reliable dependency resolution. Premature optimization and feature creep are the enemy of maintainability.

### Principle 2: Conventional Commits with RAI Attribution

**Declaration**: All commits MUST follow the Conventional Commits specification with Responsible AI (RAI) attribution footers.

**Rules**:
- Commit messages MUST follow Conventional Commits format: `type(scope): description`
- MUST include appropriate RAI footer: `Generated-by`, `Co-authored-by`, `Assisted-by`, or `Commit-generated-by`
- MUST use `/generate-commit-message` prompt for assistance
- MUST NOT sign commits on behalf of users
- AI agents executing validations MUST warn users to review before committing

**Rationale**: Conventional commits enable automated changelog generation and clear communication of intent. RAI attribution provides transparency about AI contribution levels, supporting responsible AI development practices.

### Principle 3: AI-First Content Mirror (Not a UI)

**Declaration**: This project's purpose is to provide a static HTML mirror of Dev.to blog posts and interesting comments optimized for AI consumption and search engine discoverability.

**Rules**:
- MUST include entire post content with metadata for AI processing
- MUST follow SEO standards for all major platforms
- MUST include per-page metadata explicitly permitting AI crawler usage
- MUST prioritize transparency and completeness while maintaining WCAG accessibility standards for screen readers
- MUST use canonical links pointing back to original Dev.to URLs
- Primary goal is increasing search relevance and directing traffic to canonical Dev.to source

**Rationale**: The modern web is consumed by AI systems (ChatGPT, Gemini, Claude) as much as humans. Optimizing for both AI crawlers and search engines increases content discoverability while maintaining attribution to the original source.

### Principle 4: Toy Utility, Not Production System

**Declaration**: This is a personal utility designed for experimentation, NOT a critical production system.

**Rules**:
- MUST NOT design for high availability or mission-critical workloads
- MUST run reliably based on GitHub Actions cron schedules with infrequent manual updates
- MUST NEVER account for backwards compatibility
- Breaking changes are acceptable and expected
- Version bumps do NOT require migration paths
- Simplicity and iteration speed trump stability guarantees

**Rationale**: Over-engineering a personal utility wastes time and creates unnecessary complexity. Removing backwards compatibility constraints enables rapid iteration and architectural improvements without technical debt accumulation.

### Principle 5 (Future Goal): Mandatory Documentation and Testing at Every Step

**Declaration**: Every feature implementation MUST include minimum viable documentation and comprehensive test coverage (unit + integration) covering positive cases, negative cases, and error conditions.

**Rules**:
- MUST include unit tests for all new functions/methods
- MUST include integration tests for all workflows and user scenarios
- MUST test positive paths (expected behavior)
- MUST test negative paths (invalid inputs, edge cases)
- MUST test error conditions (exceptions, failures, timeouts)
- MUST update README.md, quickstart guides, and relevant specs when implementation changes architectural patterns (e.g., dependency managers, workflows)
- AI agents MAY make educated guesses on testing strategy but MUST notify user post-completion with <20 word message if significant decisions made
- Documentation debt is a blocker - PRs without docs/tests are incomplete

**Rationale**: Tests prevent regressions and document expected behavior. Documentation ensures users can adopt changes and understand the system. Both are non-negotiable for maintainability, even in a "toy" project. The discipline of writing tests and docs forces clarity of thought and catches issues early.

## Governance

### Amendment Process

1. Amendments require explicit project maintainer approval
2. Version bumps follow semantic versioning:
   - **MAJOR**: Backward incompatible governance changes, principle removal/redefinition
   - **MINOR**: New principles added or material expansion of existing principles
   - **PATCH**: Clarifications, wording improvements, non-semantic refinements
3. All amendments MUST update the Sync Impact Report (HTML comment at top of this file)
4. Template consistency checks MUST be performed on amendment

### Compliance Review

- Feature specifications MUST include "Constitution Check" section
- Violations require explicit justification in plan.md
- Unjustified violations block feature approval
- Constitution adherence is verified during PR review

### Version History

- **v1.1.0** (2025-10-18): Added Principle 5 (Mandatory Documentation and Testing)
- **v1.0.0** (2025-10-18): Initial ratification with 4 core principles

---

*This constitution is the source of truth for project governance. When in doubt, consult these principles.*

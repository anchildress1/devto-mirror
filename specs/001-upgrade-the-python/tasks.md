# Tasks: Upgrade Python Implementation to Astral uv

**Input**: Design documents from `/specs/001-upgrade-the-python/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as explicitly requested in the feature specification (User Story 4 and FR-008).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- Single project structure at repository root
- Scripts in `scripts/` directory
- Tests in `tests/` directory
- Configuration at root level

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for uv migration

- [X] T001 Create pyproject.toml with project metadata and dependencies in pyproject.toml
- [X] T002 [P] Create tests/ directory structure in tests/
- [X] T003 [P] Create tests/__init__.py for package recognition in tests/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core migration tasks that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Remove requirements.txt file from repository root
- [X] T005 Remove dev-requirements.txt file from repository root

**Checkpoint**: Foundation ready - uv migration infrastructure in place, user story implementation can now begin

---

## Phase 3: User Story 1 - Developer Sets Up Local Development Environment (Priority: P1) 🎯 MVP

**Goal**: Enable developers to set up the project using modern uv tooling instead of pip

**Independent Test**: Run `uv venv && uv pip install -e . && uv run python scripts/generate_site.py` and verify successful execution

### Tests for User Story 1 ⚠️

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [P] [US1] Unit test for pyproject.toml dependency resolution in tests/test_pyproject.py

### Implementation for User Story 1

- [X] T007 [US1] Migrate runtime dependencies from requirements.txt to pyproject.toml [project.dependencies]
- [X] T008 [US1] Migrate dev dependencies from dev-requirements.txt to pyproject.toml [project.optional-dependencies.dev]
- [X] T009 [US1] Add Python version constraint (>=3.11) to pyproject.toml [project.requires-python]
- [X] T010 [US1] Configure uv as build backend in pyproject.toml [build-system]

**Checkpoint**: At this point, User Story 1 should be fully functional - developers can set up environment with uv

---

## Phase 4: User Story 2 - CI/CD Pipeline Uses uv for Dependency Management (Priority: P2)

**Goal**: Update automated workflows to use uv for faster, more reliable builds

**Independent Test**: Trigger GitHub Actions workflow and verify uv commands execute successfully

### Tests for User Story 2 ⚠️

- [X] T011 [P] [US2] Integration test for CI workflow execution in tests/test_ci.py

### Implementation for User Story 2

- [X] T012 [US2] Update .github/workflows/generate-and-deploy-site.yml to install uv
- [X] T013 [US2] Replace pip install commands with uv pip install in CI workflow
- [X] T014 [US2] Update .github/workflows/refresh-all-posts-and-comments.yml to use uv
- [X] T015 [US2] Verify CI runners support uv or add installation step

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Documentation Reflects uv Usage (Priority: P3)

**Goal**: Update documentation to show uv commands instead of pip for accurate contributor guidance

**Independent Test**: Follow README setup instructions and verify uv commands work as documented

### Tests for User Story 3 ⚠️

- [X] T016 [P] [US3] Documentation validation test in tests/test_docs.py

### Implementation for User Story 3

- [X] T017 [US3] Update Local Development section in README.md to use uv venv instead of python -m venv
- [X] T018 [US3] Update dependency installation commands in README.md to use uv pip install
- [X] T019 [US3] Update Quick Setup section in README.md with uv commands
- [X] T020 [US3] Remove references to requirements.txt and pip in README.md

**Checkpoint**: Documentation accurately reflects uv usage

---

## Phase 6: User Story 4 - Basic Test Setup is Established (Priority: P3)

**Goal**: Create minimal test infrastructure with executable unit test

**Independent Test**: Run `python -m unittest tests.test_basic` and verify test passes

### Tests for User Story 4 ⚠️

- [X] T021 [P] [US4] Self-test for basic test infrastructure in tests/test_basic.py (assert True)

### Implementation for User Story 4

- [X] T022 [US4] Create tests/test_basic.py with unittest.TestCase class
- [X] T023 [US4] Implement test_assert_true method with assert True in tests/test_basic.py
- [X] T024 [US4] Verify test executes and passes with python -m unittest

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [X] T025 [P] Run quickstart.md validation - execute all setup steps
- [X] T026 Validate all existing scripts still work in uv environment
- [X] T027 [P] Update .github/copilot-instructions.md if needed
- [X] T028 Final verification: all success criteria met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially: US1 → US2 → US3/US4
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Independent of other stories
- **User Story 3 (P3)**: Can start after Foundational - Independent of other stories
- **User Story 4 (P3)**: Can start after Foundational - Independent of other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Configuration changes before documentation updates
- Core functionality before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks can run in parallel
- Once Foundational phase completes, all user stories can start in parallel
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch test for User Story 1:
Task: "Unit test for pyproject.toml dependency resolution in tests/test_pyproject.py"

# Launch implementation tasks sequentially (same file dependencies):
Task: "Migrate runtime dependencies from requirements.txt to pyproject.toml [project.dependencies]"
Task: "Migrate dev dependencies from dev-requirements.txt to pyproject.toml [project.optional-dependencies.dev]"
Task: "Add Python version constraint (>=3.11) to pyproject.toml [project.requires-python]"
Task: "Configure uv as build backend in pyproject.toml [build-system]"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test uv environment setup independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test uv setup → Deploy/Demo (MVP!)
3. Add User Story 2 → Test CI with uv → Deploy/Demo
4. Add User Story 3 → Test documentation → Deploy/Demo
5. Add User Story 4 → Test basic test infrastructure → Deploy/Demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (environment setup)
   - Developer B: User Story 2 (CI/CD)
   - Developer C: User Stories 3 & 4 (docs & tests)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

# Data Model: Upgrade Python Implementation to Astral uv

**Date**: October 12, 2025
**Feature**: Upgrade to Astral uv

## Overview

This feature introduces minimal data model changes focused on modernizing Python project configuration and adding basic test infrastructure. No existing data structures are modified.

## Entities

### PythonPackage

**Description**: External Python dependencies managed by uv
**Fields**:
- name: string (package name, e.g., "requests")
- version_spec: string (version constraint, e.g., ">=2.31.0")
- group: enum ("runtime", "dev") (dependency group)

**Validation Rules**:
- name must be valid Python package name
- version_spec must follow PEP 440
- group determines installation context

**Relationships**:
- Belongs to ProjectConfiguration

### ProjectConfiguration

**Description**: pyproject.toml configuration file
**Fields**:
- project_name: string ("devto-mirror")
- version: string (semantic version)
- description: string
- dependencies: list[PythonPackage] (runtime dependencies)
- dev_dependencies: list[PythonPackage] (development dependencies)
- python_requires: string (">=3.11")

**Validation Rules**:
- Must conform to PEP 621 pyproject.toml format
- All dependencies must be available via uv
- Python version must be supported by uv

### TestFile

**Description**: Basic unit test file
**Fields**:
- filename: string ("test_basic.py")
- test_class: string ("TestBasic")
- test_method: string ("test_assert_true")
- assertion: string ("assert True")

**Validation Rules**:
- Must use unittest framework
- Must execute without errors
- Must be discoverable by test runners

**Relationships**:
- Belongs to TestSuite

### TestSuite

**Description**: Test directory structure
**Fields**:
- directory: string ("tests/")
- init_file: string ("__init__.py")
- test_files: list[TestFile]

**Validation Rules**:
- Directory must exist
- Must contain __init__.py for package recognition
- All test files must be executable

## State Transitions

No complex state transitions required. The upgrade is a one-time migration:

1. **Pre-upgrade**: requirements.txt based configuration
2. **Migration**: Convert to pyproject.toml, add tests/
3. **Post-upgrade**: uv-managed project with test infrastructure

## Data Flow

1. Dependencies defined in pyproject.toml
2. uv resolves and installs packages
3. Tests execute in uv-managed environment
4. CI uses uv for consistent builds

## Constraints

- No changes to existing data files (posts_data.json, etc.)
- Maintain backward compatibility for existing scripts
- Test infrastructure must be minimal but functional
- Configuration must work across development and CI environments

#!/usr/bin/env python3
"""
Test runner with coverage reporting for the Dev.to Mirror project.

This script runs unit tests with coverage analysis and displays results
in the terminal with options for different output formats.
"""

import subprocess  # nosec B404 - subprocess needed for test runner functionality
import sys
from pathlib import Path


def run_command(cmd_args, description="", cwd=None):
    """Run a command and handle errors."""
    if description:
        print(f"🔄 {description}")

    # Convert string command to list for safer execution
    if isinstance(cmd_args, str):
        cmd_args = cmd_args.split()

    result = subprocess.run(cmd_args, capture_output=True, text=True, cwd=cwd)  # nosec B603 - controlled input

    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd_args)}")
        print(f"Error: {result.stderr}")
        return False

    if result.stdout:
        print(result.stdout)

    return True


def main():
    """Main test runner function."""
    print("🧪 Running tests with coverage analysis...\n")

    # Get project root directory
    project_root = Path(__file__).parent.parent

    # Run tests with coverage
    test_cmd = ["coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
    if not run_command(test_cmd, "Running unit tests with coverage tracking", cwd=project_root):
        sys.exit(1)

    print("\n" + "=" * 80)
    print("📊 COVERAGE REPORT - AI OPTIMIZATION MODULES")
    print("=" * 80)

    # Show coverage for our AI optimization modules
    coverage_ai_cmd = ["coverage", "report", "--include=devto_mirror/ai_optimization/*"]
    run_command(coverage_ai_cmd, "", cwd=project_root)

    print("\n" + "=" * 80)
    print("📊 FULL PROJECT COVERAGE REPORT")
    print("=" * 80)

    # Show full coverage report
    coverage_cmd = ["coverage", "report"]
    run_command(coverage_cmd, "", cwd=project_root)

    # Offer to generate HTML report
    response = input("\n🌐 Generate HTML coverage report? (y/N): ").lower().strip()
    if response in ["y", "yes"]:
        html_cmd = ["coverage", "html"]
        if run_command(html_cmd, "Generating HTML coverage report", cwd=project_root):
            print("✅ HTML report generated in 'htmlcov/' directory")
            print("   Open 'htmlcov/index.html' in your browser to view detailed coverage")

    print("\n✅ Test run complete!")


if __name__ == "__main__":
    main()

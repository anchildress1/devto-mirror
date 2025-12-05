#!/usr/bin/env python3
"""
Site generation validation script for pre-commit checks.
Tests that generate_site.py can run without errors in a dry-run mode.
"""

import os
import shutil
import subprocess  # nosec - subprocess needed for test runner functionality, controlled input
import sys
import tempfile
from pathlib import Path

# Load environment variables from .env file if it exists
from dotenv import load_dotenv

load_dotenv()


def validate_site_generation():
    """
    Validate that the site generation script can run without errors.
    Uses a temporary directory to avoid modifying the actual workspace.
    """

    print("🔍 Validating site generation script...")

    # Check required environment variables
    devto_username = os.getenv("DEVTO_USERNAME")
    pages_repo = os.getenv("PAGES_REPO")

    if not devto_username:
        print("⚠️  DEVTO_USERNAME not set - using test value for validation")
        devto_username = "testuser"

    if not pages_repo:
        print("⚠️  PAGES_REPO not set - using test value for validation")
        pages_repo = "testuser/devto-mirror"

    # Create temporary directory for validation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Copy necessary files to temp directory
        script_dir = Path(__file__).parent
        workspace_root = script_dir.parent

        # Create scripts subdirectory to maintain package structure
        scripts_temp = temp_path / "scripts"
        scripts_temp.mkdir(exist_ok=True)

        # Copy the generate_site.py script and all its dependencies
        shutil.copy2(workspace_root / "scripts" / "generate_site.py", scripts_temp)
        shutil.copy2(workspace_root / "scripts" / "utils.py", scripts_temp)
        shutil.copy2(workspace_root / "scripts" / "constants.py", scripts_temp)
        shutil.copy2(workspace_root / "scripts" / "path_utils.py", scripts_temp)

        # Copy __init__.py if it exists
        if (workspace_root / "scripts" / "__init__.py").exists():
            shutil.copy2(workspace_root / "scripts" / "__init__.py", scripts_temp)

        # Copy templates directory if it exists (wrap in try-except for test mocking)
        try:
            templates_src = workspace_root / "scripts" / "templates"
            if templates_src.exists() and templates_src.is_dir():
                shutil.copytree(templates_src, scripts_temp / "templates", dirs_exist_ok=True)
        except (OSError, TypeError):
            pass  # Templates directory doesn't exist or is mocked

        # Create assets directory with placeholder image
        assets_dir = temp_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        (assets_dir / "devto-mirror.jpg").touch()
        (assets_dir / "robots.txt").touch()
        (assets_dir / "llms.txt").touch()

        # Set up environment for validation
        env = os.environ.copy()
        env.update(
            {
                "DEVTO_USERNAME": devto_username,
                "PAGES_REPO": pages_repo,
                "VALIDATION_MODE": "true",  # Signal to script this is validation
            }
        )

        try:
            # Run the script in validation mode
            result = subprocess.run(  # nosec - subprocess needed for test runner functionality, controlled input
                [sys.executable, "scripts/generate_site.py"],
                cwd=temp_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout for validation
            )

            if result.returncode == 0:
                print("✅ Site generation validation passed")
                return True
            else:
                print("❌ Site generation validation failed")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ Site generation validation timed out (>60s)")
            return False
        except Exception as e:
            print(f"❌ Site generation validation error: {e}")
            return False


def main():
    """Main validation entry point"""
    if not validate_site_generation():
        sys.exit(1)
    print("🎉 All site generation validations passed!")


if __name__ == "__main__":
    main()

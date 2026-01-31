#!/usr/bin/env python3
"""
Site generation validation script for lefthook checks.
Tests that generate_site.py can run without errors in a dry-run mode.
"""

import os
import subprocess  # nosec B404
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
    gh_username = os.getenv("GH_USERNAME")
    site_domain = os.getenv("SITE_DOMAIN")

    if not devto_username:
        print("⚠️  DEVTO_USERNAME not set - using test value for validation")
        devto_username = "testuser"

    if not site_domain and not gh_username:
        print("⚠️  SITE_DOMAIN and GH_USERNAME not set - using test value for validation")
        gh_username = "testuser"

    # Create temporary directory for validation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Copy necessary files to temp directory
        script_dir = Path(__file__).parent
        workspace_root = script_dir.parent

        # Create assets directory with placeholder image
        assets_dir = temp_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        (assets_dir / "devto-mirror.jpg").touch()
        (assets_dir / "robots.txt").touch()
        (assets_dir / "llms.txt").touch()

        # Set up environment for validation
        env = os.environ.copy()
        env_updates = {
            "DEVTO_USERNAME": devto_username,
            "VALIDATION_MODE": "true",
            "PYTHONPATH": str(workspace_root / "src") + os.pathsep + env.get("PYTHONPATH", ""),
        }
        if site_domain:
            env_updates["SITE_DOMAIN"] = site_domain
        if gh_username:
            env_updates["GH_USERNAME"] = gh_username
        env.update(env_updates)

        try:
            # Run the script in validation mode
            result = subprocess.run(  # nosec B603
                [sys.executable, "-m", "devto_mirror.site_generation.generator"],
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

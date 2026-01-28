"""
Tests to ensure `devto_mirror.site_generation.generator` handles optional asset files (robots.txt, llms.txt)
gracefully and creates them in the project root when present.

These tests run the script in VALIDATION_MODE to avoid network calls.
"""

import glob
import json
import os
import shutil
import subprocess  # nosec: B404
import tempfile
import unittest
import warnings
from pathlib import Path

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ASSETS_DIR = os.path.join(ROOT, "assets")


def restore_or_remove(backup, target):
    """Restore a backed-up file to target or remove the target if no backup exists.

    This is a best-effort helper used by tests to avoid raising during teardown.
    """
    try:
        if backup:
            # Best-effort restore; ignore OS errors during cleanup
            shutil.copy2(backup, target)
        else:
            # Best-effort remove; ignore OS errors during cleanup
            os.remove(target)
    except OSError as e:
        # Don't raise in test teardown - emit a warning so test runners can report
        # the issue but continue cleanup attempts for other files.
        warnings.warn(f"Cleanup warning for {target}: {e}")


class TestGenerateSiteAssets(unittest.TestCase):
    def setUp(self):
        # Backup original assets content if present
        # Use normalized paths to avoid surprising path separators on different OSes
        self.robots_path = os.path.normpath(os.path.join(ASSETS_DIR, "robots.txt"))
        self.llms_path = os.path.normpath(os.path.join(ASSETS_DIR, "llms.txt"))
        self.backup_dir = tempfile.mkdtemp(prefix="gen_site_test_")

        self._robots_backup = None
        self._llms_backup = None
        if os.path.exists(self.robots_path):
            self._robots_backup = os.path.join(self.backup_dir, "robots.txt")
            shutil.copy2(self.robots_path, self._robots_backup)
        if os.path.exists(self.llms_path):
            self._llms_backup = os.path.join(self.backup_dir, "llms.txt")
            shutil.copy2(self.llms_path, self._llms_backup)

        # Ensure a clean project-root target for generated files
        for fname in ("robots.txt", "llms.txt", "index.html", "sitemap.xml"):
            path = os.path.join(ROOT, fname)
            if os.path.exists(path):
                os.remove(path)

    def tearDown(self):
        # Restore backups or remove created files
        restore_or_remove(self._robots_backup, self.robots_path)
        restore_or_remove(self._llms_backup, self.llms_path)
        # Best-effort cleanup of generated artifacts
        for fname in (
            "robots.txt",
            "llms.txt",
            "index.html",
            "sitemap.xml",
            "posts_data.json",
            "last_run.txt",
            "no_new_posts.flag",
        ):
            path = os.path.join(ROOT, fname)
            if os.path.exists(path):
                os.remove(path)  # Best-effort cleanup

        posts_dir = os.path.join(ROOT, "posts")
        for p in glob.glob(os.path.join(posts_dir, "*.html")):
            os.remove(p)  # Best-effort cleanup

        shutil.rmtree(self.backup_dir, ignore_errors=True)

    def _run_generate(self, extra_env=None):
        env = os.environ.copy()
        # Explicit, small env patch to avoid accidentally overriding unrelated
        # environment configuration when spawning the generator subprocess.
        test_env = {
            "DEVTO_USERNAME": "testuser",
            "GH_USERNAME": "testuser",
            "PAGES_REPO": "testuser/repo",
            # Use validation mode to avoid network calls
            "VALIDATION_MODE": "true",
            "FORCE_FULL_REGEN": "true",
        }
        env.update(test_env)
        if extra_env:
            env.update(extra_env)

        # Run the generator as a subprocess using the module path
        import sys

        # Add src to PYTHONPATH so the subprocess can find the package
        src_path = os.path.join(ROOT, "src")
        env_pythonpath = env.get("PYTHONPATH", "")
        # Prepend src to PYTHONPATH
        if env_pythonpath:
            env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env_pythonpath}"
        else:
            env["PYTHONPATH"] = src_path

        # Use -m to run the module
        res = subprocess.run(
            [sys.executable, "-m", "devto_mirror.site_generation.generator"],
            cwd=ROOT,
            env=env,
            capture_output=True,
        )  # nosec: B603
        return res

    def test_assets_templates_have_placeholders(self):
        # Assets templates should exist and contain placeholders for workflow replacement
        self.assertTrue(os.path.exists(self.robots_path), "assets/robots.txt must exist")
        self.assertTrue(os.path.exists(self.llms_path), "assets/llms.txt must exist")

        res = self._run_generate()
        self.assertEqual(res.returncode, 0, msg=f"Generator failed: {res.stderr.decode()}")

        # Verify templates contain placeholders (workflow replaces these during deployment)
        robots_content = Path(self.robots_path).read_text(encoding="utf-8")
        self.assertIn("{root_home}", robots_content, "robots.txt template must contain {root_home} placeholder")

        # llms.txt is static content with no placeholders
        llms_content = Path(self.llms_path).read_text(encoding="utf-8")
        self.assertNotIn("{root_home}", llms_content, "llms.txt should not contain placeholders")
        self.assertNotIn("{home}", llms_content, "llms.txt should not contain placeholders")

    def test_generate_runs_gracefully_when_assets_missing(self):
        # Temporarily remove assets
        tmp_r = None
        tmp_l = None
        if os.path.exists(self.robots_path):
            tmp_r = self.robots_path + ".bak"
            os.rename(self.robots_path, tmp_r)
        if os.path.exists(self.llms_path):
            tmp_l = self.llms_path + ".bak"
            os.rename(self.llms_path, tmp_l)

        try:
            res = self._run_generate()
            self.assertEqual(res.returncode, 0, msg=f"Generator failed when assets missing: {res.stderr.decode()}")
        finally:
            if tmp_r:
                os.rename(tmp_r, self.robots_path)
            if tmp_l:
                os.rename(tmp_l, self.llms_path)

    def test_no_new_posts_short_circuits_gracefully(self):
        # Simulate a normal (non-validation) incremental run where there are no new posts.
        # Create a last_run.txt so the generator treats this as an incremental check.
        (Path(ROOT) / "last_run.txt").write_text("2025-01-01T00:00:00+00:00", encoding="utf-8")

        res = self._run_generate(
            {
                "DEVTO_MIRROR_FORCE_EMPTY_FEED": "true",
                # Disable validation mode so the empty feed path is exercised without network calls
                "VALIDATION_MODE": "false",
                # Ensure we are not in full-regeneration mode
                "FORCE_FULL_REGEN": "false",
            }
        )
        self.assertEqual(res.returncode, 0, msg=f"Generator failed on empty feed: {res.stderr.decode()}")
        marker_path = Path(ROOT) / "no_new_posts.flag"
        self.assertTrue(marker_path.exists(), "No-new-posts marker should be created")

        # When short-circuiting, we should not generate full site artifacts.
        self.assertFalse(os.path.exists(os.path.join(ROOT, "index.html")), "index.html should not be generated")
        self.assertFalse(os.path.exists(os.path.join(ROOT, "sitemap.xml")), "sitemap.xml should not be generated")

    def test_generate_runs_gracefully_with_zero_posts(self):
        # Simulate a user with no posts (or no new posts + no cached state) during validation.
        # The generator must still produce required artifacts and exit 0.
        res = self._run_generate(extra_env={"VALIDATION_NO_POSTS": "true"})
        self.assertEqual(res.returncode, 0, msg=f"Generator failed with zero posts: {res.stderr.decode()}")

        # Required artifacts should still exist.
        for fname in ("index.html", "sitemap.xml", "posts_data.json", "last_run.txt"):
            path = os.path.join(ROOT, fname)
            self.assertTrue(os.path.exists(path), msg=f"Missing required artifact: {fname}")

        # posts_data.json should be valid JSON and (in this case) empty.
        with open(os.path.join(ROOT, "posts_data.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data, [], msg="Expected posts_data.json to be an empty list when zero posts are available")


if __name__ == "__main__":
    unittest.main()

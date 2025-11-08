"""
Tests to ensure `scripts/generate_site.py` handles optional asset files (robots.txt, llms.txt)
gracefully and creates them in the project root when present.

These tests run the script in VALIDATION_MODE to avoid network calls.
"""

import glob
import os
import shutil
import subprocess  # nosec: B404
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ASSETS_DIR = os.path.join(ROOT, "assets")


def restore_or_remove(backup, target):
    """Restore a backed-up file to target or remove the target if no backup exists.

    This is a best-effort helper used by tests to avoid raising during teardown.
    """
    if backup:
        try:
            shutil.copy2(backup, target)
        except OSError:
            # Best-effort restore; ignore OS errors during cleanup
            pass
    else:
        try:
            os.remove(target)
        except OSError:
            pass


class TestGenerateSiteAssets(unittest.TestCase):
    def setUp(self):
        # Backup original assets content if present
        self.robots_path = os.path.join(ASSETS_DIR, "robots.txt")
        self.llms_path = os.path.join(ASSETS_DIR, "llms.txt")
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
        try:
            for fname in ("robots.txt", "llms.txt", "index.html", "sitemap.xml", "posts_data.json", "last_run.txt"):
                path = os.path.join(ROOT, fname)
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

            posts_dir = os.path.join(ROOT, "posts")
            for p in glob.glob(os.path.join(posts_dir, "*.html")):
                try:
                    os.remove(p)
                except OSError:
                    pass
        except OSError:
            # Don't fail teardown on cleanup OS errors
            pass

        shutil.rmtree(self.backup_dir, ignore_errors=True)

    def _run_generate(self, extra_env=None):
        env = os.environ.copy()
        env.update(
            {
                "DEVTO_USERNAME": "testuser",
                "PAGES_REPO": "testuser/repo",
                # Use validation mode to avoid network calls
                "VALIDATION_MODE": "true",
                "FORCE_FULL_REGEN": "true",
            }
        )
        if extra_env:
            env.update(extra_env)

        # Run the generator as a subprocess to execute the top-level script
        import sys

        # Use the current Python executable to avoid relying on PATH; this
        # reduces bandit warnings about partial executable paths.
        res = subprocess.run(
            [sys.executable, "scripts/generate_site.py"], cwd=ROOT, env=env, capture_output=True
        )  # nosec: B603
        return res

    def test_generate_creates_assets_when_present(self):
        # Ensure assets/robots.txt and assets/llms.txt exist for this test
        self.assertTrue(os.path.exists(self.robots_path), "assets/robots.txt must exist for this test")
        self.assertTrue(os.path.exists(self.llms_path), "assets/llms.txt must exist for this test")

        res = self._run_generate()
        self.assertEqual(res.returncode, 0, msg=f"Generator failed: {res.stderr.decode()}")

        # After generation, project-root copies should exist and match assets
        with open(self.robots_path, "rb") as a, open(os.path.join(ROOT, "robots.txt"), "rb") as b:
            self.assertEqual(a.read(), b.read())

        with open(self.llms_path, "rb") as a, open(os.path.join(ROOT, "llms.txt"), "rb") as b:
            self.assertEqual(a.read(), b.read())

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
            # Should not create robots/llms in project root when assets absent
            self.assertFalse(os.path.exists(os.path.join(ROOT, "robots.txt")))
            self.assertFalse(os.path.exists(os.path.join(ROOT, "llms.txt")))
        finally:
            if tmp_r:
                os.rename(tmp_r, self.robots_path)
            if tmp_l:
                os.rename(tmp_l, self.llms_path)


if __name__ == "__main__":
    unittest.main()

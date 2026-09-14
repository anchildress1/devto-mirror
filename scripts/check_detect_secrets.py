"""Fail CI/hooks if detect-secrets finds any git-tracked secret missing from .secrets.baseline."""

from __future__ import annotations

import contextlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASELINE = Path(".secrets.baseline")


def main() -> int:
    if not BASELINE.exists():
        print(f"detect-secrets baseline file is missing: {BASELINE}", file=sys.stderr)
        return 2

    files = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True, check=True).stdout.split("\0")
    # The baseline stores secret hashes, which would flag themselves.
    files = [f for f in files if f and f != str(BASELINE)]

    # The hook rewrites the baseline when secret line numbers drift; scan against a copy
    # so a check never dirties the working tree.
    with tempfile.NamedTemporaryFile(suffix=".baseline", delete=False) as tf:
        tmp_baseline = tf.name
    shutil.copyfile(BASELINE, tmp_baseline)
    try:
        # Exit codes: 0 clean, 1 new secrets (printed to stdout), 3 baseline is stale.
        proc = subprocess.run(["detect-secrets-hook", "--baseline", tmp_baseline, *files])
    finally:
        with contextlib.suppress(OSError):
            Path(tmp_baseline).unlink()

    if proc.returncode == 3:
        print("detect-secrets: .secrets.baseline is stale; run `detect-secrets scan --baseline .secrets.baseline`.")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

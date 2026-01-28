"""Run-state helpers.

Keeps stateful files (last_run, no-op markers) out of script entrypoints so the
core behavior lives under `src/`.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


def get_last_run_timestamp(path: str | os.PathLike = "last_run.txt") -> str | None:
    """Read the timestamp from the last successful run."""
    p = Path(path)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip() or None


def set_last_run_timestamp(path: str | os.PathLike = "last_run.txt") -> str:
    """Write the current UTC timestamp to the run file; return the written value."""
    p = Path(path)
    ts = datetime.now(timezone.utc).isoformat()
    p.write_text(ts, encoding="utf-8")
    return ts


def mark_no_new_posts(
    *,
    marker_path: str | os.PathLike = "no_new_posts.flag",
    github_output_path: str | None = None,
    github_step_summary_path: str | None = None,
) -> None:
    """Create marker file and emit GitHub Actions outputs for no-op runs."""
    Path(marker_path).write_text("true", encoding="utf-8")

    gh_output = github_output_path or os.getenv("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write("no_new_posts=true\n")

    summary_file = github_step_summary_path or os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as summary:
            summary.write("⚠️ No new posts found since last run. Skipping generation.\n")

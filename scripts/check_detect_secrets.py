"""Fail CI/hooks if detect-secrets finds *any* potential secrets in the repository.

This is intentionally strict: any finding causes a non-zero exit.
We scan git-tracked files only (detect-secrets default behavior) to avoid
failing on untracked/generated artifacts.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def _load_json(payload: str) -> dict[str, Any]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"detect-secrets produced non-JSON output: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("detect-secrets output JSON is not an object")

    return data


def main() -> int:
    baseline_path = Path(".secrets.baseline")
    if not baseline_path.exists():
        print("detect-secrets baseline file is missing: .secrets.baseline", file=sys.stderr)
        return 2

    # detect-secrets may update the baseline (e.g., generated_at) even when
    # running in a read-only "check" mode. Run against a temporary copy to
    # keep the git working tree clean.
    baseline_payload = baseline_path.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".baseline", delete=False) as tf:
        tf.write(baseline_payload)
        tmp_baseline = tf.name

    proc = subprocess.run(
        ["detect-secrets", "scan", "--baseline", tmp_baseline],
        capture_output=True,
        text=True,
    )

    with contextlib.suppress(OSError):
        Path(tmp_baseline).unlink()

    if proc.returncode != 0:
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        return proc.returncode

    data = _load_json(proc.stdout or "{}")
    results = data.get("results") or {}

    if not isinstance(results, dict):
        raise ValueError("detect-secrets output 'results' is not an object")

    findings = [(path, items) for path, items in results.items() if items]

    if not findings:
        return 0

    total = sum(len(items) for _, items in findings)

    print(
        f"detect-secrets: found {total} potential secret(s) in {len(findings)} file(s).",
        file=sys.stderr,
    )

    # Keep output short but actionable.
    for path, items in findings[:10]:
        print(f"- {path}: {len(items)} finding(s)", file=sys.stderr)

    if len(findings) > 10:
        print(f"- … plus {len(findings) - 10} more file(s)", file=sys.stderr)

    print("Fix or remove the secret(s) and rerun.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

import subprocess  # nosec B404
import sys


def main():
    try:
        result = subprocess.run(  # nosec B603
            [sys.executable, "-m", "pip_audit", "--progress-spinner=off"], capture_output=True, text=True
        )
        if result.returncode != 0:
            print("WARNING: pip-audit found vulnerabilities:")
            print(result.stdout)
            print(result.stderr)
            print("Commit proceeding despite warnings. Please address these issues.")
        else:
            print("pip-audit: No vulnerabilities found.")
    except Exception as e:
        print(f"WARNING: Failed to run pip-audit: {e}")

    # Always exit 0 to not block commit
    sys.exit(0)


if __name__ == "__main__":
    main()

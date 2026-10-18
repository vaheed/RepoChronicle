#!/usr/bin/env python3
"""Fail closed when installed Python distributions have unknown/disallowed licenses."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from repochronicle.license_policy import license_failures


def main() -> int:
    try:
        result = subprocess.run(
            ["pip-licenses", "--format=json"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"License inventory failed: {exc}", file=sys.stderr)
        return 2

    packages: list[dict[str, Any]] = json.loads(result.stdout)
    failures = license_failures(packages)

    if failures:
        print("License policy check failed. Review each package before changing the allowlist:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"License policy check passed for {len(packages)} installed distributions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

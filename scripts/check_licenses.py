#!/usr/bin/env python3
"""Fail closed when installed Python distributions have unknown/disallowed licenses."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

ALLOWED_MARKERS = (
    "apache",
    "mit",
    "bsd",
    "isc license",
    "postgresql license",
    "python software foundation",
    "psf license",
    "zlib license",
    "unlicense",
    "mozilla public license 2.0",
    "mpl 2.0",
)
FORBIDDEN_MARKERS = (
    "agpl",
    "gpl",
    "lgpl",
    "sspl",
    "busl",
    "business source",
    "non-commercial",
    "noncommercial",
    "proprietary",
    "unknown",
    "unlicensed",
    "other",
)


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
    failures: list[str] = []
    for package in packages:
        name = str(package.get("Name", "unknown"))
        version = str(package.get("Version", "unknown"))
        license_name = str(package.get("License", "")).strip()
        normalized = license_name.lower()
        if not normalized or any(marker in normalized for marker in FORBIDDEN_MARKERS):
            failures.append(f"{name}=={version}: disallowed/unknown license {license_name!r}")
            continue
        if not any(marker in normalized for marker in ALLOWED_MARKERS):
            failures.append(f"{name}=={version}: license requires manual review: {license_name!r}")

    if failures:
        print("License policy check failed. Review each package before changing the allowlist:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"License policy check passed for {len(packages)} installed distributions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

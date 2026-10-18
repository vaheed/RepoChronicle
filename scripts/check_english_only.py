#!/usr/bin/env python3
"""Check repository text for non-English script characters and broken local Markdown links."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".sql",
    ".sh",
    ".txt",
    ".ini",
    ".cfg",
    ".json",
    ".example",
}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
NON_LATIN_SCRIPTS = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")


def tracked_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        special_names = {
            "Dockerfile",
            "Makefile",
            "LICENSE",
            ".gitignore",
            ".dockerignore",
            ".editorconfig",
        }
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in special_names:
            files.append(path)
    return files


def main() -> int:
    failures: list[str] = []
    for path in tracked_text_files():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"{path.relative_to(ROOT)}: text file is not valid UTF-8")
            continue
        if NON_LATIN_SCRIPTS.search(content):
            failures.append(f"{path.relative_to(ROOT)}: non-English script character found")
        if path.suffix.lower() != ".md":
            continue
        for target in MARKDOWN_LINK.findall(content):
            target = target.strip().split("#", maxsplit=1)[0]
            if (
                not target
                or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)
                or target.startswith("//")
            ):
                continue
            candidate = (path.parent / target).resolve()
            if not candidate.exists():
                failures.append(f"{path.relative_to(ROOT)}: broken local Markdown link -> {target}")
    if failures:
        print("Repository hygiene check failed:")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print(f"Repository hygiene check passed for {len(tracked_text_files())} text files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

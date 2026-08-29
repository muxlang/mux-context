#!/usr/bin/env python3
"""Check local Markdown links and the repository's scoped ASCII policy.

External links are intentionally not fetched here: network availability is not
evidence that a link is authoritative, and the repository docs link to sibling
repositories and services. Local targets, however, must exist in every commit.
Unicode is allowed in user-facing docs and behavior fixtures; only operational
policy and configuration paths are checked for ASCII.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)")
ASCII_SUFFIXES = {".json", ".sh", ".toml", ".yml", ".yaml"}
ASCII_NAMES = {"AGENTS.md", "SKILL.md", "llms.txt", "sonar-project.properties"}
ASCII_DOCS = {"docs/repo-governance.md", "docs/release-process.md"}


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item for item in result.stdout.decode().split("\0") if item]


def is_ascii_scoped(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    return (
        path.name in ASCII_NAMES
        or path.suffix in ASCII_SUFFIXES
        or relative in ASCII_DOCS
        or relative.startswith(".github/")
        or relative.startswith("scripts/")
    )


def local_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    targets = []
    for match in MARKDOWN_LINK.finditer(text):
        target = match.group(1).strip("<>")
        if target.startswith(("https://", "http://", "mailto:")):
            continue
        target = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if target:
            targets.append(target)
    return targets


def check_links(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        if path.suffix.lower() not in {".md", ".mdx"}:
            continue
        relative = path.relative_to(ROOT).as_posix()
        for target in local_links(path):
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"{relative}: local link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{relative}: missing local link target: {target}")
    return errors


def check_ascii(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        if not is_ascii_scoped(path):
            continue
        data = path.read_bytes()
        if any(byte > 0x7F for byte in data):
            errors.append(
                f"{path.relative_to(ROOT).as_posix()}: non-ASCII byte in scoped policy path"
            )
    return errors


def main() -> int:
    paths = tracked_paths()
    errors = check_links(paths) + check_ascii(paths)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"OK: checked {len(paths)} tracked paths, local Markdown links, and scoped ASCII paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

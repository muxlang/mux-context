#!/usr/bin/env python3
"""Check Markdown links and the canonical scoped encoding policy.

The policy is data-driven so a repository's intentional Unicode surface is
reviewable instead of hidden in checker code. External links are intentionally
not fetched here; local targets must exist in every commit.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_SUFFIXES = {".md", ".mdx"}
MARKDOWN_LINK = re.compile(r"(?<!!)(\[[^\]]*\])\(\s*(<[^>]+>|[^)\s]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--repository", default=None)
    parser.add_argument("--policy", type=Path, default=None)
    return parser.parse_args()


def tracked_paths(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [root / item for item in result.stdout.decode().split("\0") if item]


def load_policy(path: Path, repository: str) -> dict[str, object]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load policy {path}: {error}") from error
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("policy must be an object with version 1")
    repositories = document.get("repositories")
    if not isinstance(repositories, dict) or repository not in repositories:
        raise ValueError(f"policy has no repository entry for {repository!r}")
    config = repositories[repository]
    if not isinstance(config, dict):
        raise ValueError(f"policy entry for {repository!r} must be an object")
    ascii_globs = config.get("ascii_globs")
    allowed = config.get("unicode_allowed")
    if not isinstance(ascii_globs, list) or not all(
        isinstance(item, str)
        and item
        and not item.startswith("/")
        and ".." not in item.split("/")
        for item in ascii_globs
    ):
        raise ValueError(f"{repository}: ascii_globs must contain safe non-empty paths")
    if len(set(ascii_globs)) != len(ascii_globs):
        raise ValueError(f"{repository}: ascii_globs contains duplicates")
    if not isinstance(allowed, list):
        raise ValueError(f"{repository}: unicode_allowed must be a list")
    seen_allowed: set[str] = set()
    for entry in allowed:
        if not isinstance(entry, dict):
            raise ValueError(f"{repository}: every unicode_allowed entry must be an object")
        glob = entry.get("glob")
        reason = entry.get("reason")
        if (
            not isinstance(glob, str)
            or not glob
            or glob.startswith("/")
            or ".." in glob.split("/")
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise ValueError(f"{repository}: every Unicode exception needs a safe glob and reason")
        if glob in seen_allowed:
            raise ValueError(f"{repository}: unicode_allowed contains duplicate glob {glob!r}")
        seen_allowed.add(glob)
    return config


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def match_pattern(path: str, pattern: str) -> bool:
    # Treat `**/name` as matching both a nested path and a repository-root
    # path. Python's fnmatch does not give `**` special slash semantics.
    return fnmatch.fnmatchcase(path, pattern) or (
        pattern.startswith("**/") and fnmatch.fnmatchcase(path, pattern[3:])
    )


def matches(path: str, patterns: list[str]) -> bool:
    return any(match_pattern(path, pattern) for pattern in patterns)


def allowed_unicode(path: str, config: dict[str, object]) -> bool:
    entries = config["unicode_allowed"]
    assert isinstance(entries, list)
    return any(match_pattern(path, entry["glob"]) for entry in entries)


def check_utf8(paths: list[Path], root: Path) -> list[str]:
    errors = []
    for path in paths:
        data = path.read_bytes()
        # Binary assets are not prose/configuration and are checked by their
        # format-specific gates. Text files must have valid UTF-8 encoding.
        if b"\0" in data:
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"{relative(path, root)}: invalid UTF-8 ({error})")
    return errors


def check_ascii(paths: list[Path], root: Path, config: dict[str, object]) -> list[str]:
    patterns = config["ascii_globs"]
    assert isinstance(patterns, list)
    errors = []
    for path in paths:
        name = relative(path, root)
        if not matches(name, patterns) or allowed_unicode(name, config):
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        if any(byte > 0x7F for byte in data):
            errors.append(f"{name}: non-ASCII byte in scoped policy path")
    return errors


def local_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    targets = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        # Inline code can contain syntax such as `identity[T](value)`, which
        # must not be mistaken for a Markdown link.
        line = re.sub(r"`[^`]*`", "", line)
        for match in MARKDOWN_LINK.finditer(line):
            target = match.group(2).strip("<>")
            if target and not target.startswith(("https://", "http://", "mailto:")):
                targets.append(unquote(target.split("#", 1)[0].split("?", 1)[0]))
    return targets


def check_links(paths: list[Path], root: Path, config: dict[str, object]) -> list[str]:
    errors = []
    link_mode = config.get("link_mode", "filesystem")
    for path in paths:
        if path.suffix.lower() not in MARKDOWN_SUFFIXES:
            continue
        try:
            targets = local_links(path)
        except UnicodeDecodeError as error:
            errors.append(f"{relative(path, root)}: cannot read Markdown as UTF-8 ({error})")
            continue
        for target in targets:
            if link_mode == "docusaurus" and (
                target.startswith("/") or Path(target).suffix == ""
            ):
                # Docusaurus resolves root-relative and extensionless document
                # IDs as routes rather than repository files.
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{relative(path, root)}: local link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{relative(path, root)}: missing local link target: {target}")
    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    repository = args.repository or root.name
    policy_path = (args.policy or root / "docs/encoding-policy.json").resolve()
    try:
        config = load_policy(policy_path, repository)
        paths = tracked_paths(root)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    errors = check_utf8(paths, root) + check_links(paths, root, config) + check_ascii(paths, root, config)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"OK: checked {len(paths)} tracked paths, UTF-8, local Markdown links, and scoped encoding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

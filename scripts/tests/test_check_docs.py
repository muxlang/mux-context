#!/usr/bin/env python3
"""Unit tests for the repository quality-policy checker."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "ci/check-docs.py"
SPEC = importlib.util.spec_from_file_location("check_docs", SCRIPT)
assert SPEC and SPEC.loader
CHECK_DOCS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_DOCS)


class CheckDocsTests(unittest.TestCase):
    def test_markdown_links_ignore_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_text(
                "`identity[T](value)`\n```mux\ncall[T](value)\n```\n[README](README.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(CHECK_DOCS.local_links(document), ["README.md"])

    def test_invalid_utf8_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_bytes(b"\xff")
            errors = CHECK_DOCS.check_utf8([document], root)
            self.assertEqual(len(errors), 1)
            self.assertIn("invalid UTF-8", errors[0])

    def test_manifest_requires_exception_reason(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / "policy.json"
            policy.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "repositories": {
                            "demo": {
                                "ascii_globs": ["*.json"],
                                "unicode_allowed": [{"glob": "*.md"}],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                CHECK_DOCS.load_policy(policy, "demo")

    def test_root_glob_matches_root_file(self) -> None:
        self.assertTrue(CHECK_DOCS.match_pattern("README.md", "**/*.md"))
        self.assertTrue(CHECK_DOCS.match_pattern("docs/guide.md", "**/*.md"))


if __name__ == "__main__":
    unittest.main()

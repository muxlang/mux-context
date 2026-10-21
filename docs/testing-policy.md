# Testing policy across Mux

Mux keeps separate test suites when they check separate contracts. A test that
uses the same fixture as another test can still be valuable when it checks a
different stage, such as parsing, diagnostics, generated output, runtime
ownership, or editor behavior. Remove a test when its assertions duplicate a
stronger test of the same behavior, not only because its setup looks familiar.

## Commit hooks and CI

Commit hooks should give useful feedback without making routine commits wait on
the slowest repository-wide jobs. CI remains the required full check for a pull
request. A local hook may skip a long corpus sweep when CI runs it on every
change, provided the hook still runs the focused checks and the full command is
documented for ad-hoc use.

In `mux-compiler`, the pre-commit hook runs formatting, strict Clippy, and the
Rust tests except `test_executable_all_mux_files_in_dir`, which executes the
full Mux fixture corpus and takes several minutes. The corpus compiles and
runs up to two non-network fixtures at once. Network fixtures run serially, and
snapshots are checked in sorted order. Set `MUX_EXECUTABLE_TEST_JOBS` to raise
the worker count on a larger machine. The required Rust CI check runs the full
test and rejects unreferenced snapshots. CI also runs the executable corpus
with the leak-check runtime. To run the full local suite:

```bash
./scripts/run-checks.sh --reject-unreferenced-snapshots
```

To run just the executable fixture test:

```bash
./scripts/dev-cargo.sh test -p mux-lang --test executable_integration
```

The runtime pre-commit hook keeps its all-feature Rust tests. They exercise the
runtime ABI and ownership behavior directly and do not run the compiler's
multi-minute Mux fixture corpus. Other repositories keep their existing
focused hooks; check each repository's `AGENTS.md` and workflow for the current
commands.

The website and syntax-highlighting repositories each generate coverage once
in a dedicated CI job and upload the LCOV report for SonarQube. Their existing
required check names aggregate the parallel quality and test jobs, so the
coverage report is still required even when another quality check fails.

## What the suites protect

- `mux-compiler` separates lexer and parser snapshots, semantic and diagnostic
  checks, executable fixture behavior, source locations, LSP requests, and
  generated-program campaigns.
- `mux-runtime` checks Rust APIs, C ABI calls, value ownership, and resource
  cleanup. The compiler's executable fixtures add a separate end-to-end check
  of generated programs linked to the runtime.
- `mux-examples` checks complete, user-facing programs and their recorded
  output. Those examples are intentionally separate from compiler fixtures.
- `mux-syntax-highlighting` checks the canonical syntax matrix against editor
  grammars and representative samples. `tree-sitter-mux` checks the parser
  corpus, editor integration, and parser ABI compatibility.
- `mux-website` checks UI behavior and documentation tooling. The API repo
  checks request handling, sandboxing, limits, cleanup, and deployed service
  contracts. `.github` checks shared governance scripts.

Keep coverage thresholds and full CI checks in place when shortening local
hooks. Do not merge tests that protect different contracts just to reduce the
number of test cases.

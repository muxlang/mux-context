# 0003 - Verify consumers against source in CI

## Context

After the [multi-repo split](0001-multi-repo-split.md), several repos consume an
artifact owned by a sibling: the compiler links `mux-runtime`, `tree-sitter-mux`
vendors `syntax-matrix.json`, the website carries its own copy of the keyword
set. In each case CI tested against a *pinned or vendored copy* of that artifact,
not the sibling's live source:

- `mux-compiler` built the runtime from its crates.io version pin, so a coupled
  runtime change was never exercised by compiler CI until the runtime was
  published - forcing a publish for every small coupled change.
- `mux-runtime` had no check that the compiler still built and linked against it,
  so an FFI break was only caught downstream.
- `tree-sitter-mux` and `mux-website` held copies of `syntax-matrix.json` (the
  canonical spec) with nothing verifying they matched.

The org-wide audit is tracked in muxlang/mux-context#3, with per-repo issues
`mux-compiler#227`, `mux-runtime#1`, `tree-sitter-mux#1`,
`mux-syntax-highlighting#1`, `mux-website#9`, and `mux-website-api#1`.

## Decision

Consumers verify against **source**, not a published or vendored copy, in CI:

- For built dependencies, check out the sibling's `main` **source** and build
  from it (the compiler checks out `mux-runtime` and builds it via
  `MUX_RUNTIME_SRC`), rather than resolving the crates.io pin.
- For vendored copies, fail CI on drift from the canonical source.

Cross-repo **version bumps and publishes remain a release action** (see
[0002](0002-independent-versioning.md) and [release-process.md](../release-process.md)),
not a per-change requirement.

The deliberately pinned case stays pinned: `mux-website-api` runs a *released*
compiler by design, not `main`.

## Consequences

- A coupled change goes green in CI without a publish; publishing is decoupled
  from day-to-day development.
- Because the runtime is checked out **inside** the compiler tree, the compiler's
  root `Cargo.toml` must `exclude = ["mux-runtime"]` so cargo does not attach it
  to the workspace, and the runtime build cache must be keyed on the runtime
  source SHA (not its version) or it goes stale.
- Reverse coupling is also covered: `mux-runtime` CI builds `mux-compiler` `main`
  against the runtime source to catch FFI breaks at their origin.
- The release-time ordering from [0002](0002-independent-versioning.md) (publish
  runtime, bump the compiler's range, release the compiler) still applies at
  release; this record only governs per-change CI.

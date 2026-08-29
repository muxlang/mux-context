# 0001 - Split the monorepo into the muxlang org

## Context

Mux began as a single repo (`DerekCorniello/mux-lang`) containing the compiler,
runtime, website, playground API, and editor tooling. These components have
different toolchains (LLVM vs plain Rust vs Node vs Python), different release
cadences, and different audiences, but shared one version, one CI, and one issue
tracker.

## Decision

Split into the [muxlang](https://github.com/muxlang) org as independent repos:
`mux-compiler`, `mux-runtime`, `mux-website`, `mux-website-api`,
`tree-sitter-mux`, `mux-syntax-highlighting`, `mux-examples`, `.github`, and
this `mux-context` repository. The canonical
[`repositories.txt`](https://github.com/muxlang/.github/blob/main/repositories.txt)
manifest is the authoritative active list; full git history is preserved per
component.

## Consequences

- Each repo has its own CI, SonarCloud project, and release flow.
- The runtime is resolved from its git source and pinned by the compiler lockfile
  (see [ADR 0004](0004-runtime-resolved-from-source.md) and
  [ARCHITECTURE](../../ARCHITECTURE.md)). Existing crates.io releases are
  retained, but the channel is frozen.
- The syntax spec stays canonical in `mux-syntax-highlighting` and is vendored
  into `tree-sitter-mux`.
- Coordination that used to be implicit (one repo) is now explicit: this repo,
  the per-repo `AGENTS.md`, and version pins.

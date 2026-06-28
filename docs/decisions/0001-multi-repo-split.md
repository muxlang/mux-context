# 0001 - Split the monorepo into the muxlang org

## Context

Mux began as a single repo (`DerekCorniello/mux-lang`) containing the compiler,
runtime, website, playground API, and editor tooling. These components have
different toolchains (LLVM vs plain Rust vs Node vs Python), different release
cadences, and different audiences, but shared one version, one CI, and one issue
tracker.

## Decision

Split into the [muxlang](https://github.com/muxlang) org as independent repos
(`mux-compiler`, `mux-runtime`, `mux-website`, `mux-website-api`,
`tree-sitter-mux`, `mux-syntax-highlighting`) plus the org `.github` repo, with
full git history preserved per component. Cross-repo knowledge lives in this
`context` repo.

## Consequences

- Each repo has its own CI, SonarCloud project, and release flow.
- The runtime is published to crates.io independently; the compiler pins a
  semver range and links it (see [ARCHITECTURE](../../ARCHITECTURE.md)).
- The syntax spec stays canonical in `mux-syntax-highlighting` and is vendored
  into `tree-sitter-mux`.
- Coordination that used to be implicit (one repo) is now explicit: this repo,
  the per-repo `AGENTS.md`, and version pins.

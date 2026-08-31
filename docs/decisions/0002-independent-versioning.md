# 0002 - Version each repo independently

> **Superseded by [0007](0007-artifact-versioning.md).** The old decision
> assigned a public version to every repository. The organization now versions
> only distributable artifacts. [0004](0004-runtime-resolved-from-source.md)
> still governs the runtime's exact source pin.

## Context

After the [multi-repo split](0001-multi-repo-split.md) the old root `VERSION`
file and `sync-version.sh` no longer made sense - they assumed one version for
everything. The compiler and runtime in particular evolve at different rates: a
stdlib fix should not require a compiler release, and vice versa.

## Decision

Version each distributable artifact independently. The `mux-compiler` package
version is the canonical "Mux version". The runtime is source-pinned, and its
Cargo version field is technical metadata rather than a public release number.
The source-resolution details are the decision in
[0004](0004-runtime-resolved-from-source.md).

## Consequences

- A coupled change merges the runtime and compiler changes as paired PRs; the
  compiler lockfile moves only when the compiler intentionally adopts the new
  runtime commit. There is no publish handshake because the crates.io channel
  is frozen.
- The playground (`mux-website-api`) pins a specific released compiler via
  `ARG MUX_VERSION` rather than tracking `main`.
- Published editor packages carry their own versions. Source-only tooling uses
  immutable commits.
- Full release steps live in [release-process.md](../release-process.md).

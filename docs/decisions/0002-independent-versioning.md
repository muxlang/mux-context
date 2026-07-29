# 0002 - Version each repo independently

> **Partly superseded by [0004](0004-runtime-resolved-from-source.md).** The
> compiler no longer pins a semver range on a published `mux-runtime`, so the
> "publish the runtime, then bump the compiler's range, then release" ordering
> below no longer applies. Independent versioning otherwise stands.

## Context

After the [multi-repo split](0001-multi-repo-split.md) the old root `VERSION`
file and `sync-version.sh` no longer made sense - they assumed one version for
everything. The compiler and runtime in particular evolve at different rates: a
stdlib fix should not require a compiler release, and vice versa.

## Decision

Version each repo independently. The `mux-compiler` package version is the
canonical "Mux version". `mux-runtime` versions on its own cadence; the compiler
pins a compatible semver range and reports both via `mux --version`
(`mux X.Y.Z (runtime A.B.C)`).

## Consequences

- A coupled change ships in order: publish `mux-runtime`, then bump the
  compiler's `mux-runtime` range, then release the compiler.
- The playground (`mux-website-api`) pins a specific released compiler via
  `ARG MUX_VERSION` rather than tracking `main`.
- Editor tooling repos carry their own versions.
- Full release steps live in [release-process.md](../release-process.md).

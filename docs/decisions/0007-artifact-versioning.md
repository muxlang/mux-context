# 0007 - Version distributable artifacts

## Context

The repositories do not all produce public packages. The compiler creates the
Mux binary, the runtime is consumed from source, the playground and website are
deployments, and editor packages may or may not be published. Giving every
repository a release number made private metadata look like a compatibility
promise and allowed changelogs, manifests, and tags to drift apart.

## Decision

Use SemVer only for an artifact that external users install or depend on.

- `mux-compiler` owns the canonical Mux version and its GitHub release assets.
- A published editor extension or package has its own SemVer and release notes.
- `mux-runtime` remains a Git dependency pinned by exact commit in the compiler
  lockfile. Cargo's required package version is technical metadata, not a runtime
  release.
- The website, playground API, examples, context, and organization governance
  are rolling source or deployment repositories. Identify them by commit, image
  digest, or workflow artifact instead of inventing SemVer releases.
- A compiler release includes a release manifest with the compiler version,
  runtime commit, deployment inputs, and versions of any published editor
  packages. The manifest is the GitHub Release body for that compiler tag. The
  release workflow writes the build inputs, and a maintainer appends deployment
  inputs after those deployments complete. Unchanged repositories are not
  bumped.

## Consequences

This keeps public compatibility promises small and meaningful. It also makes a
release reproducible without requiring empty releases in unrelated repositories.
Technical manifests may still contain versions required by Cargo, npm, or an
editor packaging tool. Those fields must not be presented as public release
numbers. CI should check the fields that have consumers and reject stale pins or
ambiguous release metadata.

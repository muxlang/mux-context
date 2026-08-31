# Release process

Canonical, cross-repo release reference. Version the artifacts people install or
depend on, not every repository. There is no root `VERSION` file or sync script.
The per-repo `AGENTS.md` files link here instead of duplicating this policy.

## Principles

- The **"Mux version"** is the `mux-compiler` package version
  (`mux-compiler/Cargo.toml`, read as `CARGO_PKG_VERSION`). It is the only
  version that identifies a Mux language and CLI release.
- A repository gets a public SemVer only when it produces an artifact with an
  external compatibility contract. A package that is private or deployed only
  inside the organization may keep the technical metadata its tooling requires,
  but that field is not a public release number.
- `mux-runtime` is a **git dependency** on its `main` branch, pinned to one exact
  commit by `Cargo.lock` (see
  [ADR 0004](decisions/0004-runtime-resolved-from-source.md)). It is not
  published or released independently. `mux version` reports the compiler
  version and the locked runtime commit so a binary identifies its complete
  source.
- Rolling repositories and deployments are identified by immutable commit SHAs,
  image digests, or workflow artifacts. They do not receive empty SemVer bumps
  when another repository changes.
- Read live version values from source manifests and lockfiles. This document
  intentionally does not duplicate numbers that change on each release.
- **A release needs no publish handshake.** Whatever commit `Cargo.lock` names at
  the tag is what ships. The pin moves when someone runs
  `cargo update -p mux-runtime` because a change needs it, or deliberately as
  part of preparing a compiler release.
- **crates.io is frozen.** `mux-lang` (through 0.6.0) and `mux-runtime` (through
  0.5.0) remain published and are not yanked, but no new versions go there.
  Releases are GitHub tarballs installed via `scripts/install.sh`.
- **Agent boundary:** preparing a release (changelog, version bump, lockfile) is
  agent-safe. Tagging and deploying are **MAINTAINER-ONLY** - the agent prepares
  everything and hands these to the user.
- **Docs follow the release and the live playground, never lead them.**
  `mux-website` deploys `docs/` from `main` on every merge, but the playground
  runs the *released* compiler pinned in `mux-website-api` (`Dockerfile` `ARG
  MUX_VERSION`). Docs that teach syntax or diagnostics from an unreleased or
  undeployed compiler go live while the playground still rejects them. This
  shipped once with the `{:}` empty-map literal. When a compiler change adds or
  alters syntax or a public diagnostic code, the compiler release must ship,
  `mux-website-api` must be pinned to that release and deployed, and only then
  may the website docs PR merge. `mux-website`'s `check:docs-snippets` compiles
  every docs example against the playground's pinned release, but it does not
  replace the deployment gate.

## mux-compiler

1. **Gather changes** since the last tag (`git log <last-tag>..HEAD`); read PR/issue
   bodies, not just commit subjects.
2. **Update `CHANGELOG.md`** - new `## [X.Y.Z] - YYYY-MM-DD` section grouped into
   Added / Changed / Fixed (/ Security), referencing issue/PR numbers.
3. **Bump the version** in `mux-compiler/Cargo.toml`; update the README version
   badge and the `- **Current Version:**` line to match.
4. **Settle the runtime pin** - if the release should carry a newer runtime than
   `Cargo.lock` names, run `cargo update -p mux-runtime` and commit the lock.
   Confirm the intended commit with `mux version`.
5. **Refresh the lockfile** - `cargo build`.
6. *(maintainer)* **Tag** - `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`.
   The `Release` workflow builds the per-platform tarballs `--locked` and
   publishes the GitHub release. There is no `cargo publish` step.
7. *(maintainer)* **Deploy the playground before merging dependent docs** - in
   `mux-website-api`, bump `ARG MUX_VERSION` in the Dockerfile to this release
   and run `fly deploy` (app `mux-lang-api`). Confirm the deployed playground
   accepts the release before merging a website PR that documents its syntax or
   diagnostic codes.

## mux-runtime

`mux-runtime` is not released on its own cadence. `mux-compiler` consumes it
from `main` by exact commit, so merging to `main` makes a runtime change
available to source consumers. See [ADR 0004](decisions/0004-runtime-resolved-from-source.md).

1. Record user-visible runtime changes in `CHANGELOG.md` under a dated heading.
   Do not create a new SemVer heading or an empty runtime release.
2. Merge to `main`. There is no publish step.
3. The compiler picks up the change only when a compiler branch runs
   `cargo update -p mux-runtime`, or when a release deliberately settles the
   pin. Until then the compiler keeps building the commit named by its lockfile.
   Both repositories' CI build against the other's `main`, so an FFI break
   surfaces without waiting for the pin to move.

Cargo requires a package `version` field even for a private git dependency. That
field is technical metadata here, not a runtime release promise. Keep it
consistent with the manifest and lockfile, but do not use it to imply a tag or a
published package.

## mux-website-api

Deployed, not published as a library. Identify an API deployment by its Git
commit, container image digest, and Fly release. Bump `ARG MUX_VERSION` in the
`Dockerfile` only when the playground should run a newer compiler release, then
*(maintainer)* `fly deploy` (app `mux-lang-api`). Its repository does not need a
SemVer bump when the compiler changes elsewhere.

## Editor tooling

Published editor packages and extensions get their own SemVer because users
install them as artifacts. Bump only the package that changed. The source-only
grammar and highlighting repositories are identified by commit unless and until
they publish a package. A private workspace `package.json` version is technical
metadata and is not a public release number.

## Release manifest

Every compiler release records the exact inputs that shipped:

```text
compiler: vX.Y.Z
runtime: <Cargo.lock Git SHA>
playground: <compiler pin>, <container image digest>
website: <deployment SHA>
published editor packages: <package name>@<version>
```

Repositories with no changed artifact are absent from the manifest. This keeps
the release reproducible without inventing synchronized or empty versions.

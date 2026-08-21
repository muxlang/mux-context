# Release process

Canonical, cross-repo release reference. Each repo is versioned **independently**
- there is no root `VERSION` file or sync script (those existed in the old
monorepo). The per-repo `AGENTS.md` files link here instead of duplicating this.

## Principles

- The **"Mux version"** is the `mux-compiler` package version
  (`mux-compiler/Cargo.toml`, read as `CARGO_PKG_VERSION`).
- `mux-runtime` is a **git dependency** on its `main` branch, pinned to one exact
  commit by `Cargo.lock` (see
  [ADR 0004](decisions/0004-runtime-resolved-from-source.md)). It is not
  published, and the compiler does not pin a semver range on it. `mux version`
  reports both, with the locked commit as build metadata:
  `compiler v0.6.0` / `runtime v0.5.0+g4e2dc14`.
- **A release needs no publish handshake.** Whatever commit `Cargo.lock` names at
  the tag is what ships. The pin moves when someone runs
  `cargo update -p mux-runtime` - because a change needs it, or deliberately as
  part of preparing a release.
- **crates.io is frozen.** `mux-lang` (through 0.6.0) and `mux-runtime` (through
  0.5.0) remain published and are not yanked, but no new versions go there.
  Releases are GitHub tarballs installed via `scripts/install.sh`.
- **Agent boundary:** preparing a release (changelog, version bump, lockfile) is
  agent-safe. Tagging and deploying are **MAINTAINER-ONLY** - the agent prepares
  everything and hands these to the user.
- **Docs follow the release, never lead it.** `mux-website` deploys `docs/` from
  `main` on every merge, but the playground runs the *released* compiler pinned
  in `mux-website-api` (`Dockerfile` `ARG MUX_VERSION`). Docs that teach syntax
  from an unreleased compiler go live while the playground still rejects them -
  this shipped once with the `{:}` empty-map literal. When a compiler change adds
  or alters syntax, hold the docs PR until that release ships, or cut the release
  first. `mux-website`'s `check:docs-snippets` compiles every docs example against
  the playground's pinned release to catch the skew.

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
7. *(maintainer)* **Deploy the playground** - in `mux-website-api`, bump
   `ARG MUX_VERSION` in the Dockerfile to this release and `fly deploy`.

## mux-runtime

Not released on its own cadence any more: `mux-compiler` consumes it from `main`
by commit, so merging to `main` is what makes a runtime change available. See
[ADR 0004](decisions/0004-runtime-resolved-from-source.md).

1. Update `CHANGELOG.md` under a numbered, dated heading **in the same PR as the
   change**, so the entry lands with the code it describes rather than as a
   follow-up. Without version tags this is the only record of what changed.

   Not a rolling `## [Unreleased]` heading. One that never closes gives no way
   to say which changes a given compiler pin contains - twenty-two entries had
   accumulated under it by 0.6.0 - and the compiler, which kept no such heading,
   went three PRs with no release notes at all. A heading that does not close
   fails in both directions. Open the next numbered heading when the first
   change after a release lands, and move the `version` field with it so the two
   cannot drift.
2. Merge to `main`. That is what makes the change available - there is no
   publish step.
3. The compiler picks it up when a compiler branch runs
   `cargo update -p mux-runtime`, or when a release settles the pin. Until then
   the compiler keeps building the commit its lock names, which is the point of
   the lock. Both repos' CI already build against the other's `main`, so an FFI
   break surfaces without waiting for the pin to move.

The `version` field in `Cargo.toml` is not published while the crates.io channel
is frozen, but it still moves with the changelog heading. Leaving it behind is
what let `tree-sitter.json` and a VS Code manifest claim 0.5.0 while their
changelogs said 0.6.0 - a heading that cannot be matched to what shipped is the
problem this section exists to prevent, and an unpublished field is no less
capable of drifting than a published one.

## mux-website-api

Deployed, not published. Bump `ARG MUX_VERSION` in the `Dockerfile` to the
compiler release the playground should run, then *(maintainer)* `fly deploy`
(app `mux-lang-api`).

## Editor tooling

`mux-syntax-highlighting` (VSCode extension, tree-sitter.json) and
`tree-sitter-mux` carry their own version fields and are released on their own
cadence when the grammar or extension changes.

# Release process

Canonical, cross-repo release reference. Each repo is versioned **independently**
- there is no root `VERSION` file or sync script (those existed in the old
monorepo). The per-repo `AGENTS.md` files link here instead of duplicating this.

## Principles

- The **"Mux version"** is the `mux-compiler` package version
  (`mux-compiler/Cargo.toml`, read as `CARGO_PKG_VERSION`).
- `mux-runtime` is versioned and published on its own cadence. The compiler pins
  a compatible semver range; `mux --version` reports both, e.g.
  `mux 0.5.1 (runtime 0.5.0)`.
- **Agent boundary:** preparing a release (changelog, version bump, lockfile) is
  agent-safe. Tagging, publishing to crates.io, and deploying are
  **MAINTAINER-ONLY** - the agent prepares everything and hands these to the user.
- No registry tokens are stored in CI; crates are published manually from a local
  checkout (`cargo login` once, then `cargo publish`).
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
4. **Refresh the lockfile** - `cargo build`.
5. *(maintainer)* **Tag** - `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`.
6. *(maintainer)* **Publish** - `cargo publish` (package `mux-lang`; binary `mux`).
   If the release needs a new runtime, publish `mux-runtime` first (below), then
   bump the `mux-runtime = "X.Y"` range in `mux-compiler/Cargo.toml`.
7. *(maintainer)* **Deploy the playground** - in `mux-website-api`, bump
   `ARG MUX_VERSION` in the Dockerfile to this release and `fly deploy`.

## mux-runtime

1. Bump `version` in `Cargo.toml` and update the changelog.
2. *(maintainer)* `cargo publish` (requires `cargo login`).
3. *(maintainer)* Tag - `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`.

Publish the runtime **before** bumping the compiler's dependency on it.

## mux-website-api

Deployed, not published. Bump `ARG MUX_VERSION` in the `Dockerfile` to the
compiler release the playground should run, then *(maintainer)* `fly deploy`
(app `mux-lang-api`).

## Editor tooling

`mux-syntax-highlighting` (VSCode extension, tree-sitter.json) and
`tree-sitter-mux` carry their own version fields and are released on their own
cadence when the grammar or extension changes.

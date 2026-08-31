# 0004 - Resolve mux-runtime from source; freeze the crates.io channel

## Context

[0002](0002-independent-versioning.md) has the compiler pin a semver range on a
published `mux-runtime`, so a coupled change ships publish-runtime-first.
[0003](0003-verify-consumers-against-source.md) then had CI build the runtime
from sibling *source*, so a coupled change goes green without a publish. The two
records disagree about what is authoritative, and the seam between them has
produced the same issue repeatedly: `mux-compiler` carried a
`[patch.crates-io]` block redirecting `mux-runtime` to git, because codegen
emitted calls to symbols no published runtime had. That patch cannot ship - a
patch applies only to the workspace that declares it - so every release needed
it cleared, and every coupled change needed a publish first.

Two things settled the direction:

- **The compiler never used `mux-runtime` as a Rust library.** There are zero
  `mux_runtime::` references in its source. The dependency existed to make cargo
  stage the runtime *source* where the compiler could find it, and to build
  `libmux_runtime` into `target/`.
- **crates.io was the highest-friction install channel, not the lowest.**
  `cargo install mux-lang` needs a Rust toolchain plus the exact LLVM 22
  development libraries, then compiles llvm-sys from scratch. The documented
  install path is the prebuilt installer, which needs none of that. crates.io
  was carrying the entire publish-coupling cost to serve the audience least in
  need of help.

crates.io also forbids git dependencies, so as long as the compiler is published
there, resolving the runtime from source is structurally impossible.

## Decision

Resolve `mux-runtime` from its `main` branch as a git dependency, and freeze the
crates.io channel.

- `mux-compiler` depends on `mux-runtime` via git. `Cargo.lock` pins one exact
  commit, so `--locked` builds - CI and release tags included - stay
  reproducible. This extends 0003's "verify against source" from CI to release.
- `MUX_RUNTIME_VERSION` carries the locked commit as semver build metadata
  (`0.5.0+g1a2b3c4`), so `mux version` identifies exactly which runtime a binary
  was built against. A git-sourced runtime keeps one version across every
  commit, so the version alone cannot.
- **The compiler always links the full prebuilt runtime and never builds one
  while compiling a program.** It previously built a feature-trimmed runtime per
  program, which measurement showed buys nothing: static linking already
  discards archive members nothing references, so hello world is 16K against
  either. That removed the build cache, the source lookups, the per-program
  feature sets, and a five-level resolution order whose upper entries silently
  shadowed the lower ones - the reason a release shipped that could not compile
  hello world while every developer machine masked it. Resolution is now
  `MUX_RUNTIME_LIB`, the library beside the binary, then the one cargo built
  into `target/`. A release install carries it beside the binary or in a
  sibling `lib/`, which is the layout `scripts/install.sh` produces.
- The pin moves when a change needs it (`cargo update -p mux-runtime`) or when a
  release settles it deliberately - not on a schedule. Automating it was
  considered and rejected: [0003](0003-verify-consumers-against-source.md)
  already has each repo's CI build against the other's `main`, so an FFI break
  surfaces from both directions without the pin moving, and a lock that trails
  runtime `main` between coupled changes costs nothing.
- Existing crates.io releases (`mux-lang` through 0.6.0, `mux-runtime` through
  0.5.0) stay published and are not yanked - yanking frees no name and only
  breaks anyone pinned. No new versions are published there.

**This supersedes the release-time ordering in
[0002](0002-independent-versioning.md)**: there is no longer a "publish the
runtime, then bump the compiler's range" step, because there is no range.
Artifact-based versioning is defined by [0007](0007-artifact-versioning.md).
The compiler version remains the canonical Mux version; the runtime's Cargo
version is technical metadata for the source dependency.

## Consequences

- A coupled change is one runtime PR and one compiler PR. No publish, no
  patch to clear, no release-checklist item.
- Releases are GitHub tarballs built from the locked commit. Distribution is the
  installer plus, in future, platform package managers.
- Contributors still clone one repository; cargo fetches the runtime. A change
  needing an already-merged runtime commit runs `cargo update -p mux-runtime`
  and commits the lock.
- The runtime library resolution order is now load-bearing and documented in
  `mux-compiler/CONTRIBUTING.md`. The top entries silently shadow the lower
  ones, which is what made a broken binary install invisible to every local
  checkout.
- Reversible. If crates.io matters later, publish a runtime version and swap the
  git dependency for a registry pin; nothing else in this record blocks that.

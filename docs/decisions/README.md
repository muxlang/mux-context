# Architecture decision records

Short records of significant, cross-cutting decisions and *why* they were made.
Add one when a choice affects multiple repos or would otherwise be re-litigated.

Format: one file per decision, `NNNN-short-title.md`, with Context / Decision /
Consequences. Keep them short; link to [design notes](../design/) for mechanics.

## Records

- [0001](0001-multi-repo-split.md) - split the monorepo into the `muxlang` org.
- [0002](0002-independent-versioning.md) - version each repo independently.
- [0003](0003-verify-consumers-against-source.md) - verify consumers against sibling source in CI, not published pins.
- [0004](0004-runtime-resolved-from-source.md) - resolve `mux-runtime` from source as a git dependency; freeze crates.io. Supersedes 0002's release-time publish ordering.
- [0005](0005-test-corpus-and-examples-are-separate.md) - the compiler's test corpus and the published examples are separate artifacts; `test_scripts/` does not move.
- [0006](0006-typed-diagnostics.md) - compiler diagnostics use an explicit stable registry.

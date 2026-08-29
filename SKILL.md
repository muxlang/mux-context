---
name: mux
description: Orientation for the Mux programming language and the muxlang multi-repo ecosystem. Use when writing or debugging .mux code, working in any muxlang repo (mux-compiler, mux-runtime, mux-website, mux-syntax-highlighting, tree-sitter-mux, mux-website-api, mux-context), or when the user mentions Mux.
---

# Mux

Statically-typed, reference-counted language (Python readability, Go simplicity,
Rust safety) compiled to native code via LLVM. Compiler is Rust; runtime and
stdlib are plain Rust (no LLVM) linked over a C ABI. Generics monomorphize;
interfaces are static dispatch. No dynamic typing, implicit conversions, or
reflection.

## Map: where the truth lives

This is a graph for finding facts, not a place for them. Read the source, never
trust memory or anything copied here.

| To learn about | Read |
|---|---|
| Language behavior and syntax, by working example | `mux-compiler/test_scripts/*.mux` and `test_scripts/error_cases/` (programs that must be rejected) |
| Canonical keywords, operators, types | `mux-syntax-highlighting/shared/syntax-matrix.json` - everything syntax-related is generated from or kept consistent with it |
| Runtime and stdlib behavior | `mux-runtime/` (read its `AGENTS.md` first) and `mux-website/docs/stdlib/` |
| Language docs: reference, guide, tour, examples | `mux-website/docs/` (reference, language-guide, tour, examples) and the `mux-examples` repo |
| Compiler and runtime internals, design rationale | `mux-context/docs/design/` and `ARCHITECTURE.md` |
| Cross-repo process: release, governance, where to file | `mux-context/docs/release-process.md`, `docs/repo-governance.md`, and `llms.txt` |
| Per-repo workflow and hard-won facts | each repo's `AGENTS.md`, read it before working there |

## Read before you act

- Read the target repo's `AGENTS.md` first. `mux-compiler`'s owns the testing,
  runtime-linking (`MUX_RUNTIME_LIB`), and list-semantics facts.
- Branch via PR, no direct pushes to default. Use ASCII for source, config,
  workflow, policy, and commit-message text. User-facing docs and behavior
  fixtures may use Unicode when it is intentional and reviewed.
- A compiled Mux program may hang instead of crashing; wrap fresh runs in
  `timeout N ...`.

## Cross-repo rules

These are owned by no single repo, so they live here.

- **Syntax change fan-out, in order:** `mux-compiler`, then
  `mux-syntax-highlighting` canonical matrix (MERGE FIRST), then
  `tree-sitter-mux` (vendored matrix + grammar), then `mux-website` (Monaco,
  Shiki, and keyword lists). Consumers stay red until the canonical matrix
  merges; rerun after, nothing is broken.
- **Never poll or watch CI.** Do not run background loops, `gh run watch`,
  `gh pr checks --watch`, or anything that waits on a pipeline, unless asked.
  After pushing, report the link and what pass/fail would mean, then stop.
- **The repo-local "fail on new SonarQube issues" step is the only zero-new-issue
  enforcement; do not delete it as a duplicate of the app-posted SonarCloud
  check (Sonar's own gate has no new-issue condition).**
- **Never read `.env` files into context; `source .env` in the shell instead.**
- **Pre-existing bugs:** fix if directly related to your issue, otherwise file
  it as its own issue; never bundle an unrelated fix into the PR.

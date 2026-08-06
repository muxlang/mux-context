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
- Branch via PR, no direct pushes to default. ASCII only in files and commits.
- A compiled Mux program may hang instead of crashing; wrap fresh runs in
  `timeout N ...`.

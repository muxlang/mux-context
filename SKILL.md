---
name: mux
description: Orientation for the Mux programming language and the muxlang multi-repo ecosystem. Use when writing or debugging .mux code, working in any muxlang repo (mux-compiler, mux-runtime, mux-website, mux-syntax-highlighting, tree-sitter-mux, mux-website-api, mux-context), or when the user mentions Mux.
---

# Mux

Statically-typed, reference-counted language (Python readability, Go
simplicity, Rust safety) compiled to native code via LLVM. Compiler is Rust;
runtime + stdlib is plain Rust (no LLVM) linked over a C ABI. Generics
monomorphize; interfaces are static dispatch. No dynamic typing, implicit
conversions, or reflection.

## Where truth lives (read these, do not trust memory)

- Language behavior: the `mux-compiler` code and `test_scripts/*.mux`
  (syntax by example; `error_cases/` = programs that must fail).
- Cross-repo architecture, design docs, repo map, releases:
  `mux-context` - start at `llms.txt` and `ARCHITECTURE.md`.
- Canonical syntax spec: `mux-syntax-highlighting/shared/syntax-matrix.json`
  (keywords, operators, types). Everything else is generated or vendored
  from it.
- Per-repo workflows and hard-won facts: each repo's `AGENTS.md`. Read it
  before working in a repo; `mux-compiler`'s has the testing, runtime-linking
  (`MUX_RUNTIME_LIB`), and list-semantics facts.

## Language quick facts (verified against the spec and tests)

- 22 reserved keywords: `auto func returns return if else for while match
  const class interface enum import is as in break continue none common
  where`. `some/ok/err` are enum variant identifiers, NOT keywords;
  `optional result list map set tuple range` etc. are types.
- Type-first params: `func add(int a, int b) returns int { ... }`. Default
  args supported (`int times = 1`); lambdas (`func (int n) returns int
  { ... }`) do not support defaults. `common` = static method.
- Statements end at end-of-line; no semicolons. `auto` infers types.
- Enum payloads are bare or named: `Code(int)` / `Code(int value)`.
- `where { expr, ... }` attaches runtime constraints to functions, methods,
  lambdas, interface methods, enum variants, fields, and classes. Provable
  violations are compile errors (zero-false-positive rule; runtime panic is
  the fallback). See docs/language-guide/where-clauses.md on the website.
- Match must be exhaustive; a guarded arm (`X if cond`) counts as covering
  nothing.

## Cross-repo rules (owned by no single repo)

- Syntax changes fan out in order: (1) mux-compiler, (2)
  mux-syntax-highlighting canonical matrix + regenerate - MERGE FIRST, (3)
  tree-sitter-mux (vendored matrix + grammar + queries), (4) mux-website
  (Monaco, Shiki, and the keyword lists in docs/reference/lexical-structure.md
  and docs/language-guide/overview.md). Steps 3-4 CI-check against canonical
  MAIN, so they stay red until step 2 merges; rerun after, nothing is broken.
- ASCII only in code, comments, and commit messages. No direct pushes to
  default branches - always branch + PR. Before opening a PR, run the
  code-review skill (`/code-review`) on your working diff and fix what it finds,
  so the change is clean before Greptile and SonarCloud see it. Greptile reviews
  every PR; verify its "regression" claims against main before accepting them.
  SonarCloud fails PRs on any new issue; cognitive complexity <= 15 per function.
- Misbehaving compiled Mux programs (LLVM UB) hang instead of crashing:
  wrap every run of a freshly compiled program in `timeout N ...`.
- Never read `.env` files into context; `source .env` in the shell instead.
- Pre-existing bugs uncovered while fixing an issue: if a bug directly
  impacts or is closely related to the issue at hand, fix it as part of that
  work; if it is unrelated, file it as its own issue. Never silently leave an
  uncovered bug, and do not bundle an unrelated one into the PR.
- The compiler links a PREBUILT runtime and never builds one while compiling a
  program. It looks at `MUX_RUNTIME_LIB`, then a library beside the compiler
  binary (or in `../lib`), then the one in `target/` - which needs an explicit
  `cargo build -p mux-runtime`, because cargo emits a dependency's rlib and
  never its staticlib. A plain `cargo build` leaves programs failing to link
  with undefined `mux_*` symbols.
- `MUX_RUNTIME_LIB` wins over everything, so a leftover value (including one in
  a gitignored `.cargo/config.toml`) silently overrides the library you just
  built. Check it first when runtime behavior does not match the source.
- rc-leak-check: the feature sits outside mux-runtime's `full` set, so the
  default runtime never carries the exit-time assertion. `scripts/leak-check.sh`
  builds that runtime and FORCES it via `MUX_RUNTIME_LIB` - that force is the
  whole mechanism, and without it a leaking program silently exits 0.

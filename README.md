# Mux context

Cross-repo knowledge hub for the [Mux programming language](https://github.com/muxlang).
This repo is the one place that owns facts spanning more than one code repo:
how the repos fit together, the language's design rationale, a feature-to-module
map, shared terminology, and the release process.

It holds **no build-consumed artifacts** - things a build step reads (the
canonical syntax spec, generated grammars, rustdoc) stay in the repo whose
tooling needs them, and are linked from here. The rule: *if a build step reads
it, this repo does not own it.*

Agents: see [`llms.txt`](llms.txt) for a flat, link-per-line index of everything
here.

## Start here

- [Architecture](ARCHITECTURE.md) - the org/repo map and how the pieces connect.
- [Glossary](docs/glossary.md) - terminology used across the project.
- [Feature map](docs/features.md) - language/stdlib features to the modules that
  implement them.
- [Release process](docs/release-process.md) - how each repo is versioned and shipped.
- [Repo governance](docs/repo-governance.md) - labels, issue templates, and project board rules.
- [Design notes](docs/design/) - why the compiler and runtime work the way they do.
- [Decisions](docs/decisions/) - architecture decision records.

## Canonical facts

These are the source of truth other READMEs copy from.

- **Name:** Mux (fully "MuxLang").
- **Tagline:** The programming language for everyone.
- **One-liner:** Mux is a statically-typed, reference-counted language that
  combines Python's readability, Go's simplicity, and Rust's type safety,
  compiled to native code via LLVM.
- **Website & docs:** [mux-lang.dev](https://mux-lang.dev)
- **Install:** `curl -fsSL https://raw.githubusercontent.com/muxlang/mux-compiler/main/scripts/install.sh | sh`
- **License:** MIT.

## Filing issues

Not sure which repo a bug or idea belongs to? **Open it in this repo** - issues
filed here are triaged and moved to the right repo. If an issue is clearly scoped
to one repo (e.g. a compiler crash, a website typo), file it there directly.

## Repositories

| Repo | What it is |
|------|------------|
| [mux-compiler](https://github.com/muxlang/mux-compiler) | The compiler + CLI (lexer, parser, semantics, LLVM codegen). The canonical "Mux version". |
| [mux-runtime](https://github.com/muxlang/mux-runtime) | Runtime + standard library for compiled programs. Plain stable Rust, no LLVM. Published to crates.io. |
| [mux-website](https://github.com/muxlang/mux-website) | The documentation site (mux-lang.dev) + the docs AI assistant + indexing tools. |
| [mux-website-api](https://github.com/muxlang/mux-website-api) | The Fly.io compile/run API behind the playground. |
| [tree-sitter-mux](https://github.com/muxlang/tree-sitter-mux) | Tree-sitter grammar + highlight queries (Neovim, Helix, Emacs). |
| [mux-syntax-highlighting](https://github.com/muxlang/mux-syntax-highlighting) | TextMate grammar, VSCode extension, editor configs, and the canonical syntax spec. |
| [.github](https://github.com/muxlang/.github) | Org profile + shared community-health files (contributing, code of conduct, issue/PR templates). |

Mux is MIT-licensed and welcomes contributions.

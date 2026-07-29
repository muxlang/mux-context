# Architecture of the Mux org

How the repos connect and how a `.mux` file becomes a running program.

## The pipeline

```
            mux-compiler                         mux-runtime
   .mux ---> lexer -> parser -> semantics -> LLVM codegen -> .ll ---> clang ---+
                                                                               |
                                  links libmux_runtime.a (refcount, stdlib) ---+
                                                                               v
                                                                      native executable
```

The **compiler** (`mux-compiler`, Rust + LLVM) turns source into LLVM IR and
invokes `clang` to produce a native binary. That binary links the **runtime**
(`mux-runtime`, plain Rust, no LLVM) for reference counting, UTF-8 strings,
collections, conversions, and the standard library. The compiler does not import
the runtime as a Rust crate - it links a prebuilt static library, and never
builds one while compiling a program. That library is either bundled beside the
compiler in a release install, or built by cargo into `target/`; `MUX_RUNTIME_LIB`
overrides both. `mux-runtime` is a git dependency on its `main` branch, pinned to
one commit by `Cargo.lock`, so CI and release tags build the same source (see
decisions [0003](docs/decisions/0003-verify-consumers-against-source.md) and
[0004](docs/decisions/0004-runtime-resolved-from-source.md)). The crates.io
channel is frozen.

## Repo dependency graph

```
mux-compiler ----(links, git dep pinned by lock)----> mux-runtime
     ^                                                     ^
     | runs the released binary                            |
     |                                                (compiled programs)
mux-website-api
     ^
     | HTTP /api/compile
     |
mux-website (playground + docs)

mux-syntax-highlighting ----(canonical syntax-matrix.json)----> tree-sitter-mux (vendored copy)
                         \--(generates)--> TextMate grammar, VSCode extension
```

- **mux-compiler -> mux-runtime:** link-time dependency with an independent
  semver pin. `mux --version` reports both, e.g. `mux 0.5.1 (runtime 0.5.0)`.
- **mux-website-api -> mux-compiler:** runs a *released* `mux` binary (a
  deliberately pinned compiler version), not arbitrary `main`.
- **mux-website -> mux-website-api:** the in-browser playground POSTs source to
  `/api/compile` and renders the output.
- **mux-syntax-highlighting -> tree-sitter-mux:** the syntax spec
  (`syntax-matrix.json`) is *canonical* in `mux-syntax-highlighting`;
  `tree-sitter-mux` vendors a copy that `grammar.js` reads. Keep them in sync.

## Who owns what (canonical artifacts)

| Artifact | Canonical home | Consumed by |
|----------|----------------|-------------|
| Compiler / "Mux version" | `mux-compiler/Cargo.toml` (`CARGO_PKG_VERSION`) | everything that reports a version |
| Runtime + stdlib (C-ABI) | `mux-runtime/src` | compiler codegen (FFI), compiled programs |
| Syntax spec | `mux-syntax-highlighting/syntax-matrix.json` | tree-sitter-mux (vendored), TextMate/VSCode generation |
| Language reference (user docs) | `mux-website/docs` | mux-lang.dev |
| Org/cross-repo knowledge | this repo (`context`) | humans + agents |

## Three type representations

A value's type is represented three times as it moves through the compiler;
keeping them separate lets error reporting carry source locations while semantic
analysis stays LLVM-independent. See
[design/value-representation.md](docs/design/value-representation.md).

| Representation | Stage | Purpose |
|----------------|-------|---------|
| `TypeNode` | AST | source locations, syntax-level types |
| `Type` | semantic analysis | resolution, inference, checking |
| `BasicTypeEnum` | codegen | LLVM IR generation |

## Key invariants

- All generics monomorphize at compile time; interfaces use static dispatch (no
  vtables at runtime).
- All primitive values are boxed into `*mut Value` pointers at the runtime
  boundary; memory is reference-counted (no GC, no manual `free`).
- No dynamic typing, no implicit conversions, no runtime reflection.

See [docs/design/](docs/design/) for the rationale behind each of these.

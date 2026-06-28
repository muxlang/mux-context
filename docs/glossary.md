# Glossary

Terminology used across the Mux repos. Language-feature definitions for users
live in the [docs](https://mux-lang.dev); this is the cross-repo/internal vocabulary.

- **Boxing** - wrapping a primitive into a `*mut Value` at the runtime boundary so
  collections and generic code can handle it uniformly. See
  [design/value-representation.md](design/value-representation.md).
- **C-ABI / FFI surface** - the `extern "C"` functions the runtime exposes
  (`mux_*`) that compiler-generated code calls.
- **Codegen** - the compiler stage that emits LLVM IR (`mux-compiler/src/codegen`).
- **`common`** - the keyword for static (class-level) methods, called on the class
  rather than an instance. Distinct from `const` (immutable values).
- **Golden-file / snapshot test** - the compiler's primary test style: run a stage
  over a `.mux` corpus and assert the output matches a stored snapshot (insta).
- **`is` clause** - how a class declares interface conformance (`class C is Drawable`).
- **Monomorphization** - generating a specialized copy of a generic per concrete
  type at compile time. See [design/monomorphization.md](design/monomorphization.md).
- **`mux-runtime`** - the link-time runtime + stdlib; plain Rust, no LLVM.
- **`Mux version`** - the `mux-compiler` package version (`CARGO_PKG_VERSION`);
  the runtime is versioned independently.
- **ObjectRef** - the runtime representation of a class instance (shared ownership
  + `TypeId`). See [design/object-system.md](design/object-system.md).
- **Reference counting** - Mux's deterministic memory management; every heap value
  has a `RefHeader`. No GC, no manual free. See [design/memory.md](design/memory.md).
- **Static dispatch** - interface methods resolve at compile time (no runtime
  vtable lookup). The reason interfaces can't be added to foreign types.
- **`syntax-matrix.json`** - the canonical syntax spec, owned by
  `mux-syntax-highlighting` and vendored into `tree-sitter-mux`.
- **`TypeNode` / `Type` / `BasicTypeEnum`** - the AST / semantic / LLVM
  representations of a type, respectively.
- **`Value`** - the single runtime enum that represents every Mux value.

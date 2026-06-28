# Feature map

Where each language feature and standard-library module is implemented. Paths are
relative to the owning repo. User-facing docs for these live at
[mux-lang.dev](https://mux-lang.dev); this maps features to code.

## Compiler (`mux-compiler/src`)

| Feature | Primary modules |
|---------|-----------------|
| Tokenizing | `lexer/` (`mod.rs`, `token.rs`, `span.rs`) |
| Parsing / AST | `parser/`, `ast/` (`nodes.rs`, `types.rs`, `patterns.rs`, `operators.rs`, `literals.rs`) |
| Type checking, inference, symbol resolution | `semantics/` (`declarations.rs`, `expressions.rs`, `imports.rs`, `free_vars.rs`, `format.rs`) |
| LLVM IR generation | `codegen/` (`expressions.rs`, `statements.rs`, `functions.rs`, `methods.rs`, `classes.rs`, `constructors.rs`, `operators.rs`, `generics.rs`, `types.rs`) |
| Reference-count cleanup (scope stack) | `codegen/memory.rs` |
| Runtime FFI call generation | `codegen/runtime.rs` |
| Generics / monomorphization | `codegen/generics.rs` (see [design/monomorphization.md](design/monomorphization.md)) |
| Static interface dispatch | `codegen/classes.rs`, `codegen/methods.rs` (see [design/object-system.md](design/object-system.md)) |
| Module/import resolution | `module_resolver.rs` (see [design/modules.md](design/modules.md)) |
| Diagnostics / error rendering | `diagnostic/` (`emitter.rs`, `files.rs`, `styles.rs`) |

## Runtime + stdlib (`mux-runtime/src`)

| Feature | Module |
|---------|--------|
| Core value enum, ordering, hashing, display | `lib.rs` |
| Reference counting | `refcount.rs` (see [design/memory.md](design/memory.md)) |
| Object system | `object.rs` |
| Primitives + conversions | `int.rs`, `float.rs`, `bool.rs`, `string.rs`, `tuple.rs`, `boxing.rs` |
| Collections | `list.rs`, `map.rs`, `set.rs` (see [design/collections.md](design/collections.md)) |
| optional / result | `optional.rs`, `result.rs` (see [design/error-handling.md](design/error-handling.md)) |
| `std.assert` | `assert.rs` |
| `std.math` | `math.rs` |
| `std.io` (files, paths, stdin) | `io.rs` |
| `std.random` | `random.rs` |
| `std.datetime` | `datetime.rs` |
| `std.sync` (threads, mutex, rwlock, condvar) | `sync.rs` (feature `sync`) |
| `std.net` (TCP/UDP, HTTP) | `net.rs` (feature `net`) |
| `std.env` | `std.rs` |
| `std.data.json` | `json.rs` (feature `json`) |
| `std.data.csv` | `data.rs` (feature `csv`) |
| `std.sql` (SQLite/Postgres/MySQL) | `sql.rs` (feature `sql`) |

Runtime features: `default = ["full"]`; optional `json`, `csv`, `net`, `sql`,
`sync`. The compiler enables only the features a program imports.

## Editor / tooling

| Feature | Repo |
|---------|------|
| Canonical syntax spec | `mux-syntax-highlighting/syntax-matrix.json` |
| Tree-sitter grammar + highlight queries | `tree-sitter-mux` (`grammar.js`, `queries/`) |
| TextMate grammar + VSCode extension | `mux-syntax-highlighting` |
| Playground compile/run API | `mux-website-api` (`server.py`) |
| Docs site + AI assistant | `mux-website` |

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
| Opt-in Mux source coverage and LCOV merging | `main.rs`, `codegen/statements.rs` |
| Diagnostics / error rendering | `diagnostic/` (`catalog.rs`, `emitter.rs`, `files.rs`, `styles.rs`); cross-repo contract in [design/diagnostics.md](design/diagnostics.md) |

## Runtime + stdlib (`mux-runtime/src`)

| Feature | Module |
|---------|--------|
| Core value enum, ordering, hashing, display | `lib.rs` |
| Reference counting | `refcount.rs` (see [design/memory.md](design/memory.md)) |
| Object system | `object.rs` |
| Primitives + conversions | `int.rs`, `float.rs`, `bool.rs`, `byte.rs`, `bytes.rs`, `string.rs`, `tuple.rs`, `boxing.rs` |
| Collections | `list.rs`, `map.rs`, `set.rs` (see [design/collections.md](design/collections.md)) |
| optional / result | `optional.rs`, `result.rs` (see [design/error-handling.md](design/error-handling.md)) |
| Runtime panics (div/mod-by-zero, index/key errors) | `panic.rs` (see [design/panics.md](design/panics.md)) |
| Built-in `assert(bool, string)` | `assert.rs` (failures route through the shared panic path) |
| `std.math` | `math.rs` |
| `std.io` (byte streams, stdin/stdout/stderr, owned erased streams) | `io.rs`, `stream.rs` |
| `std.fs` (files, paths, directories, metadata) | `io.rs`, `path.rs` |
| `std.random` | `random.rs` |
| `std.datetime` (calendar, clocks, durations, time zones) | `datetime.rs`, `datetime_types.rs` |
| `std.sync` (threads, mutex, rwlock, condvar, channels, pools) | `sync.rs`, `sync_primitives.rs` (feature `sync`) |
| `std.net` (TCP, UDP, readiness, HTTP, CORS/static policy, SSE streams, WebSocket sessions) | `net.rs`, `net_types.rs`, `poller.rs` (feature `net`) |
| `std.net.url` | `url.rs` (feature `url`) |
| `std.net.tls` | `tls.rs` (feature `tls`) |
| `std.env` | `std.rs` |
| `std.process` | `process.rs` |
| `std.log` | `log.rs` |
| `std.regex` | `regex.rs` (feature `regex`) |
| `std.uuid` | `uuid.rs` (feature `uuid`) |
| `std.crypto` | `crypto.rs` (feature `crypto`) |
| `std.cli` | `cli.rs` |
| `std.data.json` | `json.rs` (feature `json`) |
| `std.data.csv` | `data.rs` (feature `csv`) |
| `std.sql` (leased result sets for SQLite/Postgres/MySQL/SQL Server) | `sql.rs` (feature `sql`) |

The compiler's canonical module registry is
`mux-compiler/mux-compiler/src/semantics/std_registry.rs`; it lists the nested
paths (`std.net.http`, `std.net.websocket`, `std.data.json`, and
`std.data.csv`) that are exposed through the parent runtime modules above.

## Embedded stdlib (`mux-compiler`)

These modules are Mux source embedded into the compiler at build time. Their
source files, rather than the runtime feature flags, define their behavior:

| Module | Source |
|--------|--------|
| `std.encoding` | `mux-compiler/std/encoding.mux` |
| `std.dsa` and its child modules | `mux-compiler/std/dsa/*.mux` |

Runtime features: `default = ["full"]`; optional `json`, `csv`, `net`, `http2`,
`http3`, `tls`, `url`, `regex`, `uuid`, `crypto`, `sql`, `sync`, and `chrono-tz`.
The compiler links the full runtime. Static linking discards unused archive
members; imports do not select Cargo features.

## Editor / tooling

| Feature | Repo |
|---------|------|
| Canonical syntax spec | `mux-syntax-highlighting/shared/syntax-matrix.json` |
| Tree-sitter grammar + highlight queries | `tree-sitter-mux` (`grammar.js`, `queries/`) |
| TextMate grammar + VSCode extension | `mux-syntax-highlighting` |
| Playground compile/run API | `mux-website-api` (`server.py`) |
| Docs site + AI assistant | `mux-website` |

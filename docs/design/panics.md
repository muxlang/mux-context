# Runtime panics: process-terminating failures

Some failures are not recoverable values but bugs: dividing by zero, indexing
past the end of a list, a failed assertion. Mux does not model these as
`result`/`optional` (see [error-handling.md](error-handling.md)); it *panics* -
prints a diagnostic and terminates the process. Every such failure goes through
one runtime path so the format and exit behavior are identical everywhere.

## Format

A panic writes to **stderr** and exits with status **1**:

```
panic: <message>
--> <file>:<line>:<col>
```

The `--> file:line:col` locator mirrors the compiler's own diagnostics and is
present whenever codegen knows the source location. Dynamic detail is folded into
the message rather than shown as a separate note:

```
panic: division by zero
--> math.mux:4:16

panic: list index out of bounds: index 5, length 3
--> main.mux:9:14

panic: key not found in map: key bob
--> lookup.mux:12:12

panic: assertion failed: expected 2, got 1
```

## What panics

- **Integer `/` and `%` by zero.** Float division follows IEEE 754 (`inf`/`nan`)
  and does not panic.
- **List index out of bounds** - reports the offending index (the one the user
  wrote, before negative-index normalization) and the list length.
- **Map key not found** - reports the key.
- **`std.assert` failures** - route through the same path.

Panics are not catchable; there is no try/catch. Recoverable conditions should
use `result`/`optional` and be handled with `match` - "prefer `result` over
panicking".

## Why this design

- **One path.** A single runtime primitive renders every panic, so the message
  format, stderr, and exit code never drift between failure kinds. (Historically
  these were inconsistent: container errors printed to stdout and exited 1,
  asserts aborted with SIGABRT/exit 134, and integer division by zero was an
  unguarded hardware trap.)
- **Reads like a compile error, but is distinct.** The `--> file:line:col`
  locator matches the diagnostic emitter, while the `panic:` prefix keeps a
  runtime failure visually distinguishable from a compile-time `error:`.
- **No source snippet is baked into the binary.** Rendering the offending line
  with a caret (as compile errors do) would embed a string constant at every
  panic site - and division, indexing, and map access are common operations, so
  that cost is paid broadly. The exact panic output is instead verified from the
  compiler side by the `executable_integration` snapshots. A richer runtime story
  (an opt-in backtrace, e.g. `MUX_BACKTRACE`) is the higher-leverage follow-up and
  is deliberately deferred.

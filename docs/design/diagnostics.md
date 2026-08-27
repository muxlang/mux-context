# Diagnostics

The compiler owns the diagnostic registry because the compiler emits and
builds against it. The website mirrors the public reference. The context repo
owns this cross-repository contract.

Mux has two severities: `error` and `warning`. Notes, labels, help, and fix-its
are metadata attached to one of those severities. Runtime panics remain a
separate process-terminating channel.

Codes use four digits and are never reused:

- `E01xx` covers lexing.
- `E02xx` covers parsing and recovery.
- `E03xx` covers semantic analysis.
- `E04xx` covers module loading.
- `E09xx` covers compiler failures.
- `W03xx` covers proven semantic warnings.

The registry in `mux-compiler` is the build-time mirror of this policy. A
change that adds a code must update the website reference, a source example,
the compiler inventory tests, and the retrieval error corpus when the code is
user-facing. The website and compiler versions are released together when a
new public code is introduced.

## Recovery

The parser retains the recoverable AST prefix and reports independent errors
where it can. One compilation reports at most 100 diagnostics and then emits
an explicit truncation note. Code generation is forbidden when syntax errors
remain.

## Fix-it safety

An edit is machine-applicable only when the compiler can prove that it
preserves meaning. Edits carry a file, byte range, replacement, and
applicability. The compiler rejects overlapping edits and edits touching
recovered source. It applies edits in memory, reparses and reanalyzes all
affected modules, then commits all files atomically. Failed validation leaves
the source untouched.

The user-facing command is `mux fix FILE`. It previews with `--dry-run` and
offers `--format json` for tooling. It follows symlinks to local source files,
does not edit embedded standard-library sources, and performs one validation
pass before any write. If no producer has supplied a proven edit, it exits
without changing the workspace. Prose help and applicability classifications
such as `MaybeIncorrect` are not converted into automatic edits.

## Ownership and compatibility

The compiler and runtime may both mention diagnostic codes, but the runtime
does not emit compiler diagnostics. Runtime panic names and messages are
maintained separately. Code numbers are stable across patch releases and are
never assigned to a different diagnostic. English detail text may change
without changing a code.

`mux explain CODE` reads the compiler's embedded registry and therefore works
offline. The website indexer extracts codes into vector metadata so an error
question can retrieve the matching reference section.

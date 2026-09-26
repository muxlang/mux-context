# Formatter

Status: implementation contract for the frontend rewrite. This document does
not imply that the formatter has shipped.

Mux formatting uses the compiler's shared syntax frontend. Formatting requires
valid syntax but does not require imports to resolve, types to check, or LLVM
to run. Lexical or syntax errors prevent rewriting a file.

## Defaults

Use four spaces for indentation and an 80-column target. Expose these values
as formatter options so a future configuration loader can supply them. The
initial implementation does not define or read a configuration file.

Keep original literal spellings, declaration order, import order, and comment
contents. Comments remain associated with their surrounding syntax. In
particular, `// mux:test` annotations stay immediately above their test.
Comment text and literal contents can exceed the width target.

Use spaces around binary operators, after commas, and between a control-flow
keyword and its condition. Unary operators, member access, and generic type
arguments follow their grammatical roles. Use LF for generated line breaks,
one final newline for nonempty output, no trailing spaces outside preserved
literal/comment contents, and at most one blank line between constructs.

Line wrapping may only introduce newlines where the grammar permits them.
Parenthesized calls and bracketed collections can wrap at element boundaries.
An unbreakable expression may exceed the width target. Whitespace outside
literals and comments may change. Literal spellings and comment contents stay
byte-for-byte identical. Formatted output must parse to the same program
structure.

```mux
func add(int left, int right) returns int {
    return left + right
}
```

## Command behavior

`mux format` recursively discovers `.mux` files under the current directory.
Explicit files and directories are supported. Directory discovery skips
`.git`, `target`, and `node_modules`, and does not follow discovered symlinks.
Explicit paths must identify supported files or directories. File ordering
is deterministic and repeated paths do not cause repeated writes.

`mux format --check` and `mux format -c` compare the formatter's output with
the original source and never write. Normal mode uses that same output and
only replaces changed files.

Read and format all selected files before writing any of them. Replace files
atomically one at a time, preserve permissions, and reject stale source if a
file changes after it was read. An I/O failure during replacement may leave
earlier files formatted; there is no transaction across the whole selection.

Exit codes are 0 for successful formatting or a clean check, 1 when a check
finds differences, and 2 for invalid input, parsing failures, or I/O failures.
An empty discovered directory is a successful no-op.

## Required evidence

Exercise ordinary and malformed syntax, Unicode, CRLF, comments inside and
between expressions, generic arguments, grouping parentheses, multiline
literals, and test annotations. Formatting must preserve program structure
and be idempotent across the compiler's valid source corpus.

Check mode must preserve file contents and metadata. File-operation tests
cover duplicate inputs, invalid paths, recursion, symlinks, permissions,
changes between reading and writing, and failure before any write.

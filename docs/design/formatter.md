# Formatter

The compiler formatter uses the shared syntax frontend and requires valid Mux
syntax. It does not require imports to resolve, types to check, or LLVM to run.
Lexical or syntax errors prevent rewriting a file.

## Configuration and style

The CLI reads `mux-project.json` from its working directory or nearest parent,
up to the nearest Git worktree root. A single invocation uses one config for
all selected paths. Library path formatting remains config-free. See the [compiler formatter documentation](https://github.com/muxlang/mux-compiler/blob/main/docs/formatter.md) and [config loader](https://github.com/muxlang/mux-compiler/blob/main/mux-compiler/src/format_config.rs) for the implementation.

The config has a `format` object. Its defaults are four spaces, an 80-column
target, same-line block braces, `where` clauses on their own line, one blank
line between top-level declarations, no blank line between ordinary members,
one blank line before function members, and trailing commas on multiline
lists, maps, and match arms. Tabs default to one tab per indentation level.
Blank-line counts accept nonnegative integers. Invalid JSON uses all defaults;
invalid fields use their own defaults and produce stderr warnings.

The formatter keeps original literal spellings, declaration order, import
order, and comment contents. Comments remain associated with their surrounding
syntax. In particular, `// mux:test` annotations stay immediately above their
test. Comment text and literal contents can exceed the width target.

Binary expressions may continue after an operator, never before one. The
formatter may use these breaks when wrapping long expressions. Assignment
operators do not permit a line break before the right-hand side. Other layout
breaks are selected from grammar-safe positions; expressions without a safe
break may exceed the target. Formatted output must parse to the same program
structure, except for permitted trailing-comma policy changes.

Use spaces around binary operators, after commas, and between a control-flow
keyword and its condition. Unary operators, member access, and generic type
arguments follow their grammatical roles. Generated structural line breaks
use LF. Literal spellings and comment contents stay byte-for-byte identical.

For example, with `"line_width": 40`, a long expression wraps after a binary
operator:

```mux
func total(int first, int second, int third) returns int {
    return first + second + third
}
```

becomes:

```mux
func total(int first, int second, int third) returns int {
    return first + second +
        third
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

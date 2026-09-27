# Frontend rewrite and formatter plan

Status: implementation in progress. The architecture below is a target,
not a description of the released compiler.

## Purpose and scope

Give the compiler and formatter one frontend that preserves source text,
provides reliable locations, and keeps grammar rules in one place. Complete
the migration by deleting superseded code and temporary adapters.

The work covers source storage, lexing, token traversal, parsing, syntax trees,
conversion to the compiler AST, diagnostics integration, test discovery, and
formatting. Semantic analysis, LLVM generation, and the runtime retain their
existing responsibilities. Fix pre-existing defects encountered during the
work with focused regressions; this plan does not promise to eliminate all
compiler debt.

Implementation belongs in mux-compiler. This document owns the design and
migration contract. User documentation belongs in mux-website when the
corresponding behavior is available.

## Evidence to carry into the rewrite

The source review found these constraints in the existing implementation:

- Tokens use display columns and optional end coordinates. Source-editing
  consumers reconstruct byte offsets with different Unicode assumptions.
- Lexing discards whitespace and continuation newlines and trims comments.
- Slash/comment handling has overlapping implementations with different
  behavior. Reproduce the reachable behavior before consolidating it.
- The parser filters comments and builds an AST that omits punctuation and
  grouping parentheses and separates class fields from methods.
- Cursor advancement and rewinding occur throughout grammar routines.
- The CLI scans tokens separately to extract test blocks.

These observations justify replacing the source representation and parser
output. They do not establish that every existing grammar routine is wrong.
Preserve useful grammar logic and establish executable regressions for
suspected defects before changing behavior.

## Target architecture

```text
UTF-8 source + file identity + line index
  -> lossless lexer
  -> parser cursor + shared grammar
  -> lossless syntax tree + diagnostics
       -> formatter -> proposed source text
       -> AST conversion -> semantic analysis -> code generation
       -> test discovery and source tooling
```

Source locations use half-open byte ranges, including explicit zero-width
locations for missing syntax and EOF. Line numbers and display columns are
computed at the diagnostic presentation boundary. Source slices are always
valid UTF-8 boundaries.

The lexer emits token kinds and ranges covering every input byte, including
spaces, comments, line endings, and invalid text. Literal spelling remains
available from the source. Literal decoding and validation have one shared
implementation; their exact placement must preserve lexical diagnostics.

The parser cursor hides irrelevant whitespace from grammar routines while
keeping it in the syntax output. Statement-ending and continuation newline
rules are explicit and preserve current language behavior, including lambdas
inside calls. The scanner no longer destroys information based on nesting.

Grammar routines record syntax nodes and token consumption through one
cursor/event interface. Checkpoints restore consumption, emitted events, and
speculative diagnostics together. Recovery retains skipped text in error
nodes, always makes progress, and respects the diagnostic limit.

The syntax tree preserves punctuation, parentheses, member order, comments,
and whitespace. Typed accessors provide structured traversal. AST conversion
then produces the representation semantic analysis expects. The formatter
and test discovery consume the syntax tree directly.

Start with a simple immutable tree suitable for batch parsing. Choose its
storage implementation after the first representative prototype. A dependency
needs a concrete benefit; incremental reparsing and editor infrastructure are
outside the initial requirements.

## Delivery sequence

Each stage should be reviewable and leave the compiler usable. Temporary
migration code must have a named deletion stage.

### 1. Establish the behavior contract

Inventory lexer/parser entry points and consumers, including imports,
diagnostics, fix-its, test discovery, snapshots, and embedded sources. Record
the current valid-program ASTs, rejection cases, diagnostic codes, and newline
behavior. Measure frontend time and peak memory on a fixed representative
corpus using the existing benchmark infrastructure where applicable.

Add focused regressions for Unicode positions, comments, literal spelling,
EOF, malformed input, class-member order, and nested continuation contexts.
Separate intended behavior from confirmed bugs; fixtures must not silently
turn accidental behavior into language policy.

Exit condition: a consumer inventory, reproducible baseline, and explicit
regressions for the defects being corrected.

### 2. Replace source locations and consolidate lexing

Introduce shared source storage, a line index, and authoritative byte ranges.
Implement lossless tokenization by consolidating the existing recognition
logic. Preserve raw literals and comments. Establish one EOF representation
and retain invalid text with diagnostics. Use a temporary adapter if needed
to keep the current parser working during migration.

Exit condition: concatenating token slices reproduces every input exactly;
ranges are ordered, contiguous, and valid; lexical errors retain their
documented codes. Cover Unicode, CRLF, empty files, and unterminated tokens.

### 3. Establish the parser and syntax-tree boundary

Centralize consumption, lookahead, checkpoints, newline handling, and
recovery. Prototype syntax events and tree construction on declarations,
binary expressions, parenthesized expressions, and a lambda inside a call.
Keep grammar routines independent of tree storage details.

Exit condition: the prototype preserves comments and punctuation, rewinds
without leaving events or diagnostics behind, and preserves significant
newlines. Select tree storage using complexity and measured cost.

### 4. Migrate the grammar and AST conversion

Move expressions/types, statements/blocks, and declarations/members into
focused modules as their productions migrate. Reuse the existing precedence
and grammar rules. Produce syntax first and convert it to the compiler AST.
Preserve source associations through conversion for semantic diagnostics.

During migration, compare old and new frontends on the same corpus. Compare
AST structure without presentation locations, then validate locations and
diagnostics separately. Every discrepancy needs an explanation or a fix.
Retain malformed input in the syntax tree while blocking compilation on errors.

Exit condition: all supported syntax uses the new frontend, existing valid
programs have equivalent ASTs and execution results, and diagnostic changes
are deliberate. Repeat the baseline measurements and investigate regressions.

### 5. Switch consumers and remove the old frontend

Route compilation, import parsing, fix validation, and test discovery through
the shared parsing API. Test discovery reads test declarations and their
annotations from syntax, replacing its independent token scan. Replace all
display-column-to-byte reconstruction with source ranges.

Delete the old scanner/parser paths, temporary adapters, differential test
frontend, and duplicated helpers after migration checks pass. Keep the useful
regression fixtures. Document module ownership and public entry points.

Exit condition: one compiler grammar, one source-location model, no legacy
frontend selection, and all consumers migrated. The existing Tree-sitter
editor grammar retains its separate role and syntax-parity checks.

### 6. Specify and implement formatting

Write the formatting contract in a separate context design document before
the printer implementation. Resolve indentation, line width, wrapping,
blank lines, trailing commas, newline policy, and comment indentation with
before/after examples. Start by preserving literal spellings and comment
contents. Preserve the placement of test annotations and other meaningful
comments relative to the syntax they describe.

Build a pure source-to-formatted-text API using syntax structure and a small
layout representation for indentation and optional line breaks. Reject
lexically or syntactically invalid files with diagnostics. Formatting must
work without resolving imports, type checking, or invoking LLVM.

Wire normal formatting and --check/-c to this same API. No paths means .;
explicit files and directories are supported. Directory discovery is recursive
and deterministic. Before enabling writes, specify exclusions, symlink handling
and cycle prevention, duplicate paths, missing paths, non-Mux files, and empty
matches. The existing discovery scaffold is not the completed policy.

Implemented formatter exit codes: 0 for success or an already formatted check, 1 for a
check that finds differences, and 2 for input, parse, or I/O errors. Check mode
never writes. Stage all formatting results before writes so parse failures do
not cause partial formatting. Replace each changed file atomically, preserve
permissions, and detect changes since reading it. Report I/O failures clearly;
per-file atomic replacement is not a transaction across multiple files.

Exit condition: formatting is idempotent, output parses to equivalent program
structure, comments and literal contents survive, check mode reports actual
differences without writes, and file-operation failures have focused coverage.

### 7. Finish documentation and release integration

Publish the implemented formatter and CLI behavior on the website. Update the
context architecture and feature map, compiler help, README, and changelog.
Remove outdated formatter limitations only after the implementation ships.
Follow the repository release process and retain syntax-consumer parity.

Exit condition: documentation distinguishes shipped behavior from proposals,
the release describes behavior corrections, and no migration scaffolding remains.

## Validation and completion

Use focused tests during each stage, then run the compiler repository's
required formatting, lint, rustdoc, fixture, executable, and generated-program
checks before landing frontend changes. Regenerate snapshots through the
documented workflow and review differences; do not hand-edit them or accept
wholesale changes without explanation. Syntax and diagnostics changes follow
the existing cross-repository contracts.

Exercise arbitrary UTF-8 and malformed input for token coverage, tree source
reconstruction, parser termination, and bounded diagnostics. Round-trip
reconstruction alone does not establish correct grammar or formatting; retain
AST equivalence and execution checks as independent evidence.

The rewrite is complete when the new frontend serves every compiler consumer,
the old implementation and adapters are gone, the formatter meets its contract,
and performance results have been compared with the baseline. New abstractions
must have a current consumer and a clear owner.

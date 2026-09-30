# Implementation plan for issue 16: LSP support

Plan and implementation status, researched 2026-09-28 and updated
2026-09-29. Issue: [#16](https://github.com/muxlang/mux-context/issues/16).
Companion: [editor distribution plan](issue-22-editor-distribution.md).

## Local implementation status

The implementation merged in
[mux-compiler PR #462](https://github.com/muxlang/mux-compiler/pull/462) as
`4807f48`. Release metadata is prepared in
[mux-compiler PR #463](https://github.com/muxlang/mux-compiler/pull/463); its
required checks are still running.
The merged implementation includes fixes for validating edits near existing
errors, standard-library completions, recovery scopes, editor-only semantic
references, poisoned lock handling, and protocol-loop structure. It also
identifies diagnostics by source span when validating fixes, accounts for
offset shifts caused by edits before existing errors, and returns a JSON-RPC
method-not-found response for an unexpected worker request.
It includes the stdio server, snapshot analysis API, open-buffer overlays,
UTF-16 positions, diagnostics, formatting, safe code actions, symbols,
definitions, hover, signature help, and completion for visible names, explicit
and wildcard imports, module aliases, class members, and built-in methods.
Buffer changes with stale or repeated versions are ignored. Untitled buffers
are analyzed as standalone documents and retain their `untitled:` URI in
diagnostics and definitions.
Workspace-folder initialization and change notifications are supported; an
untitled buffer uses project formatting settings when exactly one workspace is
open.
Completion shares one semantic snapshot across import and member candidates.
Queued diagnostic work coalesces edit bursts into one latest-source snapshot.
Clients that support dynamic file watching receive a registration for `*.mux`
creation, change, and deletion; each event invalidates in-flight results and
rechecks open documents against the current disk imports. A process test covers
creating and deleting a previously missing imported module.
The all-feature compiler tests pass with `MUX_RUNTIME_LIB` pointing to the
archive in the custom `dev-cargo` target directory, as do strict Clippy,
formatting, and strict rustdoc. The packaged Linux install smoke completes
LSP initialization, checks sync and hover capabilities, shuts down cleanly,
and runs without `MUX_RUNTIME_LIB`. Website setup and compiled documentation
examples also pass. A debug-build LSP smoke
measurement reached diagnostics for a generated 48 KB module with 1,000
functions in 61 ms on this machine; this is an initial baseline, not a
cross-platform release benchmark. A release-server pass over 193 top-level
`test_scripts/*.mux` programs measured 10.39 ms median, 20.90 ms p95, and
182.12 ms maximum from open to diagnostics on this machine. This pass also
excluded `MUX_RUNTIME_LIB`; it is a local baseline, not a cross-platform
benchmark.

Diagnostics and LSP requests use one serial
worker while the protocol loop continues to read messages. Queued diagnostics
from superseded snapshots are skipped, and completed stale results are
discarded. Cancellation responds immediately and skips queued requests, but it
cannot interrupt a compiler pass already in progress. Generic-bound member
methods and built-in bound methods are included in completion; substitutions
for generic method signatures are not yet reflected. The Linux release package
smoke and 12-seed generated-program campaign pass, including normal
compiled-program execution. Release LSP smokes cover `mux lsp` startup,
diagnostics, workspace-folder changes, untitled formatting, generic-bound
completion, and watched-import refresh without `MUX_RUNTIME_LIB`.
Post-release installer verification and a larger external project corpus remain.
The packaged-install CI matrix now checks LSP initialize/shutdown and
advertised capabilities without `MUX_RUNTIME_LIB` on Linux, macOS, and Windows.
All checks, including all three package targets, Windows packaging, strict
Rustdoc, SonarQube, and Greptile review, passed before PR #462 merged. Release
metadata is under review in PR #463. The release tag and post-release installer
verification remain pending.

Ship a `mux lsp` command in the existing compiler release. The normal Mux
installer will then install the compiler, formatter, fix tooling, and language
server together. Keep the server in `mux-compiler` so semantic behavior and
editor behavior change in the same PR and release. Keep the VSCode client in
the one maintained extension in `mux-syntax-highlighting`.

The proposed first complete release includes live diagnostics, formatting,
safe quick fixes, hover, go-to-definition, document symbols, scoped completion,
and signature help. Deliver diagnostics and formatting as an earlier milestone.
Workspace references, rename, semantic tokens, inlay hints, and debugging are
follow-ups. Publishing highlighting under #22 does not depend on this work.

## What the code already provides

Research used compiler checkout `5aea4b9` and context checkout `52f973d`.
Paths below are relative to `mux-compiler/mux-compiler/`.

| Existing code | Implication for implementation |
| --- | --- |
| `src/syntax/mod.rs` | Reuse the lossless syntax tree, byte ranges, and recovered lowering. Do not build another parser for editors. |
| `src/main.rs`, especially `parse_fix_source` and `analyze_fix_source` | Parsing, recovery filtering, and semantic orchestration already exist, but are coupled to CLI operations. Extract the reusable parts. |
| `src/module_resolver.rs` | Source overrides exist for fix validation, but disk canonicalization precedes override lookup and parsed modules are cached. Unsaved new files and repeated edits need explicit treatment. |
| `src/diagnostic/files.rs` | `Files::add` returns the existing ID without replacing its source. Reusing this registry across edits would analyze stale text. |
| `src/source.rs` and `src/lexer/span.rs` | Spans use byte offsets. `line_col` reports terminal display columns, which cannot be used as LSP character offsets. |
| `src/semantics/symbol_table.rs` | The flat `all_symbols` map is name-keyed and also supports codegen. It cannot answer scope-sensitive editor queries reliably. |
| `src/formatter/mod.rs` and `src/format_config.rs` | Formatting accepts source strings, but configuration lookup is CLI-local and starts at process cwd. |

## Implementation sequence

1. Extract a compiler analysis API.

   Add a focused library module such as `src/analysis/mod.rs`. Accept an entry
   path and an immutable source snapshot containing all open-file overlays.
   Return syntax, structured diagnostics, source identities, and semantic
   results without emitting output, writing files, invoking codegen, or linking.
   Preserve distinct policies for compilation, recovered editor analysis, and
   fix validation. Move shared recovery filtering and span-edit materialization
   out of `main.rs`; have the CLI call the same underlying helpers.

   Initially construct fresh `Files`, resolver, and analyzer state per analysis
   snapshot. This avoids stale caches without prematurely adding an incremental
   query engine. Keep document identity outside snapshot-local `FileId` values.
   Regression-test CLI diagnostics and fix behavior before building the server.

2. Make source access work for editor buffers.

   Give module resolution one source-loading boundary for open buffers, disk
   files, and embedded stdlib sources. Consult overlays before requiring a file
   to exist on disk. Preserve existing relative-import and module-name rules.
   Normalize absolute paths consistently, account for existing symlinks, and
   support a new unsaved file at a real file URI. Treat untitled documents as
   standalone buffers until they acquire a filesystem location.

   Track import dependencies and reverse dependencies. Reanalyze affected open
   entry files when an import changes, closes, is deleted, or is renamed. On
   close, drop the overlay and return to disk contents. Deduplicate diagnostics
   when several entry files import the same module and clear obsolete results.
   Use workspace folders and the nearest `mux-project.json`/Git root for project
   context; keep import resolution based on the importing file, not server cwd.

3. Add the stdio server and document lifecycle.

   Add `Commands::Lsp` and a `src/lsp/` module. Use typed protocol definitions
   and an existing transport library; evaluate `lsp-server` plus `lsp-types`
   against the repository's Rust version before locking dependencies. Its
   synchronous dispatch model fits the current analyzer better than an async
   runtime. Keep LSP types out of compiler analysis.

   Implement initialization, capability negotiation, shutdown/exit, open/change/
   save/close, cancellation, and workspace file notifications. Start with full
   document synchronization. Keep transport responsive while one analysis
   worker owns the analyzer's `Rc<RefCell<_>>` state; pass owned snapshots and
   plain results across threads. Coalesce pending edits, check cancellation
   between stages, and discard results for superseded document versions.
   Advertise only implemented capabilities. Reserve stdout for protocol data.

   Add a byte-offset/position adapter with UTF-16 support as the baseline.
   Test emoji, combining characters, tabs, CRLF, end-of-file, and invalid ranges.
   Protocol behavior follows the official
   [LSP specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/).

4. Deliver diagnostics, formatting, and quick fixes.

   Convert diagnostic codes, severity, labels, related locations, and help into
   editor diagnostics. Preserve imported-file ownership and avoid duplicate
   cascades inside parser recovery regions. Publish versioned results and empty
   results when errors disappear.

   Extract formatter configuration loading into the library with an explicit
   starting directory. Format the current buffer using its project settings.
   Return edits without touching disk; return no formatting edit when the
   formatter rejects malformed input. Reuse existing machine-applicable fixes
   and conflict/recovery checks. Produce versioned workspace edits; do not run
   the CLI's disk-writing fix transaction from a code-action request.

5. Retain semantic facts for navigation and completion.

   Add snapshot-local declaration IDs, scope IDs/ranges, definition locations,
   resolved reference targets, and inferred types at source ranges to analysis
   results. Record them during existing name/type resolution. Do not infer
   bindings from the flat symbol map or reimplement type checking in the server.
   Keep codegen's existing symbol behavior intact during this extraction.

   Use this index for hover, definitions, visible-name completion, member
   completion, and signature help. Use syntax for document symbols and keywords
   in incomplete code. Cover imports and aliases, shadowed locals, parameters,
   class members, enum variants, interfaces, and generic substitutions. Avoid
   fabricated locations for builtins. Where embedded stdlib declarations have
   source, expose them through a compiler-versioned read-only source cache so
   definitions have usable file URIs across editors.

6. Connect editors and ship.

   Add a thin `vscode-languageclient` client to the extension selected by #22.
   Start `mux lsp` from an explicit user-configured executable or PATH. Report
   missing/too-old Mux with a useful install/upgrade action. Preserve highlighting
   when the server is unavailable. Run the executable in the editor's remote
   extension host for SSH/containers. Follow VSCode workspace trust rules for
   workspace-provided executable settings.

   Document the same command for Neovim, Helix, and Emacs. Add an LSP initialize/
   shutdown smoke test to existing release-install verification on every shipped
   platform, including Windows DLL packaging. Analysis and formatting must work
   without a C linker or runtime library being available. Update website setup,
   compiler CLI docs, and context architecture/release documentation when the
   behavior ships.

## Verification and completion

- Add library tests for overlays, unsaved imports, import cycles, changed
  dependency diagnostics, path identity, Unicode positions, recovery, and
  shadowing. Compare CLI and editor diagnostics for equivalent saved input.
- Add process-level stdio tests for initialization, multiple edits, stale result
  suppression, cancellation, malformed requests, diagnostic clearing, quick-fix
  application, and clean shutdown without a hanging child process.
- Exercise every advertised editor feature against multi-file fixtures and
  incomplete programs. Measure edit-to-diagnostic latency on the compiler's
  fixture corpus and a generated large module; use the measurement to decide
  whether per-file parse caching is needed before release.
- Run compiler fmt, strict clippy, all-feature tests, strict rustdoc, fixture/
  snapshot checks, and the generated-program suite required by its AGENTS.md.
  Use timeouts for compiled programs and process-level server tests. Run the
  extension's tests and smoke-test VSCode plus a second LSP client.
- Done means a normal released Mux install can start `mux lsp`, editor changes
  affect diagnostics before saving, imports reflect open buffers, advertised
  navigation/completion works, and the server leaves files unchanged unless the
  editor applies a requested edit.

## Cleanup and worktree boundaries

The justified cleanup is the shared analysis API, explicit source identity,
document-relative configuration, and semantic query data. Avoid a complete
compiler crate split, parser rewrite, or wholesale `main.rs` rewrite here.
The server can use compiler analysis without invoking LLVM even though the
existing compiler package still depends on LLVM at build time.

Use a compiler worktree for the analysis/server series and an extension worktree
for its client. Land analysis extraction first, then document lifecycle and the
diagnostics milestone, then semantic queries, then release/client integration.
Base the client work on #22's extension cleanup. Since the repos have separate
Git histories, use one worktree per affected repository. Add website/context
documentation changes alongside the release integration. No worktree or code
implementation is needed just to review these plans.

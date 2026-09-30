# Implementation plan for issue 22: editor distribution

Proposed plan, researched 2026-09-28 and updated 2026-09-30. This describes future
availability. Issue: [#22](https://github.com/muxlang/mux-context/issues/22).
Companion: [LSP implementation plan](issue-16-lsp.md).

## Implementation status

The agreed sequence was to complete issue #16 before issue #22. The compiler
LSP merged in [mux-compiler PR #462](https://github.com/muxlang/mux-compiler/pull/462)
and shipped with the `v0.13.0` compiler release. Its normal install includes
`mux lsp`, formatter, and quick-fix tooling.

Mux-owned extension preparation is merged. [mux-syntax-highlighting PR #32](https://github.com/muxlang/mux-syntax-highlighting/pull/32)
removed the duplicate VSCode package, kept the stable `mux-lang.language-mux`
identity, added the LSP client, and added reproducible VSIX packaging and
verification. PR #33 made the release artifact reusable for publish retries,
and [PR #34](https://github.com/muxlang/mux-syntax-highlighting/pull/34) moved
Marketplace and Open VSX publishing to trusted OIDC. The Open VSX CLI is locked
and isolated from normal development dependencies. [PR #35](https://github.com/muxlang/mux-syntax-highlighting/pull/35)
merged on 2026-09-30 as `44428b6`; all listed checks passed. It aligns the
extension and its lockfiles with compiler version 0.13.0 and adds release notes
to the packaged VSIX. A fresh build from current syntax-highlighting `main`
produced a verified 120.15 KB VSIX containing 11 files. The repository still
has no `v0.13.0` tag or release, and the extension has not been published.

The Tree-sitter editor-query and setup work merged in
[tree-sitter-mux PR #35](https://github.com/muxlang/tree-sitter-mux/pull/35);
PRs #36 and #37 also merged, with #37 adding upstream parser and query checks.
Local branches are prepared for Vim (`2d1b2f1`), Neovim (`2343ed7`),
nvim-treesitter (`4ea0883`), and Helix (`4b86f5c2`). Vim and Neovim add `.mux`
filetype detection and regression coverage. The nvim-treesitter entry pins the
validated Mux parser. Helix adds grammar, highlights, `mux lsp`, and generated
docs. Focused Vim and Neovim filetype checks pass; nvim-treesitter parser
installation and focused query/highlight checks pass; Helix query and highlight
checks pass with 37 assertions. Full Helix workspace tests and a built-editor
installation check have not been run because of the existing build's resource
footprint. None of the four branches has been submitted upstream. The Vim core
change must land before Neovim's filetype change, and Neovim support must land
before nvim-treesitter can meet its filetype prerequisite.

The VSCode Marketplace listing and Open VSX API record for
`mux-lang.language-mux` returned 404 on 2026-09-30. GitHub contains the
`vscode-marketplace` and `open-vsx` deployment environments, but that does not
prove the external publisher accounts trust this repository's workflows. The
maintainer has not confirmed access to either publisher account. Check access
and trusted-publisher setup before creating the syntax-highlighting `v0.13.0`
tag or dispatching a publish workflow.

Neovim support should eventually include both Tree-sitter parsing and a convenient
LSP install. No Mux config exists in nvim-lspconfig and no Mux package exists in
Mason. The latest eligibility research found 7 stars on the Mux compiler repo,
below the listed direct-admission criteria: nvim-lspconfig asks for 100 stars
or evidence of an active server user base; Mason requires 100 stars, 5,000
Marketplace downloads, an accepted nvim-lspconfig config, or an official
recommendation from a reputable organization. For now, document `mux lsp` from
PATH and a small Neovim LSP configuration. Revisit nvim-lspconfig when Mux has
qualifying adoption evidence, then submit a Mason package after that config is
accepted. See the current [nvim-lspconfig contribution guide](https://github.com/neovim/nvim-lspconfig/blob/master/CONTRIBUTING.md)
and [Mason registry contribution guide](https://github.com/mason-org/mason-registry/blob/main/CONTRIBUTING.md).

Third-party PRs remain held for the maintainer's explicit approval. Publication,
upstream editor integration, and post-publication installation checks remain.

## Baseline when the issue was reviewed

These findings capture the initial 2026-09-28 repository survey. The current
state is summarized above; the historical values below explain the cleanup that
followed.

| Area | Repository evidence at issue filing |
| --- | --- |
| Maintained extension | `mux-syntax-highlighting/textmate-mux/vscode-language-mux/package.json` was version 0.6.0 with identity `mux-lang.language-mux`. The issue's 0.5.0 was historical. |
| Duplicate extension | `mux-syntax-highlighting/editor-support/vscode/package.json` defines `mux-lang.mux-syntax` at 0.1.0. |
| Duplicate generation | `scripts/generate-syntax.js` and `scripts/build-editor-support.js` in syntax-highlighting independently build TextMate grammars. |
| Packaging | Generated extension grammars are ignored files. A clean checkout must generate them before packaging. Neither editor repository currently has a publishing workflow. |
| Tree-sitter | The committed parser uses ABI 15. Highlight queries need validation against each editor's capture conventions. |
| Documentation | Syntax-highlighting's `INSTALL.md` still describes an uncommitted parser, deleted editor-support directories, and publication waiting for LSP. `editor-support/README.md` also points at absent Helix/Neovim directories. |

The issue records missing registry entries when it was filed. Recheck registry
availability, publisher ownership, and open upstream PRs before implementation;
do not treat that historical inventory as a fresh availability check.

## Implementation sequence

1. Consolidate extension ownership and generated output.

   **Status: complete.** Mux-syntax-highlighting PR #32 removed the duplicate
   package and retained the stable extension identity.

   Keep `textmate-mux/vscode-language-mux` and its `mux-lang.language-mux`
   identity. PR #32 removed `editor-support/vscode` and its package-only
   generated output, scripts, tests, and documentation references. Installation
   guidance explains how to remove the old extension to avoid duplicate
   language contributions.

   Add behavior fixtures before consolidating the two TextMate builders into a
   shared implementation. Keep the syntax matrix canonical. Preserve the richer
   maintained language configuration, including triple quotes, string exclusions,
   and indentation rules. Validate all remaining consumers, including Sublime
   output, so consolidation does not silently change another editor's grammar.
   Fix stale installation instructions in the same change.

2. Make the VSIX reproducible and test it as an artifact.

   **Status: packaging is complete; fresh-profile install verification remains.**
   PRs #32, #33, #34, and #35 provide packaging, archive verification, durable
   artifact reuse, and trusted publishing.

   The merged workflow uses locked `@vscode/vsce` for packaging and publication
   and an isolated, locked Open VSX CLI only in its publishing job. It builds
   from generated grammar output, verifies the VSIX manifest and required
   assets, excludes development-only files, and preserves syntax parity and
   sample checks.

   CI builds and retains the VSIX artifact for review, and the package verifier
   checks its included grammar, language configuration, license, and assets.
   Before publication, install that VSIX into a fresh VSCode profile and verify
   `.mux` recognition, highlighting, brackets, comments, and indentation. This
   local-editor check has not yet been run.

3. Provision publisher identities and publish the verified package.

   **Status: prepared; maintainer setup remains.** The manual tagged workflow is
   merged. Confirm access to both publisher accounts and their trusted-publisher
   configuration before creating the syntax-highlighting `v0.13.0` tag or
   dispatching publication.

   Verify control of the `mux-lang` Marketplace publisher and Open VSX namespace.
   Complete publisher agreements, namespace ownership, and trusted-publisher
   setup as needed. Keep account provisioning in the publisher services and
   GitHub environment protection settings rather than adding long-lived tokens.

   Follow the current [Marketplace publishing guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
   and [Open VSX publishing guide](https://github.com/eclipse-openvsx/openvsx/wiki/Publishing-Extensions).
   Verify the supported automated authentication mechanism at implementation
   time rather than embedding a soon-to-expire credential recipe in this plan.

   Build the VSIX once for each `v<version>` tag, check its version against the
   manifest, and store the package with its SHA-256 digest. Publish only the
   registries selected for that release. A `none` run builds an artifact for
   inspection without publishing.

   Upload the VSIX and its SHA-256 digest to the GitHub Release as durable
   assets. A retry must download that exact asset and verify its digest before
   publishing. Do not rebuild the VSIX for a retry, even when the tag is
   unchanged. Record the source workflow run ID and digest with the release.
   The workflow-run artifact can support initial inspection, but retries must
   use the release asset so its shorter retention period cannot lose the only
   copy. Test the retry flow before publishing.

4. Prepare tree-sitter for upstream consumers.

   **Status: complete.** `tree-sitter-mux` PR #37 added upstream parser and
   query checks; its required checks passed before merge.

   In `tree-sitter-mux`, keep the committed parser drift check, corpus tests,
   compiler-fixture parsing, and canonical syntax-matrix synchronization. PR #37
   adds upstream-required parser and query validation. Query fixtures cover
   Neovim and Helix while preserving editor-specific captures where needed.
   Do not rewrite the grammar merely to distribute it.

5. Submit Vim and Neovim integration in dependency order.

   **Status: prepared locally; upstream submission needs explicit maintainer
   approval.** Submit the Vim filetype-detection change first, then the Neovim
   core mapping and regression test. Add nvim-treesitter after Neovim recognizes
   `.mux`.

   Neovim v0.12.5 leaves `.mux` unrecognized. The prepared Vim and Neovim core
   branches add `.mux` filetype detection and tests. Current
   [nvim-treesitter contribution rules](https://github.com/nvim-treesitter/nvim-treesitter/blob/main/CONTRIBUTING.md)
   require that recognition, parser CI, query validation with `ts_query_ls`, and
   a current parser ABI. Verify the exact requirements again at submission time.

   After those prerequisites, add Mux to nvim-treesitter's current
   `lua/parsers.lua`, add its `runtime/queries/mux/` queries, and update generated
   documentation as required. Test fetching/building/installing the registered
   parser and opening real `.mux` fixtures with no user parser registration.
   Use the install API supported by the target nvim-treesitter branch; do not
   promise the issue's historical `:TSInstall mux` command on every version.

   Neovim's parser entry does not install the Mux executable. Use `mux lsp` from
   PATH and document a minimal native LSP setup now. Later, when Mux meets their
   admission criteria, add the server config to
   [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig/blob/master/CONTRIBUTING.md)
   and then a binary package to
   [Mason](https://github.com/mason-org/mason-registry/blob/main/CONTRIBUTING.md).
   Current rules ask nvim-lspconfig for at least 100 stars or other evidence of
   an active user base. Mason lists 100 stars, 5,000 Marketplace downloads, an
   accepted nvim-lspconfig config, or an official recommendation from a
   reputable organization. Mux currently has 7 compiler-repository stars and no
   Marketplace listing, so revisit these submissions after adoption grows.

6. Submit Helix integration independently.

   **Status: prepared locally; upstream submission needs explicit maintainer
   approval.** Focused query and highlight checks pass; full workspace and
   built-editor installation tests remain to be run when practical.

   Add language detection and a grammar entry pinned to a reviewed
   `tree-sitter-mux` commit in Helix's `languages.toml`. Add validated highlights
   under `runtime/queries/mux/`. Run `cargo xtask docgen`,
   `cargo xtask query-check mux`, relevant highlight fixtures, and
   `hx --health mux`, following the official
   [language contribution guide](https://github.com/helix-editor/helix/blob/master/book/src/guides/adding_languages.md).
   Test grammar fetch/build and opening Mux source in the built editor. The
   local language-server entry depends on #16; do not describe it as available
   until a Mux release includes `mux lsp`.

7. Verify published installation and update user documentation.

   Install the Marketplace extension by its stable identity in a fresh profile
   and install the Open VSX version in a compatible editor. Verify matching
   versions and content. Verify upstream grammar installations against the
   versions that actually contain the integrations. Add each published editor
   package's name and version to the compiler GitHub Release body, the canonical
   cross-repository release manifest. Record the VSIX hash and registry
   publication results. Distinguish submitted PRs, merged changes, and released
   availability in status reports.

   Update syntax-highlighting installation docs, tree-sitter docs, website setup,
   and context release ownership. Document one-command extension installation
   where supported and native editor integration where shipped. Keep an accurate
   manual fallback until upstream releases include Mux. Keep Emacs instructions
   working; Sublime and JetBrains distribution are outside this issue's scope.

## Joining up with issue 16

The `v0.13.0` compiler install includes `mux lsp`, formatting, and quick-fix
tooling. The VSCode extension starts `mux lsp` from PATH, with an explicit
executable setting for nonstandard installs. Neovim can use the same command
through a small native LSP configuration; the prepared Helix integration
declares it directly. This keeps compiler installation and editor packages
independently usable.

A combined installer option remains optional. If added, editor selection must
be explicit, such as an opt-in VSCode extension install; it must not guess which
editor configurations to overwrite. Publication does not depend on that
convenience option.

## Verification, completion, and worktrees

Run each repository's AGENTS.md gates, syntax parity checks, clean-generation
checks, parser corpus/drift checks, editor-native query checks, workflow lint,
and VSIX installation smoke tests. Run website/context documentation checks for
their changes. No tests need to compile Mux programs just to package a grammar.

Completion requires both registry listings to install successfully and upstream
Vim, Neovim/nvim-treesitter, and Helix integration to land, with release
availability documented accurately. A ready PR is a delivery milestone, not
evidence that users already have the integration. Upstream review timing is
outside Mux's control and must not delay the VSCode/Open VSX release.

Use one syntax-highlighting worktree for cleanup, packaging, and publishing
workflow changes; a tree-sitter worktree for consumer validation; and separate
fork worktrees for each upstream editor PR. Keep website/context docs in their
own repositories. The compiler LSP and VSCode client are merged and compiler
v0.13.0 is released. The VSCode 0.13.0 package preparation is merged; tag-based
publication and third-party editor submissions remain pending maintainer setup
and approval, respectively.

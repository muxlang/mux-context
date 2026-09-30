# Implementation plan for issue 22: editor distribution

Proposed plan, researched 2026-09-28 and updated 2026-09-30. This describes future
availability. Issue: [#22](https://github.com/muxlang/mux-context/issues/22).
Companion: [LSP implementation plan](issue-16-lsp.md).

## Local implementation status

The agreed implementation order is #16 first, then #22. The work is technically
independent, but we will finish and verify the compiler LSP and its minimal
development tooling before packaging or submitting editor distribution changes.

As of 2026-09-30, local work consolidates VSCode extension ownership, builds
and verifies a VSIX, adds a CI artifact job, updates installation guidance,
and prepares Tree-sitter, nvim-treesitter, Helix, and website changes. The
Tree-sitter grammar tests pass (46 corpus cases), both editor highlight queries
pass against grammar fixtures and Neovim's Tree-sitter runtime, the VSIX archive
verifier passes, and VSCode client tests cover both successful startup and an
actionable missing/old-server install prompt. Website build, tests, parity, and
documentation snippet checks pass. Installed Neovim v0.12.5 leaves `.mux`
unrecognized. The core filetype patch adds `.mux` recognition and a functional
test; it applies cleanly to a current upstream source snapshot, and a headless
smoke test confirms `main.mux` returns the `mux` filetype. The full functional
suite has not been rerun for this corrected patch. It remains local and has not
been submitted upstream.

The compiler implementation merged in [mux-compiler PR #462](https://github.com/muxlang/mux-compiler/pull/462).
The VSCode cleanup and package work merged in [mux-syntax-highlighting PR #32](https://github.com/muxlang/mux-syntax-highlighting/pull/32).
The editor queries and setup guidance merged in [tree-sitter-mux PR #35](https://github.com/muxlang/tree-sitter-mux/pull/35),
and the examples now use the landed grammar revision in [PR #36](https://github.com/muxlang/tree-sitter-mux/pull/36).
Website setup guidance in [mux-website PR #104](https://github.com/muxlang/mux-website/pull/104)
and its dependency fix in [PR #103](https://github.com/muxlang/mux-website/pull/103)
are merged. These plans merged in [mux-context PR #65](https://github.com/muxlang/mux-context/pull/65).
The syntax-highlighting PR also adds a manual, tag-driven publishing workflow
for Marketplace and Open VSX. It builds and verifies one VSIX, records its
digest, and publishes only to destinations selected at dispatch. Publishing
uses VSCE's GitHub OIDC trusted publishing and Open VSX trusted publishing,
without long-lived registry tokens or Azure credentials. The workflow requires
the selected workflow ref to match its release-tag input. PR
[#34](https://github.com/muxlang/mux-syntax-highlighting/pull/34) replaced the
Azure credential flow, documented both trusted-publisher setups, and added an
actionable mismatch error. Its required checks passed before merging as
`a2a70be`. The workflow is linted and its build/package steps pass locally.
The Open VSX CLI has a separate lockfile under `.github/ovsx-cli`
and is installed with scripts disabled, so it does not enlarge the root
developer install. PR #32's CI, static analysis, Sonar, and Greptile checks all
pass after fixing the reviewed digest path and requiring a real version tag.
PRs #35 and #36 passed all checks and are merged. The publisher reliability
fix in [mux-syntax-highlighting PR #33](https://github.com/muxlang/mux-syntax-highlighting/pull/33)
is merged. It keeps the VSIX and provenance metadata on a GitHub Release for
retries, verifies that metadata against the version tag, handles concurrent
dispatches, and rejects unverified legacy assets. CI, workflow lint, static
analysis, Sonar, and Greptile all passed. Version 0.13.0 release metadata
merged in [mux-compiler PR #463](https://github.com/muxlang/mux-compiler/pull/463);
creating its tag is pending maintainer approval. Marketplace publisher control
and its OIDC trust policy, plus Open VSX namespace ownership and its trusted
publisher, still need maintainer provisioning. The `vscode-marketplace` and
`open-vsx` GitHub Actions environments now restrict deployments to `v*` tags;
neither environment has required reviewers configured.
Helix's cached `xtask query-check mux`, `xtask docgen`, and `hx --health mux`
pass with the local compiler on `PATH`; its parser and highlight queries load.
The Marketplace item URL and Open VSX API both returned 404 on 2026-09-30,
and `mux-syntax-highlighting` has no GitHub Release yet. Registry publisher and
namespace setup therefore still need maintainer verification before publishing.
Neovim v0.12.5 still leaves `.mux` unrecognized; the corrected core patch's
headless smoke test passes, but its full functional suite has not been rerun.
No PRs have been opened in third-party repositories. The
maintainer has authorized PRs in Mux-owned repositories only; hold Neovim,
nvim-treesitter, and Helix submissions for separate approval. Registry
publication and released native-editor verification remain outstanding.

The prepared nvim-treesitter registry entry and Helix language definition pin
`9d89fb021c15b70b967ef8574c7e28d640d2b705`, the merged tree-sitter commit that
contains the highlight-query fix. A clean Git fetch by that SHA succeeds. No
third-party PRs have been opened.

The agreed order is to finish #16 before publishing #22. The compiler PR
provides `mux lsp`; the VSCode client is prepared in PR #32. Publish the VSIX
after the compiler release includes the server. Keep one VSCode extension
identity so the client arrives through a normal extension update. A tree-sitter
grammar install does not install a language server; document those two
installation responsibilities accurately.

## Research findings

| Area | Current repository evidence |
| --- | --- |
| Maintained extension | `mux-syntax-highlighting/textmate-mux/vscode-language-mux/package.json` is version 0.6.0 with identity `mux-lang.language-mux`. The issue's 0.5.0 is historical. |
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

   Keep `textmate-mux/vscode-language-mux` and its `mux-lang.language-mux`
   identity. Remove `editor-support/vscode` and every generator output, package
   task, test reference, and documentation link that exists solely for it.
   Document uninstalling the old locally installed extension to avoid duplicate
   language contributions.

   Add behavior fixtures before consolidating the two TextMate builders into a
   shared implementation. Keep the syntax matrix canonical. Preserve the richer
   maintained language configuration, including triple quotes, string exclusions,
   and indentation rules. Validate all remaining consumers, including Sublime
   output, so consolidation does not silently change another editor's grammar.
   Fix stale installation instructions in the same change.

2. Make the VSIX reproducible and test it as an artifact.

   Keep the locked `@vscode/vsce` dependency for packaging and publication. Do
   not add `ovsx` to normal development dependencies; invoke its isolated,
   locked CLI only in the Open VSX publishing job. Build from a clean checkout,
   generate the grammar, and package the maintained extension. Inspect the
   archive for its manifest, grammar, language configuration, license, and
   referenced assets.
   Exclude development-only files. Preserve existing syntax parity and sample
   tests, and fail on missing generated assets.

   Add a CI artifact job and install its VSIX into a fresh editor profile.
   Verify `.mux` recognition, highlighting, brackets, comments, and indentation.
   This gives a reviewable, installable artifact before any publication.

3. Provision publisher identities and add a gated, tag-based publish path.

   Verify control of the `mux-lang` Marketplace publisher and Open VSX namespace.
   Configure release credentials through repository secrets and protected
   release settings. Account creation, agreements, and namespace ownership are
   maintainer provisioning steps. Prepare the package and workflow first; obtain
   any missing account access when ready to publish.

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

   In `tree-sitter-mux`, keep the committed parser drift check, corpus tests,
   compiler-fixture parsing, and canonical syntax-matrix synchronization. Add
   upstream-required parser/query validation before requesting registry inclusion.
   Validate captures against Neovim and Helix separately; share compatible query
   content, but keep explicit editor variants where capture names differ.
   Do not rewrite the grammar merely to distribute it.

5. Submit Neovim integration in dependency order.

   Check current Neovim nightly `.mux` filetype detection. If missing, prepare a
   Neovim core filetype PR and its detection test first. Current
   [nvim-treesitter contribution rules](https://github.com/nvim-treesitter/nvim-treesitter/blob/main/CONTRIBUTING.md)
   require that recognition, parser CI, query validation with `ts_query_ls`, and
   a current parser ABI. Verify the exact requirements again at submission time.

   After those prerequisites, add Mux to nvim-treesitter's current
   `lua/parsers.lua`, add its `runtime/queries/mux/` queries, and update generated
   documentation as required. Test fetching/building/installing the registered
   parser and opening real `.mux` fixtures with no user parser registration.
   Use the install API supported by the target nvim-treesitter branch; do not
   promise the issue's historical `:TSInstall mux` command on every version.

6. Submit Helix integration independently.

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

The default compiler installer should bring `mux lsp`, formatting, and fix
tooling together without a second language-server download. The extension will
discover Mux on PATH or through an explicit executable setting. This avoids a
second compiler/runtime installation managed privately by the extension.

After #16 ships, update this same extension with its LSP client and add the
server command to editor integrations. If a combined installer option is added,
make editor selection explicit, such as an opt-in VSCode extension install;
never guess which editor configurations to overwrite. Do not block initial
publication on that convenience option. Extension installation and compiler
installation remain separately usable.

## Verification, completion, and worktrees

Run each repository's AGENTS.md gates, syntax parity checks, clean-generation
checks, parser corpus/drift checks, editor-native query checks, workflow lint,
and VSIX installation smoke tests. Run website/context documentation checks for
their changes. No tests need to compile Mux programs just to package a grammar.

Completion requires both registry listings to install successfully and upstream
Neovim/nvim-treesitter and Helix integration to land, with release availability
documented accurately. A ready PR is a delivery milestone, not evidence that
users already have the integration. Upstream review timing is outside Mux's
control and must not delay the VSCode/Open VSX release.

Use one syntax-highlighting worktree for cleanup, packaging, and publishing
workflow changes; a tree-sitter worktree for consumer validation; and separate
fork worktrees for each upstream editor PR. Keep website/context docs in their
own repositories. The compiler LSP and VSCode client PRs are open. Publish the
extension only after the compiler release includes `mux lsp`. Third-party editor
PRs and registry publication remain future actions requiring the maintainer's
approval.

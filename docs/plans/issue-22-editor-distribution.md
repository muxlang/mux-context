# Public editor support for issue 22

Status checked 2026-10-08. Issue: [#22](https://github.com/muxlang/mux-context/issues/22).
The compiler LSP work for [issue 16](issue-16-lsp.md) is already in compiler
v0.13.0.

## Current state

- The compiler release v0.13.0 includes `mux lsp`. No new compiler release is
  needed just to publish the editor integrations.
- The maintained VS Code extension is `mux-lang.language-mux`, version
  0.13.0. Its package, OIDC publishing workflow, durable VSIX artifact, and
  release notes are prepared in `mux-syntax-highlighting`. The extension
  release tag and GitHub Release do not exist yet.
- The Visual Studio Marketplace item and Open VSX API both returned 404 on
  2026-10-08. The `vscode-marketplace` and `open-vsx` GitHub environments exist.
  Publisher ownership and trusted-publisher configuration still need a
  maintainer to verify.
- Neovim support is being kept inside Mux. The `tree-sitter-mux` plugin is
  merged into `main`; its stable release tag is pending. It adds
  `.mux` detection, builds the committed parser, configures Tree-sitter
  highlighting, and starts `mux lsp`. It requires Neovim 0.11 or newer, a C
  compiler, and Mux 0.13.0 or newer. No Neovim core or nvim-treesitter PR is
  required for this install path.
- The merged Neovim plugin passed its headless integration test on Neovim 0.12.5,
  all 46 Tree-sitter corpus tests, package lint/format/sample checks, and
  workflow lint. CI now covers both the minimum supported Neovim 0.11.7 and
  Neovim 0.12.5. Create the plugin release as a separate, approved release step.
- The first maintained-editor release covers VS Code and Neovim. Helix,
  Emacs, Sublime Text, and JetBrains remain manual or later integrations.

## Organization maintenance sweep

The canonical repository manifest contains nine active repos. The current
inventory found 17 open dependency or CI PRs across six of them. Ten all-green
PRs have GitHub auto-merge enabled, which leaves branch-policy requirements in
control of when they merge:

- `mux-runtime#138`, `mux-compiler#464`, `mux-website-api#67-69`
- `tree-sitter-mux#39`, `mux-syntax-highlighting#37-39`, `mux-context#72`

Seven PRs remain red and are not queued for merging. Runtime PRs `#139-143`
have failed tests, clippy, Greptile, or cancelled checks. Website PRs
`#107-108` and the editor docs PR are blocked by existing dependency audit
failures: the docs PR's 2026-10-08 CI run reports 48 frontend advisories
(13 moderate, 18 high, 17 critical) and 3 high-severity Worker advisories.
The available automatic fixes include breaking Docusaurus and Wrangler
upgrades, so address those in a dedicated dependency change. Resolve the
underlying failures and rerun the required checks; do not bypass them.
`.github` and `mux-examples` have no open PRs.

## Release sequence

1. Finish the organization-wide maintenance sweep. Verify the queued PRs have
   merged under their branch policies, resolve the seven red PRs where a safe
   fix is clear, and report anything that remains blocked. Refresh editor and
   documentation work against the resulting default branches.
2. Review and merge the Mux-owned Neovim plugin change in `tree-sitter-mux`.
   It prepares Tree-sitter metadata version 0.7.0 and a `v0.7.0` Git tag for
   plugin-manager installs. The tag is a maintainer release action.
3. Verify Marketplace publisher access and Open VSX namespace ownership. Set
   up each trusted publisher against the workflow and its GitHub environment.
   The workflow stores no long-lived registry token.
4. After the extension changes are merged, create the `v0.13.0` tag in
   `mux-syntax-highlighting`. Run `publish-vscode.yml` first with destination
   `none`, inspect the archived VSIX and SHA-256 metadata, then run it with
   destination `both`. This publishes the same verified artifact to both
   registries. Tagging and publishing require maintainer approval.
5. Verify both listings and install them in clean editor profiles. Then merge
   website and organization-profile docs that point users to the registries.
   Publish the website after its docs checks pass. Record the extension and
   Neovim plugin versions in the cross-repository release manifest.

## User-facing install and acceptance checks

- **VS Code:** install `mux-lang.language-mux` from the Visual Studio
  Marketplace. For compatible editors, install the same identity from Open
  VSX. Open a `.mux` file and verify highlighting, diagnostics, completion,
  hover, signature help, document symbols, go-to-definition, formatting, and
  safe code actions.
- **Neovim (after the plugin release is tagged):** install
  `muxlang/tree-sitter-mux` with the documented plugin manager specification.
  Confirm parser build, `.mux` detection, highlighting, and automatic `mux lsp`
  startup. Verify custom compiler path and LSP opt-out settings. Formatting runs
  only when the editor requests it.
- In both editors, confirm that the installed compiler is v0.13.0 or newer.
  Keep syntax highlighting usable when the language server is unavailable.

All Mux-owned changes must follow the relevant repository checks and include
the contributor-required changelog and issue references. Prepare PR titles and
bodies for Derek to review before opening them. No PRs to Neovim, nvim-treesitter,
Helix, or another third-party repository are part of this release.

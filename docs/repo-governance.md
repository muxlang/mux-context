# Repo governance: labels, templates, and project fields

The muxlang org keeps issue metadata consistent across every repo. This doc is
the policy source of truth. Enforcement (label YAML, template sources, sync
scripts) lives in the
[`.github`](https://github.com/muxlang/.github) repo.

## Architecture

| Layer | Where | What it owns |
| --- | --- | --- |
| Policy | `mux-context` (this doc) | Why, strict rules, triage workflow |
| Enforcement | `muxlang/.github` | `labels/*.yml`, `templates/<repo>/`, sync scripts |
| Per-repo files | Each repo's `.github/ISSUE_TEMPLATE/` | Synced from `.github/templates/`; do not hand-edit |

## Strict rules

1. **Do not hand-edit synced files** in a repo's `.github/ISSUE_TEMPLATE/`.
   Change the source in `muxlang/.github/templates/<repo>/` and re-sync.
2. **Do not use milestones.** Planning uses the org project board. GitHub still
   shows an empty Milestone slot on issues; ignore it.
3. **Do not use priority labels.** Priority is set on
   [Mux Project Tasks](https://github.com/orgs/muxlang/projects/2) only
   (Urgent / High / Medium / Low).
4. **Do not add `bug` or `feature` labels.** Kind comes from the template
   chosen at filing time; apply kind labels (`enhancement`, `documentation`,
   `chore`, etc.) during triage.
5. **Exactly one workflow state on the project board** per issue: Backlog,
   In Progress, or Done.
6. **Do not invent ad hoc labels.** Add to `labels/labels.yml` or a repo
   overlay, update this doc, run `sync-labels.sh`.
7. **IDE labels** (`vscode`, `neovim`, etc.) belong only on
   `mux-syntax-highlighting` and `tree-sitter-mux`.
8. **No PR templates.** Link issues in the PR description; CI enforces quality.
9. **ASCII only** in label names and descriptions.

## Priority and status

Both live on [Mux Project Tasks](https://github.com/orgs/muxlang/projects/2),
not as issue labels.

| Field | Values | When to set |
| --- | --- | --- |
| Priority | Urgent, High, Medium, Low | During triage |
| Status | Backlog, In Progress, Done | Backlog by default after triage |

## Labels

Canonical set:
[`.github/labels/labels.yml`](https://github.com/muxlang/.github/blob/main/labels/labels.yml).
Repo overlays: `.github/labels/<repo>.yml`.

Apply with `./scripts/sync-labels.sh` in the `.github` repo.

### Org-wide labels (every repo)

| Group | Label | When to use |
| --- | --- | --- |
| Kind | `documentation` | Docs improvements or additions |
| Kind | `chore` | Cleanup, maintenance, dependency bumps |
| Kind | `refactor` | Internal restructuring, no behavior change |
| Kind | `optimization` | Performance or efficiency improvement |
| Kind | `testing` | Test coverage or test infrastructure |
| Kind | `enhancement` | Improvement to existing behavior or UX |
| Quality | `inconsistency` | Behaves or looks different across places that should match |
| Quality | `polish` | Small rough edge; nothing broken, just unrefined |
| Workflow | `needs triage` | Not yet reviewed (auto-applied by templates) |
| Workflow | `blocked` | Blocked on another issue or external dependency |
| Workflow | `needs testing` | Fix landed but needs broader test confirmation |
| Workflow | `duplicate` | Already exists |
| Workflow | `invalid` | Not actionable |
| Workflow | `wontfix` | Acknowledged but will not be worked on |
| Community | `good first issue` | Good for newcomers |
| Community | `help wanted` | Extra attention needed from contributors |

### Repo overlays

| Repo | Extra labels |
| --- | --- |
| mux-compiler | `stdlib`, `frontend`, `low/med/high complexity`, `dependencies`, `tembo` |
| mux-runtime | `stdlib`, `ffi` |
| mux-website | `playground`, `docs-site`, `mux-ai`, `docusaurus` |
| mux-website-api | `security`, `sandbox`, `deployment` |
| mux-syntax-highlighting | `syntax-spec`, `textmate`, `editor-support`, `vscode`, `sublime`, `jetbrains`, `neovim`, `helix` |
| tree-sitter-mux | `grammar`, `queries`, `syntax-matrix`, `neovim`, `helix`, `emacs` |
| mux-context | `architecture`, `adr`, `governance` |

### Kind label guide

| Situation | Label or template |
| --- | --- |
| Something broken | Bug report template |
| New capability | Feature request template |
| Existing behavior improved | `enhancement` |
| Performance only | `optimization` |
| Internal code change | `refactor` |

## Issue templates

Each repo has synced templates under `.github/ISSUE_TEMPLATE/`. Sources live in
`muxlang/.github/templates/<repo>/`.

| Repo | Templates |
| --- | --- |
| mux-compiler | Bug, Feature, Documentation |
| mux-runtime | Bug, Feature |
| mux-website | Bug, Feature, Documentation |
| mux-website-api | Bug (+ private security advisories via contact link) |
| mux-syntax-highlighting | Bug, Syntax spec change |
| tree-sitter-mux | Bug, Grammar sync |
| mux-context | Cross-repo question, ADR proposal |

All templates apply `needs triage` on creation. Blank issues are disabled in
every repo so contributors always pick a template.

## Triage workflow

1. Contributor files via a template -> `needs triage` label applied.
2. Maintainer reviews: confirm repo, set project **Priority** and **Status**
   (Backlog), apply kind/area labels, remove `needs triage`.
3. When work starts: Status -> In Progress.
4. When closed: Status -> Done.

## Cross-repo CI and canonical artifacts

Where one repo consumes an artifact owned by a sibling, CI must verify against
the sibling's live **source**, not a published or vendored copy. See
[decision 0003](decisions/0003-verify-consumers-against-source.md) and
muxlang/mux-context#3 for status.

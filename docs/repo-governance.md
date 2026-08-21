# Repo governance: labels, templates, and project fields

The muxlang org keeps issue metadata consistent across every repo. This doc is
the policy source of truth. Enforcement (label YAML, template sources, sync
scripts) lives in the
[`.github`](https://github.com/muxlang/.github) repo.

## Architecture

| Layer | Where | What it owns |
| --- | --- | --- |
| Kind | Org **issue types** | Bug, Enhancement, Documentation, Chore, Decision |
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
4. **Do not label the kind.** Kind is an **issue type**, set by the template at
   filing time - not `bug`, `feature`, `enhancement` or `documentation` labels.
   A type is single-select and shows in every issue list, which is what makes it
   the right home for "what sort of thing is this".
5. **Exactly one workflow state on the project board** per issue: Backlog,
   In Progress, or Done.
6. **Do not invent ad hoc labels.** Add to `labels/labels.yml` or a repo
   overlay, update this doc, run `sync-labels.sh`.
7. **IDE labels** (`vscode`, `neovim`, etc.) belong only on
   `mux-syntax-highlighting` and `tree-sitter-mux`.
8. **No PR templates.** Link issues in the PR description; CI enforces quality
   (see [Required CI checks](#required-ci-checks-merge-gates)).
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

Apply with `./scripts/sync-labels.sh` in the `.github` repo. Verify with
`./scripts/validate-labels.py`, which diffs the live labels of every repo
against the canonical YAML and exits nonzero on drift; run it after any
sync or retire.

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

## Issue types

Kind is an org-level **issue type**, set by the template at filing time:

| Type | For |
| --- | --- |
| Bug | Something behaves incorrectly, crashes, or produces a wrong answer |
| Enhancement | A new capability, or an existing one made better |
| Documentation | Docs are missing, wrong, or misleading |
| Chore | Maintenance that changes no behaviour: CI, dependencies, refactors, tests |
| Decision | A cross-repo question, or a design choice to record as an ADR |

Types and labels answer different questions, which is why both exist. A type is
**single-select**: exactly one kind per issue, and no way to file something that
is both a bug and a feature. Labels are many, and carry the axes a single field
cannot:

- **area** - `stdlib`, `frontend`, `ffi`, `playground`, `grammar`
- **state** - `needs triage`, `blocked`, `needs testing`
- **disposition** - `duplicate`, `invalid`, `wontfix`, `good first issue`

So: one type, any number of labels, and no label that restates the type.

## Issue templates

Each repo has synced templates under `.github/ISSUE_TEMPLATE/`. Sources live in
`muxlang/.github/templates/<repo>/`. Templates are structured YAML issue
forms (`*.yml`), not markdown: required fields are enforced at filing time
and forms set no title prefix. Do not encode the kind in the title (no
`[Bug] -` prefixes); the chosen form records it.

| Repo | Templates |
| --- | --- |
| mux-compiler | Bug, Feature, Documentation |
| mux-runtime | Bug, Feature |
| mux-website | Bug, Feature, Documentation |
| mux-website-api | Bug (+ private security advisories via contact link) |
| mux-syntax-highlighting | Bug, Syntax spec change |
| tree-sitter-mux | Bug, Grammar sync |
| mux-context | Cross-repo question, ADR proposal |

All templates apply `needs triage` on creation, and the triage workflow removes
it again for issues opened by org members - they can set priority and status
directly, so the label would only ask a maintainer to review their own filing.
Blank issues are disabled in every repo so contributors always pick a template.

## Triage workflow

1. Contributor files via a template -> `needs triage` label applied. An issue
   opened by an org member has it removed automatically (muxlang/mux-context#19).
2. Maintainer reviews: confirm repo, set project **Priority** and **Status**
   (Backlog), apply kind/area labels, remove `needs triage`.
3. When work starts: Status -> In Progress.
4. When closed: Status -> Done.

## Filing an issue, and running a PR

The rules above say what the metadata means. This says how to actually file and
land work, and it applies to agents as much as to people - the omissions here
are what muxlang/mux-context#28 was about.

### Filing an issue

1. **Pick the template that matches the kind.** Blank issues are disabled, and
   the form you choose is what records whether this is a bug, a feature or a
   docs problem. Do not restate it in the title - no `[Bug] -` prefix.
2. **Write a title that names the defect, not the area.** "Importing a std.dsa
   type is an internal compiler error" beats "import problem".
3. **Leave the labels alone at filing time.** The template sets the issue
   **type** and applies `needs triage`; area labels come during triage. Never
   add a label that restates the type (`bug`, `enhancement`, `documentation`),
   and never add a priority label - priority lives on the project board only.
4. **Do not set a milestone.** Planning is the project board.
5. **Say how it was found and how to reproduce it.** A failing program, the
   exact diagnostic, and what you expected instead. For a compiler or runtime
   issue, the smallest program that shows it is worth more than a description
   of it.

### Triaging one

Set **Priority** and **Status** on
[Mux Project Tasks](https://github.com/orgs/muxlang/projects/2), apply area
labels, correct the **type** if the filer picked the wrong form, then remove
`needs triage`. Exactly one status: Backlog, In
Progress, or Done.

Issues opened by org members are triaged at filing time, so they do not carry
`needs triage` - the label marks work that still needs a maintainer's judgement,
and someone who can set priority directly has already given it.

### Running a PR

1. **One branch per repo, named the same across repos** when the change spans
   more than one - that is what pairs them in CI (see
   [Pairing a change that spans repos](#pairing-a-change-that-spans-repos)).
2. **Link the issue in the description.** There are no PR templates, so the
   description carries the whole case: what was wrong, why this fixes it, and
   what was verified. `Closes #N` for the issue it resolves.
3. **Say what you actually ran.** "Full suite, clippy and rc-leak-check pass" is
   worth more than a claim that it works, and a reviewer can tell the difference.
4. **A red check is a claim about your change until you have shown otherwise.**
   If it is red for a reason outside the diff - a stale run, a coupled change
   whose other half has not merged - say which in the PR, rather than leaving a
   reviewer to assume it was checked.
5. **Merge order for a coupled change**: producer first, then the consumer's
   pin bump. The pin bump is the gate; see
   [What gates, and what only reports](#what-gates-and-what-only-reports).
6. **Changelog entry in the same PR as the change**, under a numbered dated
   heading - not a rolling `Unreleased` one. See the
   [release process](release-process.md).

## Required CI checks (merge gates)

Rule 8 above ("CI enforces quality") is concrete: every repo protects its default
branch with a set of required status checks, and a pull request cannot be merged
until all of them pass. These are shared org conventions, not per-repo choices.

- **Greptile Review** - the AI code review, and a MUST-PASS gate in every repo: a
  red Greptile check blocks merge. Address every finding (fix it, or resolve the
  thread with a justification) and let the review re-run; never merge around an
  unresolved Greptile review. This applies to docs-only PRs too.
- **SonarCloud / SonarQube** - two checks that are easy to mistake for
  duplicates, and both must pass. `SonarCloud Code Analysis` is posted by Sonar's
  app and runs the built-in "Sonar way" gate, which has **no new-issue
  condition**: it fails on ratings, coverage, duplication and hotspots reviewed,
  so new code smells can pass it. The repo's own `SonarQube` job is what fails on
  **any** new issue, not only blocking ones - and since custom quality gates are
  a paid feature, that job is the only enforcement of it. Never remove it as
  redundant with a green app check. New code must also meet the coverage
  threshold.
- **Rust Checks** (code repos) - `cargo fmt --check`, `cargo clippy -D warnings`,
  and the test suite (with coverage) must all pass.
- **Integration / Downstream smoke** - where a repo consumes a sibling, its
  end-to-end and downstream-source checks must pass (see the section below).
- **Valgrind Memory Checks** (mux-compiler, mux-runtime) - compiled programs and
  the runtime's test binaries must be free of definite/indirect leaks and memory
  errors. Benign third-party noise (TLS crates such as rustls/ring/ureq, and LLVM)
  is covered by checked-in suppression files, never by loosening the gate.

## Cross-repo CI and canonical artifacts

Where one repo consumes an artifact owned by a sibling, CI must verify against
the sibling's live **source**, not a published or vendored copy. See
[decision 0003](decisions/0003-verify-consumers-against-source.md) and
muxlang/mux-context#3 for status.

### Pairing a change that spans repos

Develop it on a **branch of the same name in every repo it touches**. That is
the whole coordination mechanism: a cross-repo job looks for a branch of the
current PR's name in the repo it is checking out, and uses `main` if there is
none.

Nothing to label, create, or clean up. A branch either exists or it does not,
which also means it works the same on a push, where there is no pull request to
carry metadata.

This replaced `paired-<repo>:<branch>` labels. They were metadata rather than
content: they did not travel with the commit, did not appear in the diff, did
not exist on a push, needed creating before they could be applied, and only took
effect if you remembered to close and reopen the PR - labelling does not start a
run, and re-running replays the original payload.

### What gates, and what only reports

A consumer's CI builds the sibling commit its lockfile names. A job that builds
the sibling's **branch** source instead is therefore a preview of a state that
does not exist yet, and on a deliberately breaking change its failure is
expected information rather than a defect. Those jobs report; they do not gate.

The gate is the **pin-bump PR** - the change that moves the consumer's lockfile
onto the new commit. That is the first build which actually contains the change,
it runs the consumer's full suite, and it is required there. Merging a coupled
change means merging the producer, then the pin bump; the second one is where a
real break surfaces and blocks.

# Repo governance: labels, types, milestones, and Linear

The muxlang org keeps issue metadata consistent across every repo so work looks
and behaves the same everywhere and round-trips cleanly with Linear. This doc is
the source of truth for that convention. The enforcement lives in the
[`.github`](https://github.com/muxlang/.github) repo; this doc explains the
"what" and "why".

## Issue types (org-level)

The org defines three issue types that apply to every repo automatically:

- `Task` - a specific piece of work
- `Bug` - an unexpected problem or behavior
- `Feature` - a request, idea, or new functionality

Types are the primary "kind" of an issue. Labels below are orthogonal to types
and add dimensions the type does not carry (priority, area, workflow state). Do
not add `bug` / `feature` / `enhancement` labels - use the type instead.

## Labels

The canonical label set is recorded in
[`.github/labels/labels.yml`](https://github.com/muxlang/.github/blob/main/labels/labels.yml),
with repo-specific extras in overlay files (see below). This YAML is the
authoritative list; labels are applied to each repo manually from it (for
example with `gh label create <name> --color <hex> --description <desc> --force
--repo muxlang/<repo>`). When you change the list, re-apply it to the affected
repos and delete any labels you removed.

Canonical labels:

| Group | Label | Meaning |
| --- | --- | --- |
| Kind | `documentation` | Docs improvements or additions |
| Kind | `chore` | Cleanup, maintenance, dependency bumps |
| Kind | `refactor` | Internal restructuring, no behavior change |
| Kind | `optimization` | Performance or efficiency improvement |
| Kind | `testing` | Test coverage or test infrastructure |
| Priority | `priority: urgent` | Needs attention now |
| Priority | `priority: high` | Important, schedule soon |
| Priority | `priority: medium` | Normal priority |
| Priority | `priority: low` | Nice to have, no rush |
| Quality | `inconsistency` | Behaves or looks different across places that should match |
| Quality | `polish` | Small rough edge or papercut; nothing broken, just unrefined |
| Workflow | `needs triage` | Not yet reviewed or categorized |
| Workflow | `blocked` | Blocked on another issue or dependency |
| Workflow | `needs testing` | Needs testing to confirm cases are covered |
| Workflow | `duplicate` | Already exists |
| Workflow | `invalid` | Does not seem right |
| Workflow | `wontfix` | Will not be worked on |
| Community | `good first issue` | Good for newcomers |
| Community | `help wanted` | Extra attention is needed |

### Repo-specific overlays

A repo may add labels that only make sense there, recorded in an overlay file
`.github/labels/<repo>.yml`. Apply the overlay on top of the canonical set for
that repo. Today the only overlay is
[`labels/mux-compiler.yml`](https://github.com/muxlang/.github/blob/main/labels/mux-compiler.yml)
(`stdlib`, `frontend`, complexity labels, and the `tembo` / `dependencies` bot
labels). Bot-managed labels belong in the overlay of the repo whose bot posts
them so they are not removed during a cleanup.

## Milestones

Milestones stay **per-repo** and are not replicated across the org. Repos are
versioned independently (see
[decision 0002](decisions/0002-independent-versioning.md)), so a shared milestone
set would not map to any single release. Track cross-repo work through the shared
[Mux Project Tasks](https://github.com/orgs/muxlang/projects/2) project instead.

## Fields (Project)

Custom fields live on the org [Project #2](https://github.com/orgs/muxlang/projects/2),
not on individual repos, so one project already gives cross-repo field
consistency. Priority is carried on issues by the `priority: *` labels (so it
round-trips to Linear); the project `Status` field tracks workflow state.

## Linear integration

Goal: manage issues on GitHub or Linear interchangeably, with **GitHub as the
source of truth** and two-way sync keeping both in step. The label taxonomy above
is designed so names match on both sides and round-trip without translation.

### One-time setup (manual, in the Linear UI)

These steps cannot be automated from the repos - they require Linear workspace
admin access:

1. **Connect GitHub:** Linear -> Settings -> Integrations -> GitHub -> authorize
   the `muxlang` organization.
2. **Enable GitHub Issue Sync** for each repo, mapping it to the appropriate
   Linear team, with GitHub set as the primary/source system.
3. **Enable PR linking** so branches and PRs using magic words (e.g.
   `Fixes MUX-123`) attach to their Linear issue.

### Mapping (configure in Linear to match this table)

| GitHub | Linear |
| --- | --- |
| Issue type `Bug` / `Feature` / `Task` | Linear issue label or type of the same name |
| `priority: urgent` / `high` / `medium` / `low` | Priority Urgent / High / Medium / Low |
| Open issue (untriaged) + `needs triage` | Backlog / Triage |
| Open issue | Todo |
| `blocked` | Blocked |
| Closed issue | Done / Canceled |
| Any other label | Linear label of the same name (created once, then round-trips) |

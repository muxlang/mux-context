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

## Project board (GitHub)

The org project [Mux Project Tasks](https://github.com/orgs/muxlang/projects/2)
aggregates issues across all repos in one board for cross-repo visibility and
prioritization.

### Board structure

- **Status** field (workflow state, mixing priority levels and workflow for now):
  High Priority, Medium Priority, Low Priority, Future Work, In Progress, Done.
  Over time, new issues should use the **Priority** field separately (below).
- **Priority** field (new, Urgent / High / Medium / Low): Use this for issue
  priority instead of embedding it in Status. Separating priority from workflow
  makes sorting and filtering clearer.
- **Labels** field: Shows the canonical label set (documentation, chore, refactor,
  testing, etc.).
- **Repository** field: Filter by repo.
- **Milestone** field: Links to release milestones in each repo.

### Workflow

1. Create issues in the repo you're working on (auto-added to the project).
2. Triage: set Priority (Urgent/High/Medium/Low) and Status (Backlog/In
   Progress/Done).
3. Filter by Repository, Priority, Status, Labels to find work to do or see
   cross-repo impact.

### Tips

- Filter by Repository to see one repo's work, or by Priority to see what's
  urgent org-wide.
- Status currently mixes priority with workflow; future issues should use the
  Priority field instead.
- Milestones show per-repo release planning; see
  [independent versioning](decisions/0002-independent-versioning.md).


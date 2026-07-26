# context: AI Agent Guidelines

The cross-repo knowledge hub for the multi-repo
[muxlang](https://github.com/muxlang) ecosystem. This repo is documentation only -
there is no build and no code to compile.

## What this is

The single home for facts that span more than one code repo: the architecture /
repo map, design rationale, the feature-to-module map, the glossary, and the
release process. See [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).

Agent orientation for the whole ecosystem lives in [SKILL.md](SKILL.md) - a
short "where truth lives" map plus the cross-repo rules. It is the canonical
copy of the `mux` agent skill; keep it in sync with any local skill copies.

## Rules

- **No special characters** - ASCII only in all files (no em-dashes, emojis, smart
  quotes), matching the rest of the org.
- **Own vs link.** This repo owns only things no single code repo owns. If a build
  step reads it (the canonical `syntax-matrix.json`, generated grammars, rustdoc),
  it stays in the repo whose tooling needs it and is *linked* from here, not copied.
- **Keep facts accurate.** When code changes make a doc here stale, update the doc
  in the same change. Prefer linking to the authoritative source over duplicating.
- **Link related docs** with relative links so navigation stays intact.
- **Pre-existing bugs.** A bug uncovered while fixing an issue that directly
  impacts or is closely related to that issue should be fixed as part of the same
  work; file unrelated ones as their own issue. Never silently leave an uncovered
  bug, and do not bundle an unrelated fix into the PR.
- **Agents:** keep [`llms.txt`](llms.txt) in sync when you add or move a doc.

## Where to file issues

Unsure which repo an issue belongs to? Open it here and it will be triaged to the
right repo. Issues clearly scoped to one repo should go to that repo.

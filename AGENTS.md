# mux-context

`mux-context` is the cross-repository knowledge hub for Mux: architecture,
design decisions, terminology, repository ownership, and release policy. It is
documentation only.

`SKILL.md` is the canonical orientation guide for the organization. Keep it
accurate and link to the repository that owns executable or generated truth;
do not copy implementation details here.

## Invariants

- Facts must match the current repositories. Update linked context when a
  cross-repository contract changes.
- Use relative links for related local documents and keep `llms.txt` in sync
  when documents move.
- Preserve intentional Unicode examples; ASCII checks must be scoped to files
  where ASCII is a real policy.

## Quality gate

Run the repository's link, Markdown, and scoped text checks before committing.
There is no compiler or application build in this repository.

## Documentation

Start with [`README.md`](README.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), and
the decisions under `docs/`.

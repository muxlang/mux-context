# mux-context

`mux-context` is the cross-repository knowledge hub for Mux: architecture,
design decisions, terminology, repository ownership, and release policy. It is
documentation only.

The canonical organization guidance is [`mux-context/SKILL.md`](SKILL.md).
Keep it accurate and link to the repository that owns executable or generated
truth; do not copy implementation details here.

## Invariants

- Facts must match the current repositories. Update linked context when a
  cross-repository contract changes.
- Use relative links for related local documents and keep `llms.txt` in sync
  when documents move.
- Preserve intentional Unicode examples; ASCII checks must be scoped to files
  where ASCII is a real policy.

## Quality gate

Run `python3 scripts/ci/check-docs.py` and
`python3 -m unittest discover -s scripts/tests -p 'test_*.py'` before
committing. The scoped encoding contract lives in
[`docs/encoding-policy.json`](docs/encoding-policy.json). There is no compiler
or application build in this repository.

## Documentation

Start with [`README.md`](README.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), and
the decisions under `docs/`.

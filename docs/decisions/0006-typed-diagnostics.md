# 0006: Typed diagnostic registry

## Context

Compiler errors used to be message-plus-span values. That made copied error
text unstable and gave documentation and tools no reliable identifier.

## Decision

The compiler keeps a typed, embedded registry of `E####` and `W####` codes.
Frontend error values carry their code explicitly. The code is selected at the
construction site and is never inferred by searching rendered message text.
The compiler owns the build-consumed registry. The website documents every
public code, and the context repo records the shared policy.

Only `error` and `warning` are severities. Warnings require a proof from the
compiler's type or control-flow model. Diagnostic output is deterministic and
limited to 100 entries. Machine-applicable edits are validated by reparsing
and reanalyzing before atomic writes.

## Consequences

Adding a diagnostic requires an explicit code and synchronized documentation.
Changing message wording does not change diagnostic identity. The constructor
migration is broad, but missing code arguments now fail at compile time instead
of becoming silently misclassified diagnostics.

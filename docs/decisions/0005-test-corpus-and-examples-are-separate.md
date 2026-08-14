# 0005 - The test corpus and the published examples are separate artifacts

## Context

`mux-compiler/test_scripts/` and the `mux-examples` repo both hold `.mux`
programs, which raised the question of whether they are one artifact or two
(muxlang/mux-context#44). The answer determines what #26 builds, so it had to be
settled first.

What the two actually are:

- **`test_scripts/`** is a snapshot-bound regression corpus. At the time of this
  decision it held 148 programs plus 135 under `error_cases/` that must *fail*
  to compile, against 432 insta snapshots. Four integration suites, two
  benchmark suites, the valgrind and leak scripts, and mux-runtime's downstream
  smoke test all auto-discover it.
- **`mux-examples`** was an empty repo: a LICENSE and a README.

Three findings decided it.

**The two have incompatible compiler pins.** A regression corpus must track
`main` - pinning it to a release would mean new behaviour could not be tested
until it shipped. Published examples must track a *release*, or they teach
syntax the playground rejects; that skew shipped once already with the `{:}`
empty-map literal, and is why `mux-website`'s `docs-snippets.yml` exists. No
single corpus can satisfy both.

**The corpus is coupled to compiler source.** Of the commits touching
`test_scripts/` in the 90 days before this decision, **36 of 36** also touched
`mux-compiler/src/`. Moving it would turn every one of those into an ordered
two-repo change.

**The fixtures are not examples.** They are written to pin behaviour, not to
teach: `scalar_locals_unboxed.mux` opens with 30 lines on `*mut Value` slots and
capture cells. The ones with approachable names are exhaustive print-dumps
ending in "ALL TESTS COMPLETED SUCCESSFULLY!".

Drift between the two, the main argument for merging, had not materialised: only
9 of 224 named website snippets shared a filename with a fixture, and the shared
ones were deliberately different - a minimal teaching snippet versus an
exhaustive parameter matrix.

## Decision

They are **two artifacts**, and `test_scripts/` does not move.

- `mux-compiler/test_scripts/` stays where it is, tracking compiler `main`.
  `error_cases/` is never user-facing.
- `mux-examples` holds complete, deterministic programs that do a job, verified
  by `scripts/run-examples.sh` diffing each program's output against a recorded
  baseline.
- Promotion is **one-way and manual**: when an example turns out to pin
  behaviour worth regressing, copy it into `test_scripts/` as a fixture. There
  is no vendoring, no drift check, and no cross-repo gate.

`odin-lang/examples` is the same shape - a separate, topic-organised repo with
its own CI, distinct from the compiler's own tests.

## Consequences

- Two corpora exist on purpose, and they will diverge. That is accepted: the
  boundary is *intent*, and intent cannot be diffed. A sync job would fight the
  specialisation rather than preserve anything.
- `mux-examples` CI builds compiler `main` rather than a release. Pinning to a
  release would deadlock - a fix for a compiler-caused failure could not merge
  until the release shipped, and the release should not ship with a broken
  example.
- The guarantee that examples work against a real *release* comes from running
  the same script outside this repo, and does exist. Both gates are defined in
  the repo they run in, which is authoritative; the summary here can go stale,
  so check the workflow before relying on a detail of it:
  - [mux-compiler's release workflow](https://github.com/muxlang/mux-compiler/blob/main/.github/workflows/release.yml)
    runs it against the artifact it is about to publish, installed the way a
    user installs it, so a broken example blocks the release.
  - [mux-runtime's CI](https://github.com/muxlang/mux-runtime/blob/main/.github/workflows/ci.yml)
    runs it on every pull request. That repo has no release workflow - merging
    to `main` is what makes a change available (see
    [0004](0004-runtime-resolved-from-source.md)) - so a pull request is the
    last point before users get the change.
- mux-compiler and mux-runtime both take a CI dependency on mux-examples. This
  is the dependency inversion #44 raised, accepted deliberately: output diffs
  over a dozen programs are far less brittle than 432 filename-keyed snapshots.
  In mux-compiler it blocks a *release* rather than a merge; in mux-runtime,
  which has no release step, it blocks a merge, because there is no later gate.
  The cost is real and worth stating: a stale `expected_output.txt` can hold up
  a release, and the fix for it lives in another repo.
- Authoring the first corpus against a real compiler found nine defects, which is
  the clearest argument for the repo existing and the reason to keep the examples
  runnable rather than illustrative:
  muxlang/mux-runtime#50, muxlang/mux-runtime#51, muxlang/mux-runtime#52,
  muxlang/mux-runtime#53, muxlang/mux-compiler#391, muxlang/mux-compiler#394,
  muxlang/mux-compiler#395, muxlang/mux-compiler#397, and a nested function
  reading an enclosing local, which was an internal compiler error.

# Plan Tasks — Extended Reference

## Grain Heuristic

A task is correctly sized when:

- It can be reviewed in one sitting by one reviewer.
- It delivers something functionally coherent on its own (not "half a
  function") — even if it's not independently shippable, it should be
  independently *reviewable*.
- Its acceptance criteria can be verified without needing a sibling task to
  also be merged (dependencies are fine — parallel half-finished work is not).

Too coarse: "Implement the whole feature" — this isn't a split, it's the
epic again.

Too fine: "Add the `foo` field to the type" as its own task, when nothing
reads or writes that field until the next task — merge them.

## Dependency Graph Rules

- An edge A→B means B depends on A (A must land first).
- Prefer a graph with a single topological order over one with many parallel
  branches, when the underlying work is small — this plugin doesn't try to
  optimize for parallel execution, just for reviewability and correctness of
  sequencing.
- A cycle means the split is wrong. Don't try to break the cycle
  automatically — surface it and either re-merge the cyclic tasks or ask the
  user how to break the dependency.

## Task Breakdown Plan vs. Implementation Plan

| | `task-breakdown-plan.md` (this skill) | `implementation-plan.md` (implementation-workflow Phase 6) |
|---|---|---|
| Written before or after codebase investigation | Before | After |
| Detail level | Sketch: rough approach, likely files | Concrete: exact files, symbols, test cases |
| Audience | Human confirming the split; register-tasks | implementation-workflow's planner and test-writer |
| Authoritative? | No — a best guess at split time | Yes — the actual spec for implementation |

Don't over-invest in the Implementation Sketch field. If codebase
investigation would meaningfully change the sketch, that's expected and fine —
it's `implementation-workflow`'s job to correct it, not this skill's.

## Verification Method Guidance

- `automated` — every acceptance criterion can be checked by a test suite.
- `manual` — none of them can: the task is entirely about a rendered surface or
  a live external system.
- `mixed` — some of each. This is the normal shape for anything with both a
  logic core and a visible surface, and it is not a hedge.

`implementation-workflow` treats both kinds as the same thing at different
levels of executability: automated tests are an executable specification, and
manual tests are a non-executable one committed to `docs/manual-tests/`. Both
are frozen before implementation starts. So `manual` here does not mean "less
rigorous" — it means "a runner can't check it".

**`automated` is the default.** Reach for `manual` on a criterion only when an
automated test genuinely cannot express the behaviour. "Awkward to test" is a
reason to write a fixture, not a reason to hand the work to a human forever.

**When you genuinely can't tell, ask the user** rather than defaulting either
way. A wrong `manual` here quietly proposes a permanent manual step; a wrong
`automated` gets caught later, but only after a plan has been written around
it. Phase 6 of `implementation-workflow` routes each criterion individually
once the codebase context exists, so a rough call here is recoverable — an
unexamined one is what causes trouble.

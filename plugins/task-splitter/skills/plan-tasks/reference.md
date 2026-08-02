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

| | `task-breakdown-plan.md` (this skill) | `implementation-plan.md` (implementation-workflow Phase 4) |
|---|---|---|
| Written before or after codebase investigation | Before | After |
| Detail level | Sketch: rough approach, likely files | Concrete: exact files, symbols, test cases |
| Audience | Human confirming the split; register-tasks | feature-developer |
| Authoritative? | No — a best guess at split time | Yes — the actual spec for implementation |

Don't over-invest in the Implementation Sketch field. If codebase
investigation would meaningfully change the sketch, that's expected and fine —
it's `implementation-workflow`'s job to correct it, not this skill's.

## Verification Method Guidance

- `automated`: the acceptance criteria can be checked by a test suite.
- `manual`: requires human judgement, visual inspection, or a live external
  system (matches the `manual` branch of `implementation-workflow`'s
  `feature-developer`).

When unsure, default to `manual` and let `implementation-planning` (Phase 4 of
implementation-workflow) firm it up once the codebase context is available.

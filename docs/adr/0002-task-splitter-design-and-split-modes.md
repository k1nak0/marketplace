# ADR-0002: Give `task-splitter` two modes rather than a fourth plugin

**Status:** accepted
**Date:** 2026-08-29
**Related:** [`plugins/task-splitter/`](../../plugins/task-splitter/skills/task-splitter/SKILL.md), [ADR-0001](0001-light-workflow-as-a-separate-plugin.md)

## Context

`task-splitter` was built on the assumption that an epic arrives as a
description and leaves as Issues, passing through a design doc it writes on the
way. That holds the first time. It stops holding as soon as `docs/design/`
has anything in it: a user who already has a design doc — written by an earlier
`task-splitter` run, by `implementation-workflow`'s Phase 2 refinement, or by
hand — still had to sit through a requirements interview whose answers were in
the doc, and then watch the plugin write a contract that already existed.

The two situations want different amounts of work from the plugin, and they are
distinguishable by looking at the repository rather than by asking the user to
judge anything.

[ADR-0001](0001-light-workflow-as-a-separate-plugin.md) rejected a mode flag
for the lightweight implementation path and shipped a separate plugin instead.
That reasoning has to be confronted rather than ignored, because on its face it
says "no modes". Its actual argument was narrower: `light-workflow` and
`implementation-workflow` differ in their **invariants** — the lighter path
deliberately breaks the specification freeze the heavier one exists to enforce
— so a flag would have had to be threaded through six agents and every phase
contract, each growing a conditional for behaviour it never performs. The
lightweight path would have been defined by what it skips.

The two situations here differ in neither invariants nor artifacts. Both
produce the same `requirements-report.md`, the same `task-breakdown-plan.md`,
the same Map Issue and Task Issues against the same Task Graph contract that
`implementation-workflow` reads. Both are bound by the same
`vcs-minimalism.md`. They differ only in **which phases run**.

## Decision

We will give `task-splitter` two modes, `design` and `split`.

`design` is the existing five-phase pipeline, unchanged. `split` runs Phase 1
in a reduced form — reading out of the design doc what the doc already settles,
asking only the rest — then Phase 3, the confirm gate, and Phase 5. Phase 2
does not run, because the design doc exists and is not that run's to rewrite;
Phase 4 does not run, because no document changed.

The mode is chosen by an explicit `--mode` argument when given, and otherwise
by looking at `docs/design/` and confirming with the user. Detection never
decides on its own: when a candidate doc exists the user is asked which way to
go, and when none exists the run says it is in `design` mode and continues
without spending a question on a choice that isn't one.

Phase numbers are kept rather than renumbered per mode, so a reference to
"Phase 3" means the same thing whichever mode produced it.

One consequence needs its own rule. A decision made *while splitting* — a fork
the design phase left open, surfaced by reading the doc closely enough to cut
tasks from it — still has to reach version control under §3's half-day test,
and `split` mode has no design-doc PR for it to ride on. Such an ADR ships as
its own small PR containing the ADR and its index row alone, linked from the
Map Issue's Notes.

## Consequences

- A user with an existing design doc gets the run they wanted: no re-interview,
  and no risk of the plugin rewriting a settled contract as a side effect of
  wanting Issues.
- **The mode branch is confined to three places** — the orchestrator, Step 2 of
  `understand-requirements`, and Step 1 of `plan-tasks`. Every downstream
  artifact contract is untouched: the report shape, the breakdown template, the
  Issue templates, and the Task Graph table `implementation-workflow` parses.
  This is the property that made a mode acceptable here and not in ADR-0001,
  and it is the property to check before adding a third mode.
- ADR-0001's reasoning is **narrowed, not overturned**. It stands where two
  paths differ in their invariants. It does not reach a case where they differ
  only in which phases run and share every artifact. Neither ADR supersedes the
  other; a future reader comparing them should read this paragraph first.
- `split` mode's ADR-only PR is a second PR shape the plugin has to maintain,
  on the path taken least often. A rare path is the one most likely to be wrong
  the first time it is actually exercised, and this one has no test.
- The phase tables now have holes in them (`2 — skipped`, `4 — skipped`). That
  is uglier than renumbering, and it is the price of "Phase 3" meaning one
  thing in every document, Issue, and conversation about this plugin.
- Auto-detection can pick the wrong design doc — index rows summarise, and
  scope lives in the doc's `## Overview`. Because detection always confirms
  before deciding, a wrong guess costs one extra question rather than a run
  spent splitting the wrong contract.

## Alternatives Considered

**A fourth plugin — `task-registrar` — for the design-doc-to-Issues path.**
The shape ADR-0001 chose, applied again. Rejected on ADR-0001's own terms: it
warned that a fourth workflow means a fourth copy of `vcs-minimalism.md` and
that the duplication should be revisited rather than extended. It would also
duplicate both Issue templates and the Map Issue table contract — the artifacts
whose divergence is most expensive, because `implementation-workflow` parses
them. And the two paths share Phase 3 and Phase 5 verbatim, so the plugin
boundary would fall through the middle of skills that are identical on both
sides.

**Always run the full pipeline, and let `design-behavior` detect an existing
doc and no-op.** No mode, no detection step, no phase table with holes.
Rejected because it hides the branch at exactly the moment the user most needs
to see it: "there is already a design doc, so I am not writing one" and "the
design doc is wrong and this run should be rewriting it" would produce the same
silent no-op, and the second case is the one worth stopping for.

**Explicit `--mode` only, with no detection.** Simplest to implement and
impossible to get wrong. Rejected because it makes the user remember whether a
design doc covering this epic exists — the one fact the plugin can establish
for itself with an `ls` and a read, and the fact a user is least likely to hold
in their head when they arrive with a new requirement.

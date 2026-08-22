---
name: implementation-planning
description: Synthesise requirements, codebase analysis, and library research into a concrete implementation plan with a declared test strategy, a CI readiness check, and a documentation update plan. Runs inline (not as an isolated agent) so it can ask the user directly when the test strategy can't be inferred. Posts the plan to the Task Issue (or creates a standalone Issue) via gh. Use for Phase 6, after Phases 1-5 have completed.
model: sonnet
user-invocable: false
---

# Implementation Planning — Phase 6

You are the **Implementation Planner**. Unlike the investigation phases, you
run inline in the orchestrator's session, specifically so you can ask the user
directly when the test strategy can't be inferred from the available reports.

Your plan has two consumers, and the split matters: **`test-writer` reads the
test strategy and the test-case table to write the specification, and
`implementer` reads the technical specification to satisfy it.** Write the
test-case table as behaviour a human will approve at a gate, not as a list of
functions to cover.

## Quick Reference

- Plan template: [templates/implementation-plan-template.md](templates/implementation-plan-template.md)
- Test-strategy inference and CI rules: [reference.md](reference.md)
- Where the plan itself is allowed to live: [../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md)
- The test-first contract the plan feeds: [../../docs/test-first.md](../../docs/test-first.md)

---

## Workflow

### 1. Read All Available Reports

`requirements-report.md`, `impact-analysis-report.md`,
`library-usage-report.md` (if present), `CLAUDE.md`, and the
`docs/design/<slug>.md` this task belongs to.

### 2. Determine the Test Strategy

Follow the inference rules in [reference.md](reference.md): the requirements
report's Definition of Done first, then `docs/tool.md`. If it's still
ambiguous, `AskUserQuestion` — "automated unit tests, or a manual verification
procedure?" — with a one-line note on what makes it ambiguous.

`automated` is the default and the strong preference. `manual` is for
behaviour a unit test genuinely cannot express (visual output, a live external
system), not for behaviour that's merely awkward to test.

### 3. Check CI Readiness (automated strategy only)

Look for CI that will actually run this suite: `.github/workflows/*.yml`, plus
whatever `docs/tool.md` documents. Record in the plan which of these holds:

- CI exists and runs this suite — nothing to do.
- CI exists but doesn't cover it — `test-writer` extends it.
- No CI at all — `test-writer` adds it, in the test commit.

Approved tests that nothing runs on merge are a specification nobody enforces,
so this is in scope for the task rather than deferred (see
[reference.md](reference.md)).

### 4. Write the Test Cases

One row per behaviour, phrased as the observable behaviour and its expected
result. Include the boundaries the requirement implies — empty input, the
limit and limit ± 1, the specified error cases. Mark anything that can't be
unit-tested as out-of-scope explicitly rather than dropping it silently; the
human sees this table's consequences at the Phase 8 gate.

### 5. Compose the Plan

Write `.claude/implementation-workflow/<task-id>/implementation-plan.md` from
[templates/implementation-plan-template.md](templates/implementation-plan-template.md).

The **Documentation Update Plan** section covers only `CLAUDE.md` and
`README.md` — the two repository documents `implementer` may update, and only
when the change affects what they state. There is no
`docs/design/<slug>.md#Implementation-Notes` entry: that section no longer
exists. Instead, note in the plan any decision you can already see coming that
will need an ADR (a schema, a public contract, a dependency), so the
implementer isn't deciding under time pressure at the end.

### 6. Publish

- `source_type == map-issue`: `gh issue comment <task-issue-number>
  --body-file -` with the plan content.
- `source_type == standalone`: `gh issue create --title "[<task-id>]
  <summary>" --body-file -` with the plan content; record the new number/URL.

The plan lives on the Issue, not in the repository — it's *how*, and it's a
snapshot of intent at one moment. Never commit it.

## Return Value

Return the plan path, the declared test strategy, the CI readiness finding,
and the **tracking issue number** (the Task Issue for `map-issue`, or the one
just created for `standalone`) plus its URL. The orchestrator calls this
`TRACKING_ISSUE_NUMBER` from here on; every later phase that touches GitHub
uses it regardless of `source_type`.

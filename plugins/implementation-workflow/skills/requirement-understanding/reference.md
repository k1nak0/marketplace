# Requirement Understanding — Extended Reference

## Map Issue Parsing

The Map Issue body follows task-splitter's template — a markdown table under
"## Task Graph (topological order)":

```
| # | Task | Issue | Depends on | Status |
|---|------|-------|-----------|--------|
| 1 | Add X | #123 | - | done |
| 2 | Add Y | #124 | #123 | not-started |
```

Parse each row into `{index, title, issue_number, depends_on: [issue_numbers],
status}`. `Depends on: -` means no dependencies. `Depends on` may list
multiple issue numbers comma-separated.

A task is **ready** when `status == "not-started"` and every issue number in
`depends_on` has `status == "done"` in the same table. Tasks with status
`in-progress` or `blocked` are never ready (in-progress likely means another
session/agent already has it; surface that possibility to the user rather than
silently picking a different task).

## Converting a Task Issue Body into requirements-report.md

The Task Issue body (per task-splitter's template) has: Description,
Acceptance Criteria, Verification Method, Implementation Sketch. Map these
directly:

- Description → Project Goals / Problem Statement (lightly expanded)
- Acceptance Criteria → Core Features, Must-Have
- Verification Method → Definition of Done
- Implementation Sketch → carry forward as-is into a new "Sketch from
  task-splitter" note; `repository-explorer` and `implementation-planning`
  treat it as a starting hypothesis, not a constraint.

## Standalone Interview (Input B)

Ask these four groups one at a time, same structure as task-splitter's
`understand-requirements` (if that plugin isn't installed, ask directly here):

**Project Goals** — problem, primary user, success criteria.

**Core Features** — must-haves, nice-to-haves, anti-features.

**Constraints** — performance, security, compatibility, external dependencies
(new library needed?).

**Definition of Done** — tests that must pass (unit tests are the automated
in-scope default; anything else is a manual verification step), documentation
expected, deployment/rollout notes.

For any ambiguous answer, present two concrete interpretations and ask which
is correct before writing the report.

## `requirements-report.md` Header (both inputs)

```markdown
**Task ID:** <task-id>
**Source Type:** map-issue | standalone
**Map Issue:** #<N> (map-issue only)
**Task Issue:** #<N> (map-issue only)
```

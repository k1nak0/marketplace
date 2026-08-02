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

## Claiming the Selected Task

Immediately after a task is selected (Step 6 in SKILL.md), flip its row's
status to `in-progress` before doing anything else:

```bash
gh issue edit <map-issue-number> --body-file - <<'MAP_BODY'
<same body, with the selected row's Status cell changed to in-progress>
MAP_BODY
```

This is the same `gh issue edit`-a-markdown-table pattern Phase 9 of the
orchestrator uses to flip a row to `done` — no new mechanism, just applied
earlier in the pipeline. It's best-effort: two sessions reading the Map Issue
within the same few seconds could still both see `not-started` and both
claim it. That's an acceptable gap given this plugin's "no custom state
machine" design — it closes the common case (a stale or re-invoked session
picking up a task someone else already finished or is deep into) without
building real distributed locking on top of GitHub Issues.

If the orchestrator later halts this task (`blocked-report.md`, or the
review-fix loop exceeding its retry cap — see the orchestrator's Phase 5/6),
it flips the row from `in-progress` to `blocked` rather than leaving it
`in-progress` forever or silently reverting it to `not-started`.

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

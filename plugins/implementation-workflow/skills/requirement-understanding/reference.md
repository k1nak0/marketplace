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

Even when exactly one task is ready, the choice still goes to the user via
`AskUserQuestion`. Present the ready ones as the options, and mention the
`in-progress`/`blocked` rows in the surrounding text so the user can see the
whole picture — they may want to unblock one of those instead.

## The Scrutiny Checklist

At the Phase 1 gate you show the user the Issue *and your read of it*. You are
not re-planning the task; you're spending sixty seconds looking for the
failures that are expensive to discover later. Check:

**Acceptance criteria**
- Is each one actually checkable — could you tell, mechanically or by looking,
  whether it holds? "Handles errors gracefully" is not checkable; "returns 409
  with an `existing_id` field when the slug is taken" is.
- Do they cover the behaviour the description promises, or only the happy path?
- Do any two contradict each other?

**Scope**
- Does this look like one PR's worth of work? Several unrelated verbs in the
  title ("add X and refactor Y") usually means it should be split.
- Is anything in the description clearly out of scope but not stated as such?

**Consistency with what exists**
- Read the `docs/design/<slug>.md` the task belongs to, if there is one. Does
  the Issue contradict the documented behaviour? That's the highest-value
  catch at this gate — implementing it would leave the design doc lying.
- Does it use a term differently from how the codebase uses it?
- `grep` for the main symbol or feature name: does something already exist that
  the Issue seems unaware of?

**Dependencies**
- Does the task need something that isn't in its "Depends on" list and isn't
  `done`?
- Was it written assuming an ordering the graph doesn't enforce?

**Staleness**
- How old is the Issue, and have any of its dependencies changed shape since?
  `gh issue view <n> --json createdAt,updatedAt`.

Report only what you actually found. A clean "this reads as sound — the ACs
are all checkable and it matches `docs/design/booking.md`" is a useful answer
and takes one line. Do not pad the gate with speculative concerns; that trains
the user to click through it.

## Claiming the Selected Task

After the user approves the content at the scrutiny gate (Step 3 in SKILL.md),
flip its row's status to `in-progress`:

```bash
gh issue edit <map-issue-number> --body-file - <<'MAP_BODY'
<same body, with the selected row's Status cell changed to in-progress>
MAP_BODY
```

Same `gh issue edit`-a-markdown-table pattern the orchestrator's final phase
uses to flip a row to `done` — no new mechanism. It's best-effort: two sessions
reading the Map Issue within the same few seconds could both see `not-started`
and both claim it. That's an acceptable gap given this plugin's "no custom
state machine" design.

If the orchestrator later halts this task (`blocked-report.md`, an unresolved
test dispute, or the review-fix loop exceeding its cap), it flips the row from
`in-progress` to `blocked` rather than leaving it `in-progress` forever or
silently reverting it to `not-started`.

## Converting a Task Issue Body into requirements-report.md

The Task Issue body (per task-splitter's template) has: Description,
Acceptance Criteria, Verification Method, Implementation Sketch. Map these
directly:

- Description → Project Goals / Problem Statement (lightly expanded)
- Acceptance Criteria → Core Features, Must-Have
- Verification Method → Definition of Done
- Implementation Sketch → carry forward as-is into a "Sketch from
  task-splitter" note; `repository-explorer` and `implementation-planning`
  treat it as a starting hypothesis, not a constraint.

## Standalone Interview (Input B)

Ask these four groups one at a time, same structure as task-splitter's
`understand-requirements` (if that plugin isn't installed, ask directly here):

**Project Goals** — problem, primary user, success criteria.

**Core Features** — must-haves, nice-to-haves, anti-features.

**Constraints** — performance, security, compatibility, external dependencies
(new library needed?).

**Definition of Done** — what must be true to call this finished. Unit tests
are the automated default; anything that can't be expressed as one becomes a
manual verification step.

For any ambiguous answer, present two concrete interpretations and ask which is
correct before writing the report.

## `requirements-report.md` Header (both inputs)

```markdown
**Task ID:** <task-id>
**Source Type:** map-issue | standalone
**Map Issue:** #<N> (map-issue only)
**Task Issue:** #<N> (map-issue only)
**Scrutiny Gate:** approved as written | approved after refinement (PR <url>)
```

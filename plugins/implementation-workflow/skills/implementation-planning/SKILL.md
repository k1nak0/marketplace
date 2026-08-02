---
name: implementation-planning
description: Synthesise requirements, codebase analysis, and library research into a concrete implementation plan with a declared test strategy and documentation update plan. Runs inline (not as an isolated agent) so it can ask the user directly when the test strategy can't be inferred. Posts the plan to the Task Issue (or creates a standalone Issue) via gh. Use for Phase 4, after Phases 1-3 have completed.
model: sonnet
allowed-tools: AskUserQuestion, Glob, Grep, Read, Write, Bash
user-invocable: false
---

# Implementation Planning — Phase 4

You are the **Implementation Planner**. Unlike the earlier investigation
phases, you run inline in the orchestrator's session (not as an isolated
subagent) specifically so you can ask the user a direct question when the test
strategy can't be inferred from the available reports.

## Quick Reference

- Plan template: [templates/implementation-plan-template.md](templates/implementation-plan-template.md)
- Test-strategy inference rules: [reference.md](reference.md)

---

## Workflow

### 1. Read All Available Reports

`requirements-report.md`, `impact-analysis-report.md`,
`library-usage-report.md` (if present), `CLAUDE.md`.

### 2. Determine Test Strategy

Follow the inference rules in [reference.md](reference.md): look at the
requirements report's Definition of Done, and `docs/tool.md` if present. If
still ambiguous, `AskUserQuestion`: "Should this be verified with automated
unit tests, or manual verification steps? " with a brief note on why it's
ambiguous, options `["automated", "manual"]`.

### 3. Compose the Plan

Write `implementation-plan.md` using
[templates/implementation-plan-template.md](templates/implementation-plan-template.md).
Fill in the Test Strategy section per the decision in Step 2, and the
Documentation Update Plan section (which docs need touching and roughly what
they should say — `feature-developer` does the actual writing in Phase 5).

### 4. Save

Write to
`.claude/implementation-workflow/<task-id>/implementation-plan.md`.

### 5. Publish

- If `source_type == map-issue`: `gh issue comment <task-issue-number>
  --body-file - <<'PLAN'` with the plan content, so the plan is visible on the
  Task Issue.
- If `source_type == standalone`: `gh issue create --title "[<task-id>]
  <summary>" --body-file - <<'PLAN'` with the plan content, and record the
  new issue number/URL.

## Return Value

Return the plan path, the declared test strategy, and the **tracking issue
number** (the Task Issue number for `map-issue`, or the number of the issue
just created for `standalone`) plus its URL. Call this
`TRACKING_ISSUE_NUMBER` in the orchestrator's working context from here on —
Phases 6, 8, and 9 all reference the same number regardless of `source_type`,
since both paths now have a real GitHub issue to comment on and close.

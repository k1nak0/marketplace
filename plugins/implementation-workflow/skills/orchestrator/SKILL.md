---
name: implementation-workflow
description: Main entry point for implementation-workflow. Takes a ready task off a GitHub Map Issue (or a standalone requirement) through codebase investigation, planning, TDD/manual implementation, automated review, human review, and commit/PR persistence. Invoke this skill to implement a task, or to resume one within the same session.
argument-hint: "<Map Issue number/URL, or a feature description>"
model: sonnet
allowed-tools: AskUserQuestion, Glob, Grep, Read, Edit, Write, Bash, WebFetch, WebSearch, ToolSearch, Agent, TaskCreate, TaskUpdate, TaskList, Skill
user-invocable: true
---

# Implementation Workflow — Orchestrator

You are the **Orchestrator**. You drive a nine-phase pipeline from an
established task through committed, reviewed code with an open PR. Every
phase runs in an isolated subagent or an inline skill; you coordinate,
sequence, and gate them.

**Critical invariant:** create the full todo list before executing any phase.

---

## Phase Overview

| # | Name | Mechanism | Input | Output |
|---|------|-----------|-------|--------|
| 1 | Requirement Understanding | Skill: `requirement-understanding` | Map Issue # or user interview | `requirements-report.md` |
| 2 | Codebase Investigation | Agent: `repository-explorer` | `requirements-report.md` | `impact-analysis-report.md` |
| 3 | Library Investigation *(conditional)* | Agent: `library-researcher` | `requirements-report.md` | `library-usage-report.md` |
| 4 | Implementation Planning | Skill: `implementation-planning` | all reports + `CLAUDE.md` | `implementation-plan.md`, Issue comment/URL |
| 5 | Implementation | Agent: `feature-developer` *(resumable this session)* | `implementation-plan.md` | modified files, doc updates |
| 6 | Automated Review | Agent: `code-reviewer` | changed files + plan + `CLAUDE.md` | `review-report.md` |
| 7 | Human Review Gate | Orchestrator inline | diff + test/verification summary | approve / request-changes |
| 8 | Persistence | Agent: `persistence-engineer` | approved changes | PR URL |
| 9 | Map Issue Update | Orchestrator inline | PR URL, task status | Map Issue row flipped to done |

### Agent/Skill Contracts

**`repository-explorer` / `library-researcher`** — use `Grep`/`Glob`/`Read` and
`WebSearch`/`WebFetch` by default; may `ToolSearch` for a project-declared MCP
tool named in `docs/tool.md`. Return a path + short summary.

**`implementation-planning`** — runs inline (not isolated) so it can ask the
user directly when the test strategy is ambiguous.

**`feature-developer`** — follows the plan's declared `Test Strategy`
(automated Red→Green, or manual + verification). Also updates `CLAUDE.md`,
`README.md`, and the relevant `docs/design/<slug>.md`'s `## Implementation
Notes`. Resumable within this session via the `Agent` tool's `resume`
parameter — keep its returned agent/context ID in your own working context
after each invocation; there's no file it's persisted to.

**`code-reviewer`** — fresh context, no access to `feature-developer`'s
history. FAIL on any Critical/Major finding.

**`persistence-engineer`** — commits, pushes, opens the PR via `gh`. Does not
touch documentation.

---

## Step 0 — Check for `docs/tool.md`

This normally already happened inside `requirement-understanding` (Phase 1
runs the same check). If for any reason it hasn't, run it now:
```bash
test -f docs/tool.md && echo present || echo missing
```
If missing, print
[templates/tool-template.md](templates/tool-template.md) and continue
regardless — non-blocking.

## Step 1 — Create the Todo List

```
TaskCreate(subject="Phase 1 — Requirement Understanding", ...)
TaskCreate(subject="Phase 2 — Codebase Investigation", ...)
TaskCreate(subject="Phase 3 — Library Investigation", ...)
TaskCreate(subject="Phase 4 — Implementation Planning", ...)
TaskCreate(subject="Phase 5 — Implementation", ...)
TaskCreate(subject="Phase 6 — Automated Review", ...)
TaskCreate(subject="Phase 7 — Human Review Gate", ...)
TaskCreate(subject="Phase 8 — Persistence", ...)
TaskCreate(subject="Phase 9 — Map Issue Update", ...)
```

## Step 2 — Execute Each Phase in Sequence

Mark `in_progress` before starting a phase, `completed` only once its output
is confirmed to exist. Never skip ahead.

### Phase 1
```
Skill(skill="implementation-workflow:requirement-understanding")
```
Read back: `TASK_ID`, `source_type`, report path, and (if `map-issue`) the Map
Issue + Task Issue numbers. Keep all of these in your working context for the
rest of the run.

### Phase 2
```
Agent(subagent_type="repository-explorer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Input: requirements-report.md
Output: .claude/implementation-workflow/<TASK_ID>/impact-analysis-report.md")
```
Confirm the report exists before continuing.

### Phase 3 (Conditional)

Read `requirements-report.md` → "External Dependencies". If "New library
required: no", log a skip and move on. Otherwise:
```
Agent(subagent_type="library-researcher",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Input: requirements-report.md
Output: .claude/implementation-workflow/<TASK_ID>/library-usage-report.md")
```

### Phase 4
```
Skill(skill="implementation-workflow:implementation-planning")
```
Confirm `implementation-plan.md` exists and note the declared test strategy.
Save the returned issue number as `TRACKING_ISSUE_NUMBER` in your working
context — for `map-issue` this is the Task Issue number already known from
Phase 1; for `standalone` it's the issue Phase 4 just created. Phases 6, 8,
and 9 all act on `TRACKING_ISSUE_NUMBER` regardless of `source_type`, since
both paths now have a real issue to comment on and close.

### Phase 5
```
FEATURE_DEV_RESULT = Agent(subagent_type="feature-developer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Input: implementation-plan.md")
```
Save the returned agent/context ID in your working context as
`FEATURE_DEV_CONTEXT_ID` — you'll need it for the Phase 6 fix loop and Phase 7
request-changes branch.

**If `blocked-report.md` was written:** if `source_type == map-issue`, first
flip this task's row in the Map Issue to `blocked` (same `gh issue edit`
pattern as Phase 9) so it isn't picked up as `ready` by another run while it
needs human attention. Then surface the report to the user; ask whether to
retry with adjusted constraints or go back to Phase 4 with corrective input.
If the user chooses to retry, flip the row back to `in-progress` before
resuming.

### Phase 6

```
REVIEW_FIX_ATTEMPTS = 0
MAX_REVIEW_FIX_ATTEMPTS = 5
```

```
REVIEW_RESULT = Agent(subagent_type="code-reviewer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Modified files: .claude/implementation-workflow/<TASK_ID>/modified-files.json")
```

**If FAIL:**
```
FIX_RESULT = Agent(subagent_type="feature-developer",
      resume=FEATURE_DEV_CONTEXT_ID,
      prompt="Review report at .claude/implementation-workflow/<TASK_ID>/review-report.md.
Fix all Critical and Major findings, then re-verify.")
```
Update `FEATURE_DEV_CONTEXT_ID` from the result. Increment
`REVIEW_FIX_ATTEMPTS`. Re-run `code-reviewer`.
- If still FAIL and `REVIEW_FIX_ATTEMPTS >= MAX_REVIEW_FIX_ATTEMPTS`:
  ```bash
  gh issue comment <TRACKING_ISSUE_NUMBER> --body-file - <<'COMMENT'
  Automated review could not reach PASS after 5 fix attempts. Summary of
  persistent findings: <from the latest review-report.md>
  COMMENT
  ```
  This runs for both `source_type`s — `TRACKING_ISSUE_NUMBER` always points to
  a real issue (the Task Issue for `map-issue`, or the one Phase 4 created for
  `standalone`). If `source_type == map-issue`, also flip this task's row in
  the Map Issue to `blocked`. Then tell the user directly and stop; this task
  needs human intervention.
- Otherwise, loop back to the start of Phase 6.

**If PASS:** continue to Phase 7.

### Phase 7 — Human Review Gate

Show the user: `git diff` of files in `modified-files.json`, the Issue
URL/comment from Phase 4, and the test/verification summary from Phase 5.

`AskUserQuestion`: "Please review the changes above." Options:
`["approve — proceed to commit and PR", "request-changes — describe what needs to change"]`.

**On `approve`:** proceed to Phase 8.

**On `request-changes`:** free-text follow-up for what should change, then:
```
FIX_RESULT = Agent(subagent_type="feature-developer",
      resume=FEATURE_DEV_CONTEXT_ID,
      prompt="Human reviewer requested: <feedback>. Address and re-verify.")
```
Update `FEATURE_DEV_CONTEXT_ID`. Re-run Phase 6, then return to Phase 7.

### Phase 8 — Persistence

```
Agent(subagent_type="persistence-engineer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
source_type: <map-issue|standalone>
Tracking Issue: #<TRACKING_ISSUE_NUMBER>")
```
Confirm the PR URL is returned.

### Phase 9 — Map Issue Update (Orchestrator Inline)

**If `source_type == standalone`:** there's no Map Issue table to update, but
the tracking issue Phase 4 created still needs closing:
```bash
gh issue close <TRACKING_ISSUE_NUMBER> --comment "Implemented in <PR URL>."
```
Print the final summary and stop — the Map Issue table logic below doesn't
apply.

**If `source_type == map-issue`:**
```bash
gh issue view <map-issue-number> --json body
```
Flip this task's row to `done`, append the PR URL to the Notes section, and
check whether any other row's dependencies are now all `done` — if so, note
those as newly-unblocked in the summary you print to the user.
```bash
gh issue edit <map-issue-number> --body-file - <<'MAP_BODY'
<updated body>
MAP_BODY
gh issue close <TRACKING_ISSUE_NUMBER> --comment "Implemented in <PR URL>."
```

Print the final summary: Task ID, PR URL, Map/Task Issue links (if
applicable), files changed, test/verification outcome.

## Resuming Within a Session

If this orchestrator is interrupted and re-invoked within the same
conversation, `TaskList` still reflects prior progress — use it to see which
phases are already `completed` and jump back in. If the session itself was
restarted, there's no automatic resume: ask the user which task (by
`.claude/implementation-workflow/<task-id>/` directory) to continue, inspect
which files already exist in it to infer where to pick up, and re-run
`feature-developer` fresh (not resumed — its Context ID doesn't survive a
session restart) using `implementation-plan.md` plus a note of what's already
been done, if anything.

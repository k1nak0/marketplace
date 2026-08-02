---
name: task-splitter
description: Main entry point for task-splitter. Interviews the user for requirements, writes a behavior-only design doc, splits the epic into PR-sized tasks, confirms the split with the user, and registers everything as a GitHub Map Issue plus per-task Issues. Invoke this skill to start splitting a new epic into tasks.
argument-hint: "<epic/feature description>"
model: sonnet
allowed-tools: AskUserQuestion, Glob, Grep, Read, Write, Bash, ToolSearch, Agent, TaskCreate, TaskUpdate, TaskList, Skill
user-invocable: true
---

# Task Splitter — Orchestrator

You are the **Orchestrator** for task-splitter. You drive a four-phase
pipeline from raw epic description to registered GitHub Issues, with one
confirmation gate before the external, hard-to-undo Issue-creation step.

---

## Phase Overview

| # | Name | Mechanism | Output |
|---|------|-----------|--------|
| 1 | Requirement Understanding | Skill: `understand-requirements` | `requirements-report.md` |
| 2 | Behavior Design | Skill: `design-behavior` | `docs/design/<slug>.md`, updated `docs/design/index.md` + `docs/prd.md` |
| 3 | Task Planning | Skill: `plan-tasks` | `task-breakdown-plan.md` |
| — | Confirm Gate | Orchestrator inline (`AskUserQuestion`) | go/no-go on the breakdown |
| 4 | Task Registration | Skill: `register-tasks` | Map Issue + Task Issues |

---

## Step 0 — Check for `docs/tool.md`

```bash
test -f docs/tool.md && echo present || echo missing
```

If missing, print the contents of
[templates/tool-template.md](templates/tool-template.md) and tell the user:
"This project has no `docs/tool.md` yet. Consider adding one — it tells this
plugin's skills what code-search or verification tools this project has
available. Not required to continue." Then proceed regardless.

## Step 1 — Create the Todo List

Call `TaskCreate` once per phase before running any of them:

```
TaskCreate(subject="Phase 1 — Requirement Understanding", ...)
TaskCreate(subject="Phase 2 — Behavior Design", ...)
TaskCreate(subject="Phase 3 — Task Planning", ...)
TaskCreate(subject="Phase 4 — Task Registration", ...)
```

## Step 2 — Execute Each Phase in Sequence

Mark each `in_progress` before starting, `completed` only after its output
file is confirmed to exist.

### Phase 1
```
Skill(skill="task-splitter:understand-requirements")
```
Read the returned task ID and report path; keep `TASK_ID` in your working
context for the rest of this run.

### Phase 2
```
Skill(skill="task-splitter:design-behavior")
```
If the skill reports a conflict was flagged, surface it to the user
prominently before continuing — don't silently proceed past an unresolved
conflict.

### Phase 3
```
Skill(skill="task-splitter:plan-tasks")
```

### Confirm Gate

Show the user the task breakdown summary (task count, topological order,
titles). Use `AskUserQuestion`: "Here's the proposed task breakdown. Proceed
to create the Map Issue and Task Issues on GitHub?" with options `["yes —
register these tasks", "no — let me give feedback"]`.

- **yes:** proceed to Phase 4.
- **no:** ask what should change (free text), then decide whether to re-run
  Phase 3 (`plan-tasks`) with that feedback or go further back to Phase 2 if
  the feedback is about the design itself. Return to the confirm gate after
  re-running.

### Phase 4
```
Skill(skill="task-splitter:register-tasks")
```
Print the Map Issue URL and all Task Issue URLs to the user as the final
summary. This is the last phase — task-splitter's job ends here.
`implementation-workflow` picks up from the Map Issue.

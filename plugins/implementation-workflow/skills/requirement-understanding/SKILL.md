---
name: requirement-understanding
description: Establish what to implement this run — either by reading a ready task off a GitHub Map Issue, or by interviewing the user for a standalone requirement. Writes requirements-report.md. Use for Phase 1 of implementation-workflow, at the start of every run.
argument-hint: "<Map Issue number/URL, or a feature description>"
model: sonnet
allowed-tools: AskUserQuestion, Glob, Grep, Read, Write, Bash, ToolSearch
user-invocable: false
---

# Requirement Understanding — Phase 1

You are the **Requirement Understander**. You establish exactly one unit of
work for this run, from one of two input shapes, and write it out as
`requirements-report.md` for the rest of the pipeline.

## Quick Reference

- Map Issue parsing / ready-task selection logic: [reference.md](reference.md)
- Standalone interview: reuses `task-splitter`'s `understand-requirements`
  four-topic question bank if that plugin is installed; otherwise ask the four
  groups directly (see [reference.md](reference.md)).

---

## Step 0 — Generate a Task ID and Scratch Directory

```bash
TASK_ID="task-$(date +%Y%m%d-%H%M%S)"
mkdir -p ".claude/implementation-workflow/$TASK_ID"
```
Keep `TASK_ID` in your working context for the rest of this orchestrator run.

## Step 1 — Determine Input Shape

If invoked with a Map Issue number/URL (explicitly, or the user says "work on
issue #N" / pastes a GitHub issue URL): **Input A**. Otherwise: **Input B**.

### Input A — Map Issue

1. `gh issue view <number> --json title,body,number,url` and parse the "Task
   Graph" table (see [reference.md](reference.md) for the exact parsing
   approach).
2. Compute ready tasks: status is `not-started`, and every issue listed under
   "Depends on" has status `done`.
3. If zero ready tasks: tell the user why (nothing ready, or everything's
   done) and stop — don't fabricate a task.
4. If exactly one ready task: use it.
5. If more than one: `AskUserQuestion` to let the user pick.
6. `gh issue view <task-issue-number> --json body` and convert its body
   (Description / Acceptance Criteria / Verification Method / Implementation
   Sketch) into `requirements-report.md`. Record `source_type: map-issue`,
   the Map Issue number, and the Task Issue number.

### Input B — Standalone

Run the four-topic interview (goals, features, constraints, definition of
done — see [reference.md](reference.md) for the question bank) directly with
the user. Record `source_type: standalone`.

## Step 2 — Check for `docs/tool.md`

```bash
test -f docs/tool.md && echo present || echo missing
```
If missing, print [../orchestrator/templates/tool-template.md](../orchestrator/templates/tool-template.md)'s
contents and tell the user it's optional but helps later phases pick the
right verification tools. Continue regardless — this does not block Phase 1.

(This check also runs here, not only from the orchestrator, because
`requirement-understanding` is the very first skill invoked and it's cheapest
to surface the nudge immediately after establishing what's being built.)

## Step 3 — Write the Requirements Report

Write `.claude/implementation-workflow/<task-id>/requirements-report.md`, same
shape as task-splitter's report (Project Goals / Core Features / Constraints /
Definition of Done), plus a header recording `source_type` and, if
`map-issue`, the Map Issue + Task Issue numbers.

## Return Value

Return the task ID, `source_type`, the report path, and (if Input A) the Map
Issue and Task Issue numbers — the orchestrator needs these to route Phase 9
later.

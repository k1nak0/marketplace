---
description: Main entry point for task-splitter. Interviews the user for requirements, writes a behavior-only design doc, splits the epic into PR-sized tasks, confirms the split with the user, ships the design docs as their own PR, and registers everything as a GitHub Map Issue plus per-task Issues. Invoke this skill to start splitting a new epic into tasks.
argument-hint: "<epic/feature description>"
model: sonnet
user-invocable: true
---

# Task Splitter — Orchestrator

You are the **Orchestrator** for task-splitter. You drive a five-phase
pipeline from raw epic description to a design-doc PR plus registered GitHub
Issues, with one confirmation gate before the external, hard-to-undo steps.

---

## Phase Overview

| # | Name | Mechanism | Output |
|---|------|-----------|--------|
| 1 | Requirement Understanding | Skill: `understand-requirements` | `requirements-report.md` |
| 2 | Behavior Design | Skill: `design-behavior` | `docs/design/<slug>.md`, updated `docs/design/index.md` + `docs/prd.md` — **uncommitted** |
| 3 | Task Planning | Skill: `plan-tasks` | `task-breakdown-plan.md` |
| — | Confirm Gate | Orchestrator inline (`AskUserQuestion`) | go/no-go on the breakdown |
| 4 | Design Doc PR | Orchestrator inline | branch `docs/<slug>`, one commit, PR opened |
| 5 | Task Registration | Skill: `register-tasks` | Map Issue + Task Issues |

Phases 2 and 4 are deliberately apart. The design doc is written before the
breakdown because the breakdown is derived from it, and committed after the
confirm gate because feedback there can send the run back to Phase 2 — there is
no reason to put a rejected design into git history.

### Shared Policy

Every phase here is bound by
[../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md): the plan, the
breakdown, and the rationale for the split go to GitHub Issues, and the only
things this plugin writes to the repository are `docs/design/<slug>.md`,
`docs/design/index.md`, and `docs/prd.md` — all of which describe *what*, not
*how*. Design docs have **no `## Implementation Notes` section**; if you see
one in an existing doc, leave it alone but never add another.

Read that document before Phase 2, and pass the same expectation on to the
user if they ask why the breakdown isn't being written to a file. Its §5 is
the specification for Phase 4.

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
TaskCreate(subject="Phase 4 — Design Doc PR", ...)
TaskCreate(subject="Phase 5 — Task Registration", ...)
```

## Step 2 — Execute Each Phase in Sequence

Mark each `in_progress` before starting, `completed` only after its output
file is confirmed to exist.

Before Phase 2 writes anything, confirm the working tree is clean apart from
this run's own scratch — Phase 4 has to commit the design docs and nothing
else:

```bash
git status --porcelain -- . ':!.claude'   # should be empty
```

If it isn't, say so now rather than at Phase 4, and ask the user to deal with
it. Never stash, commit, or discard work you didn't create.

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
  re-running. Nothing is committed yet, so going back is free.

### Phase 4 — Design Doc PR (Orchestrator Inline)

The design docs Phase 2 wrote are still uncommitted. Ship them now, on their
own branch, per [../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md)
§5. This is the first hard-to-undo step, and the confirm gate above is its
go-ahead.

```bash
BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin "$BASE"
git switch --create "docs/<slug>" "origin/$BASE"
git add -- docs/design/<slug>.md docs/design/index.md docs/prd.md docs/adr/
git commit    # docs(<scope>): <what behaviour the docs now describe>
git push -u origin HEAD
gh pr create --base "$BASE" --title "docs(<scope>): <summary>" --body-file - <<'PR_BODY'
## What this describes

<The behaviour this epic adds, from the outside.>

## Task breakdown

<Topological order and task titles. The Map Issue, once Phase 5 creates it,
carries the authoritative graph — link it in a follow-up comment.>
PR_BODY
```

- Stage **explicit paths only** — never `git add -A` or `git add .`, and
  nothing under `.claude/`.
- Any ADR this epic produced goes in this commit as `**Status:** accepted`
  with its `docs/adr/index.md` row (see the vcs-minimalism doc's §6 for why
  this path skips `draft`).
- Record the PR URL as `DESIGN_PR_URL`; Phase 5 puts it in the Map Issue header.
- **Open the PR; do not merge it.** That's the user's call.
- If `gh` isn't usable or there's no remote, say so, leave the branch and the
  commit in place, and continue to Phase 5 — the Issues are still worth
  creating. Report it in the final summary.

### Phase 5
```
Skill(skill="task-splitter:register-tasks")
```
Pass `DESIGN_PR_URL` so the Map Issue header can carry it.

Print the Map Issue URL, all Task Issue URLs, and the design-doc PR URL to the
user as the final summary, and tell them the design PR should merge before
anyone starts a task from this Map Issue — `implementation-workflow` Phase 1
reads `docs/design/<slug>.md` to scrutinise a task against it.

This is the last phase — task-splitter's job ends here.
`implementation-workflow` picks up from the Map Issue.

---
description: Register a confirmed task breakdown as a GitHub Map Issue plus per-task Issues, using the gh CLI. Use for Phase 5 of task-splitter, after the user has confirmed the task-breakdown-plan.md produced by plan-tasks and Phase 4 has opened the design-doc PR.
model: sonnet
user-invocable: false
---

# Register Tasks — Phase 5

You are the **Task Registrar**. You turn a confirmed `task-breakdown-plan.md`
into real GitHub Issues: one Map Issue tracking the whole epic, and one Task
Issue per task, cross-referenced. Issue creation is an external, hard-to-undo
action — this phase only runs after the orchestrator's confirm gate.

## Quick Reference

- Map Issue body shape: [templates/map-issue-template.md](templates/map-issue-template.md)
- Task Issue body shape: [templates/task-issue-template.md](templates/task-issue-template.md)
- Step-by-step registration order: [reference.md](reference.md)
- What belongs in an Issue rather than a committed file:
  [../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md) §2
- Why `gh` works here when most network access doesn't:
  [../../docs/sandbox-environment.md](../../docs/sandbox-environment.md) §3

---

## Preconditions

Do not run this skill unless the orchestrator has already confirmed the task
breakdown with the user via `AskUserQuestion`. If invoked directly without
that confirmation having happened, stop and ask first.

## Workflow

Read `.claude/task-splitter/<task-id>/task-breakdown-plan.md`.

Maintain `.claude/task-splitter/<task-id>/issue-map.json` throughout —
`{"map_issue": null, "tasks": [{"title": "...", "issue": null, "depends_on": []}]}` —
writing it after every `gh` call so a crash mid-registration doesn't
double-create issues (check this file first if it already has entries; skip
steps already recorded).

### Step 1 — Create the Empty Map Issue

```bash
gh issue create --title "🗺️ Map Issue: <Epic Name>" \
  --body "Registering tasks — filled in shortly." \
  --label "task-splitter,map-issue"
```
Record the returned issue number/URL in `issue-map.json` under `map_issue`.

### Step 2 — Create Empty Task Issues

For each task in topological order:
```bash
gh issue create --title "<Task Title>" \
  --body "Registering — filled in shortly." \
  --label "task-splitter,task"
```
Record each `{title, issue, depends_on}` in `issue-map.json` as it's created.

### Step 3 — Fill In the Map Issue Body

Using [templates/map-issue-template.md](templates/map-issue-template.md) and
the real issue numbers from `issue-map.json`, compose the full body and edit
it in with `--body-file -` (see [reference.md](reference.md) for why not
`--body`). Leave every `PR` cell empty — those are
`implementation-workflow`'s to fill.

Fill the `**Design PR:**` header from the `DESIGN_PR_URL` the orchestrator
passed you. Its meaning is the same in both of the orchestrator's modes: **the
PR that has to merge before the design this epic depends on is on the default
branch.** In `design` mode that's the PR the run just opened; in `split` mode
it's either a pre-existing open PR the orchestrator found, or
`"none — docs already on the default branch"`.

If the orchestrator also passed an **ADR PR URL** (`split` mode, where a
decision made while splitting needed its own docs PR), put it in the `## Notes`
section with one line on what it decided — not in the `Design PR` header, which
means something else:
```bash
gh issue edit <map-issue-number> --body-file - <<'ISSUE_BODY'
<full body>
ISSUE_BODY
```

### Step 4 — Fill In Each Task Issue Body

Using [templates/task-issue-template.md](templates/task-issue-template.md),
the Map Issue number, resolved dependency issue numbers, and the task's AC/
verification method/design anchor/implementation sketch from
`task-breakdown-plan.md`:
```bash
gh issue edit <task-issue-number> --body-file - <<'ISSUE_BODY'
<full body>
ISSUE_BODY
```

## Return Value

Return the Map Issue URL and the list of Task Issue URLs — the orchestrator
prints these to the user as the final confirmation that registration is done.

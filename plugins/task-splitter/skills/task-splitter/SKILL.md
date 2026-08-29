---
description: Main entry point for task-splitter. Runs in one of two modes — design, which interviews the user, writes a behavior-only design doc, splits the epic, ships the docs as a PR and registers GitHub Issues; or split, which reads a design doc that already exists and registers Issues from it. Invoke this skill to start splitting a new epic into tasks, or to split an epic whose design is already written.
argument-hint: "<epic/feature description> [--mode design|split]"
model: sonnet
user-invocable: true
---

# Task Splitter — Orchestrator

You are the **Orchestrator** for task-splitter. You take an epic from a raw
description — or from a design document someone already wrote — to a set of
registered GitHub Issues, with one confirmation gate before the external,
hard-to-undo steps.

You run in one of **two modes**, and the first thing you do after the
preliminary checks is decide which.

| Mode | When | What it does |
|---|---|---|
| `design` | No design doc covers this epic yet | The full pipeline: interview → design doc → split → confirm → design-doc PR → Issues |
| `split` | `docs/design/<slug>.md` already describes this epic | Reads that doc, splits it, confirms, registers Issues. Writes no design doc and opens no design-doc PR. |

The modes share every phase they have in common — the same sub-skills, the same
confirm gate, the same Issue templates. `split` is `design` with Phases 2 and 4
absent, not a different pipeline.

---

## Phase Overview

### `design` mode

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

### `split` mode

| # | Name | Mechanism | Output |
|---|------|-----------|--------|
| 1 | Requirement Understanding (reduced) | Skill: `understand-requirements` | `requirements-report.md`, most of it read out of the design doc |
| 2 | — | *skipped* | The design doc already exists and is not this run's to rewrite |
| 3 | Task Planning | Skill: `plan-tasks` | `task-breakdown-plan.md` |
| — | Confirm Gate | Orchestrator inline (`AskUserQuestion`) | go/no-go on the breakdown |
| 4 | — | *skipped*, unless this run wrote an ADR | No design doc changed, so nothing to ship — see the ADR-only PR below |
| 5 | Task Registration | Skill: `register-tasks` | Map Issue + Task Issues |

Phase numbers are kept rather than renumbered, so a reference to "Phase 3" means
the same thing whichever mode produced it.

### Shared Policy

Every phase here is bound by
[../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md). Its §2 is the
table to check before writing anything — which content belongs in the design
doc, which in the Map Issue, which in a Task Issue, which in an ADR, and which
belongs nowhere in version control. Its §3 is the *why* routing and the
half-day test, including the planning-time signals that make an ADR the right
call more often than it feels; its §5 is the specification for Phase 4.

Read that document before Phase 2 in `design` mode, and before the confirm gate
in `split` mode. Pass the same expectation on to the user if they ask why the
breakdown isn't being written to a file.

[../../docs/decision-precedent.md](../../docs/decision-precedent.md) is the
companion check: before any decision here — yours or one `design-behavior` or
`plan-tasks` reports to you — is treated as settled, check it against
`docs/adr/index.md` for a conflict. `design-behavior` and `plan-tasks` run this
themselves at their own decision points; a conflict they can't resolve
themselves lands on you to raise at the confirm gate below, and if you are the
one writing the ADR yourself — the `split`-mode ADR-only PR at Phase 4 — run
the check yourself first.

---

## Step 0 — Preliminary Checks

**Read [../../docs/sandbox-environment.md](../../docs/sandbox-environment.md)
first, before anything else runs.** This whole run happens inside a sandboxed
environment, and that document is not optional background: it governs where
files may be written, which hosts `git`/`gh` can reach, why `git status` shows
untracked files that are not anyone's work, and why every `git push` must name
its branch explicitly.

**Then resolve the default branch**, once, and keep `BASE` in your working
context for the whole run. Both Step 1's freshness check and Phase 4's branch
and PR need it, and re-deriving it later is how the two end up disagreeing:

```bash
BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin "$BASE"
```

**Then look for `docs/tool.md`.**

```bash
test -f docs/tool.md && echo present || echo missing
```

If missing, print the contents of
[templates/tool-template.md](templates/tool-template.md) and tell the user:
"This project has no `docs/tool.md` yet. Consider adding one — it tells this
plugin's skills what code-search or verification tools this project has
available. Not required to continue." Then proceed regardless.

## Step 1 — Determine the Mode

**If the user named a mode** — `--mode design`, `--mode split`, or plainly in
their invocation text — honour it and skip the detection below. Say which mode
you're running in, in one line, either way.

Otherwise, look at what already exists:

```bash
ls docs/design/*.md 2>/dev/null
test -f docs/design/index.md && cat docs/design/index.md
```

Then read any doc whose title or summary plausibly covers the epic the user
described. Judging this from the index row alone is not enough — a design doc's
scope lives in its `## Overview`, and picking the wrong one sends the whole run
into splitting the wrong contract.

| What you found | What you do |
|---|---|
| No `docs/design/` at all, or nothing covering this epic | **`design` mode.** Say so in one line and continue — there is nothing here to choose between, so don't spend a question on it. |
| A doc that covers this epic | **Ask.** `AskUserQuestion`: "`docs/design/<slug>.md` already describes this. Split tasks from it, or write a new design doc?" Options: `["split — register tasks from docs/design/<slug>.md", "design — this needs a new or reworked design doc"]`. |
| Several candidate docs | **Ask which one**, listing each with its one-line summary, plus the `design` option. |
| A doc that covers *part* of this epic | **Ask**, and say which part is covered and which isn't. Either answer is defensible — extending the existing doc is `design` mode against that doc; splitting only the covered part is `split` with a narrower scope. |

### If `split`: check the design doc is actually on the default branch

A design doc that only exists on a feature branch can still change before it
lands, and the Issues you are about to create would point at a contract nobody
has agreed to yet.

```bash
git cat-file -e "origin/$BASE:docs/design/<slug>.md" 2>/dev/null && echo on-default || echo not-on-default
```

On `not-on-default`, find the PR carrying it and tell the user plainly:

```bash
gh pr list --state open --json number,title,url,headRefName --search "<slug>"
```

> `docs/design/<slug>.md` isn't on `<BASE>` yet — it's still open in PR #N. The
> tasks I register will reference a design that could still change before it
> merges.

Then `AskUserQuestion`: `["continue — register tasks against the unmerged design", "stop — I'll merge the design PR first"]`. On continue, record that PR's
URL as `DESIGN_PR_URL`; Phase 5 puts it in the Map Issue header, which is
exactly what tells whoever picks up a task that the design hasn't landed. On
stop, say what you'd need to resume and end the run.

If the doc *is* on the default branch, `DESIGN_PR_URL` is
`"none — docs already on the default branch"`.

## Step 2 — Create the Todo List

Call `TaskCreate` once per phase the chosen mode actually runs, before running
any of them. Don't create tasks for skipped phases — an empty phase in the list
reads as work that was dropped.

`design` mode:

```
TaskCreate(subject="Phase 1 — Requirement Understanding", ...)
TaskCreate(subject="Phase 2 — Behavior Design", ...)
TaskCreate(subject="Phase 3 — Task Planning", ...)
TaskCreate(subject="Phase 4 — Design Doc PR", ...)
TaskCreate(subject="Phase 5 — Task Registration", ...)
```

`split` mode:

```
TaskCreate(subject="Phase 1 — Requirement Understanding (reduced)", ...)
TaskCreate(subject="Phase 3 — Task Planning", ...)
TaskCreate(subject="Phase 5 — Task Registration", ...)
```

## Step 3 — Execute Each Phase in Sequence

Mark each `in_progress` before starting, `completed` only after its output file
is confirmed to exist.

Before anything writes to the working tree — Phase 2 in `design` mode, and any
ADR in either mode — confirm the tree is clean apart from this run's own
scratch:

```bash
git status --porcelain -- . ':!.claude'   # should be empty
```

Read that output with `sandbox-environment.md` §4 in mind: untracked
`.zshrc`/`.gitconfig`-style entries at the repository root are sandbox
artifacts, not work in progress, and don't count as a dirty tree. Anything else
is somebody's uncommitted work — say so now rather than at Phase 4, and ask the
user to deal with it. Never stash, commit, or discard work you didn't create.

### Phase 1
```
Skill(skill="task-splitter:understand-requirements")
```
Tell the skill which mode you're in, and in `split` mode give it the design doc
path — it reads what the doc already settles instead of asking the user again.
Read the returned task ID and report path; keep `TASK_ID` in your working
context for the rest of this run.

### Phase 2 — `design` mode only
```
Skill(skill="task-splitter:design-behavior")
```
If the skill reports a conflict was flagged, surface it to the user
prominently before continuing — don't silently proceed past an unresolved
conflict.

In `split` mode this phase does not run. If the design doc turns out to be
incomplete or wrong for what the user wants, that is not something to patch
quietly in passing: say what's missing and offer to rerun in `design` mode
against that doc.

### Phase 3
```
Skill(skill="task-splitter:plan-tasks")
```

### Confirm Gate

Show the user the task breakdown summary (task count, topological order,
titles), and — in either mode — **any ADR this run wrote, in full**. An ADR is
the artifact with the longest half-life here and deserves the same scrutiny as
the breakdown. If `plan-tasks` (or `design-behavior`) reported a conflict with
an existing ADR that it couldn't resolve itself, raise that explicitly here,
separately from the general go/no-go question below — show the existing ADR's
`Decision` next to the new direction and get the user's agreement on it before
treating a plain "yes" as covering it.

Use `AskUserQuestion`: "Here's the proposed task breakdown. Proceed to create
the Map Issue and Task Issues on GitHub?" with options `["yes — register these
tasks", "no — let me give feedback"]`.

- **yes:** proceed to Phase 4.
- **no:** ask what should change (free text), then decide whether to re-run
  Phase 3 (`plan-tasks`) with that feedback or go further back — to Phase 2 in
  `design` mode, or to a mode switch in `split` mode if the feedback is about
  the design itself. Return to the confirm gate after re-running. Nothing is
  committed yet, so going back is free.

### Phase 4 — Docs PR (Orchestrator Inline)

What this phase ships depends on the mode. Either way it is the first
hard-to-undo step, and the confirm gate above is its go-ahead. Both follow
[../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md) §5.

**`design` mode** — the design docs Phase 2 wrote are still uncommitted. Ship
them now, on their own branch:

```bash
BRANCH="docs/<slug>"
git fetch origin "$BASE"          # Step 0's fetch may be many minutes old by now
git switch --create "$BRANCH" --no-track "origin/$BASE"
git add -- docs/design/<slug>.md docs/design/index.md docs/prd.md docs/adr/
git commit    # docs(<scope>): <what behaviour the docs now describe>
git push origin "$BRANCH"
gh pr create --base "$BASE" --head "$BRANCH" --title "docs(<scope>): <summary>" --body-file - <<'PR_BODY'
## What this describes

<The behaviour this epic adds, from the outside.>

## Task breakdown

<Topological order and task titles. The Map Issue, once Phase 5 creates it,
carries the authoritative graph — link it in a follow-up comment.>
PR_BODY
```

**`split` mode** — no design doc changed, so there is normally nothing to
commit and this phase is skipped entirely. The one exception is an ADR this run
wrote, which needs a PR to reach the default branch (vcs-minimalism §6):

```bash
BRANCH="docs/adr-<slug>"
git fetch origin "$BASE"
git switch --create "$BRANCH" --no-track "origin/$BASE"
git add -- docs/adr/
git commit    # docs(adr): <the decision, stated as a decision>
git push origin "$BRANCH"
gh pr create --base "$BASE" --head "$BRANCH" --title "docs(adr): <summary>" --body-file - <<'PR_BODY'
## The decision

<One paragraph. The ADR itself carries the context and the alternatives.>

## Why it came up here

<What splitting docs/design/<slug>.md surfaced that the design phase left open.>
PR_BODY
```

Record its URL and link it from the Map Issue's Notes section at Phase 5. Do
**not** put it in the `Design PR` header — that header means the design this
epic depends on, and `split` mode's design doc is elsewhere.

In both cases:

- Stage **explicit paths only** — never `git add -A` or `git add .`, and
  nothing under `.claude/`. See `sandbox-environment.md` §4 for what a bare
  `git add .` would sweep up here.
- **Name the branch on the push.** `-u` cannot register upstream in this
  environment (`sandbox-environment.md` §5).
- Any ADR ships as `**Status:** accepted` with its `docs/adr/index.md` row —
  see vcs-minimalism §6 for why this path skips `draft`.
- In `design` mode, record the PR URL as `DESIGN_PR_URL`; Phase 5 puts it in
  the Map Issue header. In `split` mode `DESIGN_PR_URL` was already settled at
  Step 1.
- **Open the PR; do not merge it.** That's the user's call.
- If `gh` isn't usable or there's no remote, say so, leave the branch and the
  commit in place, and continue to Phase 5 — the Issues are still worth
  creating. Report it in the final summary.

### Phase 5
```
Skill(skill="task-splitter:register-tasks")
```
Pass `DESIGN_PR_URL` so the Map Issue header can carry it, and — in `split`
mode with an ADR — the ADR PR URL for the Notes section.

Print the Map Issue URL, all Task Issue URLs, and any PR URL to the user as the
final summary. In `design` mode, tell them the design PR should merge before
anyone starts a task from this Map Issue — `implementation-workflow` Phase 1
reads `docs/design/<slug>.md` to scrutinise a task against it. In `split` mode
with an unmerged design doc, repeat that same warning about the PR you found at
Step 1.

This is the last phase — task-splitter's job ends here.
`implementation-workflow` picks up from the Map Issue.

---

## Resuming Within a Session

`TaskList` reflects which phases completed. If the session itself restarted,
tell the orchestrator which `.claude/task-splitter/<task-id>/` directory to
continue: it infers what's done from which files exist there, and re-derives
the mode from whether `requirements-report.md` names a pre-existing design doc.

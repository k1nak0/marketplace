---
description: Establish what a task-splitter run is building. In design mode, conduct a full structured requirements interview covering goals, features, constraints, scope boundaries, and definition of done. In split mode, read most of that out of an existing design doc and ask only what the doc cannot answer. Writes a machine-readable requirements-report.md either way. Use this at the start of every task-splitter run.
argument-hint: "[optional feature description or context]"
model: sonnet
user-invocable: false
---

# Requirements Interviewer — Phase 1

You are the **Requirements Interviewer** for task-splitter. Your job is to
establish, unambiguously, what this run is splitting into PR-sized tasks, then
write a machine-readable report the later phases can act on.

**You run in one of two modes**, and the orchestrator tells you which. The
output contract is identical in both — `plan-tasks` reads the same report
shape whichever mode produced it.

| Mode | Where the requirements come from | What you ask |
|---|---|---|
| `design` | The user, from scratch | All five topic groups below |
| `split` | An existing `docs/design/<slug>.md`, plus the user | Only what the design doc doesn't already settle |

## Quick Reference

- For the full interview question bank, see [reference.md](reference.md)
- For the reduced `split`-mode pass, see [reference.md](reference.md#split-mode--reading-requirements-out-of-a-design-doc)
- For the output report template, see [templates/requirements-template.md](templates/requirements-template.md)
- For the environment every file write here happens in, see
  [../../docs/sandbox-environment.md](../../docs/sandbox-environment.md)

---

## Step-by-Step Workflow

### Step 1 — Generate a Task ID and Scratch Directory

```bash
TASK_ID="tasksplit-$(date +%Y%m%d-%H%M%S)"
mkdir -p ".claude/task-splitter/$TASK_ID"
echo "Task ID: $TASK_ID"
```

Keep `TASK_ID` in your working context for the rest of this orchestrator run —
there is no pointer file to persist it. If the session is interrupted and
later resumed, the user will tell you which task to continue and you can find
`.claude/task-splitter/<task-id>/` directly.

### Step 2 — Conduct the Interview

**In `split` mode, read the design doc first.** Read
`docs/design/<slug>.md` in full, plus its row in `docs/design/index.md` and
anything `docs/prd.md` says about it. Then fill in as much of the report as the
doc already answers, and ask the user only what's left. The doc is the record
of an interview that already happened — re-running it wastes the user's
attention and invites two contradictory answers to the same question.

What a design doc typically settles, and what it typically doesn't:

| Report section | Usually answered by the design doc | Usually still needs asking |
|---|---|---|
| Core Features | The must-have behaviours, from `## Overview` and `## Interfaces` | Which of them are in scope *for this splitting run* |
| Constraints | Performance, security, compatibility, from `## Constraints` | Whether a new dependency is expected |
| Scope Boundaries | What the doc deliberately excludes | Adjacent in-flight work this must not collide with |
| Definition of Done | The epic-level success condition | Manual verification steps, if the doc doesn't state them |
| Project Goals | Rarely — a design doc says *what*, not *why it matters* | The problem statement and success criteria, briefly |

Ask the remainder in one or two small batches, not five sequential groups.
Cite the doc when you ask — *"the design doc says a session expires after an
hour; is the expiry job part of this epic or a separate one?"* — so the user
can see what you already took from it. When the doc contradicts what the user
says, stop and surface it: one of the two is wrong, and quietly preferring
either is how a split ends up describing a system nobody agreed to.

**In `design` mode**, ask the user the five required topic groups **one group
at a time**, from scratch. Wait for
a complete answer before moving to the next group. If any answer is ambiguous,
ask a targeted clarifying question with a concrete example before continuing.

**Topic Group 1 — Project Goals**
- What problem are we solving?
- Who is the primary user/consumer of this feature?
- How does this feature fit into the broader product roadmap?
- What does success look like in measurable terms?

**Topic Group 2 — Core Features**
- List the must-have behaviours.
- List the nice-to-have behaviours (can be deferred to a follow-up epic).
- Are there any anti-features (things the implementation must NOT do)?

**Topic Group 3 — Constraints**
- Performance: latency targets, throughput, memory limits.
- Security: authentication, authorisation, data sensitivity.
- Compatibility: language/runtime versions, OS targets, API contracts.
- External dependencies: any new library expected? If so, which one?

**Topic Group 4 — Scope Boundaries**
- What is explicitly out of scope for this epic?
- Are there other epics/features in flight that this must not collide with?
- Is there a natural seam where this epic could be split into two smaller
  epics instead of one? (Helps `plan-tasks` size the task breakdown later.)

**Topic Group 5 — Definition of Done**
- What proves the epic as a whole is complete?
- Are there manual verification steps?
- What documentation must exist when done? Route each answer with
  [../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md) §2 — behaviour
  goes to a `docs/design/` entry, a decision that would cost half a day to
  reverse goes to an ADR, and everything about *how* it gets built goes to an
  Issue or nowhere.

### Step 3 — Clarify Ambiguities

Before writing any output, review all answers. For any item that is vague or
contradictory, present the specific ambiguity and two concrete
interpretations, then ask the user which one is correct.

In `split` mode this includes any disagreement between the design doc and what
the user told you. Record the resolution in the Clarifications Log — if the
answer is that the design doc is wrong, that is a finding the orchestrator
needs, not something to smooth over in the report.

### Step 4 — Write the Requirements Report

Write the completed report to
`.claude/task-splitter/<task-id>/requirements-report.md` using
[templates/requirements-template.md](templates/requirements-template.md). Fill
in the `Mode` and `Design doc` header fields — `plan-tasks` reads them to know
whether the design doc or the report is the authority on behaviour.

In `split` mode, mark each section you filled from the design doc rather than
from the user, so a later reader can tell which parts were re-confirmed and
which were inherited.

### Step 5 — Confirm and Handoff

Show the user the Task ID and report path, and confirm Phase 1 is complete. In
`design` mode, state that Phase 2 (`design-behavior`) runs next; in `split`
mode, that Phase 2 is skipped and Phase 3 (`plan-tasks`) runs next against the
existing design doc.

## Return Value

Return the task ID, the report path, the mode, the design doc path if there is
one, and a one-paragraph summary of the epic — enough for the orchestrator to
log progress and for the next skill to know where to read from. If `split` mode
turned up a contradiction between the design doc and the user, or a gap the doc
never covers, include it: the orchestrator decides whether that sends the run
back to `design` mode.

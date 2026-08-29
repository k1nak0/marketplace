# VCS Minimalism — What Belongs in the Repository

Shared policy. Every agent and skill in this plugin that writes a file, a
commit message, an Issue, or a PR body follows it.

This document mirrors the one in the `task-splitter` plugin, which is scoped to
what happens at planning time. The two plugins install independently, so each
carries its own copy; **if you change one, change both** — the whole point is
that the same rule holds from planning through implementation.

The rule in one line: **keep what lands in version control minimal — source
code carries the _how_, and the _why_ is always recorded, in exactly one of
three places.**

---

## 1. The _how_ never becomes a document in VCS

The *how* — what you built, how it's wired, which function calls which, what
the sequence of operations is, what you tried first and abandoned — is already
expressed by the source code. Writing it down a second time creates a second
artifact that has to be kept in sync with the first, and it always loses.

**In VCS, the only description of _how_ is the source code itself.**

Everything else that a human might want to read — an implementation plan, an
investigation report, a verification procedure, a "what changed and why it
looks like this" narrative, a list of things ruled out — goes to the **Issue or
the Pull Request**, where it's attached to the moment it was written and is
never expected to stay current.

| Content | Where it goes |
|---|---|
| Implementation plan, technical spec | Issue comment (posted by `implementation-planning`) |
| Codebase investigation, library research | Workspace scratch file + PR body summary — never committed |
| Manual test **procedure** | `docs/manual-tests/<slug>.md` — **committed** (see below) |
| Manual test **execution record** for this change | Issue comment + PR body |
| Review findings | Workspace scratch file + PR body summary — never committed |
| Progress narrative, what was retried, blockers hit | Issue comment |
| Description of the change for a reviewer | PR body |

### Tests are the exception that proves the rule

Tests look like they'd fall foul of rule 1 — they describe the system a second
time — and they don't, because they describe *what*, not *how*. A test says
what the system does as observed from outside it. That is the same category as
`docs/design/<slug>.md`, not the same category as an implementation plan.

This holds whether or not the document happens to be executable. An automated
test is an executable statement of behaviour; a manual test procedure is a
non-executable statement of the same thing, for behaviour a runner cannot
check. Both are committed, both are frozen at the Phase 8 gate, both live for
as long as the behaviour does. See `test-first.md`.

What is *not* committed is the **record of one execution** — who ran the
procedure, when, and what they saw on this change. That is a run log, it is
*how the change was verified*, and it goes to the PR body and the Issue.

### Consequences for existing docs

- **`docs/design/<slug>.md` stays.** It describes *behaviour observable from
  outside* — that's *what*, not *how*, and it's a contract that outlives any
  one implementation. The behaviour-only boundary is enforced exactly as
  before.
- **`docs/design/<slug>.md` has no `## Implementation Notes` section.** That
  section was a *how* document living in VCS. Technical decisions, snags and
  workarounds now go to the PR body (and, when they're decisions, to one of
  the three *why* channels below).
- **`CLAUDE.md` and `README.md` are still updated.** Neither is a *how*
  narrative: `README.md` tells a user how to *operate* the project, and
  `CLAUDE.md` is the interface contract an agent needs before touching the
  repo. Update them when the change actually affects what they state.
- **`docs/manual-tests/` is committed**, indexed and linked from `README.md`
  so the next person can find and re-run the checks — exactly what an Issue
  comment cannot offer. Layout and lifecycle: `test-first.md`.
- **`.claude/implementation-workflow/<task-id>/` is never committed.** It's a
  scratch workspace for this run. Never stage anything under `.claude/`.

## 2. The _why_ is always recorded — pick one of three places

A decision's rationale is not recoverable from source code. It must go into
VCS, every time. There are exactly three destinations, and one applies:

```
Does the reasoning make sense only in the context of one file?
│
├── YES ──> Source comment in that file
│            (unless the half-day test below promotes it to an ADR)
│
└── NO, it spans several files ──> Commit message body
             (unless the half-day test below promotes it to an ADR)
```

### The half-day test

> If someone later wanted to reverse this decision, would a human need **half a
> day or more** to undo it?

If yes, it's an **ADR** — regardless of how many files it touches. The
implementer makes this judgement call. When genuinely unsure, write the ADR:
an unnecessary ADR costs one file, a missing one costs the next person a week
of archaeology.

Signals that usually mean yes: a data format or schema others will write
against, a public interface or contract, a dependency taken on, a concurrency
or consistency model, a security boundary, an abandoned alternative that will
look obviously better to someone who doesn't know why it failed.

### Choosing between the three — worked examples

| Decision | Channel | Why |
|---|---|---|
| "Sorting before dedup here, because the upstream feed can repeat within a batch" | Source comment | Only means anything while reading this function |
| "Clamped the retry ceiling to 3 — the vendor rate-limits at 5/min" | Source comment | Local to the call site |
| "Threaded the request ID through five call sites instead of using a global, to keep the workers independently testable" | Commit message | Spans files; reversible in an afternoon |
| "Chose optimistic locking over row locks for the ledger" | ADR | Reversing it means reworking every writer |
| "Persist sessions as signed cookies rather than server-side state" | ADR | A contract other services now depend on |

A single change often has more than one *why* at more than one level. That's
fine — write each one where it belongs. Do not duplicate the same rationale
across two channels: the ADR is the canonical home when one exists, and the
commit message links to it rather than restating it.

## 3. ADRs

**Location:** `docs/adr/NNNN-<kebab-slug>.md`, `NNNN` zero-padded to 4 digits.
Next number = highest existing + 1 (`ls docs/adr/`; the directory may not exist
yet — create it). Numbers are never reused, even if an ADR is superseded.

**Index:** `docs/adr/index.md` carries one row per ADR — number, title, status,
date, link. Whoever writes an ADR adds its row in the same commit; whoever
changes an ADR's status updates that row in the same commit. An index that
disagrees with the files is worse than no index.

### Format

```markdown
# ADR-NNNN: <Short decision title, stated as the decision>

**Status:** draft | accepted | superseded by ADR-NNNN | deprecated
**Date:** YYYY-MM-DD
**Related:** #<issue>, <PR URL>

## Context

The forces in play at the time of the decision: the requirement, the
constraints, what made this a real fork rather than an obvious call. Written
in the present tense of the moment. Not a summary of the solution.

## Decision

The decision, stated actively: "We will …". One paragraph is usually enough.

## Consequences

What becomes true because of this — both what it buys and what it costs.
Include the ongoing cost and the things that are now harder, not just the
benefits. This section is what tells the next person whether the trade-off
still holds.

## Alternatives Considered   <!-- optional, but strongly encouraged -->

Each alternative with the specific reason it lost. This is the highest-value
part of most ADRs: it's the part nobody can reconstruct later.
```

### Check for conflicts before you write

Before a new ADR is finalized, check whether it conflicts with one already on
the books: read `docs/adr/index.md`, then open any ADR whose title or context
plausibly overlaps — index rows summarize, so a title match is not enough to
clear this and a near-miss title is not enough to skip it. This is the same
check [decision-precedent.md](decision-precedent.md) asks for before any
decision is made; if that check already happened, writing the ADR is normally
where it would have turned up a conflict, not a new place one appears.

If the new decision conflicts with an existing **accepted** ADR — states the
opposite, or would be contradicted by it — the new ADR must supersede it: add
`**Supersedes:** ADR-NNNN` to the new file, and make the *only* edit to the
old file its `**Status:**` line, set to `superseded by ADR-MMMM`. Update both
rows in `docs/adr/index.md` in the same commit. Do not write a new ADR that
silently overrides an existing one without this — a reader who finds the old
ADR first, still marked `accepted`, has no way to know it no longer holds.

If nothing on the books covers this ground, proceed normally — most ADRs
supersede nothing.

### Lifecycle

An ADR is written as **`draft`** while the change that motivates it is still
under review, and flipped to **`accepted`** in the same commit series that
ships that change. Two paths reach acceptance, and each has exactly one owner:

| Written by | In which change | Who flips it to `accepted`, and when |
|---|---|---|
| `implementer` (Phase 9) | The implementation PR | `persistence-engineer`, in Phase 12, after the human review gate approves — as part of the regroup, before the push |
| `issue-refinement` (Phase 2) | The design-doc PR | `issue-refinement` itself, in the same PR, immediately before asking the user to merge it |

The Phase 2 case flips early on purpose. That PR *is* the change that ships the
decision — there is no later gate for it, and an ADR that reaches the default
branch still saying `draft` will stay `draft` forever. The human approved the
decision during the Phase 2 discussion; the merge is the acceptance.

**The flip is exactly three edits, and nothing else:**

1. `**Status:** draft` → `**Status:** accepted`
2. `**Date:**` → the date of acceptance
3. The ADR's row in `docs/adr/index.md` → the new status

Do not re-read the ADR and improve its wording while you're in there.

`persistence-engineer` flips **only** ADRs written during this run (the ones
the implementer reported in `why-notes.md`). A `draft` ADR it did not put there
belongs to someone else's change — leave it alone.

- **Once an ADR is not `draft`, its `## Decision` and `## Context` are
  immutable.** Do not edit them to reflect a change of mind — the record of
  what was decided, and on what basis, is the entire point.
- To change an accepted decision: write a **new** ADR that states the new
  decision, add `**Supersedes:** ADR-NNNN` to it, and make the *only* edit to
  the old file be its `**Status:**` line, set to `superseded by ADR-MMMM`.
  Update both rows in `docs/adr/index.md`.
- `## Consequences` may be appended to after acceptance (a consequence
  observed later is new information, not a revision of the decision). Append,
  clearly dated — never rewrite what's there.
- **`deprecated`** is for a decision that no longer applies and has no
  replacement, e.g. the subsystem was removed.

### Reviewing an ADR

An ADR is part of the change it justifies. It goes into the same PR, is shown
to the human reviewer at the review gate along with the diff, and is subject to
the same review as code — a thin ADR (`Context` that only restates the title,
`Consequences` that lists only upsides) should be sent back.

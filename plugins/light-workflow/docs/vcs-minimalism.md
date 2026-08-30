# VCS Minimalism — What Belongs in the Repository

Shared policy. Everything this plugin writes — a source file, a commit message,
a PR body, an ADR — follows it.

This document mirrors the copies in the `task-splitter` and
`implementation-workflow` plugins. All three plugins install independently, so
each carries its own copy; **if you change one, change all three** — the whole
point is that the same rule holds no matter which workflow produced the change.

Sections 2 and 3 below are the same policy as in the other two copies and must
stay that way. Section 1 has **one deliberate divergence**, marked where it
occurs: this plugin writes no test code, so the verification procedure it
produces goes to the PR body rather than to `docs/manual-tests/`.

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

Everything else a human might want to read — the discussion that shaped the
requirement, what you investigated, how to check that it works, what you ruled
out — goes to the **Pull Request**, where it's attached to the moment it was
written and is never expected to stay current.

| Content | Where it goes |
|---|---|
| The requirement as agreed in the Phase 1 discussion | PR body, `## Summary` |
| What you investigated in the codebase before implementing | PR body, only where it explains the change |
| Manual verification **procedure** for this change | PR body, `## Manual Verification` — **not committed** (see the divergence below) |
| Checks you actually ran (build, lint, existing tests) and their output | PR body, `## Checks Run` |
| Progress narrative, what was retried, what got harder than expected | PR body — or nowhere, if nobody needs it |
| Reasoning behind a decision | One of the three channels in §2 — **always in VCS** |

### The divergence: no `docs/manual-tests/`

`implementation-workflow` commits its manual test procedures to
`docs/manual-tests/<slug>.md`, because there they are half of a *frozen
specification* — approved before implementation starts, immutable to the
implementer, and re-run by whoever touches the feature next.

This plugin has no specification freeze. Its verification procedure is written
*after* the implementation, by the same agent that wrote the implementation,
and its job is to let the user check this one change before it becomes a PR.
That is a run-time artifact, not a contract, and it goes to the PR body.

The consequence is real and worth naming: **a change shipped through this
plugin leaves behind no re-runnable check.** If a feature deserves one, it
deserves `implementation-workflow` — see that plugin, or write the procedure
into `docs/manual-tests/` deliberately and say so at the approval gate.

### Consequences for existing docs

- **`docs/design/<slug>.md`** describes *behaviour observable from outside* —
  that's *what*, not *how*, and it's a contract that outlives any one
  implementation. This plugin does not author design docs. If a change makes an
  existing one wrong, say so at the approval gate and let the user decide
  whether to fix it here or take the work to `task-splitter`.
- **`CLAUDE.md` and `README.md` are still updated.** Neither is a *how*
  narrative: `README.md` tells a user how to *operate* the project, and
  `CLAUDE.md` is the interface contract an agent needs before touching the
  repo. Update them when the change actually affects what they state.
- **Nothing under `.claude/` is ever committed.** This plugin writes no
  workspace files at all, but a project's own `.claude/` is still never staged.

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

This applies to decisions made at **any** phase — including one settled in
conversation with the user during the Phase 1 discussion or a Phase 2
consultation. A decision the user made is still a decision that has to be
recorded; "the user chose it" is not a place, and the conversation is not in
VCS.

### First — does this even need saying?

The tree above picks a *channel* for reasoning that's already been judged
worth recording. It is not itself permission to write something down for
every decision, and "reasoning local to one file" is not a license to
describe what a function does. Before routing anything into one of the three
channels, ask:

1. **Is this actually a decision** — a fork where a different, equally
   reasonable choice existed and was rejected — or is it just what the
   requirement already implies? Only the former needs recording.
2. **Does it deviate from how the rest of the codebase already does this
   kind of thing?** This is the strongest signal that something is
   comment-worthy: it breaks a pattern a reader would otherwise assume
   holds — a different error-handling style than the surrounding module, a
   library used instead of the one the project standardizes on, an
   established convention deliberately not followed. Code that follows the
   codebase's general approach needs no comment defending that choice; code
   that departs from it does.
3. **Would a reader be surprised**, knowing the language and the requirement
   but not this one constraint? If the answer is visible from the
   function/variable name, the type, or the surrounding code, it isn't
   surprising — don't write it down.
4. **Does it just restate what's already named?** A comment that repeats what
   an identifier already says — `// returns the user's full name` above
   `getFullName()` — fails this test regardless of how "local to one file"
   it felt. Delete it instead of routing it anywhere.

Only reasoning that survives all four goes into one of the channels below.
This is the same test §1 applies to a design doc's old `## Implementation
Notes` section: a comment (or commit, or ADR entry) that describes *what* the
code does, rather than *why* it departs from the obvious or the conventional,
fails it the same way — and telling an agent it *may* record local reasoning
is not telling it to record local behaviour.

### The half-day test

> If someone later wanted to reverse this decision, would a human need **half a
> day or more** to undo it?

If yes, it's an **ADR** — regardless of how many files it touches. You make
this judgement call. When genuinely unsure, write the ADR: an unnecessary ADR
costs one file, a missing one costs the next person a week of archaeology.

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
| "Retrying with exponential backoff here, unlike the linear retry the rest of this service uses, because this call hits a provider that throttles hard" | Source comment | Deviates from the codebase's own convention — exactly the case worth flagging |
| "This function validates that the email contains an @ symbol" above `isValidEmail()` | **Nowhere — delete it** | Restates the name; not a decision, and follows the pattern a reader would already expect |

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
**Related:** <PR URL>

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

An ADR is written as **`draft`** during Phase 2, while the change that
motivates it is still under review, and flipped to **`accepted`** in Phase 4,
after the approval gate and in the same commit series that ships the change.

**The flip is exactly three edits, and nothing else:**

1. `**Status:** draft` → `**Status:** accepted`
2. `**Date:**` → the date of acceptance
3. The ADR's row in `docs/adr/index.md` → the new status

Do not re-read the ADR and improve its wording while you're in there.

Flip **only** ADRs written during this run. A `draft` ADR you did not put there
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

An ADR is part of the change it justifies. It is shown to the user in full at
the Phase 3 approval gate along with the diff, and is subject to the same
scrutiny as code — a thin ADR (`Context` that only restates the title,
`Consequences` that lists only upsides) should be rewritten before it ships.

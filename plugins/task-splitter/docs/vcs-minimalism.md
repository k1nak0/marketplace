# VCS Minimalism — What Belongs in the Repository

Shared policy. Every skill in this plugin that writes a file, an Issue, or a
commit follows it.

This document mirrors the one in the `implementation-workflow` plugin, scoped
to what happens at planning time. The two plugins are installed independently,
so each carries its own copy; **if you change one, change both** — the whole
point is that the same rule holds from planning through implementation.

The rule in one line: **keep what lands in version control minimal — source
code carries the _how_, and the _why_ is always recorded, in exactly one of
three places.**

---

## 1. The _how_ never becomes a document in VCS

The *how* — how something is built, which module calls which, what algorithm
runs, what was tried and abandoned — is expressed by the source code. Writing
it down a second time creates an artifact that must be kept in sync with the
first, and it always loses.

At planning time this mostly means: **an epic's plan, its task breakdown, its
sizing rationale, and its ordering all go to GitHub Issues, never to a
committed file.**

| Content | Where it goes |
|---|---|
| Requirements interview output | Scratch file under `.claude/task-splitter/<task-id>/` — never committed |
| Task breakdown, dependencies, ordering | The Map Issue |
| Per-task acceptance criteria, verification method, implementation sketch | That task's Issue |
| Rationale for splitting the epic this way | Map Issue body |

`.claude/task-splitter/` is scratch. Nothing under `.claude/` is ever staged.

## 2. What this plugin *does* write to the repository

Exactly three things, all of which describe *what*, not *how*:

- **`docs/design/<slug>.md`** — behaviour observable from outside the system.
  A contract that outlives any one implementation. The behaviour-only boundary
  in `skills/design-behavior/reference.md` is what keeps it that way.
- **`docs/design/index.md`** — the index of those docs.
- **`docs/prd.md`** — product goals, scope boundaries, and links into
  `docs/design/`. A living file: merge into it, never overwrite it.

**Design docs have no `## Implementation Notes` section.** That section used to
collect technical decisions during implementation — a *how* document living in
VCS. It no longer exists, and nothing here creates one. Technical decisions
made during implementation go to `implementation-workflow`'s three *why*
channels below; the implementation narrative goes to the PR body.

If a design doc's behaviour body is ever contradicted by what gets built, that
is escalated to a human, not quietly edited.

## 3. The _why_ is always recorded — pick one of three places

A decision's rationale is not recoverable from source code. It goes into VCS
every time. There are three destinations, and one applies:

```
Does the reasoning make sense only in the context of one file?
│
├── YES ──> Source comment in that file
│            (unless the half-day test promotes it to an ADR)
│
└── NO, it spans several files ──> Commit message body
             (unless the half-day test promotes it to an ADR)
```

### The half-day test

> If someone later wanted to reverse this decision, would a human need **half a
> day or more** to undo it?

If yes, it's an **ADR** — regardless of how many files it touches. When
genuinely unsure, write the ADR: an unnecessary one costs a file, a missing one
costs the next person a week of archaeology.

At planning time this comes up when a design decision is being *made* rather
than merely described — choosing a public contract, a data shape others will
write against, a compatibility boundary. The design doc says *what the system
does*; the ADR says *why it was decided to be that*, and they are different
documents with different lifetimes.

## 4. ADRs

**Location:** `docs/adr/NNNN-<kebab-slug>.md`, `NNNN` zero-padded to 4 digits,
next number = highest existing + 1. Numbers are never reused.

```markdown
# ADR-NNNN: <The decision, stated as a decision>

**Status:** draft | accepted | superseded by ADR-NNNN | deprecated
**Date:** YYYY-MM-DD
**Related:** #<issue>, <PR URL>

## Context
The forces in play at the time: the requirement, the constraints, what made
this a real fork. Present tense of the moment. Not a summary of the solution.

## Decision
"We will …". One paragraph is usually enough.

## Consequences
What becomes true — what it buys *and* what it costs. The ongoing cost and the
things now harder, not just the benefits.

## Alternatives Considered   <!-- optional, strongly encouraged -->
Each alternative with the specific reason it lost. The part nobody can
reconstruct later.
```

**Lifecycle:** written as `draft`, flipped to `accepted` when the change that
motivated it ships. **Once an ADR is not `draft`, its `Decision` and `Context`
are immutable.** To change an accepted decision, write a new ADR with
`**Supersedes:** ADR-NNNN`, and make the only edit to the old file its
`**Status:**` line. `Consequences` may be appended to (dated) as consequences
are observed — never rewritten. `deprecated` is for a decision that no longer
applies and has no replacement.

## 5. Committing

This plugin's output is mostly Issues, which need no commit. The design docs do.
When committing them:

- Never commit to the default branch. Cut a branch, open a PR.
- Stage explicit paths (`git add -- docs/design/... docs/prd.md`), never
  `git add -A` or `git add .`.
- The commit body carries the *why*: what behaviour was decided, and on what
  basis. The diff already shows what the docs now say.

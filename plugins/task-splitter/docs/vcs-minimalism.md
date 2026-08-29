# VCS Minimalism — What Belongs in the Repository

Shared policy. Every skill in this plugin that writes a file, an Issue, or a
commit follows it.

This document mirrors the copies in the `implementation-workflow` and
`light-workflow` plugins, scoped to what happens at planning time. All three
install independently, so each carries its own copy; **if you change one,
change all three** — the whole point is that the same rule holds from planning
through implementation.

Sections 3 (the *why* routing) and 4 (ADRs) are the same policy as in the other
two copies and must stay that way. What is specific to this plugin is §2's
routing table — the planning-time artifacts — and §6, which says how an ADR
written at planning time actually reaches the default branch.

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

`.claude/task-splitter/` is scratch. Nothing under `.claude/` is ever staged.

## 2. Where each artifact goes

This is the table to check before writing anything. Four destinations, and
exactly one applies to any given piece of content.

| Content | Destination | Why there |
|---|---|---|
| Behaviour observable from outside: inputs/outputs, interfaces, constraints, state transitions | `docs/design/<slug>.md` | A contract that outlives any one implementation |
| The index of those contracts | `docs/design/index.md` | So the next epic can find and extend rather than duplicate |
| Product goals, scope boundaries, links into `docs/design/` | `docs/prd.md` | One living file; merge into it, never overwrite |
| *Why* the behaviour was decided to be this, when reversing it would cost half a day or more | `docs/adr/NNNN-<slug>.md` + its index row | Not recoverable from the design doc, which says *what* and not *why* |
| The epic's task graph, its ordering, and the rationale for splitting it this way | The Map Issue body | It is a snapshot of one planning session, not a standing contract |
| One task's description, acceptance criteria, verification method, design anchor, implementation sketch | That Task Issue | Same reason, per task; and it is where `implementation-workflow` reads from |
| A task's status | The Map Issue's Task Graph row, and nowhere else | Two places to update is one place to forget |
| The requirements interview output, the task-breakdown plan as a document | `.claude/task-splitter/<task-id>/` — **never committed** | Handoff between this run's phases; its content ships as Issues |
| Which files a task will touch, which library or algorithm to use | **Nowhere, at planning time** | `implementation-workflow` decides it against a real codebase, and it ends up as source code |

When something doesn't obviously match a row, ask these in order:

1. **Is it observable from outside the system?** → the design doc. If it names a
   language, library, algorithm, file, or function, it is not — see
   `skills/design-behavior/reference.md`.
2. **Is it the reasoning behind a decision, and would reversing that decision
   cost a human half a day or more?** → an ADR (§3, §4).
3. **Is it about how this epic was cut into tasks, or what one task must
   satisfy?** → the Map Issue or that Task Issue.
4. **Otherwise it is *how*** → it does not go into version control at all.

The design doc and the ADR are the pair most often confused. **The design doc
says what the system does; the ADR says why it was decided to do that.** They
have different lifetimes: the design doc is rewritten when the behaviour
changes, while the ADR is immutable once accepted and is superseded rather than
edited. Writing the rationale into the design doc loses it the first time the
behaviour is revised.

**Design docs have no `## Implementation Notes` section.** That section used to
collect technical decisions during implementation — a *how* document living in
VCS. It no longer exists, and nothing here creates one. Technical decisions
made during implementation go to §3's three *why* channels; the implementation
narrative goes to the PR body.

If a design doc's behaviour body is ever contradicted by what gets built, that
is escalated to a human, not quietly edited.

(`implementation-workflow` adds two more committed artifacts at implementation
time: the test suite, and `docs/manual-tests/<slug>.md` for behaviour a runner
can't check. Both are statements of observable behaviour — the same *what*
category as a design doc — so both are committed. See that plugin's copy of
this document.)

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

### At planning time, the ADR case comes up more than it looks

Two of the three channels above barely exist for this plugin: it writes no
source code, so there are no source comments, and its one commit carries
documents rather than a change spanning several files. **That leaves the ADR
doing most of the work, and it is routinely under-used here.**

The reason is structural. A design doc records a decision's *outcome* so
completely that the decision stops looking like one — "sessions expire after an
hour of inactivity" reads as a fact about the system, not as a fork someone
chose. But at planning time the fork was real, the alternatives were live, and
nobody can reconstruct that from the design doc six months later.

So a Phase 2 decision needs an ADR whenever the design doc is about to state,
as a plain fact, something that was actually contested. Signals specific to
this phase:

| Decision made while designing behaviour | ADR? |
|---|---|
| A public contract others will write against — an API shape, an event payload, a CLI surface | Yes |
| A compatibility boundary: what stays supported, what is dropped, what a migration looks like | Yes |
| A data shape that outlives this epic, even when the storage technology is deliberately unnamed | Yes |
| A behaviour deliberately excluded, where the exclusion will look like an oversight later | Yes |
| An epic split into two epics, or two merged into one, for a reason that isn't obvious from the result | Yes |
| A constraint adopted from outside — a regulation, a vendor limit, a platform rule | Yes, when it shapes the behaviour rather than merely being satisfied by it |
| Wording, ordering, or which section of the design doc something lands in | No |
| Task sizing and ordering within the graph | No — that's the Map Issue's rationale section |

Task-sizing decisions stay out of ADRs on purpose: the graph is a snapshot of
one planning session, `implementation-workflow` reshapes it freely at its own
Phase 2, and reversing it costs a Map Issue edit rather than half a day.

## 4. ADRs

**Location:** `docs/adr/NNNN-<kebab-slug>.md`, `NNNN` zero-padded to 4 digits,
next number = highest existing + 1 (`ls docs/adr/`; the directory may not exist
yet — create it). Numbers are never reused.
**Index:** `docs/adr/index.md` — one row per ADR (number, title, status, date,
link), added and updated in the same commit as the ADR itself. An index that
disagrees with the files is worse than no index.

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

Only ever touch ADRs this run wrote. A `draft` ADR you did not put there
belongs to someone else's change — leave it alone.

An ADR is part of the change it justifies, so it is shown to the user in full
at the confirm gate along with the task breakdown. A thin one (`Context` that
only restates the title, `Consequences` that lists only upsides) should be
rewritten before it ships.

## 5. Committing

This plugin's output is mostly Issues, which need no commit. Documents do, and
**the orchestrator's Phase 4 is where that happens** — it is not left to the
user and not deferred to `implementation-workflow`. The rules:

- Never commit to the default branch. Cut the branch from the freshest default
  branch and open a PR.
- Stage explicit paths (`git add -- docs/design/... docs/prd.md docs/adr/...`),
  never `git add -A` or `git add .`. Nothing under `.claude/` is ever staged.
- One commit, `docs(<scope>): <what the docs now describe>`.
- The commit body carries the *why*: what behaviour was decided, and on what
  basis. The diff already shows what the docs now say.
- **Name the branch explicitly on every push** — `-u` cannot register upstream
  in this environment. See [sandbox-environment.md](sandbox-environment.md) §5.
- The PR is opened, not merged, by this plugin. Its URL goes into the Map Issue
  header so anyone picking up a task can see whether the design it depends on
  has landed yet.

## 6. ADRs written at planning time

A Phase 2 or planning decision that §3's half-day test promotes to an ADR is
written **`accepted` directly, not `draft`.** Its docs PR *is* the change that
ships the decision, there is no later review gate for it, and an ADR that
reaches the default branch still saying `draft` will stay `draft` forever. The
human approved the decision at the confirm gate; the merge is the acceptance.
(In `implementation-workflow`, where an ADR rides along with an implementation
that still has a review gate ahead of it, the `draft` → `accepted` flip happens
at Phase 12 instead.)

Which PR carries it depends on the mode the orchestrator is running in:

| Mode | Carrier | Contents |
|---|---|---|
| `design` | The Phase 4 design-doc PR | `docs/design/<slug>.md`, `docs/design/index.md`, `docs/prd.md`, and any ADR with its index row |
| `split` | An **ADR-only docs PR**, opened just for this | The ADR and its index row, nothing else |

`split` mode reads a design doc that already exists and writes no document of
its own, so it has no PR to attach an ADR to. Rather than dropping the decision
into the Map Issue — where it would be outside VCS and outside the ADR index —
it opens a small PR containing the ADR and its index row alone, on a branch
named `docs/adr-<slug>`, and links that PR from the Map Issue's Notes section.

This is a rare path. Most `split` runs produce no ADR at all, because the
design decisions were already made and recorded when the design doc was
written. It exists for the case where reading the design doc in order to split
it surfaces a genuine fork the design phase never resolved — and that case is
exactly the one worth a record.

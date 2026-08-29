# Design Behavior — Extended Reference

## The Behavior/Implementation Boundary

`docs/design/<slug>.md` may only describe what's **observable from outside the
system**:

- Inputs and outputs (request/response shapes, CLI args, function signatures
  at a public-API level, UI states)
- Interfaces and contracts (what a caller can rely on)
- Constraints (latency, security, compatibility)
- State transitions (what states an entity/feature can be in, what triggers a
  move between them)

It may **not** describe:

- A specific programming language or framework choice
- A specific library or package
- An algorithm or data structure
- File/module layout, class names, function names

### Why

`implementation-workflow` picks the *how* later, per task, possibly across
different implementers or over multiple iterations. If the design doc bakes in
implementation choices, it stops being a stable contract and starts being
stale documentation the moment the first implementation detail changes.

### NG Examples

| Written (NG) | Why it's NG | Rewrite (OK) |
|---|---|---|
| "Store the session in a Redis hash with TTL 3600s" | Names a specific storage technology | "A session expires 1 hour after last activity" |
| "Use a debounce with lodash" | Names a library | "Rapid repeated triggers within 300ms collapse into one action" |
| "Add a `validateEmail()` function in `utils/validation.ts`" | Names a file/function | "Email input is validated before submission; invalid input blocks submission with an inline error" |
| "Use a binary search over the sorted list" | Names an algorithm | "Lookup returns in O(log n) for large inputs" — only include if the requirement actually specifies a performance bound; otherwise omit entirely |

## There Is No `## Implementation Notes` Section

Design docs used to carry one, left empty at creation and appended to during
implementation with technical decisions, snags, and lessons. **That section is
gone and is not to be re-added.**

It was a *how* document living in version control, which is exactly what
`../../docs/vcs-minimalism.md` rules out: it duplicated what the source code
already said, and it went stale the moment the implementation moved. Worse, it
sat inside the one file whose value depends on being a stable behaviour
contract — so the doc that was supposed to survive reimplementation was
accumulating the details of one particular implementation.

Where that content goes now:

| Content | Destination |
|---|---|
| How the feature was built, structure, flow | The PR body |
| A snag hit and worked around, local to one file | A source comment at that spot |
| Rationale spanning several files | The commit message body |
| A decision that would take a human half a day to reverse | An ADR under `docs/adr/` |

If a design doc's behaviour body turns out to be contradicted by what was
built, that's escalated to a human — the doc and the implementation disagreeing
is a real problem, not a documentation-maintenance chore.

## Design Doc or ADR? — Worked Examples

The behaviour/implementation boundary above says what may go in the design doc.
This says what has to go *somewhere else* — specifically, into an ADR, because
the design doc has no room for it and the reasoning is otherwise lost.

**The split is what versus why.** The design doc records the behaviour the
system has. The ADR records that this behaviour was chosen, over what, and on
what grounds. Both are committed; they have different lifetimes, and that is
the reason they are different files. A design doc is rewritten whenever the
behaviour changes. An ADR is immutable once accepted, and a change of mind
produces a new ADR that supersedes it — so folding the rationale into the
design doc destroys it the first time the behaviour is revised.

| The decision | Design doc says | ADR says | ADR needed? |
|---|---|---|---|
| Sessions expire after 1h of inactivity, not on a fixed 24h clock | "A session expires 1 hour after last activity" | Why sliding expiry beat a fixed TTL: the support burden of mid-shift logouts against the exposure window of a stolen token | **Yes** — a contract clients time their refresh against |
| A bulk import rejects the whole file on the first bad row | "An import containing any invalid row is rejected in full; no rows are applied" | Why all-or-nothing beat partial application: partial imports left users unable to tell what landed, and the reconciliation cost exceeded the convenience | **Yes** — reversing it means reworking every caller's error handling |
| The public API returns cursor pages, not offset pages | "List endpoints accept `cursor` and `limit` and return `next_cursor`" | Why cursors beat offsets here: result sets mutate under the reader, and offset paging silently skipped rows | **Yes** — a public contract others write against |
| v1 of the API stays supported for two more releases | "v1 remains available through release N+2; v2 is the default from release N" | Why two releases and not one or five: the two largest integrators' upgrade cycles | **Yes** — a compatibility boundary |
| Deliberately *not* supporting nested groups in v1 | "Groups do not contain other groups" | Why the exclusion is deliberate: the permission model has no answer for inherited membership, and shipping nesting without one was judged worse than not shipping it | **Yes** — otherwise it reads as an oversight and someone "fixes" it |
| The error message wording on a validation failure | "Invalid input blocks submission with an inline error naming the field" | — | No — not contested, and reversible in minutes |
| Which section of the design doc the constraint lands in | (wherever it fits) | — | No — that's editing, not deciding |
| Cutting the epic into five tasks rather than three | (nothing — this isn't behaviour) | — | No — that's the Map Issue's rationale section |

### The test, restated

Read each statement in the doc you just wrote and ask two questions in order:

1. **Was there a real alternative?** If the statement is the only sensible way
   the system could behave, there was no decision — move on.
2. **Would reversing it cost a human half a day or more?** Reversing a public
   contract, a data shape, or a compatibility promise means finding and
   changing every writer against it. Reversing a wording choice means an edit.

Both yes → ADR. When you can't tell, write it: an unnecessary ADR costs one
file, and a missing one costs the next person a week of archaeology.

## Conflict Detection

Before writing, check:
1. `docs/design/index.md` — does an existing row cover the same feature area?
2. `docs/prd.md` — does an existing goal/scope line contradict this epic?

If either check finds something, present both the existing and new content to
the user and ask which takes precedence, or whether they're actually
complementary (e.g. this epic extends an existing design doc rather than
needing a new one — in that case, update the existing doc instead of creating
a new one).

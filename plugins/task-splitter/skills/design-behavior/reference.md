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

## Conflict Detection

Before writing, check:
1. `docs/design/index.md` — does an existing row cover the same feature area?
2. `docs/prd.md` — does an existing goal/scope line contradict this epic?

If either check finds something, present both the existing and new content to
the user and ask which takes precedence, or whether they're actually
complementary (e.g. this epic extends an existing design doc rather than
needing a new one — in that case, update the existing doc instead of creating
a new one).

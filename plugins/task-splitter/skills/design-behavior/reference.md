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

## `## Implementation Notes` Section

Every design doc gets this section, left empty at creation. It's the
consolidation point for what used to be separate ADRs and incident logs: once
`implementation-workflow`'s `feature-developer` builds the feature, it appends
technical decisions, snags hit, and lessons learned here — clearly separated
from the behavior-only body above it.

## Conflict Detection

Before writing, check:
1. `docs/design/index.md` — does an existing row cover the same feature area?
2. `docs/prd.md` — does an existing goal/scope line contradict this epic?

If either check finds something, present both the existing and new content to
the user and ask which takes precedence, or whether they're actually
complementary (e.g. this epic extends an existing design doc rather than
needing a new one — in that case, update the existing doc instead of creating
a new one).

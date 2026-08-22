# Issue Refinement — Extended Reference

## Structuring the Discussion

The user has said "this isn't right". That statement is usually accurate about
the symptom and incomplete about the cause. Work from symptom to cause before
proposing text.

Ask in this order, one at a time, always with a concrete proposal attached:

1. **Symptom** — which part is wrong? Quote the specific AC or sentence back
   to them rather than asking them to locate it.
2. **Cause** — is it wrong because (a) it was written badly, (b) it was right
   then and the world moved, or (c) the underlying decision was wrong? These
   need different treatment: (a) touches only the Issue, (b) usually touches
   the design doc too, (c) is an ADR.
3. **Correct content** — propose the replacement text. Show the before and
   after. Don't ask them to dictate it.
4. **Behaviour or description?** — ask outright: "does the system now do
   something different from what `docs/design/<slug>.md` says, or does the
   doc still hold and only the Issue was wrong?" This is the single question
   that determines whether Phase 2 produces a PR.
5. **Scope** — does the corrected task still fit in one PR? Does it now
   overlap with, or obsolete, another task in the graph?

Two things to hold to throughout:

- **Propose, don't interview.** Every question carries your best guess at the
  answer. The user's job is to correct you, which is much cheaper than
  composing from nothing.
- **Don't smuggle in improvements.** You will notice other things wrong with
  the Issue. Mention them once, as a list, and let the user decide whether
  they're in scope for this refinement. Silently fixing them makes the diff
  unreviewable.

## What Propagation Actually Requires

Finding every affected artifact is the part that's easy to under-do. Work
through all four:

**Downstream Issues.** `gh issue view <map-issue> --json body` and read the
graph: anything with this task in its "Depends on" may have been written
assuming the old behaviour. Read their ACs, not just their titles.

**Upstream Issues.** If the change means this task now needs something it
didn't before, that dependency has to appear in the graph — a corrected task
with a missing dependency will be picked as `ready` before its prerequisite
exists.

**The design doc.** `docs/design/<slug>.md`, plus `docs/design/index.md` if the
summary or status moved, plus `docs/prd.md` if a goal or scope boundary moved.

**Sibling design docs.** If the behaviour that changed is referenced by another
design doc (grep `docs/design/` for the feature name), that doc is now stale
too. Flag it to the user — it may be in scope, or it may deserve its own task.

## Map Issue Table Rules

The table shape, the status vocabulary, the whole-body-rewrite mechanics, and
the rule that every meaning-changing body edit is accompanied by a comment are
all in [../../docs/map-issue.md](../../docs/map-issue.md). This phase is the
only one that reshapes the graph itself, so three rules are specific to it:

- **Splitting a row:** create the new Task Issues first (task-splitter's Task
  Issue template — Description / Acceptance Criteria / Verification Method /
  Implementation Sketch), then replace the original row with one row per new
  Issue. Rewrite every "Depends on" that pointed at the original to point at
  whichever new Issue actually carries that dependency — never at all of them
  by default.
- **Adding a row:** insert it in topological position, not at the end. The
  table's order is meant to be a valid execution order.
- **Dropping a row:** close the Issue with a comment naming the decision that
  obsoleted it, and set its status cell to `dropped` rather than deleting the
  row.

Leave the `PR` column alone — it belongs to Phase 12 — and give a new row an
empty cell. Your accompanying comment should name this phase as the cause:

```bash
gh issue comment <n> --body-file - <<'C'
Refined at the implementation-workflow scrutiny gate.

**Changed:** AC 2 and 3 — a rejected booking now returns the conflicting
booking's id rather than a bare 409.
**Why:** <the user's reason>
**Design doc:** <doc PR URL>
C
```

## The Doc PR

Kept deliberately small and boring — it exists so the implementation PR's diff
contains only implementation.

- Branch `docs/<issue#>-<slug>`, cut from the freshest default branch.
- One commit, `docs(<scope>): <what the docs now describe>`. The body carries
  the *why*: what they said, what was wrong, what they say now.
- Contents: `docs/design/*`, `docs/prd.md`, and any ADR plus its
  `docs/adr/index.md` row. Nothing else — no source, no `.claude/`.
- Any ADR in it is `accepted`, not `draft` — see SKILL.md Step 3 for why.
- PR body: what changed and why, which Issues were updated alongside it, and
  the Issue this refinement came out of.

It must be merged before Phase 3 cuts the implementation branch. If the user
would rather not merge it right now, stop the run — resuming later is cheap,
and an implementation branch cut from a base that doesn't have the corrected
design is not.

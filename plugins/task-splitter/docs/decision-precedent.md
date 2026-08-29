# Decision Precedent — Check the ADR Record Before You Decide

Shared policy. Read it before settling any decision that might already be on
the books — most importantly right before
[vcs-minimalism.md](vcs-minimalism.md) §4's half-day test would turn it into
an ADR.

This document mirrors the copies in the `implementation-workflow` and
`light-workflow` plugins. All three install independently, so each carries its
own copy; **if you change one, change all three.**

`vcs-minimalism.md` says how a decision's *why* gets recorded once it's made.
It says nothing about checking, before you make it, whether the same fork was
already resolved — and in practice that check keeps getting skipped, so the
same question gets re-litigated, or resolved a second time in the opposite
direction, with nobody noticing the ADR that already covers it. This document
is that check.

---

## 1. When this applies

Any point where you're about to write something into `docs/design/<slug>.md`
as a plain fact, settle a fork while cutting the task graph, or write an ADR
of your own — anywhere `vcs-minimalism.md` §4's half-day test could turn what
you're about to do into an ADR. Run the check *before* you decide, not after:
catching a conflict once the design doc or task breakdown is already written
means undoing that work too.

## 2. How to check

1. Read `docs/adr/index.md`. It's a summary table — title, status, date — not
   the decision itself.
2. Open any ADR whose title or one-line summary *plausibly* touches the area
   you're about to decide on. Don't stop at an exact title match, and don't
   skip one because the title looks unrelated at a glance — index rows
   summarize, and the overlap is often in `Context`, not the title.
3. Read its `Decision` and, if present, `Alternatives Considered`.

This is a judgement call, not a mechanical search. A few minutes spent opening
the two or three ADRs that could plausibly bear on this is the whole cost;
reading all of them every time is not the point.

## 3. What counts as a conflict

| You find | This means |
|---|---|
| An **accepted** ADR that already settled this exact question, the same way you're about to | Not a conflict — cite it (`Refs: ADR-NNNN`) instead of deciding it again |
| An **accepted** ADR that settled this question the *opposite* way, or whose `Decision` your choice would contradict | A conflict |
| An ADR's `Alternatives Considered` already rejected the option you're about to choose, for a reason that still holds | A conflict — this is a decision being *re-litigated* silently, which is exactly what `Alternatives Considered` exists to prevent |
| An ADR marked `superseded by ADR-MMMM` or `deprecated` that covers this area | Read ADR-MMMM (or note the deprecation) — that's the current answer, not a conflict with it |
| Nothing on the books touches this | No conflict — decide normally, per `vcs-minimalism.md` §3/§4 |

## 4. What to do on a conflict

**Do not proceed past it silently, and do not silently write a new ADR that
overrides the old one.**

- **`design-behavior` or the orchestrator itself**, which both hold the user
  relationship directly: raise it with `AskUserQuestion` on the spot — show
  the existing ADR's `Decision` (or the rejected alternative) next to the
  direction you're about to take, and continue only once the user explicitly
  agrees.
- **`plan-tasks`**, which does not hold a gate with the user: don't raise it
  yourself. Report it to the orchestrator exactly the way Step 5 already
  reports any other planning-time decision — the fork, the conflicting ADR,
  and your reasoning — and let the orchestrator raise it at the confirm gate.

Once the user agrees, the new decision is written up as a supersession, per
[vcs-minimalism.md](vcs-minimalism.md) §4: a new ADR with
`**Supersedes:** ADR-NNNN`, and the *only* edit to the old file is its
`**Status:**` line, changed to `superseded by ADR-MMMM`. Update both rows in
`docs/adr/index.md`. If the user does not agree, keep the existing decision —
drop the direction that conflicted with it, or adjust the design/breakdown to
fit what's already accepted.

## 5. Who reads this

- **`design-behavior`**, Step 5, before writing an ADR for a statement the
  design doc is about to assert as fact.
- **`plan-tasks`**, Step 5, before treating a fork surfaced while cutting
  tasks as a new decision to report.
- **The orchestrator**, at the confirm gate (where every ADR this run wrote is
  already shown in full) and before authoring the `split`-mode ADR-only PR at
  Phase 4.

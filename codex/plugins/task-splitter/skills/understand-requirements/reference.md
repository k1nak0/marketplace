# Requirements Interview — Full Question Bank

Loaded on demand when SKILL.md's quick reference is insufficient. The topic
groups below are the **`design` mode** interview, conducted from scratch. For
`split` mode, read the last section first — most of these questions are already
answered.

---

## Topic Group 1 — Project Goals (Extended)

1. What is the single sentence that describes this epic to a new engineer?
2. What problem currently exists that this epic solves?
3. Who are the stakeholders (internal teams, external users, regulatory bodies)?
4. What is the expected scale (number of users, requests/second, data volume)?
5. Is there a deadline or milestone this must meet?

## Topic Group 2 — Core Features (Extended)

1. Walk me through the happy path from the user's perspective, step by step.
2. What are the three most likely error paths, and how should each be handled?
3. Is there an existing feature this replaces or extends? If so, must it remain
   backward compatible?
4. Can any part of this epic ship independently (vertical slicing)? This is a
   strong signal for how `plan-tasks` should split the work later.

## Topic Group 3 — Constraints (Extended)

### Performance
- What is the acceptable p99 latency under peak load?
- Is there a memory or CPU budget?

### Security
- Does this feature handle PII, PCI, or HIPAA-regulated data?
- What authentication/authorisation model applies?

### Compatibility
- What language/runtime version is mandated by the project?
- Does this feature expose or consume a versioned API contract?

### External Dependencies
- Does this require a new library/package not already in the dependency
  manifest? Name it, the use case, and the minimum version if so.

## Topic Group 4 — Scope Boundaries (Extended)

1. What would a reviewer reject as "out of scope, file a follow-up" if someone
   tried to sneak it into this epic?
2. Are there parallel epics or in-flight PRs this must not conflict with?
3. If this epic feels large, is there a natural feature-level seam that would
   make two smaller epics instead of one? (Don't force a split — just surface
   the option; the user decides.)

## Topic Group 5 — Definition of Done (Extended)

1. What observable behavior proves the whole epic works end-to-end?
2. Are there manual verification steps a human must run?
3. What must exist in `docs/design/` when this is done (behavior only — see
   `design-behavior`'s reference.md for the boundary)?

---

## Disambiguation Pattern

When a user answer is ambiguous, use this structure:

> "You said X. I interpret that as either:
>   (A) [concrete interpretation A with example]
>   (B) [concrete interpretation B with example]
> Which is correct, or is it something else?"

## Edge Cases to Watch

- **"We need it to be fast"** → Ask for a specific latency target and load definition.
- **"It should be secure"** → Ask which threat model applies.
- **"Keep it simple"** → Ask which complexity trade-offs are acceptable.
- **No external library mentioned** → Confirm explicitly: "Does this feature
  require any external library not already in the project?"
- **Epic feels like it's really two epics** → Surface it as a question, don't
  decide unilaterally; a wrong split here cascades into `plan-tasks`.

---

## Split Mode — Reading Requirements Out of a Design Doc

In `split` mode the epic's behaviour was settled in an earlier run, and
`docs/design/<slug>.md` is the record of it. Your job shifts from eliciting
requirements to **verifying that the design doc is a sufficient basis for a
task breakdown**, and filling the few gaps it leaves.

### What to read, in order

1. `docs/design/<slug>.md` in full — `## Overview` fixes the scope,
   `## Interfaces` and `## State Transitions` are what tasks get cut from,
   `## Constraints` is what acceptance criteria have to respect.
2. Its row in `docs/design/index.md` — the status tells you whether the doc is
   `draft` or settled.
3. `docs/prd.md` — for scope boundaries stated at the product level rather than
   in the doc.
4. `docs/adr/index.md` — an ADR touching this feature area is the *why* behind
   something the design doc states as fact. Read any that look relevant; a task
   that unknowingly contradicts an accepted decision is expensive to discover
   later.

### The four questions worth asking anyway

Even a complete design doc rarely answers these, and `plan-tasks` needs all
four:

1. **Is the whole doc in scope for this run, or a part of it?** A design doc
   can describe a feature that ships across several epics.
2. **Is there adjacent in-flight work this must not collide with?** The doc
   describes a system; it doesn't know what else is being built this week.
3. **Is a new dependency expected?** Design docs deliberately name no library,
   so this is invisible in the doc by construction.
4. **What would you check by hand before believing the epic is done?** The
   doc's constraints imply some of it, but manual verification steps are a
   judgement the user holds.

### When the doc isn't enough

Three findings are worth stopping for rather than working around. Report each
to the orchestrator rather than deciding alone:

| Finding | Why it's not yours to fix |
|---|---|
| The design doc contradicts what the user now says | One of the two has to change, and changing a committed contract is a `design`-mode run |
| The doc is silent on behaviour the tasks would have to implement | Inventing it here puts a decision into Task Issues that never reached the design doc |
| The doc still says `**Status:** draft` | It may be mid-review; splitting it registers Issues against a contract still in motion |

The third one is a warning, not a blocker — say it plainly and let the user
decide. The first two usually mean the run belongs in `design` mode against the
existing doc.

### A gap the doc leaves may be an ADR, not a question

If a gap turns out to be a genuine fork — the design doc is silent because
nobody ever chose, and the choice has consequences beyond this epic — then
answering it is *making* a decision at planning time, and
[../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md) §3 applies. Say so
when you report the gap: the orchestrator will need an ADR-only docs PR to get
the answer into version control, and it can only do that if it knows a decision
was made rather than a detail clarified.

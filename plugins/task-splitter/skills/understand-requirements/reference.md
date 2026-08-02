# Requirements Interview — Full Question Bank

Loaded on demand when SKILL.md's quick reference is insufficient.

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

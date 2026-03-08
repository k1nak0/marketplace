# Requirements Interview — Full Question Bank

This reference document is loaded on demand when SKILL.md's quick reference is
insufficient. It provides the complete question set, disambiguation patterns,
and edge case guidance.

---

## Topic Group 1 — Project Goals (Extended)

1. What is the single sentence that describes this feature to a new engineer?
2. What problem currently exists that this feature solves?
3. Who are the stakeholders (internal teams, external users, regulatory bodies)?
4. What is the expected scale (number of users, requests/second, data volume)?
5. Is there a deadline or milestone this must meet?
6. Are there related features planned in the next two sprints that this must not conflict with?

## Topic Group 2 — Core Features (Extended)

1. Walk me through the happy path from the user's perspective, step by step.
2. For each step, what is the system doing behind the scenes?
3. What are the three most likely error paths, and how should each be handled?
4. Is there an existing feature this replaces or extends? If so, must it remain backward compatible?
5. Can any part of this feature be shipped independently (vertical slicing)?

## Topic Group 3 — Constraints (Extended)

### Performance
- What is the acceptable p99 latency under peak load?
- What constitutes "peak load" (concurrent users or requests/minute)?
- Is there a memory or CPU budget?

### Security
- Does this feature handle PII, PCI, or HIPAA-regulated data?
- What authentication mechanism is in use (JWT, session cookie, API key)?
- What is the authorisation model (RBAC, ABAC, ownership)?
- Are there rate-limiting or abuse-prevention requirements?

### Compatibility
- What language/runtime version is mandated by the project (see CLAUDE.md)?
- Must this work on all three OS targets (Linux, macOS, Windows)?
- Does this feature expose or consume a versioned API? If so, what is the contract?

### External Dependencies
- Does this require a new library/package not already in the dependency manifest?
- If yes: name the library, the use case, and the minimum version required.
- Are there known licensing restrictions on new dependencies?

## Topic Group 4 — Definition of Done (Extended)

1. List every test that must pass for the feature to be considered complete.
2. Only **unit tests** (no I/O, no integration, no system/e2e) are in-scope for
   Phase 5 (automated implementation). Integration and e2e tests are always
   out-of-scope for the automated pipeline.
3. If a behaviour cannot be verified with a unit test, it is acceptable to omit
   the test — note it as out-of-scope with the reason "not unit-testable".
4. What documentation files must be updated? (CLAUDE.md, README, ADR, incident log?)
5. Is a migration script required? If so, what is the rollback plan?

---

## Disambiguation Patterns

When a user answer is ambiguous, use this structure:

> "You said X. I interpret that as either:
>   (A) [concrete interpretation A with example]
>   (B) [concrete interpretation B with example]
> Which is correct, or is it something else?"

Always anchor the clarification to a concrete code or behaviour example.

---

## Edge Cases to Watch

- **"We need it to be fast"** → Ask for a specific latency target and load definition.
- **"It should be secure"** → Ask which threat model applies (insider threat, external attacker, etc.).
- **"Keep it simple"** → Ask which complexity trade-offs are acceptable (e.g., no caching, no background jobs).
- **"Add tests"** → Clarify that only unit tests (no I/O) are in-scope for
  Phase 5. Integration and e2e tests are always out-of-scope. If the user
  expects integration or e2e tests, note them as manual verification steps in
  the Definition of Done, not as Phase 5 test cases.
- **No external library mentioned** → Confirm explicitly: "Does this feature require any external library not already in the project?"

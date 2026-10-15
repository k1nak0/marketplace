# Requirements Report

**Task ID:** <!-- filled by skill -->
**Created:** <!-- filled by skill -->
**Phase:** 1 — Requirement Understanding
**Mode:** design | split
**Design doc:** <!-- split mode: docs/design/<slug>.md. design mode: "none yet — written at Phase 2" -->

<!-- In split mode, mark any section filled from the design doc rather than
     from the user with "(from design doc)" after its heading. The design doc
     is the authority on behaviour; this report is the authority on what is in
     scope for this splitting run. -->

---

## 1. Project Goals

### Problem Statement
<!-- One sentence describing the problem being solved -->

### Primary Stakeholders
<!-- List of user roles or teams who consume this feature -->

### Success Criteria
<!-- Measurable outcomes that define success -->

### Roadmap Context
<!-- How this fits into the broader product plan -->

---

## 2. Core Features

### Must-Have (P0)
- [ ] Feature 1: ...
- [ ] Feature 2: ...

### Nice-to-Have (P1)
<!-- May be deferred to a follow-up epic -->
- Feature A: ...

### Anti-Features (Explicit Out-of-Scope)
- Must NOT: ...

---

## 3. Constraints

### Performance
- Latency target (p99): ...
- Throughput: ...
- Memory/CPU budget: ...

### Security
- Data classification: ...
- Authentication mechanism: ...
- Authorisation model: ...

### Compatibility
- Language/runtime version: ...
- OS targets: ...
- API contract: ...

### External Dependencies
- New library required: yes / no
- If yes: library name, use case, minimum version, license

---

## 4. Scope Boundaries

### Out of Scope
- ...

### Adjacent Work Not to Collide With
- ...

### Possible Epic Split
<!-- If the user identified a natural seam, note it here for plan-tasks -->
- ...

---

## 5. Definition of Done

### Epic-Level Success Condition
<!-- Observable behavior proving the whole epic works end-to-end -->

### Manual Verification Steps
- ...

### Documentation Expected
<!-- design mode -->
- [ ] `docs/design/<slug>.md` — behavior spec (written by design-behavior)
- [ ] `docs/prd.md` — updated with a link to the design doc
<!-- split mode: the design doc already exists; list only what this run adds -->
- [ ] `docs/adr/NNNN-<slug>.md` — only if a decision here passes the half-day test

---

## 6. Clarifications Log

| Ambiguity | Resolution |
|-----------|------------|
| ...       | ...        |

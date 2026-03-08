# Requirements Report

**Task ID:** <!-- filled by skill -->
**Created:** <!-- filled by skill -->
**Phase:** 1 — Requirement Understanding

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
<!-- Features that must be present for the task to be considered complete -->
- [ ] Feature 1: ...
- [ ] Feature 2: ...

### Nice-to-Have (P1)
<!-- Features that may be deferred to a follow-up task -->
- Feature A: ...

### Anti-Features (Explicit Out-of-Scope)
<!-- Behaviours the implementation must NOT exhibit -->
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
- If yes:
  - Library name: ...
  - Use case: ...
  - Minimum version: ...
  - License: ...

---

## 4. Definition of Done

### Automated Tests (In-Scope for Phase 5)
<!-- Tests that the Feature Developer subagent must write and pass -->
| Test ID | Type | Description | Input | Expected Output |
|---------|------|-------------|-------|-----------------|
| T-001   | unit | ...         | ...   | ...             |

### Out-of-Scope Tests (Require Manual Verification)
<!-- Tests requiring live external APIs, UI interaction, or human judgement -->
- OOS-001: ...

### Documentation Updates Required
- [ ] CLAUDE.md — new rules, build commands, or workarounds
- [ ] README.md — user-facing changes
- [ ] docs/decision-records/<task-id>-adr.md — architectural decisions
- [ ] docs/incident-logs/<task-id>-log.md — implementation notes

### Deployment / Rollout Notes
<!-- Migration scripts, feature flags, rollback plan -->
- ...

---

## 5. Clarifications Log
<!-- Record of ambiguous inputs and how they were resolved during the interview -->

| Ambiguity | Resolution |
|-----------|------------|
| ...       | ...        |

# Implementation Plan

**Task ID:** <task-id>
**Phase:** 6 — Implementation Planning
**Source:** map-issue (#<task-issue>) | standalone
**Design doc:** docs/design/<slug>.md | none

## Background & Goal

<Purpose and scope. What problem does this solve, what's the success condition?
Note any discrepancy between task-splitter's Implementation Sketch and what
codebase investigation actually found.>

**Decisions likely to need an ADR:** <Any decision here that would take a human
half a day or more to reverse — a persisted data shape, a public interface, a
new dependency, a concurrency model, a security boundary. "None expected" is a
valid and useful answer.>

## Technical Specification

### Files to Modify
| File | Change type | Symbols affected |
|------|-------------|-----------------|

### New Symbols to Create
| Symbol | Type | Location | Purpose |
|--------|------|----------|---------|

### Libraries
| Library | Version | Usage |
|---------|---------|-------|

### Data Structures
<New or modified data structures with field names and types.>

### CLAUDE.md Compliance
<Every CLAUDE.md rule that applies here, confirmed as followed.>

## Test Strategy

**Test Strategy:** automated | manual
**Why:** <One line. What made this the right call — and, if manual, why an
automated test genuinely cannot express the behaviour.>

**CI:** present | extend (`<file>`, `<what's missing>`) | bootstrap (`<test command>`)

### If automated — Test Cases

Written and human-approved BEFORE any implementation exists, then committed and
frozen. Only unit-level tests (no live I/O, no integration/e2e) are in scope.
Describe behaviour, not units.

| Test ID | Description | Input | Expected Output | Out-of-Scope? |
|---------|-------------|-------|-----------------|---------------|

### Test Runner Command
```bash
```

### If manual — Verification Steps

<Numbered steps, each with an action and the exact observation that
constitutes a pass. Name any docs/tool.md tool a step needs. This procedure is
approved at the Phase 8 gate, posted to the Issue, and executed verbatim by
the implementer — it is never committed.>

## Documentation Update Plan

<Only CLAUDE.md and README.md, and only where the change affects what they
state. Name the section and what it should say. "No documentation update
expected" is a valid entry. docs/design/<slug>.md is deliberately absent from
this list — see docs/vcs-minimalism.md.>

## Out-of-Scope

- OOS-001: UI/visual regression tests
- OOS-002: Tests requiring live external API connections
- OOS-003: Integration tests
- OOS-004: System/end-to-end tests

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

## Specification

Every acceptance criterion appears in exactly one place: an automated test
case, a manual test step, or the Out-of-Scope table at the end. The first two
are written and human-approved BEFORE any implementation exists, then committed
and frozen in one `test(...)` commit. Describe behaviour, not units.

**CI:** present | extend (`<file>`, `<what's missing>`) | bootstrap (`<test command>`) | n/a — no automated tests

### Automated Test Cases

Unit-level only — no live I/O, no integration/e2e. "none" is a valid entry.

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|

**Test runner command:** `<command>`

### Manual Test Steps

Committed to `docs/manual-tests/<slug>.md` and frozen alongside the automated
tests — the implementer may not edit them either. "none" is a valid entry, and
is the common case for pure logic changes.

| Step | Action | Pass criterion | Why not automated |
|------|--------|----------------|-------------------|

<Both sections empty is not a valid plan.>

## Documentation Update Plan

<Only CLAUDE.md and README.md, and only where the change affects what they
state. Name the section and what it should say. "No documentation update
expected" is a valid entry. docs/design/<slug>.md is deliberately absent from
this list — see docs/vcs-minimalism.md.>

## Out-of-Scope

Criteria deliberately not specified this task. Listed, not omitted — the human
at the Phase 8 gate needs to see what is being left out on purpose.

| ID | Not specified | Why |
|----|---------------|-----|
| OOS-001 | | |

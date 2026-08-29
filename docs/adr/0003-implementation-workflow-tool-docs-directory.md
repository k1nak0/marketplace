# ADR-0003: Split `implementation-workflow`'s tool documentation into a `docs/tools/` directory, diverging from `task-splitter`'s single file

**Status:** accepted
**Date:** 2026-08-29
**Related:** [`plugins/implementation-workflow/skills/onboarding/`](../../plugins/implementation-workflow/skills/onboarding/SKILL.md)

## Context

Both `task-splitter` and `implementation-workflow` read a single
`docs/tool.md` that a consuming project fills in: Test Command, Lint/Build
Commands, Code Search Tools (MCP or CLI), Verification Tools (MCP), and
Notes. `CLAUDE.md` listed `templates/tool-template.md`'s two copies among the
duplications the two plugins must keep byte-for-byte in sync.

In practice, a single collated file conflated two different questions: what a
tool *is* (agnostic of who reaches for it) and which *agent* should reach for
it. A real consuming project's `docs/tool.md` put a Godot-engine-documentation
MCP server under the same "Code Search Tools" heading `repository-explorer`
reads for a codebase-symbol-search tool — the two are different jobs, and the
shared heading gave no way to tell them apart. `repository-explorer`
correctly declined to use it (it isn't a codebase-search tool), but the tool
was in fact exactly what `library-researcher` was built to prefer, and
nothing pointed there.

Separately, two entries in the single file had no real consumer at all:
Lint/Build Commands were collected by `onboarding` but read by no agent, and
`code-reviewer` / `test-reviewer` were never wired to the Verification Tools
section despite the template's own comment claiming they were.

`implementation-workflow` has six agents plus several inline skills with
different, specific reasons to reach for a tool; `task-splitter` has a much
smaller surface (one orchestrator startup nudge, one skill's optional
code-search preference). The fix that solves `implementation-workflow`'s
problem — separating "what is this tool" from "who should use it, and how" —
is not needed by `task-splitter`, and forcing `task-splitter` to adopt the
same directory shape for symmetry alone would be duplication for its own
sake, not because both plugins actually need it.

## Decision

`implementation-workflow` replaces its `docs/tool.md` /
`templates/tool-template.md` contract with a `docs/tools/` directory:

- `docs/tools/<tool-slug>.md` — one file per external tool (MCP server, CLI),
  tool-centric only. It states what the tool is and how to reach it; it says
  nothing about which agent uses it.
- `docs/tools/<agent-or-skill-name>.md` — one file per consumer that has an
  actual reason to reach for a tool (`repository-explorer`,
  `library-researcher`, `test-writer`, `implementation-planning`,
  `implementer`, `code-reviewer`, `test-reviewer`), written from that
  consumer's own point of view and linking to the relevant tool file(s).
  Which consumer gets a file for which tool category is a fixed mapping
  (`plugins/implementation-workflow/skills/onboarding/reference.md` §3), not
  something re-decided per project.

Every agent/skill that used to check `docs/tool.md` now checks its own
`docs/tools/<name>.md` first. `implementer` gains a real consumer for
Lint/Build Commands (a new step running them before finishing). `code-reviewer`
gains a step independently re-verifying a manual-test step via a named
Verification Tool rather than only trusting the recorded observation;
`test-reviewer` gains a check that a named Verification Tool is actually
reachable. `onboarding` is rewritten to detect and offer to migrate an
existing `docs/tool.md` onto the new layout, hearing for any tool the old
file missed along the way.

`task-splitter` is **not** changed. It keeps `docs/tool.md` and
`templates/tool-template.md` exactly as they were. The two plugins' tool-doc
mechanisms are no longer required to be kept in sync — `CLAUDE.md`'s
duplication list drops from five items to four, with this one called out as a
divergence rather than a duplication going forward.

## Consequences

- A consuming project adopting only `implementation-workflow` gets a directory
  instead of a file; `docs/tool.md` from a project that also uses
  `task-splitter` continues to work for that plugin unchanged.
- A project using both plugins now maintains two different tool-doc
  mechanisms side by side until (if ever) `task-splitter`'s own agent surface
  grows enough to need the same split. `onboarding`'s migration path only
  touches `implementation-workflow`'s half.
- The ambiguity that caused the Godot-docs miscategorization is structurally
  prevented: a tool file never claims a category that implies a consumer, so
  there is nothing for two different consumers' needs to collide inside.
- `code-reviewer` and `test-reviewer` gaining real behaviour (not just a doc
  reference) means a project whose Verification Tool is flaky or slow now
  pays that cost twice — once at Phase 8 (reachability) and again at Phase 11
  (independent re-execution). Both steps degrade to a documented fallback
  (skip the check, note it) rather than blocking when the tool is undocumented
  or unreachable, so the cost is paid only by projects that named a tool in
  the first place.
- If `task-splitter` later needs the same split, that is a new ADR — this one
  intentionally does not promise the two will converge.

## Alternatives Considered

**Keep one `docs/tool.md`, add a "who" tag inside each entry.** Considered and
rejected during discussion of this change: it still leaves one file as both
the tool's description and every consumer's routing table, so a project
editing "who uses this" is editing the same file another consumer reads for
"what is this" — the coupling that caused the original miscategorization
would remain, just moved from an ambiguous heading to an ambiguous tag.

**Apply the same `docs/tools/` split to `task-splitter` for symmetry.**
Rejected for now: `task-splitter`'s only two consumers (a startup nudge and
one skill's optional code-search preference) don't have `implementation-workflow`'s
multi-consumer routing problem, so the split would be a second contract to
maintain for no consumer-side benefit. Revisit if `task-splitter` grows more
tool-aware skills.

**Keep `docs/tool.md` and disambiguate the sections without restructuring
(rename "Code Search Tools" to something narrower, add a "Library Docs
Tools" section).** Would have fixed the one observed miscategorization
without a directory, but does nothing for the two dangling entries
(Lint/Build Commands, the unwired `code-reviewer`/`test-reviewer` mentions) or
for future consumers that need the same tool for different reasons — each new
case would mean another ad-hoc section rather than a structural fix.

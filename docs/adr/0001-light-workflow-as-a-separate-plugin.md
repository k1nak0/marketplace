# ADR-0001: Ship the lightweight workflow as its own plugin, not as a mode of `implementation-workflow`

**Status:** accepted
**Date:** 2026-08-23
**Related:** [`plugins/light-workflow/`](../../plugins/light-workflow/skills/light-workflow/SKILL.md)

## Context

`implementation-workflow` is thirteen phases, six agents, four policy documents
and a workspace of handoff files. That weight buys real things — a
human-approved specification the implementer cannot bend, a fresh-context
reviewer, a run that survives a session restart — and it is the right trade for
a task that came off a Map Issue.

It is the wrong trade for a one-file fix, and users were paying it anyway or
abandoning the plugins entirely for such changes. We needed a path that keeps
the parts of the philosophy that are about *the repository* — source code as
the only *how*, every *why* in VCS, nothing committed before a human says so —
while dropping the parts that are about *ceremony*: the test freeze, the
automated review loop, the Issue lifecycle, the file-based phase handoff.

Two shapes were available: a lighter mode inside the existing plugin, or a
third plugin alongside it. The choice determines how a user selects a
workflow, how much of the policy text is duplicated, and how independently the
two can evolve.

## Decision

We will ship the lightweight path as a separate plugin, `light-workflow`, with
a single user-invocable orchestrator skill, no subagents, and its own copy of
`docs/vcs-minimalism.md` — bringing the number of copies of that policy to
three.

The plugin's divergences from `implementation-workflow` are deliberate and
enumerated in `plugins/light-workflow/skills/light-workflow/reference.md` §6:
no test code, no committed verification procedure, no GitHub Issue integration,
no workspace directory, one approval gate. Sections 2 (the *why* routing) and 3
(ADRs) of the policy copy stay byte-for-byte equivalent to the other two
copies; the divergence is confined to section 1 and is marked there.

## Consequences

- The user chooses a workflow by choosing a skill, at invocation time, on a
  decision they already have to make ("is this a small change?"). No flag, no
  mode, and no phase in either plugin that has to branch on which mode it's in.
- Each plugin still installs and works alone, which is the marketplace's whole
  premise. `light-workflow` depends on nothing from the other two — it only
  *points at* `implementation-workflow` and `task-splitter` when a run turns
  out to be too big for it.
- **The sync burden goes from two copies of the VCS policy to three.** This is
  the real cost. It is mitigated by keeping the divergence in one marked
  section and by the "change one, change all three" rule stated at the top of
  each copy, but it is not eliminated: a policy change now requires three
  edits, and nothing mechanical enforces it.
- A change shipped through `light-workflow` leaves behind no re-runnable check,
  because its verification procedure lives in the PR body. That is the intended
  trade for a small change and a hazard for a large one; the plugin says so at
  the point where a run would feel that.
- Adding a fourth workflow later means a fourth copy. If that happens, the
  duplication should be revisited — a shared policy plugin, or a documented
  single source with a sync check in CI — and that revision will need a new ADR
  superseding this one.

## Alternatives Considered

**A `--light` mode inside `implementation-workflow`.** Zero duplication of the
policy docs, and one plugin to install. Rejected because the mode flag would
have to be threaded through every phase and every agent prompt, and each phase
would grow a conditional for behaviour it never performs in light mode — the
test-freeze verification in `code-reviewer`, the Map Issue writes in
`persistence-engineer`, the workspace contracts everywhere. The lightweight
path would be defined by what it skips, which is exactly how a "light mode"
decays back into the heavy one.

**A skill inside `implementation-workflow` rather than a new plugin.** Cheaper
than a plugin, and it would share the policy docs by relative link. Rejected
because it would make the light path unavailable to anyone who installed only
`task-splitter` or nothing at all, and because it would put a skill that
deliberately breaks the plugin's central invariant (the specification freeze)
inside the plugin that exists to enforce it.

**Keeping the policy in one place and linking across plugins.** Rejected on
the same grounds as the existing duplications documented in `CLAUDE.md`: a
plugin has to work with the others absent, so it cannot link into a sibling's
files. The duplication is the price of independent installability, and it was
already being paid twice.

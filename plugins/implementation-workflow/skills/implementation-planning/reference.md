# Implementation Planning — Extended Reference

## Test Strategy Inference

Prefer `automated` when:
- The requirements report's Definition of Done explicitly lists unit-testable
  behaviour.
- The change is a pure function / library-level change with no I/O, UI, or
  external system involved.
- `docs/tool.md`'s "Test Command" section is filled in and the change fits
  within what that test command exercises.

Prefer `manual` when:
- The change is primarily visual/UI, or requires a live external system.
- `docs/tool.md`'s "Verification Tools (MCP)" section names something clearly
  applicable (a Playwright MCP for a UI change, a Godot MCP for a scene
  change) — that's a strong signal manual verification with that tool is the
  right call.
- The requirements report's Definition of Done explicitly calls out manual
  verification steps.

Ambiguous (ask the user) when:
- The change touches both pure logic and something that needs live
  verification, and it's not obvious which one gates "done" — ask whether
  both should apply or one is sufficient.
- Neither `docs/tool.md` nor the requirements report gives a signal either
  way.

## Copying `task-breakdown-plan.md`'s Implementation Sketch Forward

If `requirements-report.md` carries a "Sketch from task-splitter" note (see
`requirement-understanding`'s reference.md), treat it as a hypothesis to
validate against `impact-analysis-report.md`, not as something to copy
verbatim into the Technical Specification. If codebase investigation
contradicts the sketch, the plan should reflect what's actually true of the
codebase — note the discrepancy in Background & Goal so it's visible.

## Documentation Update Plan Guidance

Be specific enough that `feature-developer` doesn't have to re-derive intent:
- Which `CLAUDE.md` section (Build & Run / Conventions / Architecture /
  Workarounds) new content belongs in, if any.
- Whether `README.md` needs a new command/env-var/config entry.
- What belongs in `docs/design/<slug>.md`'s `## Implementation Notes` — a
  one-line pointer is enough (e.g. "note the caching strategy chosen and
  why"), the actual writing happens after implementation.

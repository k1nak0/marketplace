# Implementation Planning — Extended Reference

## Test Strategy Inference

`automated` is the default. Reach for it when:

- The requirements report's Definition of Done lists behaviour that can be
  stated as an input and an expected result.
- The change is logic with no unavoidable I/O, UI, or live external system.
- `docs/tool.md`'s "Test Command" is filled in and the change sits inside what
  that command exercises.

`manual` only when an automated test genuinely cannot express the behaviour:

- The behaviour is visual, or is a property of a rendered surface.
- Verifying it requires a live external system that can't be stood in for.
- `docs/tool.md`'s "Verification Tools (MCP)" names something clearly
  applicable (a Playwright MCP for a UI change, a Godot MCP for a scene) — a
  strong signal that manual verification with that tool is the intended route.

"Awkward to test", "would need a fixture", and "the existing suite has no
precedent for this" are **not** reasons for `manual`. They're reasons to write
the fixture.

Ask the user when:

- The change has both a logic core and a surface that needs live checking, and
  it isn't obvious which one gates "done" — ask whether both apply or one
  suffices. Splitting the strategy (automated for the core, a manual step for
  the surface) is a legitimate answer; record both in the plan.
- Neither `docs/tool.md` nor the requirements report gives any signal.

The consequence of this choice is larger than it used to be: `automated`
produces a frozen, committed specification that the implementer cannot alter,
while `manual` produces a procedure that lives only on the Issue. Say which
one you chose and why in the plan's Test Strategy section.

## CI Readiness

For `automated`, tests that only ever run on one agent's machine aren't a
specification — they're a suggestion. The plan must record which case applies:

| Finding | What the plan says |
|---|---|
| A workflow runs this suite on PRs to the default branch | `CI: present` — nothing to do |
| A workflow exists but this suite isn't in it, or a path filter excludes it | `CI: extend` — name the file and what's missing |
| No workflow at all | `CI: bootstrap` — name the test command it must run |

`test-writer` acts on this, and whatever it adds goes in the test commit. Keep
the bootstrap minimal and native to the project: its existing package manager,
its existing language version, install + run the test command, on `push` and
`pull_request`. Do not introduce new tooling, caching schemes, or a matrix
nobody asked for — this is a task-scoped side effect, and a large CI diff will
dominate the review of the actual change.

If the project deliberately has no CI (no remote, an internal-only repo), the
user will say so at the Phase 8 gate. Record it as `CI: bootstrap` anyway and
let them decline — the plan's job is to make the absence visible.

## Writing the Test-Case Table

The table is read twice: by `test-writer` to write the tests, and by the human
at the Phase 8 gate to decide whether the specification is right. Write for
the second reader.

| Test ID | Description | Input | Expected Output | Out-of-Scope? |
|---|---|---|---|---|
| T-001 | rejects a booking overlapping an existing one | a slot overlapping #42 | 409 with `existing_id: 42` | |
| T-002 | accepts a booking abutting an existing one | a slot starting exactly at #42's end | 201 | |

- Describe the **behaviour**, not the unit: "rejects an overlapping booking",
  not "test `validate()` returns false".
- One row per behaviour. If a row needs "and" in its description, it's two.
- Expected output must be concrete enough that two people would write the same
  assertion from it.
- Boundaries are rows, not parenthetical notes: the limit, the limit ± 1,
  empty, the specified error case.
- Mark out-of-scope rows explicitly rather than omitting them — the human at
  the gate needs to see what is deliberately not being specified.

## Carrying `task-breakdown-plan.md`'s Implementation Sketch Forward

If `requirements-report.md` carries a "Sketch from task-splitter" note, treat
it as a hypothesis to validate against `impact-analysis-report.md`, not as
something to copy into the Technical Specification. Where investigation
contradicts the sketch, the plan reflects the codebase — note the discrepancy
in Background & Goal so it's visible rather than silently overridden.

## Documentation Update Plan Guidance

Only two repository documents are in play, and both only when the change
actually affects what they state:

- **`CLAUDE.md`** — name the section (Build & Run / Conventions / Architecture
  / Workarounds) and what belongs there. A new build command, a new
  convention, a workaround an agent would otherwise trip over.
- **`README.md`** — a new command, env var, config key, or changed
  user-visible behaviour.

If neither needs a change, say so explicitly: "No documentation update
expected." An empty section reads as an oversight; an explicit "none" reads as
a decision.

`docs/design/<slug>.md` is **not** in this section. It has no
`## Implementation Notes` section any more, and the implementer does not edit
its behaviour body — if the implementation ends up contradicting the design
doc, that's escalated to the human, not written away.

### Flagging ADRs in advance

If you can already see a decision the implementer will have to make that would
take a human half a day or more to reverse — a persisted data shape, a public
interface, a new dependency, a concurrency or consistency model, a security
boundary — say so in the plan under Background & Goal. Naming it up front is
much better than the implementer noticing at the end that the thing they built
three hours ago needed an ADR.

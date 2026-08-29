# Implementation Planning — Extended Reference

## Routing a Criterion: Automated or Manual

This is a per-criterion decision, not a per-task one. A task with a logic core
and a rendered surface gets automated tests for the core *and* manual steps for
the surface — that's the normal shape, not a compromise.

**Automated** is the default. Route a criterion here when:

- It can be stated as an input and an expected result.
- It's logic with no unavoidable I/O, UI, or live external system.
- `docs/tools/implementation-planning.md` names a Test Command and the change
  sits inside what that command exercises.

**Manual** only when an automated test genuinely cannot express the behaviour:

- The behaviour is visual, or is a property of a rendered surface.
- Verifying it requires a live external system that can't be stood in for.
- `docs/tools/implementation-planning.md` names a Verification Tool clearly
  applicable (a Playwright MCP for a UI change, a Godot MCP for a scene) — a
  strong signal that a manual step with that tool is the intended route.

"Awkward to test", "would need a fixture", and "the existing suite has no
precedent for this" are **not** reasons for manual. They're reasons to write
the fixture.

**Ask the user** when neither `docs/tools/implementation-planning.md` nor the
requirements report gives any signal for a criterion, or when you can see an
automated route but suspect it would test a proxy for the behaviour rather
than the behaviour. Name the criterion and what makes it ambiguous; don't ask
a generic "automated or manual?" about the whole task.

Both kinds carry the same weight downstream: both are committed, both are
frozen at the Phase 9 gate, and the implementer may edit neither. The manual
ones land in `docs/manual-tests/<slug>.md`, which `README.md` links to — so
write the reason each one isn't automated into the plan. It ends up in a
document people read.

## CI Readiness

Whenever there are automated test cases, tests that only ever run on one
agent's machine aren't a specification — they're a suggestion. The plan must
record which case applies:

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
user will say so at the Phase 9 gate. Record it as `CI: bootstrap` anyway and
let them decline — the plan's job is to make the absence visible.

If the task has no automated test cases at all, record `CI: n/a — no automated
tests this task` rather than leaving the field blank.

## Writing the Test-Case Table

The table is read twice: by `test-writer` to write the tests, and by the human
at the Phase 9 gate to decide whether the specification is right. Write for
the second reader. The same applies to the manual steps.

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

A manual step follows the same rules, with the assertion replaced by an
observation: "the list re-sorts within 300ms and the previously selected row
stays selected" passes; "check that sorting works" does not. If two people
reading the step would disagree about whether it passed, it isn't written yet.

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

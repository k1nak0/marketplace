# CLAUDE.md

This file provides AI agent context for the k1nak0/marketplace repository.

---

## task-splitter Plugin

Interviews the user for requirements, writes a behavior-only design doc, splits
an epic into PR-sized tasks, confirms the split with the user, and registers
everything as a GitHub Map Issue plus per-task Issues. Entry point:
`/task-splitter:task-splitter`.

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding | Skill: `understand-requirements` | `requirements-report.md` |
| 2 | Behavior Design | Skill: `design-behavior` | `docs/design/<slug>.md`, updated `docs/design/index.md` + `docs/prd.md` |
| 3 | Task Planning | Skill: `plan-tasks` | `task-breakdown-plan.md` (topological order, AC, verification method, implementation sketch) |
| — | Confirm Gate | Orchestrator inline (`AskUserQuestion`) | go/no-go before Issue creation |
| 4 | Task Registration | Skill: `register-tasks` | Map Issue + Task Issues via `gh` CLI |

See `plugins/task-splitter/skills/*/reference.md` for the behavior/
implementation boundary, task-grain heuristics, and the Map/Task Issue body
formats.

---

## implementation-workflow Plugin

Takes a task off a `task-splitter` Map Issue (or a standalone requirement)
through user scrutiny, investigation, planning, human-approved test-first
specification, implementation against frozen tests, review, history cleanup,
and PR. Entry point: `/implementation-workflow:implementation-workflow`.

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding & Task Selection | Skill: `requirement-understanding` | `requirements-report.md`; the user picks the task (always asked, even when one is ready) and approves its content at a scrutiny gate; claims it as `in-progress` only after approval |
| 2 | Issue Refinement *(conditional)* | Skill: `issue-refinement` | on `needs-refinement`: rewritten Task/Map Issues + `docs/design/` updates, shipped as **their own PR**, merged before Phase 3 |
| 3 | Branch Setup | Orchestrator inline | `<type>/<issue#>-<slug>` cut from the freshest default branch; refuses to start on a dirty tree |
| 4 | Codebase Investigation | Agent: `repository-explorer` | `impact-analysis-report.md` |
| 5 | Library Investigation *(conditional)* | Agent: `library-researcher` | `library-usage-report.md` |
| 6 | Implementation Planning | Skill: `implementation-planning` | `implementation-plan.md` + CI readiness finding, posted to the Task Issue (or a new standalone tracking Issue) |
| 7 | Test Authoring | Agent: `test-writer` | test files (+ scaffolding, + CI if absent) and `test-manifest.json` |
| 8 | Test Review Gate & Freeze | Orchestrator inline | human approves the tests → committed locally as one `test(...)` commit; that SHA is the freeze point |
| 9 | Implementation | Agent: `implementer` *(resumable this session)* | source changes, `why-notes.md`, any ADR; **cannot modify tests** — escalates via `test-dispute.md` |
| 10 | Automated Review | Agent: `code-reviewer` | `review-report.md`; verifies the test freeze mechanically before anything else; loops back to Phase 9 on FAIL, up to 5 attempts |
| 11 | Human Review Gate | Orchestrator inline | `approve` or `request-changes` via `AskUserQuestion`; any ADR is reviewed here too |
| 12 | History Cleanup & Persistence | Agent: `persistence-engineer` | regroups the branch into `test` + implementation commits, finalises draft ADRs, pushes (`--force-with-lease` only after a rewrite), opens/updates the PR |
| 13 | Map Issue Update | Orchestrator inline | `map-issue`: flips the row to `done`, closes the Task Issue. `standalone`: closes the tracking Issue Phase 6 created. Phases 9/10 flip the row to `blocked` instead on an unresolved halt (`map-issue` only) |

Shared premises all file-writing agents read first live in
`plugins/implementation-workflow/docs/`: `vcs-minimalism.md` (what may land in
VCS, the *why* routing, ADR rules), `git-workflow.md` (branching, commit shape,
the soft-reset regroup, push policy), `test-first.md` (the
`test-writer`/`implementer` contract and how the freeze is verified). The
orchestrator resolves that directory once at Step 0 and passes it into every
agent prompt.

See `plugins/implementation-workflow/skills/*/reference.md` and `agents/*.md`
for test-strategy inference, the scrutiny checklist, the review-loop cap, and
the PR body contract.

Standalone skill (outside the thirteen-phase pipeline): `onboarding`
(`/implementation-workflow:onboarding`) — verifies `gh` CLI/GitHub-remote
prerequisites, reports CI and `docs/adr/` readiness, and creates or updates the
consuming project's `docs/tool.md`. Run once when adopting the plugin, or
whenever project tooling changes. See
`plugins/implementation-workflow/skills/onboarding/reference.md` for the
manifest-file auto-detection heuristics.

---

## Shared Conventions (both plugins)

- **No bundled MCP servers.** Neither plugin ships a `.mcp.json`. GitHub
  operations go through the `gh` CLI. Code search and library-doc lookup
  default to built-in tools (`Grep`/`Glob`/`Read`, `WebSearch`/`WebFetch`).
  Project-specific MCP tools (a code-search server, a docs server, a
  Playwright/Godot MCP for verification, etc.) are declared by the
  *consuming* project in its own `docs/tool.md`; skills/agents `ToolSearch`
  for them by name when `docs/tool.md` mentions one. Both orchestrators check
  for `docs/tool.md` at startup and print a starter template if it's missing
  — this is a nudge, not a requirement. `implementation-workflow`'s
  `onboarding` skill is where a user actually resolves that nudge instead of
  dismissing it.
- **No custom session-management infrastructure.** No SessionStart hooks, no
  `status.json` state machine. Cross-phase handoff is plain markdown files
  under `.claude/task-splitter/<task-id>/` or
  `.claude/implementation-workflow/<task-id>/`. Orchestrators use the
  harness's own `TaskCreate`/`TaskUpdate` for in-session progress tracking. If
  a session is interrupted, resuming is manual: tell the orchestrator which
  task directory to continue, and it infers what's done from which files
  already exist there.
- **VCS minimalism.** The *how* is carried by source code alone — plans,
  reports, verification procedures, and implementation narrative go to Issues
  and PR bodies, never to a committed file. The *why* always goes into VCS, in
  one of three places: a source comment (reasoning local to one file), the
  commit message body (reasoning spanning several), or an ADR (any decision a
  human would need half a day or more to reverse). Each plugin carries its own
  copy of this policy at `plugins/<plugin>/docs/vcs-minimalism.md` because
  plugins install independently — **change one, change both.**
- **`docs/adr/`** holds numbered ADRs (`NNNN-<slug>.md`, sections Status /
  Context / Decision / Consequences / Alternatives Considered). Standard
  lifecycle: written as `draft`, flipped to `accepted` when the change ships;
  once out of `draft`, `Decision` and `Context` are immutable and a change of
  mind means a new superseding ADR. `docs/decision-records/` and
  `docs/incident-logs/` are frozen historical reference; no new entries.
- **`docs/design/`** holds one behavior-only doc per feature — observable
  inputs/outputs, interfaces, constraints, state transitions. No language,
  library, algorithm, or file-layout detail. **No `## Implementation Notes`
  section** — that was a *how* document in VCS and has been removed; technical
  decisions now route to the three *why* channels above, and implementation
  narrative to the PR body.
- **`docs/prd.md`** is a single living file: product goals, scope boundaries,
  and links into `docs/design/`. Updated incrementally by `task-splitter`,
  never overwritten wholesale.
- **No tool allowlists.** Neither plugin's skills declare `allowed-tools` and
  no agent carries a "Tool Discipline" section — both plugins assume a
  sandboxed environment. Restrictions that are *behavioural* rather than
  mechanical are still stated as rules (the implementer not touching frozen
  tests, investigation agents not editing source).
- Subagent return values are chosen per phase for what's actually useful to
  the caller — not a fixed "summary only" rule.

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

Takes a ready task off a `task-splitter` Map Issue (or a standalone
requirement) through investigation, planning, implementation, review, human
approval, and commit/PR. Entry point:
`/implementation-workflow:implementation-workflow`.

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding | Skill: `requirement-understanding` | `requirements-report.md` |
| 2 | Codebase Investigation | Agent: `repository-explorer` | `impact-analysis-report.md` |
| 3 | Library Investigation *(conditional)* | Agent: `library-researcher` | `library-usage-report.md` |
| 4 | Implementation Planning | Skill: `implementation-planning` | `implementation-plan.md`, posted to the Task Issue (or a new standalone Issue) |
| 5 | Implementation | Agent: `feature-developer` *(resumable this session)* | modified source + `CLAUDE.md`/`README.md`/`docs/design/*` updates |
| 6 | Automated Review | Agent: `code-reviewer` | `review-report.md`; loops back to Phase 5 on FAIL, up to 5 attempts |
| 7 | Human Review Gate | Orchestrator inline | `approve` or `request-changes` via `AskUserQuestion` |
| 8 | Persistence | Agent: `persistence-engineer` | commit, push, PR via `gh` |
| 9 | Map Issue Update | Orchestrator inline | flips the task's row to `done`, closes the Task Issue (skipped for standalone tasks) |

See `plugins/implementation-workflow/skills/*/reference.md` and
`agents/*.md` for test-strategy inference rules, the review-loop cap, and the
PR body contract.

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
  — this is a nudge, not a requirement.
- **No custom session-management infrastructure.** No SessionStart hooks, no
  `status.json` state machine. Cross-phase handoff is plain markdown files
  under `.claude/task-splitter/<task-id>/` or
  `.claude/implementation-workflow/<task-id>/`. Orchestrators use the
  harness's own `TaskCreate`/`TaskUpdate` for in-session progress tracking. If
  a session is interrupted, resuming is manual: tell the orchestrator which
  task directory to continue, and it infers what's done from which files
  already exist there.
- **`docs/design/`** holds one behavior-only doc per feature — observable
  inputs/outputs, interfaces, constraints, state transitions. No language,
  library, algorithm, or file-layout detail. Each doc carries an
  `## Implementation Notes` section that `feature-developer` appends to after
  implementing — this is where technical decisions, snags, and lessons live
  (the replacement for the old separate ADR/incident-log directories).
  `docs/decision-records/` and `docs/incident-logs/` are kept as historical
  reference only; no new entries are added to them.
- **`docs/prd.md`** is a single living file: product goals, scope boundaries,
  and links into `docs/design/`. Updated incrementally by `task-splitter`,
  never overwritten wholesale.
- Subagent return values are chosen per phase for what's actually useful to
  the caller — not a fixed "summary only" rule.

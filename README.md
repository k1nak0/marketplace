# Development Workflow Plugins

Two Claude Code plugins that together take a raw idea to a merged pull
request: **task-splitter** turns requirements into a behavior design and a set
of GitHub Issues, and **implementation-workflow** turns one of those Issues
into reviewed, committed code.

They're independent — either can be installed and used on its own.
`implementation-workflow` accepts a `task-splitter`-generated Map Issue, but
also works from a standalone requirement description.

---

## task-splitter

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding | Skill: `understand-requirements` | `requirements-report.md` |
| 2 | Behavior Design | Skill: `design-behavior` | `docs/design/<slug>.md` |
| 3 | Task Planning | Skill: `plan-tasks` | `task-breakdown-plan.md` |
| — | Confirm Gate | `AskUserQuestion` | go/no-go before Issue creation |
| 4 | Task Registration | Skill: `register-tasks` | Map Issue + Task Issues |

## implementation-workflow

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding | Skill: `requirement-understanding` | `requirements-report.md` |
| 2 | Codebase Investigation | Agent: `repository-explorer` | `impact-analysis-report.md` |
| 3 | Library Investigation | Agent: `library-researcher` | `library-usage-report.md` (conditional) |
| 4 | Implementation Planning | Skill: `implementation-planning` | `implementation-plan.md` |
| 5 | Implementation | Agent: `feature-developer` | modified source + doc updates |
| 6 | Automated Review | Agent: `code-reviewer` | `review-report.md` (loops to 5 on FAIL, up to 5x) |
| 7 | Human Review Gate | Orchestrator inline | `approve` / `request-changes` |
| 8 | Persistence | Agent: `persistence-engineer` | commit, push, PR |
| 9 | Map Issue Update | Orchestrator inline | flips the task row to `done` |

---

## Prerequisites

- Claude Code (latest)
- `gh` CLI, installed and authenticated with push/issue/PR access to your
  repository — both plugins use it directly instead of a bundled GitHub MCP
  server
- `git` configured with push access to your repository
- Optionally, a `docs/tool.md` in your project describing your test/lint
  commands and any project-specific MCP tools (code search, docs, browser/
  verification tools). Neither plugin ships its own MCP servers — this is how
  they discover what your project has available. If it's missing, both
  orchestrators print a starter template the first time they run; this is a
  nudge, not a requirement.

---

## Installation

```shell
/plugin install task-splitter@k1nak0
/plugin install implementation-workflow@k1nak0
```

---

## Usage

### Splitting an epic into tasks

```
/task-splitter:task-splitter
```

Walks through requirements → design → task breakdown → a confirmation
question → Map Issue + Task Issue creation on GitHub.

### Implementing a task

```
/implementation-workflow:implementation-workflow
```

Give it a Map Issue number/URL to pick up the next ready task from
`task-splitter`, or describe a standalone requirement to skip the Map Issue
entirely. Walks through investigation → planning → implementation → review →
your approval → commit/PR → (if it came from a Map Issue) marking that task
`done`.

### Resuming an interrupted run

Within the same session, `TaskList` still reflects progress — just ask the
orchestrator to continue. If the session itself restarted, there's no
automatic resume (neither plugin uses a startup hook): tell the orchestrator
which task to continue (`.claude/task-splitter/<task-id>/` or
`.claude/implementation-workflow/<task-id>/`), and it works out what's already
done from which files exist in that directory.

---

## Workspace Layout

Inter-phase artifacts are plain markdown/JSON files, not a state machine:

```
.claude/
├── task-splitter/<task-id>/
│   ├── requirements-report.md
│   ├── task-breakdown-plan.md
│   └── issue-map.json              # task → issue number, for register-tasks
└── implementation-workflow/<task-id>/
    ├── requirements-report.md
    ├── impact-analysis-report.md
    ├── library-usage-report.md     # if applicable
    ├── implementation-plan.md
    ├── modified-files.json
    ├── review-report.md
    └── blocked-report.md           # if the retry limit was exceeded
```

Design docs land in `docs/design/<slug>.md` (permanent, not scratch) —
behavior-only, with an `## Implementation Notes` section that
`feature-developer` appends technical decisions and lessons to after
implementing.

---

## Design Principles

1. **Behavior/implementation separation** — `docs/design/` describes what a
   feature does, never how it's built. `implementation-workflow` picks the
   how, per task, grounded in an actual codebase investigation.
2. **No bundled infrastructure** — no plugin-owned MCP servers, no hooks, no
   custom state machine. GitHub via `gh`, code/doc search via built-in tools
   or whatever the consuming project declares in `docs/tool.md`.
3. **One external action per confirmation** — Issue creation, commits, and PRs
   only happen after an explicit human go-ahead.
4. **Traceability** — every task is a GitHub Issue; every implementation has a
   PR referencing it.

---

## License

MIT

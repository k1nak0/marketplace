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
| 1 | Requirement Understanding & Task Selection | Skill: `requirement-understanding` | `requirements-report.md`; you pick the task and approve its content |
| 2 | Issue Refinement *(conditional)* | Skill: `issue-refinement` | rewritten Issues + design-doc updates, as their own PR |
| 3 | Branch Setup | Orchestrator inline | `<type>/<issue#>-<slug>` off the default branch |
| 4 | Codebase Investigation | Agent: `repository-explorer` | `impact-analysis-report.md` |
| 5 | Library Investigation | Agent: `library-researcher` | `library-usage-report.md` (conditional) |
| 6 | Implementation Planning | Skill: `implementation-planning` | `implementation-plan.md` |
| 7 | Test Authoring | Agent: `test-writer` | tests specifying the behaviour (+ CI, if absent) |
| 8 | Test Review Gate & Freeze | Orchestrator inline | you approve the tests → they're committed and frozen |
| 9 | Implementation | Agent: `implementer` | source changes; cannot modify the frozen tests |
| 10 | Automated Review | Agent: `code-reviewer` | `review-report.md` (verifies the freeze; loops to 9 on FAIL, up to 5x) |
| 11 | Human Review Gate | Orchestrator inline | `approve` / `request-changes` |
| 12 | History Cleanup & Persistence | Agent: `persistence-engineer` | regrouped history, push, PR |
| 13 | Map Issue Update | Orchestrator inline | flips the task row to `done` (map issue) or closes the standalone tracking issue |

### What's distinctive

- **You approve the task before work starts.** Phase 1 shows you the Issue and
  its own reading of it; if it's wrong, Phase 2 talks the change through, fixes
  every affected Issue, and brings `docs/design/` back in line as a separate PR.
- **Test-first, not TDD.** A separate agent writes the tests, *you* approve
  them, and they're committed before implementation begins. The implementer
  cannot edit them — if it thinks a test is wrong it has to say so and let you
  decide. The reviewer verifies the freeze mechanically.
- **Minimal footprint in version control.** Source code carries the *how*;
  plans, reports, and narrative live on the Issue and the PR. The *why* always
  lands in VCS — a source comment, a commit message, or an ADR under
  `docs/adr/` when reversing the decision would cost a human half a day.
- **Clean history.** Send-backs are expected and none of them survive: the
  branch is regrouped into a test commit plus implementation commits before
  every push.

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
your approval → commit/PR → marking that task `done` (Map Issue) or closing
its own tracking issue (standalone). A Map Issue task is claimed
(`in-progress`) as soon as it's selected, and flipped to `blocked` instead of
left dangling if implementation or review can't reach a resolution.

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
    ├── test-manifest.json          # frozen test files + the freeze commit SHA
    ├── verification-procedure.md   # manual strategy only
    ├── why-notes.md                # rationale bound for commit messages / the PR
    ├── modified-files.json
    ├── review-report.md
    ├── test-dispute.md             # if the implementer contests a frozen test
    └── blocked-report.md           # if the retry limit was exceeded
```

**Nothing under `.claude/` is ever committed.** What lands in the repository
permanently is only: source code, `docs/design/<slug>.md` (behavior-only, no
implementation notes), `docs/design/index.md`, `docs/prd.md`, and ADRs under
`docs/adr/`. Everything else that a human might want to read afterwards is on
the Issue or the PR by design — see each plugin's `docs/vcs-minimalism.md`.

---

## Design Principles

1. **Behavior/implementation separation** — `docs/design/` describes what a
   feature does, never how it's built. `implementation-workflow` picks the
   how, per task, grounded in an actual codebase investigation.
2. **The specification is approved before it can be bent** — tests are written
   by a different agent than the one that satisfies them, approved by a human,
   and frozen in a commit. An implementer that can edit the tests is grading
   its own work.
3. **Minimal footprint in version control** — the *how* is the source code and
   nothing else; the *why* always lands in VCS, routed to a comment, a commit
   message, or an ADR by how expensive it would be to reverse.
4. **The history is the change, not the work** — send-backs, retries, and
   review loops happen and are then regrouped away before anything is pushed.
5. **No bundled infrastructure** — no plugin-owned MCP servers, no hooks, no
   custom state machine, no tool allowlists (a sandbox is assumed). GitHub via
   `gh`, code/doc search via built-in tools or whatever the consuming project
   declares in `docs/tool.md`.
6. **One external action per confirmation** — Issue creation, commits, and PRs
   only happen after an explicit human go-ahead.
7. **Traceability** — every task is a GitHub Issue; every implementation has a
   PR referencing it.

---

## License

MIT

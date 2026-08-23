# Development Workflow Plugins

Three Claude Code plugins that take a raw idea to a merged pull request:
**task-splitter** turns requirements into a behavior design and a set of GitHub
Issues, **implementation-workflow** turns one of those Issues into reviewed,
committed code, and **light-workflow** takes a small change from a discussion
straight to a PR without the heavy gates.

They're independent — any one can be installed and used on its own.
`implementation-workflow` accepts a `task-splitter`-generated Map Issue, but
also works from a standalone requirement description. `light-workflow` needs
neither.

**Which one for this change?** If it came off a Map Issue, or it's big enough
that you'd want an approved test suite standing between the requirement and the
implementation, use `implementation-workflow`. If you'd have just made the
change yourself, use `light-workflow`.

---

## task-splitter

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding | Skill: `understand-requirements` | `requirements-report.md` |
| 2 | Behavior Design | Skill: `design-behavior` | `docs/design/<slug>.md` (uncommitted) |
| 3 | Task Planning | Skill: `plan-tasks` | `task-breakdown-plan.md` |
| — | Confirm Gate | `AskUserQuestion` | go/no-go before anything external |
| 4 | Design Doc PR | Orchestrator inline | branch `docs/<slug>`, one commit, PR opened |
| 5 | Task Registration | Skill: `register-tasks` | Map Issue + Task Issues |

## implementation-workflow

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 1 | Requirement Understanding & Task Selection | Skill: `requirement-understanding` | `requirements-report.md`; you pick the task and approve its content |
| 2 | Issue Refinement *(conditional)* | Skill: `issue-refinement` | rewritten Issues + design-doc updates, as their own PR |
| 3 | Branch Setup | Orchestrator inline | `<type>/<issue#>-<slug>` off the default branch |
| 4 | Codebase Investigation | Agent: `repository-explorer` | `impact-analysis-report.md` |
| 5 | Library Investigation | Agent: `library-researcher` | `library-usage-report.md` (conditional) |
| 6 | Implementation Planning | Skill: `implementation-planning` | `implementation-plan.md` |
| 7 | Test Authoring | Agent: `test-writer` | automated tests + `docs/manual-tests/<slug>.md` (+ CI, if absent) |
| 8 | Test Review Gate & Freeze | Orchestrator inline | you approve the specification → it's committed and frozen |
| 9 | Implementation | Agent: `implementer` | source changes; cannot modify the frozen specification |
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
- **Manual tests are tests.** An automated test is an executable document; a
  manual test procedure is a non-executable one, for behaviour a runner can't
  check. Both are committed — the manual ones to `docs/manual-tests/`, indexed
  and linked from your `README.md` — both are frozen at the same gate, and
  neither is the implementer's to edit. What *isn't* committed is the record of
  one execution; that goes to the PR.

The other two things that make it distinctive — what lands in version control,
and what the history looks like when it does — are shared with `task-splitter`
and covered under Design Principles below.

## light-workflow

| Phase | Name | Mechanism | Output |
|-------|------|-----------|--------|
| 0 | Branch Preparation | Orchestrator inline | a feature branch cut from the current tip of the default branch |
| 1 | Requirement Discussion | Orchestrator inline | a written-back understanding you confirm in one line |
| 2 | Implementation | Orchestrator inline | uncommitted changes, any draft ADR, a verification procedure |
| 3 | Approval Gate | Orchestrator inline | your `approve` / `request-changes` |
| 4 | Commit, Push, PR | Orchestrator inline | the commit series, the pushed branch, the PR |

### What's distinctive

- **It's the same philosophy with the ceremony removed.** No test freeze, no
  automated reviewer, no Issue lifecycle, no handoff files — but the *how*
  still lives only in source code, every *why* still lands in a comment, a
  commit message, or an ADR, and nothing is committed until you approve it.
- **One skill, no subagents.** Every phase runs in your conversation, because
  every phase might need to ask you something. When it hits a real fork — a
  data shape, a new dependency, a fix that would widen the scope — it stops and
  asks rather than deciding quietly.
- **No tests; a verification procedure instead.** It writes no test code (it
  does run whatever checks your project already has) and hands you a numbered
  procedure with concrete inputs and expected results, which then lives in the
  PR body. The trade-off is explicit: the change leaves behind no re-runnable
  check. When that matters, the run belongs in `implementation-workflow`.

---

## Prerequisites

- Claude Code (latest)
- `gh` CLI, installed and authenticated with push/issue/PR access to your
  repository — all three plugins use it directly instead of a bundled GitHub
  MCP server
- `git` configured with push access to your repository
- Optionally, a `docs/tool.md` in your project describing your test/lint
  commands and any project-specific MCP tools (code search, docs, browser/
  verification tools). None of the plugins ship their own MCP servers — this is
  how they discover what your project has available. If it's missing,
  `task-splitter` and `implementation-workflow` print a starter template the
  first time they run and `light-workflow` mentions it in one line; either way
  it's a nudge, not a requirement.

---

## Installation

```shell
/plugin install task-splitter@k1nak0
/plugin install implementation-workflow@k1nak0
/plugin install light-workflow@k1nak0
```

---

## Usage

### Splitting an epic into tasks

```
/task-splitter:task-splitter
```

Walks through requirements → design → task breakdown → a confirmation
question → a design-doc PR → Map Issue + Task Issue creation on GitHub. The
design docs are committed and pushed by the plugin, on their own branch; the
PR is opened for you and left for you to merge.

### Implementing a task

```
/implementation-workflow:implementation-workflow
```

Give it a Map Issue number/URL to pick up the next ready task from
`task-splitter`, or describe a standalone requirement to skip the Map Issue
entirely. Walks through investigation → planning → implementation → review →
your approval → commit/PR → marking that task `done` (Map Issue) or closing
its own tracking issue (standalone). A Map Issue task is claimed
(`in-progress`) once you've approved its content at the scrutiny gate — not
merely when it's selected, so a task you send back for rewriting isn't left
marked as in flight. It's flipped to `blocked` instead of left dangling if
implementation or review can't reach a resolution.

### Implementing a small change

```
/light-workflow:light-workflow <what you want built>
```

Prepares the branch, talks the requirement through with you, implements it —
asking whenever it hits a fork it shouldn't decide alone — then shows you the
uncommitted diff, the checks it ran, and a verification procedure, and waits
for your approval before it commits, pushes, and opens the PR. No Issue is
created, claimed, or closed.

### Resuming an interrupted run

Within the same session, `TaskList` still reflects progress — just ask the
orchestrator to continue. If the session itself restarted, there's no
automatic resume (no plugin uses a startup hook): tell the orchestrator
which task to continue (`.claude/task-splitter/<task-id>/` or
`.claude/implementation-workflow/<task-id>/`), and it works out what's already
done from which files exist in that directory.

`light-workflow` writes no such files, by design. After a restart, what's left
is the branch and the working tree — re-invoke it, name the branch, and it
reads the working tree and re-confirms the requirement before continuing.

---

## Workspace Layout

Inter-phase artifacts are plain markdown/JSON files, not a state machine.
`light-workflow` has none of this — it runs inline in one conversation and
keeps nothing on disk:

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
    ├── test-manifest.json          # frozen file lists + the freeze commit SHA
    ├── test-authoring-log.md       # test-writer's memory across its rounds
    ├── implementation-log.md       # implementer's memory across its rounds
    ├── why-notes.md                # rationale bound for commit messages / the PR
    ├── modified-files.json
    ├── review-report.md
    ├── test-dispute.md             # if the implementer contests a frozen test
    └── blocked-report.md           # if the retry limit was exceeded
```

The two `*-log.md` files are how agents keep continuity: every phase re-invokes
its agent as a **fresh context**, and the agent reads its own log before it
starts. There is no conversation to resume and no session state machine — which
is also why an interrupted run resumes from these files just as well as an
uninterrupted one continues.

**Nothing under `.claude/` is ever committed.** What lands in the repository
permanently is: source code, the test suite, `docs/manual-tests/<slug>.md` and
its index, `docs/design/<slug>.md` (behavior-only, no implementation notes),
`docs/design/index.md`, `docs/prd.md`, and ADRs under `docs/adr/` with their
index. Everything else that a human might want to read afterwards is on the
Issue or the PR by design — see each plugin's `docs/vcs-minimalism.md`.

---

## Design Principles

1. **Behavior/implementation separation** — `docs/design/` describes what a
   feature does, never how it's built. `implementation-workflow` picks the
   how, per task, grounded in an actual codebase investigation.
2. **The specification is approved before it can be bent** — tests are written
   by a different agent than the one that satisfies them, approved by a human,
   and frozen in a commit. An implementer that can edit the tests is grading
   its own work. (`implementation-workflow` only — this is precisely the
   guarantee `light-workflow` trades away, and the reason to reach for the
   heavier plugin.)
3. **Minimal footprint in version control** — the *how* is the source code and
   nothing else; the *why* always lands in VCS, routed to a comment, a commit
   message, or an ADR by how expensive it would be to reverse.
4. **The history is the change, not the work** — send-backs, retries, and
   review loops happen against an uncommitted working tree, and the whole
   change becomes commits for the first time at the end. Nothing has to be
   squashed away because the mess was never a commit.
5. **No bundled infrastructure** — no plugin-owned MCP servers, no hooks, no
   custom state machine, no tool allowlists (a sandbox is assumed). GitHub via
   `gh`, code/doc search via built-in tools or whatever the consuming project
   declares in `docs/tool.md`.
6. **One external action per confirmation** — Issue creation, commits, and PRs
   only happen after an explicit human go-ahead.
7. **Traceability** — every planned task is a GitHub Issue, and every change
   arrives as a PR carrying the reasoning that isn't in the diff.
   `light-workflow` skips the Issue and keeps the PR.

---

## License

MIT

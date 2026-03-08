# Universal Development Workflow Plugin

A Claude Code plugin that orchestrates a full development lifecycle — from raw user intent to committed, reviewed, and documented code — using a multi-agent pipeline with strict context isolation.

---

## What It Does

| Phase | Name | Mechanism | Model |
|-------|------|-----------|-------|
| 1 | Requirement Understanding | Skill: `/analyze-requirements` | sonnet |
| 2 | Codebase Investigation | Subagent: `repository-explorer` | sonnet |
| 3 | Library Investigation | Subagent: `library-researcher` | sonnet |
| 4 | Implementation Planning | Subagent: `implementation-architect` | opus |
| 5 | Implementation (TDD) | Subagent: `feature-developer` | sonnet |
| 6 | Automated Review | Subagent: `code-reviewer` | sonnet |
| 7 | Human Review Gate | Orchestrator (main session) | — |
| a-8/a-9 | Documentation & Persistence | Skill: `/doc-git-specialist` | fsonnet |
| b-8 | Fix Report (on major rejection) | Subagent: `post-mortem-analyst` | sonnet |

---

## Prerequisites

- Claude Code (latest)
- `jq` installed on the host (used by the SessionStart hook)
- `git` configured with push access to your repository

---

## Installation

### From the Marketplace

```shell
/plugin install dev-workflow@k1nak0
```

---

## Usage

### Starting a New Task

Run Phase 1 to begin:

```
/analyze-requirements
```

The skill will:
1. Generate a unique task ID (e.g., `task-20260308-143022`)
2. Create `.claude/workspaces/<task-id>/`
3. Conduct a structured interview (goals → features → constraints → DoD)
4. Write `requirements-report.md` and `status.json`

### Running the Pipeline

After Phase 1, the orchestrator (main Claude session) invokes each subsequent
phase in order using the `Agent` tool:

```
Phase 2: Use the repository-explorer subagent with input .claude/workspaces/<task-id>/requirements-report.md
Phase 3: Use the library-researcher subagent (skip if no external library needed)
Phase 4: Use the implementation-architect subagent
Phase 5: Use the feature-developer subagent
Phase 6: Use the code-reviewer subagent
Phase 7: Human review gate (see below)
Phase a-8/a-9: /doc-git-specialist <task-id>
```

### Phase 7 — Human Review Gate

After Phase 6 passes, the orchestrator displays:
- Git diff of all changed files
- GitHub Issue link (from `status.json`)
- Test result summary

You then choose one of three outcomes:

| Input | Action |
|-------|--------|
| `approve` | Run `/doc-git-specialist <task-id>` |
| `minor-fix` | Orchestrator resumes `feature-developer` via saved Context ID |
| `major-rework` | Orchestrator runs `post-mortem-analyst`, then restarts from Phase 4 |

### Resuming a Session

The SessionStart hook automatically loads the current task state when Claude Code
starts. If a task is in progress, you will see:

```
=== Active Task State ===
Task ID:       task-20260308-143022
Current Phase: phase-5
Status:        in_progress
GitHub Issue:  https://github.com/owner/repo/issues/42
========================
```

To resume, tell Claude which phase to continue from.

---

## Workspace Layout

All inter-phase data lives under `.claude/workspaces/<task-id>/`:

```
.claude/
└── workspaces/
    └── task-20260308-143022/
        ├── status.json                  # Task state, Context IDs, Issue/PR URLs
        ├── requirements-report.md       # Phase 1 output
        ├── impact-analysis-report.md    # Phase 2 output
        ├── library-usage-report.md      # Phase 3 output (if applicable)
        ├── implementation-plan.md       # Phase 4 output
        ├── review-report.md             # Phase 6 output
        ├── fix-report.md                # Phase b-8 output (if applicable)
        └── blocked-report.md            # Phase 5 output on retry failure (if applicable)
```

`status.json` schema:
```json
{
  "task_id": "<task-id>",
  "current_phase": "phase-5",
  "feature_developer_context_id": "<agent-id>",
  "github_issue_url": "https://github.com/...",
  "github_pr_url": null,
  "status": "in_progress"
}
```

---

## Design Principles

1. **Context purity** — Heavy work (investigation, generation, analysis) runs in
   isolated subagents. The main REPL context receives only structured summaries.

2. **Test-first** — Phase 5 writes failing tests before any implementation code.
   The loop continues until all tests pass.

3. **Persistence** — All inter-phase data is written to `.claude/workspaces/`
   so sessions can be interrupted and resumed without loss.

4. **Traceability** — Every plan is a GitHub Issue. Every implementation has a PR.
   Every rejection has a fix report posted as a GitHub comment.

---

## License

MIT

# CLAUDE.md

This file provides AI agent context for the k1nak0/marketplace repository.

---

## Dev-Workflow Plugin

The `dev-workflow` plugin implements a nine-phase software-development pipeline
that takes raw user intent through to a committed, reviewed, and documented pull
request. The orchestrator is the single entry point; invoke it via
`/dev-workflow:orchestrator`.

### Workflow Overview

The pipeline runs sequentially through the following phases. Each phase is
executed by either an agent (isolated subagent with its own context) or a skill
(runs inline in the main session). The orchestrator coordinates sequencing,
gates each phase on its predecessor's output, and persists state to `status.json`
after every transition.

| Phase | Name | Mechanism | Responsibility |
|-------|------|-----------|----------------|
| 1 | Requirement Understanding | Skill: `analyze-requirements` | Structured interview with the user; writes `requirements-report.md` and initialises `status.json` |
| 2 | Codebase Investigation | Agent: `repository-explorer` | Serena MCP symbol search; writes `impact-analysis-report.md` |
| 3 | Library Investigation *(conditional)* | Agent: `library-researcher` | Context7 MCP doc fetch; writes `library-usage-report.md`; skipped when no new library is required |
| 4 | Implementation Planning | Agent: `implementation-architect` (sonnet) | Reads all reports + `CLAUDE.md`; writes `implementation-plan.md`; creates GitHub Issue |
| 5 | Implementation (TDD) | Agent: `feature-developer` *(resumable)* | Red → Green TDD loop; saves Context ID to `status.json`; writes modified source files |
| 6 | Automated Review | Agent: `code-reviewer` | Independent review; classifies findings as Critical / Major / Minor; PASS/FAIL verdict; loops back to Phase 5 on FAIL |
| 7 | Human Review Gate | Orchestrator inline | Displays diff + Issue link + test summary; accepts `approve`, `minor-fix`, or `major-rework` via `AskUserQuestion` |
| a-8/a-9 | Documentation & Persistence | Skill: `doc-git-specialist` | Updates docs, commits, pushes, creates PR; sets `status = "completed"` |
| b-8 | Fix Report *(on major rejection)* | Agent: `post-mortem-analyst` | Root-cause analysis; writes `fix-report.md`; posts GitHub Issue comment; restarts from Phase 4 |

**Resume behaviour:** If a session is interrupted, re-invoke
`/dev-workflow:orchestrator`. It reads `.claude/.claude-status.json` → `status.json`
to detect the active task and offers to resume from the saved `current_phase`.

---

### File Structure

```
plugins/dev-workflow/
├── .claude-plugin/
│   └── plugin.json              — Plugin manifest: name, version, skills list,
│                                    agents list, mcpServers pointer
├── .mcp.json                    — MCP server configuration for context7, serena,
│                                    and github tools
├── agents/
│   ├── feature-developer.md     — TDD implementation agent; saves Context ID to
│   │                                status.json; resumable via Context ID
│   ├── library-researcher.md    — Context7-only agent; skipped when no new
│   │                                library is required
│   ├── repository-explorer.md   — Serena MCP-only agent; writes
│   │                                impact-analysis-report.md
│   ├── code-reviewer.md         — Independent reviewer; returns PASS/FAIL verdict
│   ├── implementation-architect.md — claude-sonnet agent; writes
│   │                                implementation-plan.md and GitHub Issue
│   └── post-mortem-analyst.md   — Runs on major-rework rejection; writes
│                                    fix-report.md and posts GitHub comment
├── hooks/
│   └── hooks.json               — Claude Code hook configuration
├── scripts/
│   └── session-start.sh         — Session startup script (runs at session open)
└── skills/
    ├── analyze-requirements/
    │   ├── SKILL.md             — Phase 1 skill: structured user interview;
    │   │                           writes requirements-report.md
    │   ├── reference.md         — Reference material for the skill
    │   └── templates/
    │       └── requirements-template.md — Markdown template for
    │                                       requirements-report.md
    ├── doc-git-specialist/
    │   ├── SKILL.md             — Phase a-8/a-9 skill: docs update + git
    │   │                           commit / push / PR creation
    │   └── reference.md         — Reference material for the skill
    └── orchestrator/
        └── SKILL.md             — Main entry point; nine-phase pipeline
                                    coordinator; human review gate
```

---

### Status/Workspace Schema

All persistent state lives under `.claude/`. Two files are used:

#### `.claude/.claude-status.json`

Static pointer file written once by `analyze-requirements` (Phase 1). Never
overwritten after creation. Acts as a stable index so every phase can locate
the workspace without explicit path passing.

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Unique task identifier, e.g. `task-20260308-223337` |
| `workspace` | string | Relative path to the workspace directory, e.g. `.claude/workspaces/task-20260308-223337` |

#### `.claude/workspaces/<task-id>/status.json`

Mutable state file updated by the orchestrator at every phase transition. Always
updated with `jq '. + {...}'` piped through a `.tmp` file — never overwritten
wholesale.

| Field | Type | Set by | Description |
|-------|------|--------|-------------|
| `task_id` | string | Phase 1 | Matches `.claude-status.json → task_id` |
| `current_phase` | string | Orchestrator (each transition) | Current pipeline position; valid values: `phase-1`, `phase-2`, `phase-3`, `phase-4`, `phase-5`, `phase-6`, `phase-7`, `phase-5-review-fix`, `phase-a8`, `phase-4-restart`, `phase-b8` |
| `feature_developer_context_id` | string \| null | Phase 5, Phase 6 fix loop, Phase 7 minor-fix | Agent Context ID for resuming the `feature-developer` agent |
| `github_issue_url` | string \| null | Phase 4 (`implementation-architect`) | URL of the GitHub Issue created for this task |
| `github_pr_url` | string \| null | Phase a-8/a-9 (`doc-git-specialist`) | URL of the Pull Request created |
| `status` | string | Phase 1 init; Phase b-8 restart; Phase a-9 complete | Overall task status: `in_progress`, `restarting`, or `completed` |
| `fix_report_path` | string | Phase b-8 (`post-mortem-analyst`) | Relative path to `fix-report.md`; present only after a major-rework cycle |

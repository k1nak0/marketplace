# Codex runtime adapter

This package reuses the original workflow's phase, artifact and approval contracts.
The operation examples in its documents are workflow pseudocode, not executable
Python or names of registered tools. Map them to the capabilities of this session:

- `run_skill(skill="plugin:step")`: read `skills/step/SKILL.md` in this
  installed package and follow it inline in the current conversation, resolving
  its links relative to that skill directory. No nested skill tool is required.
- `plan_add(subject=...)`, `plan_update(...)`, `plan_list`: maintain the
  session plan (use the available plan tool or a visible checklist). Preserve
  phase ordering; mark completion only after checking the required outputs.
- `ask_user`: ask in the conversation and wait when the answer is required.
  Use a question tool only when available and suitable. Prior authorization
  satisfies a gate; silence never satisfies a required approval.
- `delegate(role="name", prompt=...)`: read `agents/name.md` in this package
  and start a NEW native Codex subagent with the complete role body plus the
  supplied prompt. Use the default/general agent type; these role names are
  instructions, not registered Codex agent types. Use fresh context without
  parent conversation inheritance (for example `fork_context=false`, or the
  equivalent exposed by the host). Include the absolute workspace, policy docs,
  tool doc and role paths. Wait for completion, collect its report/result, check
  outputs, and close the agent before starting the next dependent phase.
  Every fix round is another new agent; logs on disk carry continuity.
  Never reuse the writer's context for its reviewer. All agents share the
  working tree; phases are sequential, including investigation and persistence.
  If native fresh subagents are unavailable, STOP before delegated phases and
  explain that independent review cannot be guaranteed. Offer a supported Codex
  client with subagents enabled; do not silently review the work yourself.
- `discover_tools`: inspect the session's exposed tools and use its tool-search
  capability if present. A project's docs/tools file describes a desired tool;
  it does not install or authenticate it. Fall back to built-in tools only when
  they can satisfy the task, otherwise report the missing capability.
- Use the shell for `rg`, `rg --files`, and file reads; use the host file-edit
  tool for edits. Use available web tools for search and page retrieval. Exact
  tool names differ between Codex CLI, IDE and desktop hosts.

Determine the installed package root from this skill's actual path (two parents
above SKILL.md's directory), not from the consuming project's working directory.
When shell examples use `WORKFLOW_PLUGIN_ROOT`, explicitly set that task-scoped
variable to the resolved absolute package root first. It is NOT a Codex-provided
environment variable. Resolve policy docs to `<package-root>/docs`; do not search
the consuming project for another installation. Pass absolute paths to agents.

Use AGENTS.md and any scoped AGENTS.override.md as Codex project instructions.
Run artifacts live under `.codex/workflow-runs/<workflow>/<task-id>/`; never stage them.
Existing Claude runs under .claude are not automatically migrated or resumed.
Keep the original test freeze, role boundaries, retry limits, issue contracts
and external-action approval rules. A plugin never grants sandbox permissions.

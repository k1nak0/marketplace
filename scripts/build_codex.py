#!/usr/bin/env python3
"""Build standalone Codex packages from the unchanged Claude plugin sources."""
import argparse
import difflib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/"

SANDBOX = """# Codex execution environment

Read this before writing files or calling network tools. The active Codex
session's permissions, sandbox, network policy and approval rules are authoritative.
Do not assume any host is reachable, home directories writable, or temporary
directories forbidden. Use only permitted paths. Request an approved escalation
when required; never bypass a restriction using another tool.

Keep scratch files and run artifacts untracked. Inspect all existing changes;
do not dismiss unfamiliar files as sandbox artifacts or discard user work.
Use explicit paths for staging, and explicit branch names for pushes. Upstream
tracking availability depends on the session, not on this plugin. Never force
push except with --force-with-lease after an authorized history rewrite.

Use available web search/page retrieval or a configured documentation MCP for
external documentation. If unavailable, report the missing capability rather
than pretending research succeeded. MCP configuration and authentication belong
to the consuming project/user; this package needs no bundled MCP servers.

The orchestrator and every delegated file-writing or network-calling role must
read this policy. User authorization and host instructions take precedence over
workflow confirmation defaults; do not ask again for actions already authorized.

## 1. Filesystem reads
Follow the active session's read permissions.
## 2. Filesystem writes
Use the working tree and permitted scratch locations only.
## 3. Network
Follow actual network policy; prefer available documentation tools.
## 4. Existing changes
Treat unfamiliar files as user work until inspected; never ignore by filename.
## 5. Pushes
Name the branch explicitly. No fixed claim about upstream tracking is made.
## 6. Readers
The orchestrator and all delegated roles read this document before execution.
"""

RUNTIME = """# Codex runtime adapter

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
"""


def adapt(text):
    replacements = {
        "${CLAUDE_PLUGIN_ROOT}": "${WORKFLOW_PLUGIN_ROOT}",
        "CLAUDE.md": "AGENTS.md",
        "Claude Code": "Codex",
        "~/.claude/projects/": "the session's permitted memory location",
        ".claude/": ".codex/workflow-runs/",
        "':!.claude'": "':!.codex/workflow-runs'",
        "AskUserQuestion": "ask_user",
        "TaskCreate": "plan_add", "TaskUpdate": "plan_update", "TaskList": "plan_list",
        "ToolSearch": "discover_tools", "WebSearch": "web search",
        "WebFetch": "web page retrieval",
        "`Grep`": "`rg`", "`Glob`": "`rg --files`", "`Read`": "the file reader",
        "Grep/Glob/Read": "rg/file discovery/file reading",
        "Skill(": "run_skill(", "Agent(": "delegate(",
        "subagent_type=": "role=",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"Read that output with `sandbox-environment.md` §4 in mind:.*?Anything else\n"
                  r"is somebody's uncommitted work", "Inspect every existing change; treat it as somebody's uncommitted work",
                  text, flags=re.S)
    text = re.sub(r"\*\*Read this plugin's `sandbox-environment.md` before you start\*\*.*?it will fail, not degrade\.",
                  "Read the supplied sandbox-environment.md before starting. Follow the active "
                  "network policy and available documentation tools. If research is blocked, "
                  "report it rather than bypassing the restriction.", text, flags=re.S)
    text = re.sub(r"This environment can't register upstream tracking\s*"
                  r"\(?`?sandbox-environment.md`?\s*§5\)?,?", "Use explicit branch names for pushes",
                  text)
    text = text.replace("this environment can't register upstream tracking (sandbox-environment.md §5)",
                        "explicit branch names avoid reliance on upstream configuration")
    text = text.replace("`-u` cannot register upstream in this\n  environment (`sandbox-environment.md` §5).",
                        "Do not rely on an upstream being configured.")
    text = text.replace("`-u` cannot register upstream\n  in this environment.",
                        "do not rely on an upstream being configured.")
    text = text.replace("^\\.claude/?$|^/\\.claude/?$", "^\\.codex/workflow-runs/?$|^/\\.codex/workflow-runs/?$")
    text = re.sub(r"/(task-splitter|implementation-workflow|light-workflow):([a-z-]+)",
                  lambda m: "$" + m[1] + ":" + m[2], text)
    return text


def frontmatter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError("Expected YAML frontmatter")
    fields = dict(line.split(":", 1) for line in match[1].splitlines() if ":" in line)
    return {key: value.strip() for key, value in fields.items()}, text[match.end():]


def outputs():
    result = {}
    entries = []
    for source in sorted((ROOT / "plugins").iterdir()):
        manifest = json.loads((source / ".claude-plugin/plugin.json").read_text())
        name = manifest["name"]
        dest = Path("codex/plugins") / name
        extension = {"interface": {"displayName": name,
                     "shortDescription": "Reusable development workflow for Codex"}}
        if name == "implementation-workflow":
            extension["onboardingSkill"] = "./skills/onboarding/SKILL.md"
        result[dest / "plugin.json"] = json.dumps({
            "$schema": SCHEMA + "plugin.schema.json",
            "name": name, "version": manifest["version"],
            "description": manifest["description"],
            "extensions": {"com.openai": extension},
        }, indent=2) + "\n"
        entries.append({"name": name, "source": {
            "source": "local", "path": "./" + dest.as_posix()},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity"})
        result[dest / "docs/codex-runtime.md"] = RUNTIME
        # No MCP or hooks exist today. Fail loudly if future source additions
        # require an explicit transport/event/schema migration.
        for pattern in ("**/*mcp*.json", "hooks/**/*", "commands/**/*"):
            if any(p.is_file() for p in source.glob(pattern)):
                raise ValueError(f"New component requires explicit migration: {source}/{pattern}")
        for folder in ("skills", "docs", "agents"):
            for path in sorted((source / folder).rglob("*.md")):
                relative = path.relative_to(source)
                content = path.read_text()
                if path.name == "SKILL.md":
                    fields, body = frontmatter(content)
                    content = ("---\nname: " + path.parent.name + "\ndescription: "
                               + json.dumps(adapt(fields["description"]), ensure_ascii=False)
                               + "\n---\n\n"
                               + "Read [the Codex runtime adapter](../../docs/codex-runtime.md) "
                               + "before following this workflow.\n" + adapt(body))
                    result[dest / "skills" / path.parent.name / "agents/openai.yaml"] = (
                        "policy:\n  allow_implicit_invocation: false\n")
                elif folder == "agents":
                    _, body = frontmatter(content)
                    content = ("Read [the Codex runtime adapter](../docs/codex-runtime.md) "
                               + "before starting this role.\n" + adapt(body))
                elif path.name == "sandbox-environment.md":
                    content = SANDBOX
                else:
                    content = adapt(content)
                result[dest / relative] = content
    result[Path(".agents/plugins/marketplace.json")] = json.dumps({
        "name": "k1nak0", "interface": {"displayName": "k1nak0 workflows"},
        "plugins": entries,
    }, indent=2) + "\n"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on stale generated packages")
    args = parser.parse_args()
    expected = outputs()
    stale = False
    for relative, content in expected.items():
        path = ROOT / relative
        actual = path.read_text() if path.exists() else ""
        if actual == content:
            continue
        if args.check:
            stale = True
            print("Out of date:", relative)
            print("".join(difflib.unified_diff(actual.splitlines(True),
                        content.splitlines(True), n=2)), end="")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    generated = {p.relative_to(ROOT) for p in (ROOT / "codex/plugins").rglob("*") if p.is_file()}
    unexpected = generated - expected.keys()
    if unexpected:
        print("Unexpected generated files (remove explicitly):", *sorted(unexpected), file=sys.stderr)
    if stale or unexpected:
        return 1
    print(f"{'Checked' if args.check else 'Built'} {len(expected)} Codex package files")
    return 0


if __name__ == "__main__":
    sys.exit(main())

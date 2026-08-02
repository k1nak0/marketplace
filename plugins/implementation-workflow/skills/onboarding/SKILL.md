---
name: onboarding
description: Set up a project to use implementation-workflow — verifies gh CLI/GitHub remote prerequisites and creates or updates docs/tool.md. Run once when adopting the plugin in a new project, or whenever docs/tool.md needs revisiting. Not part of the nine-phase pipeline; user-invoked directly.
model: sonnet
allowed-tools: AskUserQuestion, Glob, Grep, Read, Write, Edit, Bash
user-invocable: true
---

# Onboarding

You are the **Onboarder**. implementation-workflow's phases quietly assume two
things are in place: a working `gh` CLI pointed at a real GitHub repo (Phases
1, 4, 8, 9 all shell out to it), and a `docs/tool.md` telling later phases
which test/lint/build commands and MCP tools this specific project uses. Both
are currently only checked as a non-blocking nudge from inside
`requirement-understanding`. This skill is where a user actually resolves
that nudge, once, up front.

## Quick Reference

- Auto-detection heuristics per manifest file: [reference.md](reference.md)
- Template this skill fills in:
  [../orchestrator/templates/tool-template.md](../orchestrator/templates/tool-template.md)
  (the same file `requirement-understanding`/orchestrator print as a bare
  nudge — reused here rather than duplicated)

---

## Step 1 — Verify `gh` CLI Prerequisites

```bash
gh --version
gh auth status
git remote -v
gh repo view --json url 2>&1
```

Report each check as pass/fail. On any failure, tell the user the exact
command to run themselves (`gh auth login`, `git remote add origin <url>`,
etc.) — do not attempt to authenticate or add a remote on their behalf. This
is informational: continue to Step 2 regardless of the outcome here, but
call out clearly in the final summary if `gh` isn't usable yet, since Phases
1/4/8/9 of the main pipeline will fail without it.

## Step 2 — Check for `docs/tool.md`

```bash
test -f docs/tool.md && echo present || echo missing
```

**If present:** show the current contents and ask the user (`AskUserQuestion`,
options `["leave as-is", "update it"]`) whether to leave it or walk through an
update. If "leave as-is", skip to Step 4.

**If missing:** continue to Step 3.

## Step 3 — Populate `docs/tool.md`

1. Auto-detect Test / Lint / Build commands by inspecting the project's
   manifest files per the heuristics in [reference.md](reference.md)
   (`package.json`, `Makefile`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
   `Gemfile`, etc.). Propose what you found; ask the user to confirm or
   correct it rather than guessing silently — a wrong test command will
   silently break `feature-developer`'s Red→Green loop later.
2. Ask the user directly (these can't be inferred from files):
   - Does this project have a code-search MCP server configured (a symbol
     index, Serena, etc.)? If so, its name.
   - Does this project have a verification MCP tool (Playwright, a
     Godot MCP, etc.) for manual verification steps? If so, its name.
   - Anything else an automated agent should know before touching this repo
     (the "Notes" section) — optional, skip if the user has nothing to add.
3. Write `docs/tool.md` using
   [../orchestrator/templates/tool-template.md](../orchestrator/templates/tool-template.md)'s
   structure, filled in with the answers above. Leave a section's body empty
   (matching the template's placeholder comment) if nothing applies rather
   than inventing content.

## Step 4 — Summary

Report what's in place and what still needs the user's action:
- `gh` CLI: usable / needs `gh auth login` / needs a remote
- `docs/tool.md`: created / updated / left as-is, with its path

Nothing here writes to `.claude/implementation-workflow/` — that's created
per-task by `requirement-understanding` when a real run starts.

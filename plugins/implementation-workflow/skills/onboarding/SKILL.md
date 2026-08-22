---
description: Set up a project to use implementation-workflow — verifies gh CLI/GitHub remote prerequisites, reports CI and docs/adr readiness, checks for a root CLAUDE.md, and creates or updates docs/tool.md. Run once when adopting the plugin in a new project, or whenever project tooling changes. Not part of the thirteen-phase pipeline; user-invoked directly.
model: sonnet
user-invocable: true
---

# Onboarding

You are the **Onboarder**. implementation-workflow's phases quietly assume a
few things are in place: a working `gh` CLI pointed at a real GitHub repo
(Phases 1, 2, 6, 12 and 13 all shell out to it), a `docs/tool.md` telling
later phases which test/lint/build commands and MCP tools this project uses,
and — for the test-first gate to mean anything — CI that actually runs the
suite. All of these are otherwise only surfaced as non-blocking nudges mid-run.
This skill is where a user resolves them, once, up front.

## Quick Reference

- Auto-detection heuristics per manifest file: [reference.md](reference.md)
- Template this skill fills in:
  [../implementation-workflow/templates/tool-template.md](../implementation-workflow/templates/tool-template.md)
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
1/2/6/12/13 of the main pipeline will fail without it.

Also check that a work branch can be cut — the pipeline never commits to the
default branch, and Phase 3 refuses to start on a dirty tree:

```bash
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
git status --porcelain -- . ':!.claude' | head
```

## Step 2 — Check for a Root `CLAUDE.md`

```bash
test -f CLAUDE.md && echo present || echo missing
```

**If present:** nothing to do, move on to Step 3.

**If missing:** don't generate one yourself — that's the built-in `init`
skill's job, and duplicating it here would just create a second, likely
worse, code path for the same output. Tell the user to run `/init` first,
then continue to Step 3 regardless; note in the final summary that
`CLAUDE.md` is still missing so it isn't lost as a follow-up.

## Step 3 — Check for `docs/tool.md`

```bash
test -f docs/tool.md && echo present || echo missing
```

**If present:** show the current contents and ask the user (`AskUserQuestion`,
options `["leave as-is", "update it"]`) whether to leave it or walk through an
update. If "leave as-is", skip to Step 5.

**If missing:** continue to Step 4.

## Step 4 — Populate `docs/tool.md`

1. Auto-detect Test / Lint / Build commands by inspecting the project's
   manifest files per the heuristics in [reference.md](reference.md)
   (`package.json`, `Makefile`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
   `Gemfile`, etc.). Propose what you found; ask the user to confirm or
   correct it rather than guessing silently — a wrong test command will
   silently break `test-writer`'s red-confirmation step later.
2. Ask the user directly (these can't be inferred from files):
   - Does this project have a code-search MCP server configured (a symbol
     index, Serena, etc.)? If so, its name.
   - Does this project have a verification MCP tool (Playwright, a
     Godot MCP, etc.) for manual verification steps? If so, its name.
   - Anything else an automated agent should know before touching this repo
     (the "Notes" section) — optional, skip if the user has nothing to add.
3. Write `docs/tool.md` using
   [../implementation-workflow/templates/tool-template.md](../implementation-workflow/templates/tool-template.md)'s
   structure, filled in with the answers above. Leave a section's body empty
   (matching the template's placeholder comment) if nothing applies rather
   than inventing content.

## Step 5 — Report CI, ADR, and Manual-Test Readiness

Neither of these is created here — both are produced by the pipeline itself
when a task needs them — but a user adopting the plugin should know where they
stand before the first run.

```bash
ls .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null
test -d docs/adr && ls docs/adr/ || echo "no docs/adr yet"
test -d docs/manual-tests && ls docs/manual-tests/ || echo "no docs/manual-tests yet"
```

Report, without fixing:

- **CI.** Does a workflow run the test command from Step 4, on pull requests to
  the default branch? If not, tell the user that the first task with automated
  tests will include CI bootstrap in its test commit (per
  `../../docs/test-first.md`), so the first PR will carry a slightly larger
  diff than the feature alone.
- **`docs/adr/`.** If it doesn't exist, say that it'll be created by the first
  decision heavy enough to warrant one — the half-day test in
  `../../docs/vcs-minimalism.md` — and point them at that document so the bar
  isn't a surprise. If it exists but has no `index.md`, mention that too: the
  index is part of the ADR contract, and the first ADR this plugin writes will
  create it.
- **`docs/manual-tests/`.** Behaviour a test runner can't check gets a
  committed procedure here, indexed by `docs/manual-tests/index.md` and linked
  from `README.md` (`../../docs/test-first.md`). If the directory doesn't
  exist, say the first task with a manual test will create it along with the
  README link — so that link appearing in a feature PR isn't a surprise.
- **Legacy directories.** If `docs/decision-records/` or `docs/incident-logs/`
  exist, say they're read-only history: this plugin writes ADRs to `docs/adr/`
  and no longer produces incident logs at all.

## Step 6 — Offer to Ignore the Scratch Workspace

Each run writes its cross-phase handoff files to
`.claude/implementation-workflow/<task-id>/` — requirements report, impact
analysis, plan, test manifest, review report. They're working files, not
deliverables, and nothing in the pipeline ever commits them.

If `.gitignore` doesn't already cover `.claude/`, those files show up as
untracked in every `git status` for the rest of the project's life, and can be
swept into a commit by anyone who reaches for `git add -A`.

```bash
grep -qE '^\.claude/?$|^/\.claude/?$' .gitignore 2>/dev/null && echo covered || echo "not covered"
```

**If not covered**, ask with `AskUserQuestion` whether to add it — options
`["add .claude/ to .gitignore", "leave .gitignore alone"]`. On approval, append
a single entry with a comment saying what it is:

```gitignore
# Claude Code agent scratch workspaces (task-splitter / implementation-workflow)
.claude/
```

Do not edit `.gitignore` without asking, do not reorder or tidy what's already
there, and do not commit the change — mention it in the summary as an
uncommitted edit the user should include in their next commit.

If the project deliberately tracks something under `.claude/` (checked-in
settings, project-scoped agents or commands), say so rather than proposing the
blanket entry — `.claude/implementation-workflow/` and `.claude/task-splitter/`
are the narrower pair that covers only the scratch workspaces.

## Step 7 — Summary

Report what's in place and what still needs the user's action:

- `gh` CLI: usable / needs `gh auth login` / needs a remote
- Default branch and working-tree state: ready / dirty tree to resolve
- `CLAUDE.md`: present / missing (run `/init`)
- `docs/tool.md`: created / updated / left as-is, with its path
- CI: runs the test suite / exists but doesn't cover it / absent
- `docs/adr/` and its `index.md`: present / will be created on first need
- `docs/manual-tests/`: present / will be created on first need
- `.gitignore`: already covers `.claude/` / entry added (uncommitted) / left
  alone at the user's request

Nothing here writes to `.claude/implementation-workflow/` — that's created
per-task by `requirement-understanding` when a real run starts. Nothing here
commits, either; if `docs/tool.md` was created or changed, tell the user it's
an uncommitted change in their working tree, since Phase 3 of a run will
refuse to start on a dirty tree.

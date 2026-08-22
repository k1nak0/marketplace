---
name: implementation-workflow
description: Main entry point for implementation-workflow. Takes a task off a GitHub Map Issue (or a standalone requirement) through user scrutiny, optional Issue refinement, codebase investigation, planning, human-approved test-first specification, implementation against frozen tests, automated and human review, history cleanup, and PR. Invoke this skill to implement a task, or to resume one within the same session.
argument-hint: "<Map Issue number/URL, or a feature description>"
model: sonnet
user-invocable: true
---

# Implementation Workflow — Orchestrator

You are the **Orchestrator**. You drive a thirteen-phase pipeline from a task
someone wrote down to a reviewed PR with a history that looks like the change
rather than like the work. Every phase runs in an isolated subagent or an
inline skill; you coordinate, sequence, and gate them.

**Critical invariant:** create the full todo list before executing any phase.

Three things this pipeline refuses to do, which shape most of the routing
below:

1. **Start work on a task nobody looked at.** Phase 1 puts the Issue in front
   of the user; Phase 2 exists to fix it when they say no.
2. **Let the implementer define what "done" means.** The tests are written by
   a different agent, approved by a human, and frozen before implementation
   starts. Phase 10 verifies the freeze mechanically.
3. **Publish the shape of the work.** Everything is regrouped into a clean
   series before any push. Send-backs are expected; they just don't survive
   into the history.

---

## Phase Overview

| # | Name | Mechanism | Output |
|---|------|-----------|--------|
| 1 | Requirement Understanding & Task Selection | Skill: `requirement-understanding` | `requirements-report.md`, verdict `ready`/`needs-refinement` |
| 2 | Issue Refinement *(conditional)* | Skill: `issue-refinement` | revised Issues, design-doc PR (merged) |
| 3 | Branch Setup | Orchestrator inline | work branch cut from the default branch |
| 4 | Codebase Investigation | Agent: `repository-explorer` | `impact-analysis-report.md` |
| 5 | Library Investigation *(conditional)* | Agent: `library-researcher` | `library-usage-report.md` |
| 6 | Implementation Planning | Skill: `implementation-planning` | `implementation-plan.md`, Issue comment |
| 7 | Test Authoring | Agent: `test-writer` | test files + `test-manifest.json` |
| 8 | Test Review Gate & Freeze | Orchestrator inline | human approval → the test commit |
| 9 | Implementation | Agent: `implementer` *(resumable this session)* | source changes, `why-notes.md`, any ADR |
| 10 | Automated Review | Agent: `code-reviewer` | `review-report.md` (freeze verification first) |
| 11 | Human Review Gate | Orchestrator inline | approve / request-changes |
| 12 | History Cleanup & Persistence | Agent: `persistence-engineer` | clean series, push, PR |
| 13 | Map Issue Update | Orchestrator inline | task row → `done`, Issue closed |

### Agent/Skill Contracts

**`repository-explorer` / `library-researcher`** — investigate only, change
nothing. Return a path plus a short summary.

**`implementation-planning`** — runs inline (not isolated) so it can ask the
user directly when the test strategy is ambiguous.

**`test-writer`** — writes the specification as tests; no production code
beyond signature-only scaffolding. Resumable this session for gate feedback.

**`implementer`** — makes the frozen tests pass. Cannot modify them; escalates
via `test-dispute.md` instead. Resumable within this session via the `Agent`
tool's `resume` parameter — keep its returned agent/context ID in your working
context after each invocation; there's no file it's persisted to.

**`code-reviewer`** — fresh context, no access to the implementer's history.
Verifies the test freeze before reviewing anything else. FAIL on any
Critical/Major finding.

**`persistence-engineer`** — regroups the history, finalises ADRs, pushes,
opens the PR. Does not touch documentation content.

---

## Step 0 — Resolve the Shared Policy Docs

Every file-writing agent in this plugin is bound by three shared documents.
Resolve their location once and pass it into every agent prompt:

```bash
ls "${CLAUDE_PLUGIN_ROOT}/docs/" 2>/dev/null && echo "POLICY_DOCS=${CLAUDE_PLUGIN_ROOT}/docs"
```

If that comes back empty, `Glob` for `**/implementation-workflow/docs/vcs-minimalism.md`
and use its parent directory. Record the result as `POLICY_DOCS`. Every
`Agent(...)` prompt below includes the line:

```
Policy docs: <POLICY_DOCS>/  (vcs-minimalism.md, git-workflow.md, test-first.md)
```

## Step 0b — Check for `docs/tool.md`

Phase 1 runs this same check; if for any reason it hasn't:

```bash
test -f docs/tool.md && echo present || echo missing
```

If missing, print [templates/tool-template.md](templates/tool-template.md) and
continue regardless — non-blocking. Point the user at
`/implementation-workflow:onboarding` if they want to resolve it properly.

## Step 1 — Create the Todo List

```
TaskCreate(subject="Phase 1 — Requirement Understanding & Task Selection", ...)
TaskCreate(subject="Phase 2 — Issue Refinement (conditional)", ...)
TaskCreate(subject="Phase 3 — Branch Setup", ...)
TaskCreate(subject="Phase 4 — Codebase Investigation", ...)
TaskCreate(subject="Phase 5 — Library Investigation (conditional)", ...)
TaskCreate(subject="Phase 6 — Implementation Planning", ...)
TaskCreate(subject="Phase 7 — Test Authoring", ...)
TaskCreate(subject="Phase 8 — Test Review Gate & Freeze", ...)
TaskCreate(subject="Phase 9 — Implementation", ...)
TaskCreate(subject="Phase 10 — Automated Review", ...)
TaskCreate(subject="Phase 11 — Human Review Gate", ...)
TaskCreate(subject="Phase 12 — History Cleanup & Persistence", ...)
TaskCreate(subject="Phase 13 — Map Issue Update", ...)
```

## Step 2 — Execute Each Phase in Sequence

Mark `in_progress` before starting a phase, `completed` only once its output is
confirmed to exist. Never skip ahead.

### Phase 1

```
Skill(skill="implementation-workflow:requirement-understanding")
```

Read back: `verdict`, `TASK_ID`, `source_type`, the report path, and (for
`map-issue`) the Map Issue number, Task Issue number, and Task Issue title.
Keep all of these in your working context for the rest of the run.

- `verdict == ready` → Phase 3 (mark Phase 2 skipped).
- `verdict == needs-refinement` → Phase 2.

### Phase 2 — Issue Refinement (Conditional)

```
Skill(skill="implementation-workflow:issue-refinement")
```

Runs only on `needs-refinement`. It discusses the change with the user,
rewrites the Issues, updates `docs/design/`, ships those as their own PR, and
waits for that PR to merge.

When it returns:

- **The task was split or replaced** → re-run Phase 1 from the top. The
  selection itself has to be redone, not just the scrutiny gate.
- **Otherwise** → re-run Phase 1 to re-read the revised Issue and pass the
  scrutiny gate again. A second `needs-refinement` is legitimate; a third in
  one run means something is wrong with the task at a level this pipeline
  can't fix — say so and ask the user whether to continue or stop.
- **The doc PR is unmerged and the user chose to stop** → stop the run
  cleanly, telling them the task directory to resume from.

### Phase 3 — Branch Setup (Orchestrator Inline)

Nothing in this pipeline commits to the default branch.

```bash
git status --porcelain -- . ':!.claude'   # must be empty
BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin "$BASE"
git switch --create "<type>/<issue#>-<slug>" "origin/$BASE"
```

The `:!.claude` exclusion is required, not optional: Phase 1 created this run's
own scratch workspace under `.claude/implementation-workflow/<TASK_ID>/`, and
in a project whose `.gitignore` doesn't cover `.claude/` those files are
untracked. Without the exclusion this check would trip over the pipeline's own
working files every time.

- `<type>` is the Conventional Commits type this change will land as; `<slug>`
  is 3–5 kebab-case words from the Task Issue title; `<issue#>` is the Task
  Issue number (for `standalone`, the branch is cut now and renamed in Phase 6
  once the tracking Issue exists).
- **If the working tree isn't clean, stop.** Surface it and let the user deal
  with it — never stash, commit, or discard work you didn't create.
- Record `WORK_BRANCH` and `BASE` in your working context.

Full rules: `<POLICY_DOCS>/git-workflow.md`.

### Phase 4

```
Agent(subagent_type="repository-explorer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Policy docs: <POLICY_DOCS>/
Input: requirements-report.md
Output: .claude/implementation-workflow/<TASK_ID>/impact-analysis-report.md")
```

Confirm the report exists before continuing.

### Phase 5 (Conditional)

Read `requirements-report.md` → "External Dependencies". If "New library
required: no", log a skip and move on. Otherwise:

```
Agent(subagent_type="library-researcher",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Policy docs: <POLICY_DOCS>/
Input: requirements-report.md
Output: .claude/implementation-workflow/<TASK_ID>/library-usage-report.md")
```

### Phase 6

```
Skill(skill="implementation-workflow:implementation-planning")
```

Confirm `implementation-plan.md` exists. Record `TEST_STRATEGY`
(`automated`|`manual`), the CI readiness finding, and
`TRACKING_ISSUE_NUMBER` — the Task Issue number for `map-issue`, or the Issue
this phase just created for `standalone`. Every later phase that touches
GitHub uses `TRACKING_ISSUE_NUMBER` regardless of `source_type`.

For `standalone`, rename the branch now that the Issue number exists:
`git branch -m "<type>/<TRACKING_ISSUE_NUMBER>-<slug>"`.

### Phase 7 — Test Authoring

```
TEST_WRITER_RESULT = Agent(subagent_type="test-writer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Policy docs: <POLICY_DOCS>/
Input: implementation-plan.md, requirements-report.md")
```

Save the returned agent/context ID as `TEST_WRITER_CONTEXT_ID`. Confirm
`test-manifest.json` exists.

### Phase 8 — Test Review Gate & Freeze (Orchestrator Inline)

This gate is the point of the whole design. Give the user enough to actually
judge the specification, not just acknowledge it:

- Every test name paired with the behaviour it pins down (from
  `TEST_WRITER_RESULT`), so they can read the spec without opening files.
- `git diff` of the test files.
- The failure output proving each test fails for the right reason.
- What `test-writer` did about CI.
- Any acceptance criterion it could not express as a test, and any ambiguity it
  had to resolve by choosing an interpretation. **Surface these prominently** —
  they're the things that are cheap to fix now and expensive later.

For `manual` strategy, show `verification-procedure.md` instead of tests.

`AskUserQuestion`: "このテストで振る舞いを固定してよいですか？" Options:
`["approve — freeze the tests and start implementation", "request-changes — describe what the tests should say instead"]`.

**On `request-changes`:** collect the free-text feedback, then:

```
Agent(subagent_type="test-writer", resume=TEST_WRITER_CONTEXT_ID,
      prompt="Human reviewer requested: <feedback>. Amend the tests and re-confirm they fail for the right reason.")
```

Update `TEST_WRITER_CONTEXT_ID` and return to the start of Phase 8.

**On `approve` — create the freeze point:**

```bash
git add -- <test_files> <scaffold_files> <ci_files>   # from test-manifest.json
git commit -m "test(<scope>): <what behaviour is now specified>"
git rev-parse HEAD
```

Write that SHA into `test-manifest.json`'s `test_commit`. **Local commit only
— do not push.** Nothing is published until Phase 12.

**Manual strategy:** there is no test commit. Post
`verification-procedure.md` to the tracking Issue instead:
`gh issue comment <TRACKING_ISSUE_NUMBER> --body-file .claude/implementation-workflow/<TASK_ID>/verification-procedure.md`.

### Phase 9 — Implementation

```
IMPL_RESULT = Agent(subagent_type="implementer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Policy docs: <POLICY_DOCS>/
Input: implementation-plan.md, test-manifest.json
The tests at <test_commit> are frozen. You cannot modify them.")
```

Save the returned agent/context ID as `IMPL_CONTEXT_ID` — needed for the Phase
10 fix loop and the Phase 11 request-changes branch.

**If `test-dispute.md` was written:** the implementer believes a frozen test is
wrong. Show the user the dispute in full alongside the test it concerns, and
`AskUserQuestion`: `["amend the tests — the dispute is valid", "reject the dispute — implement against the tests as written"]`.

- **Amend:** resume `test-writer` with the dispute, re-run Phase 8's gate, then
  **amend the test commit** rather than adding a new one (`git add -- <test
  files>; git commit --amend --no-edit`), update `test_commit` in the manifest,
  and resume the implementer with the updated tests.
- **Reject:** resume the implementer with the user's reasoning and the
  instruction to implement against the tests as written.

**If `blocked-report.md` was written:** if `source_type == map-issue`, flip
this task's row in the Map Issue to `blocked` (same `gh issue edit` pattern as
Phase 13) so another run doesn't pick it up as ready. Surface the report and
ask whether to retry with adjusted constraints or go back to Phase 6. If the
user retries, flip the row back to `in-progress` first.

### Phase 10 — Automated Review

```
REVIEW_FIX_ATTEMPTS = 0
MAX_REVIEW_FIX_ATTEMPTS = 5
```

```
REVIEW_RESULT = Agent(subagent_type="code-reviewer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Policy docs: <POLICY_DOCS>/
Input: test-manifest.json, implementation-plan.md, modified-files.json")
```

**If the test freeze was violated** (reported first in the return): this is not
an ordinary FAIL. Tell the user plainly what was changed and show the diff —
an agent editing a human-approved specification is worth their attention even
though it's about to be reverted. Then resume the implementer with the
instruction to restore the frozen files exactly and either satisfy them as
written or file a `test-dispute.md`. Count it against
`REVIEW_FIX_ATTEMPTS` and re-run Phase 10.

**If FAIL:**

```
FIX_RESULT = Agent(subagent_type="implementer", resume=IMPL_CONTEXT_ID,
      prompt="Review report at .claude/implementation-workflow/<TASK_ID>/review-report.md.
Fix all Critical and Major findings, then re-verify. The test freeze still applies.")
```

Update `IMPL_CONTEXT_ID`, increment `REVIEW_FIX_ATTEMPTS`, re-run
`code-reviewer`.

- Still FAIL at `REVIEW_FIX_ATTEMPTS >= MAX_REVIEW_FIX_ATTEMPTS`:
  ```bash
  gh issue comment <TRACKING_ISSUE_NUMBER> --body-file - <<'COMMENT'
  Automated review could not reach PASS after 5 fix attempts. Persistent
  findings: <from the latest review-report.md>
  COMMENT
  ```
  If `source_type == map-issue`, also flip the row to `blocked`. Then tell the
  user directly and stop — this needs human intervention.
- Otherwise loop back to the start of Phase 10.

**If PASS:** continue to Phase 11.

### Phase 11 — Human Review Gate (Orchestrator Inline)

Show the user:

- `git diff <test_commit>..HEAD` — the implementation, separate from the
  specification they already approved.
- The test result (`N passing`) or the manual verification results per step.
- Any ADR the implementer wrote, in full. **An ADR is reviewed as carefully as
  code** — it's the artifact with the longest half-life in the repository.
- Anything the implementer flagged rather than resolved: doc contradictions, a
  design doc now out of step, an interpretation it had to choose.
- The Minor findings from `review-report.md` that were left unfixed.

`AskUserQuestion`: "この実装でPRを作成してよいですか？" Options:
`["approve — clean up history and open the PR", "request-changes — describe what needs to change"]`.

**On `request-changes`:**

```
FIX_RESULT = Agent(subagent_type="implementer", resume=IMPL_CONTEXT_ID,
      prompt="Human reviewer requested: <feedback>. Address and re-verify. The test freeze still applies.")
```

Update `IMPL_CONTEXT_ID`, re-run Phase 10, then return to Phase 11. Let the
commits pile up messily — Phase 12 regroups the whole series, so there is no
reason to keep the history tidy along the way.

If the feedback is really about the *specification* rather than the
implementation, route it to Phase 8's amend path instead — resume
`test-writer`, re-approve, amend the test commit.

### Phase 12 — History Cleanup & Persistence

```
Agent(subagent_type="persistence-engineer",
      prompt="Workspace: .claude/implementation-workflow/<TASK_ID>/
Policy docs: <POLICY_DOCS>/
source_type: <map-issue|standalone>
Tracking Issue: #<TRACKING_ISSUE_NUMBER>
Work branch: <WORK_BRANCH>   Base: <BASE>")
```

Confirm the PR URL comes back, and show the user the final commit series — the
history is the deliverable here as much as the code is.

If it reports an aborted rewrite or a rejected push, do not retry blindly:
surface the branch state and ask the user how to proceed.

### Phase 13 — Map Issue Update (Orchestrator Inline)

**If `source_type == standalone`:** no Map Issue table exists, but the
tracking Issue Phase 6 created still needs closing:

```bash
gh issue close <TRACKING_ISSUE_NUMBER> --comment "Implemented in <PR URL>."
```

Print the final summary and stop.

**If `source_type == map-issue`:**

```bash
gh issue view <map-issue-number> --json body
```

Flip this task's row to `done`, append the PR URL to Notes, and check whether
any other row's dependencies are now all `done` — call those out as
newly-unblocked in your summary.

```bash
gh issue edit <map-issue-number> --body-file - <<'MAP_BODY'
<updated body>
MAP_BODY
gh issue close <TRACKING_ISSUE_NUMBER> --comment "Implemented in <PR URL>."
```

Print the final summary: Task ID, PR URL, the commit series, Map/Task Issue
links, files changed, test/verification outcome, any ADR written, and any task
newly unblocked.

## Resuming Within a Session

If this orchestrator is interrupted and re-invoked in the same conversation,
`TaskList` still reflects prior progress — use it to see which phases are
`completed` and pick up from there.

If the session itself restarted there's no automatic resume. Ask which task
directory (`.claude/implementation-workflow/<task-id>/`) to continue, then
infer the position from what's on disk and in git:

| Evidence | Resume at |
|---|---|
| Only `requirements-report.md` | Phase 3 (check the branch exists first) |
| `implementation-plan.md`, no `test-manifest.json` | Phase 7 |
| `test-manifest.json` with `test_commit: null` | Phase 8's gate |
| `test_commit` set, `git log` shows only the test commit | Phase 9 |
| Implementation commits present, no `review-report.md` | Phase 10 |

Subagent context IDs do not survive a session restart: re-run `test-writer` or
`implementer` fresh, giving it the plan plus a note of what's already on disk.
The test freeze is unaffected — it lives in git, not in an agent's memory.

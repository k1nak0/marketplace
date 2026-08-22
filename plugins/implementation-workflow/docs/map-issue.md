# The Map Issue — Reading and Editing It

Shared policy. Any skill or agent in this plugin that reads or writes a
`task-splitter` Map Issue, a Task Issue, or a tracking Issue follows it.

The Map Issue is the pipeline's source of truth for what's next. It lives on
GitHub and is reached only through `gh` — this plugin ships no GitHub MCP
server.

§1 restates the table contract from `task-splitter`'s
`skills/register-tasks/templates/map-issue-template.md`. It is restated rather
than linked because the two plugins install independently and this one must be
able to read a Map Issue with `task-splitter` absent — **if you change the
table shape or the status vocabulary in one, change both.**

---

## 1. The Task Graph table

The table below is `task-splitter`'s Map Issue template. This plugin consumes
it and writes back two cells, `Status` and `PR`; it never restructures the
table beyond adding a missing `PR` column.

```
## Task Graph (topological order)

| # | Task | Issue | Depends on | Status | PR |
|---|------|-------|-----------|--------|----|
| 1 | Add X | #123 | - | done | <url> |
| 2 | Add Y | #124 | #123 | not-started | |
```

Parse each row into `{index, title, issue_number, depends_on: [issue_numbers],
status, pr}`. `Depends on: -` means no dependencies; multiple are
comma-separated.

**Statuses**, and nothing outside this vocabulary:
`not-started` → `in-progress` → `done`, plus `blocked` and `dropped`.

A row is **ready** when its status is `not-started` and every issue in its
`Depends on` is `done`. `in-progress` and `blocked` rows are never ready — an
`in-progress` row most likely means another session already has that task,
which is worth surfacing to the user rather than silently picking a different
one.

`dropped` rows stay in the table rather than being deleted, so a
`Depends on: #124` elsewhere still resolves to something.

If a table predates the `PR` column, add it — header, separator, and an empty
cell on every other row — rather than dropping a URL into Notes.

## 2. Who writes which cell, and when

| Cell | Written by | When |
|---|---|---|
| `Status` → `in-progress` | `requirement-understanding` (Phase 1) | after the user approves the task's content at the scrutiny gate — not merely when it's selected |
| `Status` → `blocked` | Orchestrator (Phase 9/10) | an unresolved halt: a blocked report, or the review-fix loop exceeding its cap |
| `Status` → `done` | Orchestrator (Phase 13) | after the PR is open |
| `Status` → `dropped` | `issue-refinement` (Phase 2) | the task became unnecessary |
| `PR` | `persistence-engineer` (Phase 12) | as soon as the PR URL exists |
| rows, titles, dependencies | `issue-refinement` (Phase 2) | a refinement reshaped the graph |

Claiming a row is best-effort, not a lock: two sessions reading the Map Issue
within the same few seconds could both see `not-started` and both claim it.
That's an acceptable gap given this plugin's "no custom state machine" design.

A halted task is flipped to `blocked` rather than left `in-progress` forever or
silently reverted to `not-started`. If the user retries it, flip it back to
`in-progress` first.

## 3. Editing an Issue body

There is no partial edit. Read the whole body, change what you need, write the
whole body back:

```bash
gh issue view <number> --json body -q .body      # read it, edit it, write it back
gh issue edit <number> --body-file - <<'ISSUE_BODY'
<full updated body>
ISSUE_BODY
```

Always `--body-file -` with a heredoc — never `--body "<inline string>"`, and
never a temp file. Markdown tables and code fences do not survive shell
escaping intact.

**Rewriting a body loses the old text**, and Issue bodies have no history a
reader will find. So every edit that changes *meaning* — as opposed to flipping
one status cell — is accompanied by a comment recording what changed and why:

```bash
gh issue comment <number> --body-file - <<'COMMENT'
**Changed:** <what, specifically>
**Why:** <the reason — the user's own words where they gave them>
COMMENT
```

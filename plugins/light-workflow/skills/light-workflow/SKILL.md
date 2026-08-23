---
description: Main entry point for light-workflow. Takes a requirement from a discussion with the user through implementation, a single human approval gate, and a commit/push/PR — with no test freeze, no automated review, and no Issue registration. Use for a change small or clear enough that implementation-workflow's gates would cost more than they buy, or to resume such a run within the same session.
argument-hint: "<what you want built, in a sentence or two>"
model: sonnet
user-invocable: true
---

# Light Workflow — Orchestrator

You drive a five-phase run from something the user wants to a pull request. You
do all of it yourself, inline: this plugin has no subagents and no sub-skills,
because every phase needs the user within reach.

**It is `implementation-workflow` with the heavy gates removed, not with the
principles removed.** What's gone is the test freeze, the separate-agent
review, the Issue lifecycle, and the workspace of handoff files. What stays,
unchanged:

1. **Source code is the only _how_ in VCS.** No plan, no report, no
   "what-I-did" document ever becomes a committed file.
2. **Every _why_ lands in VCS** — a source comment, a commit message body, or
   an ADR, chosen by [../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md) §2.
3. **Nothing reaches git history without the user's go-ahead**, and the history
   is the shape of the change, not the shape of the work.

**Critical invariant:** create the full todo list before executing any phase.

## Phase Overview

| # | Name | Output |
|---|------|--------|
| 0 | Branch Preparation | a feature branch cut from the current tip of the default branch |
| 1 | Requirement Discussion | a shared, written-back understanding of what to build — in the conversation, not in a file |
| 2 | Implementation | **uncommitted** source changes, any `draft` ADR, a verification procedure, source comments carrying local *why* |
| 3 | Approval Gate | the user's `approve` or `request-changes` |
| 4 | Commit, Push, PR | the commit series, the pushed branch, the PR URL |

### Quick Reference

- The discussion question bank, the "when do I stop and ask" test, the
  verification-procedure format, the PR body contract, and the full list of
  divergences from `implementation-workflow`: [reference.md](reference.md)
- What may land in VCS, the *why* routing, and the ADR rules:
  [../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md)

### What this plugin does not do

Do not invent these back in when a run feels like it wants them. If a change
genuinely needs them, say so and point the user at
`/implementation-workflow:implementation-workflow`:

- **No test code.** You write none, and you add no test file, unless the user
  asks for one in so many words. Verification is the procedure you hand the
  user at Phase 3 (`reference.md` §4). You do still *run* whatever the project
  already has — see Phase 2.
- **No GitHub Issue.** Nothing is created, claimed, closed, or marked `done`.
  If the user names an existing Issue, reference it (`Refs: #N`) and stop
  there.
- **No workspace directory.** No `.claude/light-workflow/` handoff files: the
  run lives in this conversation, the working tree, and the PR body.

---

## Step 0 — Look for `docs/tool.md`

```bash
test -f docs/tool.md && echo present || echo missing
```

If it's there, read it: it names the project's build/test/lint commands and any
project-specific MCP tools, and Phase 2 uses both. If it's missing, say so in
one line, mention `/implementation-workflow:onboarding` as the way to create
one, and continue — this never blocks, and this plugin does not print a
template for it.

## Step 1 — Create the Todo List

```
TaskCreate(subject="Phase 0 — Branch Preparation", ...)
TaskCreate(subject="Phase 1 — Requirement Discussion", ...)
TaskCreate(subject="Phase 2 — Implementation", ...)
TaskCreate(subject="Phase 3 — Approval Gate", ...)
TaskCreate(subject="Phase 4 — Commit, Push, PR", ...)
```

Mark `in_progress` before starting a phase and `completed` only once its output
actually exists.

---

## Phase 0 — Branch Preparation

Nothing here ever commits to the default branch, and no run starts from a
branch that is behind it.

```bash
git rev-parse --abbrev-ref HEAD
BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin "$BASE"
git status --porcelain -- . ':!.claude'
git merge-base --is-ancestor "origin/$BASE" HEAD && echo reuse || echo cut-new
```

Record `BASE`. Then, from those four answers:

| Situation | What you do |
|---|---|
| On a non-default branch that already contains `origin/$BASE` | **Reuse it.** This is a re-invocation or a branch the user prepared. Say which branch you're continuing on. |
| On the default branch, or on a branch that does not contain `origin/$BASE` (stale, or already merged) | **Cut a new one** from `origin/$BASE`. |
| Working tree dirty | Deal with it before either, below. |

To cut it:

```bash
git switch --create "<type>/<slug>" --no-track "origin/$BASE"
```

- `<type>` is the Conventional Commits type this change will land as — `feat`,
  `fix`, `refactor`, `perf`, `docs`, `chore`.
- `<slug>` is 3–5 kebab-case words for the change. There is no Issue number in
  the name, because this plugin creates no Issue.
- Derive both from the user's invocation text. **If they invoked the skill with
  nothing**, ask for a one-line description of the change before cutting —
  don't invent a name. Phase 1 may rename the branch (`git branch -m
  "<type>/<slug>"`) if the discussion changes the type or the scope; nothing is
  pushed until Phase 4, so that's free.

**If the working tree is dirty**, stop and show `git status`. Never stash,
commit, or discard work you didn't create. Ask the user with `AskUserQuestion`
whether those changes are part of this task (carry them onto the new branch and
continue) or someone else's work in progress (stop, and let them deal with it).

## Phase 1 — Requirement Discussion

The user brought a requirement, not a specification. This phase is the 壁打ち
that turns one into the other, and it is the only place where a
misunderstanding is still cheap.

**Read before you ask.** Spend a few minutes in the codebase first — `Grep` for
the feature name and the main symbols, `Read` the files that would change, skim
`docs/design/` for a doc that covers this area. A question you could have
answered from the repository burns the user's attention for nothing, and a
question grounded in a file you just read is worth answering.

Then run the discussion with `AskUserQuestion`, in small batches, until you can
state all five of these without guessing (question bank and worked examples in
[reference.md](reference.md) §1):

1. **What changes, observed from outside** — for a user, a caller, or an
   operator. Not which files you'll touch.
2. **What's explicitly out of scope** for this change.
3. **How anyone can tell it's done** — conditions checkable by looking or
   running something, not "works well".
4. **Constraints that bind the implementation** — compatibility, performance,
   a convention in the codebase, whether a new dependency is acceptable.
5. **Which existing behaviour must not change.**

Prefer offering two concrete interpretations over asking an open question. When
the user's answer implies a decision with consequences beyond this change, name
it as a decision — you'll be routing it to one of the three *why* channels in
Phase 2, and it's much easier to write down now.

Close the discussion by writing the understanding back in a short block the
user can correct in one line: the five points above, plus the branch name and
the `<type>`. Confirm it, adjust if they push back, and go. This is a
confirmation, not a gate — the gate is Phase 3.

If the discussion reveals the change is much larger than it looked — several
PRs' worth, or it needs a design doc first — say so plainly and offer
`/task-splitter:task-splitter`. Do not quietly build a third of it.

## Phase 2 — Implementation

Build it. You are the implementer here, working in the main conversation with
the user watching.

**Nothing is committed in this phase.** Read-only `git` (`status`, `diff`,
`log`) is fine; `git add`, `git commit`, `git stash` and anything that rewrites
history are not, and `git reset --hard` is never run on this branch — the whole
implementation is uncommitted, so it is the one command that can destroy it.
Phase 4 is where this becomes commits.

**Record the _why_ as you go, not at the end.** Per
[../../docs/vcs-minimalism.md](../../docs/vcs-minimalism.md) §2:

- Reasoning local to one file → a source comment, written *now*, in that file.
- Reasoning spanning several files → keep it in your working context, phrased
  as you'd write it, for Phase 4's commit message body.
- Anything that fails the half-day test → an ADR under `docs/adr/`, written
  with `**Status:** draft` and its row added to `docs/adr/index.md`. Phase 4
  flips it to `accepted` after the user approves.

A decision the *user* made in conversation is covered by exactly the same rule.
The chat log is not in VCS.

**When you get stuck, ask.** The test for what counts is in
[reference.md](reference.md) §2, and it is narrower than it sounds: a genuine
fork with materially different consequences, a contradiction between the
requirement and the code, a requirement nobody stated, a fix that would take
the change outside the agreed scope, or a new dependency. Anything you can
settle by reading the code, you settle by reading the code. Ask with
`AskUserQuestion`, with your recommendation as the first option and the actual
trade-off in the descriptions.

**Run whatever the project already has** before you call the phase done — the
build, the linter, the existing test suite (`docs/tool.md`, or the manifest and
CI config if there isn't one). You write no new tests; you do not get to skip
the ones that exist. Keep the real output — Phase 3 shows it.

**Draft the verification procedure** while the change is fresh: the numbered
steps a human runs to convince themselves this works, each with its expected
result. Format and an example in [reference.md](reference.md) §4. It goes to
the user at Phase 3 and into the PR body at Phase 4 — not into a committed
file.

## Phase 3 — Approval Gate

One gate, and it carries the weight of all the ones this plugin doesn't have.
Give the user enough to actually judge the change:

- **What changed, in behaviour terms**, against the understanding you confirmed
  at the end of Phase 1 — including anything that turned out differently.
- **The diff.** It's uncommitted, so:
  ```bash
  git status --porcelain -- . ':!.claude'
  git diff HEAD -- . ':!.claude'
  ```
  `git status` matters as much as `git diff` here — new files aren't in the
  diff until they're staged.
- **The checks you ran**, with their actual output. Say plainly if something
  failed or you skipped it.
- **The verification procedure**, in full, ready for the user to run.
- **Every decision you made and where its _why_ landed** — comment, commit
  message, or ADR. Show any ADR **in full**: it's the artifact with the longest
  half-life in the repository and deserves the same scrutiny as the code.
- **What you left out** — out-of-scope things you noticed, interpretations you
  had to choose, an existing `docs/design/` doc this change makes wrong.

Then `AskUserQuestion`:

> この実装でコミットしてPRを作成してよいですか？

Options: `["approve — commit, push, and open the PR", "request-changes — describe what needs to change"]`.

**On `request-changes`:** take the free-text feedback back to Phase 2, then
return here. There's no retry cap and no automated reviewer — the loop ends
when the user says it does. The work stays uncommitted throughout, so a
send-back leaves no trace in the history.

## Phase 4 — Commit, Push, PR

Only reached with an explicit `approve`.

**1. Finalise any ADR from this run.** Flip `draft` → `accepted`, update the
date, update its row in `docs/adr/index.md` — exactly those three edits, and
only for ADRs *this run* wrote.

**2. Build the commit series.** Staging is always explicit; nothing under
`.claude/` is ever staged.

```bash
git add -- <explicit paths>
git commit -m "<type>(<scope>): <summary>" -m "<body>"
```

One commit is fine. Split into several when the change has genuinely separable
parts, each building on its own — split by *meaning*, never by when you did the
work. The message format, and what belongs in the body, is in
[reference.md](reference.md) §5; the short version is that the body is where
every cross-file *why* from Phase 2 goes, with `Refs: ADR-NNNN` when one exists.

**3. Push.**

```bash
git push -u origin HEAD
```

`--force-with-lease`, never bare `--force`, and only after rewriting a branch
this run already pushed. If a push is rejected for any other reason (auth,
protected branch, network), surface the error and stop — do not retry with
`--force`.

**4. Open the PR** against `$BASE`, with the body contract from
[reference.md](reference.md) §3 — Summary, Why, Manual Verification, Checks
Run, Out of Scope. The verification procedure lives here permanently; this is
the only durable copy.

```bash
gh pr create --base "$BASE" --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "<same as the first commit's summary>" --body-file -
```

**Do not merge it.** Print the PR URL, the commit series
(`git log --oneline "origin/$BASE"..HEAD`), the files changed, and one line on
what the user still has to verify by hand.

---

## Resuming Within a Session

`TaskList` still reflects which phases completed — ask this skill to continue
and it picks up from there.

If the session itself restarted, there is nothing on disk to resume from: this
plugin writes no workspace files, and up to Phase 4 the implementation is
uncommitted. What survives is the branch and the working tree. Re-invoke the
skill, tell it the branch, and let it read `git status` / `git diff HEAD` to
see what's already built — then re-run Phase 1's confirmation briefly so you
are working from a stated requirement rather than a guess.

That's the cost of being light. A run you cannot afford to lose belongs in
`implementation-workflow`, where the specification is committed at its own gate
and the phases hand off through files.

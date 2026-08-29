# Git Workflow — Branches, Commits, and History

Shared policy. Any agent or skill in this plugin that runs `git` or `gh`
follows it. It exists so that what reaches the default branch is the *shape of
the change*, never the *shape of the work that produced it*.

This doc assumes the network and filesystem constraints in
`sandbox-environment.md` — read that one first if you haven't. It's why every
push below names the branch explicitly instead of `-u`, and why interactive
rebase (below) isn't an option.

---

## 1. Branches

**Nothing in this pipeline ever commits to the default branch.** A work branch
is cut in Phase 3, immediately after the task is confirmed, and every commit
this run produces lands on it.

```bash
BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin "$BASE"
git switch --create "<type>/<issue#>-<slug>" "origin/$BASE"
```

**Naming:** `<type>/<issue#>-<slug>`

- `<type>` — the Conventional Commits type the change will land as: `feat`,
  `fix`, `refactor`, `perf`, `docs`, `test`, `chore`.
- `<issue#>` — the tracking Issue number, no `#`.
- `<slug>` — 3–5 kebab-case words from the Issue title.

`feat/124-add-user-search`, `fix/301-null-session-on-logout`.

For a `standalone` run the Issue is created in Phase 6 before any commit
exists, so the same rule applies — the branch is cut in Phase 3 with a
placeholder-free name derived from the requirement, and renamed once the Issue
number is known if it isn't yet.

**Before cutting the branch**, verify the working tree is clean:

```bash
git status --porcelain -- . ':!.claude'   # must be empty
```

If it isn't, stop and surface it — do not stash, commit, or discard someone
else's work in progress. The `:!.claude` exclusion belongs on **every**
cleanliness check in this pipeline: the run's own scratch workspace lives under
`.claude/implementation-workflow/<task-id>/` and is untracked in any project
that doesn't gitignore `.claude/`, so a bare `git status --porcelain` would
report the pipeline's own handoff files as a dirty tree.

### The design-doc branch is separate

When Phase 2 (`issue-refinement`) revises Issues and design docs, those changes
go out as their **own** branch and PR (`docs/<issue#>-<slug>`), and the run
waits for that PR to be merged before Phase 3 cuts the implementation branch
from the updated default branch. Design-doc churn never appears in the
implementation PR's diff.

## 2. The shape of a finished PR

A PR from this pipeline reaches the reviewer as:

```
$ git log --oneline <base>..HEAD      # newest first, so read this bottom-up
<type>(<scope>): <implementation summary>          ← one or more, split by meaning
test(<scope>): <what behaviour is now specified>   ← always exactly one, oldest
```

- **The test commit is first in the series** (oldest — last line above, since
  `git log` prints newest first) **and is exactly one commit.** It contains the
  test files, the manual-test document under `docs/manual-tests/`, any
  signature-only scaffolding the tests need to compile, and — if the project
  had no CI able to run them — the CI configuration that now does.
- **The implementation commits follow.** One is fine; splitting into several is
  encouraged when the change has genuinely separable parts (each commit
  building and passing on its own). Never split them along the lines of *when
  you did the work*.
- Nothing else. No "fix review comment", no "wip", no "revert previous", no
  merge commits from the base branch.

## 3. Commit messages

```
<type>(<scope>): <summary — imperative mood, ≤72 chars, no trailing period>

<Body. Present tense. This is one of the three places the *why* lives — see
vcs-minimalism.md. Include the rationale for any decision that spans more than
one file in this commit and isn't heavy enough to warrant an ADR. Do not
narrate the *how*: the diff already says what changed.>

Refs: ADR-NNNN            <- when this commit implements a recorded decision
Closes #<tracking-issue>  <- on the last commit of the series only
```

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `chore`.

Staging is always explicit — `git add -- <paths>`, never `git add -A` or
`git add .`. Nothing under `.claude/` is ever staged.

## 4. Where the implementation gets committed

**Only one commit exists before Phase 13: the test commit.** The implementer
does not run `git` at all — its work sits in the working tree as uncommitted
changes and new files, through Phase 10, through every Phase 11 fix round, and
through every Phase 12 send-back. Phase 13 is where the implementation becomes
commits for the first time.

That is deliberate: nothing has to be squashed, reworded, or rebased away,
because the messy intermediate states were never commits to begin with. It
costs one thing — an interrupted session loses uncommitted work — and the
freeze point is unaffected, because the tests *are* committed.

The test commit itself is created the moment the human approves the tests at
Phase 9, and it is **local only** — nothing is pushed until the change has
cleared the human review gate and the history has been regrouped. The approved
tests are safe from a later rewrite either way: they are in a commit, in the
reflog, and in the recorded recovery SHA.

Two consequences you have to hold on to:

- **The regroup is a build, not a rewrite.** `git reset --soft` moves HEAD back
  over the test commit; the implementation is already in the working tree.
- **Never `git reset --hard` on this branch.** It is the one command that can
  destroy the implementation, because the implementation is not in any commit.

## 5. Rewriting history before you push

Work does not proceed in a straight line: automated review sends the
implementation back, the human gate sends it back, and sometimes a problem is
only visible once everything is assembled. **All of that is expected — it just
doesn't get to be part of the history.** Let the work be messy locally, then
regroup before it becomes visible.

**The invariant: `git log <base>..HEAD` matches §2 at the moment of every
push.** Not before, not after — every push.

### Regrouping

Work in `W=.claude/implementation-workflow/<task-id>`. Snapshot first, then
rebuild the series:

```bash
git rev-parse HEAD > "$W/pre-rewrite-head"          # recovery point for HEAD
BASE_SHA=$(git merge-base HEAD "origin/$BASE")

# Stage every path that belongs in the finished series — the union of
# test-manifest.json (test_files, manual_test_files, scaffold_files, ci_files)
# and modified-files.json. Explicit paths only; nothing under .claude/.
git add -- <all those paths>

# The snapshot is the *index* tree, not HEAD's tree: the implementation is
# uncommitted, so HEAD's tree does not contain it and comparing against HEAD
# would report every implementation file as a spurious difference.
git write-tree > "$W/pre-rewrite-tree"

git reset --soft "$BASE_SHA"   # HEAD moves back over the test commit
git restore --staged .         # unstage, keeping the working tree untouched

# then, once per commit in the target series:
git add -- <paths belonging to this commit>
git commit -m "..."
```

The first commit built this way is the test commit (test files, the
manual-test document, scaffolding, CI config); the rest are the implementation
commits, split by meaning.

**Verify: the tree at `HEAD` must be identical to the snapshot.**

```bash
if [ "$(git rev-parse HEAD^{tree})" = "$(cat "$W/pre-rewrite-tree")" ]; then
  echo "tree preserved"
else
  echo "SERIES DOES NOT MATCH THE SNAPSHOT"
  git diff "$(cat "$W/pre-rewrite-tree")" HEAD > "$W/regroup-discrepancy.diff"
fi
```

A mismatch means a path was missed, staged into the wrong commit, or picked up
that shouldn't have been. **Do not push, and do not `git reset --hard`.**
Recover non-destructively and hand it back:

```bash
git reset --soft "$(cat "$W/pre-rewrite-head")"   # HEAD back to the test commit
git restore --staged .                            # working tree untouched throughout
```

Then report the discrepancy, pointing at `regroup-discrepancy.diff`. The
orchestrator routes it back to Phase 10 — usually the cause is a file the
implementer created but left out of `modified-files.json`, which the
implementer is the one who can answer for.

Never use `git rebase -i` — interactive rebase isn't available in this
environment. The soft-reset regroup above needs no editor and is deterministic.

### Pushing

This environment can't register upstream tracking
(`sandbox-environment.md` §5), so every push names the branch explicitly —
never `-u`/`--set-upstream`, and never a bare `HEAD`:

```bash
git push origin "<branch-name>"                     # first push, and every push after
git push --force-with-lease origin "<branch-name>"  # after any rewrite of a pushed branch
```

- `--force-with-lease`, never bare `--force`.
- **Only ever force-push the work branch this run created.** Never the default
  branch, never a branch you didn't cut.
- If a push is rejected for a reason other than the lease (auth, protected
  branch, network), surface the error and stop. Do not retry with `--force`.

Once the PR is open and a reviewer sends the change back, the same regroup
applies, followed by `--force-with-lease`.
